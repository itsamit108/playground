"""
╔═══════════════════════════════════════════════════════════════╗
║  OVERTAKE — Multi-User Multimedia Note-Taking API            ║
║  Self-contained single-file FastAPI backend                  ║
║  Stack: FastAPI · SQLModel · PostgreSQL (RDS) · S3 · JWT     ║
╚═══════════════════════════════════════════════════════════════╝
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from io import BytesIO
from typing import List, Optional, Sequence

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field as PydanticField
from sqlmodel import (
    Field,
    Relationship,
    Session,
    SQLModel,
    col,
    create_engine,
    select,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://overtake:overtake123@localhost:4510/overtake_db",
)
AWS_ENDPOINT_URL: str = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
S3_BUCKET: str = os.getenv("S3_BUCKET_NAME", "overtake-media")

JWT_SECRET: str = os.getenv("JWT_SECRET_KEY", "super-secret-change-me-in-production")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MIN: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. DATABASE ENGINE & S3 CLIENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

engine = create_engine(DATABASE_URL, echo=False)


def get_s3_client():
    """Create a boto3 S3 client pointing at LocalStack."""
    return boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. ORM MODELS  (SQLModel — SQLAlchemy + Pydantic hybrid)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class User(SQLModel, table=True):
    """Application user."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=64)
    email: str = Field(index=True, unique=True, max_length=256)
    hashed_password: str = Field(max_length=256)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # relationships
    notes: List["Note"] = Relationship(back_populates="owner", cascade_delete=True)


class Note(SQLModel, table=True):
    """A user's note — can have rich text content + multimedia attachments."""

    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=256)
    content: str = Field(default="")
    is_pinned: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # foreign key
    user_id: int = Field(foreign_key="users.id", index=True)

    # relationships
    owner: Optional["User"] = Relationship(back_populates="notes")
    attachments: List["Attachment"] = Relationship(
        back_populates="note", cascade_delete=True
    )


class Attachment(SQLModel, table=True):
    """A multimedia file attached to a note, stored in S3."""

    __tablename__ = "attachments"

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=512)
    s3_key: str = Field(max_length=1024)
    content_type: str = Field(default="application/octet-stream", max_length=128)
    size_bytes: int = Field(default=0)
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # foreign key
    note_id: int = Field(foreign_key="notes.id", index=True)

    # relationships
    note: Optional["Note"] = Relationship(back_populates="attachments")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. PYDANTIC SCHEMAS  (request / response)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


# ── Auth ─────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = PydanticField(min_length=3, max_length=64)
    email: EmailStr
    password: str = PydanticField(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


# ── Notes ────────────────────────────────────────────────────
class NoteCreate(BaseModel):
    title: str = PydanticField(min_length=1, max_length=256)
    content: str = ""
    is_pinned: bool = False


class NoteUpdate(BaseModel):
    title: Optional[str] = PydanticField(default=None, max_length=256)
    content: Optional[str] = None
    is_pinned: Optional[bool] = None


class AttachmentResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentResponse] = []


class NoteListResponse(BaseModel):
    notes: list[NoteResponse]
    total: int
    page: int
    page_size: int


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. AUTH UTILITIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MIN)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    """Return user_id from a JWT, or raise 401."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


# ── FastAPI dependency: get current user from token ──────────
def get_session():
    """Yield a SQLModel database session."""
    with Session(engine) as session:
        yield session


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    user_id = decode_access_token(token)
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. APP LIFESPAN (create tables + ensure S3 bucket)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables & S3 bucket. Shutdown: nothing special."""
    # Create all tables
    SQLModel.metadata.create_all(engine)
    print("[OK] Database tables created / verified")

    # Ensure S3 bucket exists
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"[OK] S3 bucket '{S3_BUCKET}' already exists")
    except ClientError:
        s3.create_bucket(Bucket=S3_BUCKET)
        print(f"[OK] S3 bucket '{S3_BUCKET}' created")

    yield  # app runs here


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. FASTAPI APPLICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="Overtake",
    description="Multi-user multimedia note-taking API",
    version="0.1.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────────
