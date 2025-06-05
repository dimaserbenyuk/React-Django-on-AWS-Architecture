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
        Sid       = "AllowSSLRequestsOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          "${aws_s3_bucket.django-invoice.arn}",
          "${aws_s3_bucket.django-invoice.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}
