"""Attachment endpoints: upload, list, download, delete."""

from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, SessionDep, StorageDep
from app.schemas.common import AttachmentResponse
from app.services import attachment_service

router = APIRouter(tags=["Attachments"])


@router.post(
    "/notes/{note_id}/attachments",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a multimedia file to a note",
)
async def upload_attachment(
    note_id: int,
    current_user: CurrentUser,
    session: SessionDep,
    storage: StorageDep,
    file: UploadFile = File(...),
) -> AttachmentResponse:
    data = await file.read()
    attachment = attachment_service.upload_attachment(
        session,
        current_user,
        note_id,
        storage,
        filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        data=data,
    )
    return AttachmentResponse.model_validate(attachment, from_attributes=True)


@router.get(
    "/notes/{note_id}/attachments",
    response_model=list[AttachmentResponse],
    summary="List attachments for a note",
)
def list_attachments(
    note_id: int, current_user: CurrentUser, session: SessionDep
) -> list[AttachmentResponse]:
    attachments = attachment_service.list_attachments(session, current_user, note_id)
    return [
        AttachmentResponse.model_validate(a, from_attributes=True)
        for a in attachments
    ]


@router.get(
    "/attachments/{attachment_id}/download",
    summary="Download / stream an attachment from S3",
)
def download_attachment(
    attachment_id: int,
    current_user: CurrentUser,
    session: SessionDep,
    storage: StorageDep,
) -> StreamingResponse:
    attachment, data = attachment_service.get_attachment_bytes(
        session, current_user, attachment_id, storage
    )
    return StreamingResponse(
        BytesIO(data),
        media_type=attachment.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{attachment.filename}"'
        },
    )


@router.delete(
    "/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete an attachment",
)
def delete_attachment(
    attachment_id: int,
    current_user: CurrentUser,
    session: SessionDep,
    storage: StorageDep,
) -> None:
    attachment_service.delete_attachment(
        session, current_user, attachment_id, storage
    )