# 7a. AUTH ENDPOINTS
# ─────────────────────────────────────────────────────────────


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
    summary="Register a new user",
)
def register(body: RegisterRequest, session: Session = Depends(get_session)):
    # Check uniqueness
    existing = session.exec(
        select(User).where(
            (col(User.username) == body.username) | (col(User.email) == body.email)
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already taken",
        )

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["Auth"],
    summary="Authenticate and receive JWT",
)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(col(User.username) == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(user.id)  # type: ignore[arg-type]
    return TokenResponse(access_token=token)


@app.get(
    "/auth/me",
    response_model=UserResponse,
    tags=["Auth"],
    summary="Get current user profile",
)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ─────────────────────────────────────────────────────────────
# 7b. NOTES ENDPOINTS
# ─────────────────────────────────────────────────────────────


def _get_user_note(note_id: int, user: User, session: Session) -> Note:
    """Fetch a note owned by the user or 404."""
    note = session.get(Note, note_id)
    if not note or note.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    return note


@app.post(
    "/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Notes"],
    summary="Create a new note",
)
def create_note(
    body: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = Note(
        title=body.title,
        content=body.content,
        is_pinned=body.is_pinned,
        user_id=current_user.id,  # type: ignore[arg-type]
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return _note_to_response(note, session)


@app.get(
    "/notes",
    response_model=NoteListResponse,
    tags=["Notes"],
    summary="List notes (with search & pagination)",
)
def list_notes(
    search: Optional[str] = Query(
        default=None, description="Search in title or content"
    ),
    is_pinned: Optional[bool] = Query(default=None, description="Filter pinned notes"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Base query — only this user's notes
    stmt = select(Note).where(col(Note.user_id) == current_user.id)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            col(Note.title).ilike(pattern) | col(Note.content).ilike(pattern)
        )
    if is_pinned is not None:
        stmt = stmt.where(col(Note.is_pinned) == is_pinned)

    # Count total
    count_results: Sequence[Note] = session.exec(stmt).all()
    total = len(count_results)

    # Paginate
    stmt = stmt.order_by(col(Note.updated_at).desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    notes: Sequence[Note] = session.exec(stmt).all()

    return NoteListResponse(
        notes=[_note_to_response(n, session) for n in notes],
        total=total,
        page=page,
        page_size=page_size,
    )


@app.get(
    "/notes/{note_id}",
    response_model=NoteResponse,
    tags=["Notes"],
    summary="Get a single note with its attachments",
)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = _get_user_note(note_id, current_user, session)
    return _note_to_response(note, session)


@app.put(
    "/notes/{note_id}",
    response_model=NoteResponse,
    tags=["Notes"],
    summary="Update a note",
)
def update_note(
    note_id: int,
    body: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = _get_user_note(note_id, current_user, session)

    if body.title is not None:
        note.title = body.title
    if body.content is not None:
        note.content = body.content
    if body.is_pinned is not None:
        note.is_pinned = body.is_pinned

    note.updated_at = datetime.now(timezone.utc)
    session.add(note)
    session.commit()
    session.refresh(note)
    return _note_to_response(note, session)


@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Notes"],
    summary="Delete a note and all its attachments",
)
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = _get_user_note(note_id, current_user, session)

    # Delete all S3 objects for this note's attachments
    s3 = get_s3_client()
    attachments = session.exec(
        select(Attachment).where(col(Attachment.note_id) == note.id)
    ).all()
    for att in attachments:
        try:
            s3.delete_object(Bucket=S3_BUCKET, Key=att.s3_key)
        except ClientError:
            pass  # best-effort cleanup

    session.delete(note)
    session.commit()
    return None


# ─────────────────────────────────────────────────────────────
# 7c. ATTACHMENT ENDPOINTS
# ─────────────────────────────────────────────────────────────


@app.post(
    "/notes/{note_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Attachments"],
    summary="Upload a multimedia file to a note",
)
async def upload_attachment(
    note_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = _get_user_note(note_id, current_user, session)

    # Read file
    file_bytes = await file.read()
    file_size = len(file_bytes)
    original_name = file.filename or "unnamed"
    content_type = file.content_type or "application/octet-stream"

    # Build unique S3 key
    ext = os.path.splitext(original_name)[1]
    s3_key = f"users/{current_user.id}/notes/{note.id}/{uuid.uuid4().hex}{ext}"

    # Upload to S3
    s3 = get_s3_client()
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=file_bytes,
        ContentType=content_type,
    )

    # Save metadata to DB
    attachment = Attachment(
        filename=original_name,
        s3_key=s3_key,
        content_type=content_type,
        size_bytes=file_size,
        note_id=note.id,  # type: ignore[arg-type]
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return attachment


@app.get(
    "/notes/{note_id}/attachments",
    response_model=list[AttachmentResponse],
    tags=["Attachments"],
    summary="List attachments for a note",
)
def list_attachments(
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    note = _get_user_note(note_id, current_user, session)
    attachments = session.exec(
        select(Attachment).where(col(Attachment.note_id) == note.id)
    ).all()
    return attachments


@app.get(
    "/attachments/{attachment_id}/download",
    tags=["Attachments"],
    summary="Download / stream an attachment file from S3",
)
def download_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    attachment = session.get(Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Verify ownership
    note = session.get(Note, attachment.note_id)
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Fetch from S3
    s3 = get_s3_client()
    try:
        s3_obj = s3.get_object(Bucket=S3_BUCKET, Key=attachment.s3_key)
    except ClientError:
        raise HTTPException(status_code=404, detail="File not found in storage")

    return StreamingResponse(
        BytesIO(s3_obj["Body"].read()),
        media_type=attachment.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{attachment.filename}"'
        },
    )


@app.delete(
    "/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Attachments"],
    summary="Delete an attachment",
)
def delete_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    attachment = session.get(Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Verify ownership
    note = session.get(Note, attachment.note_id)
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Delete from S3
    s3 = get_s3_client()
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=attachment.s3_key)
    except ClientError:
        pass  # best-effort

    session.delete(attachment)
    session.commit()
    return None


# ─────────────────────────────────────────────────────────────
# 7d. HEALTH CHECK
# ─────────────────────────────────────────────────────────────


@app.get("/health", tags=["Health"], summary="Health check")
def health():
    return {"status": "ok", "service": "overtake", "version": "0.1.0"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _note_to_response(note: Note, session: Session) -> NoteResponse:
    """Convert a Note ORM object to a NoteResponse with attachments."""
    attachments = session.exec(
        select(Attachment).where(col(Attachment.note_id) == note.id)
    ).all()
    return NoteResponse(
        id=note.id,  # type: ignore[arg-type]
        title=note.title,
        content=note.content,
        is_pinned=note.is_pinned,
        created_at=note.created_at,
        updated_at=note.updated_at,
        attachments=[
            AttachmentResponse(
                id=a.id,  # type: ignore[arg-type]
                filename=a.filename,
                content_type=a.content_type,
                size_bytes=a.size_bytes,
                uploaded_at=a.uploaded_at,
            )
            for a in attachments
        ],
    )


# Run with: fastapi dev main.py
