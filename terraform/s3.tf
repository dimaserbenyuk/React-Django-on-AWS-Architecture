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

resource "aws_s3_bucket" "react_app" {
  bucket = "react-app-projectnext"
}

resource "aws_s3_bucket_website_configuration" "react_app" {
  bucket = aws_s3_bucket.react_app.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "react_app" {
  bucket = aws_s3_bucket.react_app.bucket

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "react_app" {
  bucket = aws_s3_bucket.react_app.bucket

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "cloudfront.amazonaws.com"
        },
        Action = "s3:GetObject",
        Resource = "${aws_s3_bucket.react_app.arn}/*",
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.react_app.arn
          }
        }
      }
    ]
  })
}

resource "aws_cloudfront_origin_access_control" "s3_access" {
  name                              = "react-app-access"
  description                       = "OAC for React S3"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}


resource "aws_cloudfront_distribution" "react_app" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "React frontend for projectnext.uk"
  default_root_object = "index.html"

  aliases = ["app.projectnext.uk"]

  origin {
    domain_name = "${aws_s3_bucket.react_app.bucket_regional_domain_name}"
    origin_id   = "s3-react-app"

    origin_access_control_id = aws_cloudfront_origin_access_control.s3_access.id
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-react-app"

    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn            = aws_acm_certificate.main.arn
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2021"
  }

  depends_on = [aws_acm_certificate_validation.main]
}
