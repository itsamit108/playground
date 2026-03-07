# ──────────────────────────────────────────────────────────
# Overtake Infrastructure — LocalStack (RDS PostgreSQL + S3)
# ──────────────────────────────────────────────────────────

# ── S3 Bucket for multimedia attachments ─────────────────
resource "aws_s3_bucket" "media" {
  bucket        = "overtake-media"
  force_destroy = true

  tags = {
    Project = "overtake"
    Env     = "local"
  }
}

# ── RDS PostgreSQL Instance ──────────────────────────────
resource "aws_db_instance" "postgres" {
  identifier              = "overtake-db"
  engine                  = "postgres"
  engine_version          = "16.1"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  db_name                 = "overtake_db"
  username                = "overtake"
  password                = "overtake123"
  port                    = 4510
  skip_final_snapshot     = true
  publicly_accessible     = true
  apply_immediately       = true

  tags = {
    Project = "overtake"
    Env     = "local"
  }
}

# ── Outputs ──────────────────────────────────────────────
output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "s3_bucket" {
  description = "S3 bucket for media"
  value       = aws_s3_bucket.media.bucket
}
