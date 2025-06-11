# ✅ 1. Hosted zone (если вы управляете зоной из Terraform — иначе уберите этот блок)
resource "aws_route53_zone" "main" {
  name = "projectnext.uk"
}

# ✅ 2. Data source to get zone ID (используется валидация и записи)
data "aws_route53_zone" "main" {
  name         = "projectnext.uk"
  private_zone = false
}

#✅ 3. ACM Certificate with SAN (*.projectnext.uk)
resource "aws_acm_certificate" "main" {
  domain_name               = "projectnext.uk"
  validation_method         = "DNS"
  subject_alternative_names = ["*.projectnext.uk"]

  lifecycle {
    create_before_destroy = true
  }
}

# ✅ 4. Route53 records for certificate validation (автоматически для всех SAN)
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }

  zone_id         = data.aws_route53_zone.main.zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 300
  records         = [each.value.record]
  allow_overwrite = true
}

# ✅ 5. Certificate validation step
resource "aws_acm_certificate_validation" "main" {
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

resource "aws_route53_record" "api_alias" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "api.projectnext.uk"
  type    = "A"

  alias {
    name                   = aws_alb.nginx_alb.dns_name
    zone_id                = aws_alb.nginx_alb.zone_id
    evaluate_target_health = true
  }
}


resource "aws_route53_record" "app_alias" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "app.projectnext.uk"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.react_app.domain_name
    zone_id                = aws_cloudfront_distribution.react_app.hosted_zone_id
    evaluate_target_health = false
  }
}
