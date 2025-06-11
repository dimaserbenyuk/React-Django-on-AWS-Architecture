resource "random_id" "bucket_suffix" {
  byte_length = 4 # 4 bytes = 8 hex chars
}

resource "aws_s3_bucket" "django-invoice" {
  bucket = "django-invoice-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "django-invoice" {
  bucket = aws_s3_bucket.django-invoice.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_ownership_controls" "django-invoice" {
  bucket = aws_s3_bucket.django-invoice.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "django-invoice" {
  bucket = aws_s3_bucket.django-invoice.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_policy" "django-invoice" {
  bucket = aws_s3_bucket.django-invoice.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "AllowPublicReadForStaticAssets"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.django-invoice.arn}/static/*"
      },
      {
        Sid    = "AllowECSAccess"
        Effect = "Allow"
        Principal = {
          AWS = [
            aws_iam_role.celery_execution_role.arn,
            aws_iam_role.ecs_task_execution_role.arn
          ]
        }
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.django-invoice.arn}",
          "${aws_s3_bucket.django-invoice.arn}/*"
        ]
      }
    ]
  })
}


resource "aws_s3_bucket_cors_configuration" "django_invoice_cors" {
  bucket = aws_s3_bucket.django-invoice.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "POST", "PUT", "HEAD"]
    allowed_origins = [
      "http://localhost:5173",
      "http://localhost:3000",
      "http://127.0.0.1:8000"
    ]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
