resource "random_id" "bucket_suffix" {
  byte_length = 4 # 4 bytes = 8 hex chars
}

resource "aws_s3_bucket" "django-invoice" {
  bucket = "django-invoice-${random_id.bucket_suffix.hex}"
}

resource "aws_s3_bucket_public_access_block" "django-invoice" {
  bucket = aws_s3_bucket.django-invoice.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
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
        Sid       = "AllowS3Access"
        Effect    = "Allow"
        Principal = "*"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.django-invoice.arn}",
          "${aws_s3_bucket.django-invoice.arn}/static/*"
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
