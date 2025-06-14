# ============================
# ECS FARGATE + Django WORKER
# ============================

resource "aws_ecs_cluster" "django-cluster" {
  name = "django-cluster"
  tags = {
    environment = "development"
  }
}

resource "aws_ecs_task_definition" "django-worker" {
  family                   = "django-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.celery_execution_role.arn

  container_definitions = jsonencode([
    {
      name         = "django"
      image        = "272509770066.dkr.ecr.us-east-1.amazonaws.com/django-backend:latest"
      essential    = true
      command      = ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2", "--timeout=120", "--log-level=info"]
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]
      environment = [
        { name = "DJANGO_ENV", value = "prod" },
        { name = "DJANGO_SETTINGS_MODULE", value = "backend.settings.prod" },
        { name = "CSRF_TRUSTED_ORIGINS", value = "https://api.projectnext.uk,https://projectnext.uk,https://api.projectnext.uk/admin" },
        { name = "ALLOWED_HOSTS", value = "*" },
        { name = "USE_S3", value = "TRUE" }, 
        { name = "DEBUG", value = "true" }, 
        { name = "AWS_STORAGE_BUCKET_NAME", value = "django-invoice-d4aa5bee" }
      ],
      secrets = [
        { name = "SECRET_KEY", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SECRET_KEY" },
        { name = "DJANGO_SU_NAME", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SU_NAME" },
        { name = "DJANGO_SU_EMAIL", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SU_EMAIL" },
        { name = "DJANGO_SU_PASSWORD", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SU_PASSWORD" },
        { name = "POSTGRES_DB", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_DB" },
        { name = "POSTGRES_USER", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_USER" },
        { name = "POSTGRES_PASSWORD", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_PASSWORD" },
        { name = "POSTGRES_HOST", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_HOST" },
        { name = "POSTGRES_PORT", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_PORT" }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = "/ecs/django",
          awslogs-region        = "us-east-1",
          awslogs-stream-prefix = "django"
        }
      }
    }
  ])
  tags = {
    environment = "development"
  }
}

resource "aws_ecs_task_definition" "django_migrate" {
  family                   = "django-migrate"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.celery_execution_role.arn

  container_definitions = jsonencode([
    {
      name         = "django-migrate"
      image        = "272509770066.dkr.ecr.us-east-1.amazonaws.com/django-backend:latest"
      essential    = true
      command      = ["python", "manage.py", "migrate"]
      environment = [
        { name = "DJANGO_ENV", value = "prod" },
        { name = "DJANGO_SETTINGS_MODULE", value = "backend.settings.prod" },
        { name = "DEBUG", value = "false" }
      ],
      secrets = [
        { name = "SECRET_KEY", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SECRET_KEY" },
        { name = "POSTGRES_DB", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_DB" },
        { name = "POSTGRES_USER", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_USER" },
        { name = "POSTGRES_PASSWORD", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_PASSWORD" },
        { name = "POSTGRES_HOST", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_HOST" },
        { name = "POSTGRES_PORT", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_PORT" }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = "/ecs/migrate",
          awslogs-region        = "us-east-1",
          awslogs-stream-prefix = "migrate"
        }
      }
    }
  ])

  tags = {
    environment = "production"
  }
}


###

resource "aws_ecs_task_definition" "celery-worker" {
  family                   = "celery-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.celery_execution_role.arn

  container_definitions = jsonencode([
    {
      name         = "celery"
      image        = "272509770066.dkr.ecr.us-east-1.amazonaws.com/django-backend:latest"
      essential    = true
      command      = ["celery", "-A", "backend", "worker", "--loglevel=info"]
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]
      environment = [
        { name = "DJANGO_ENV", value = "prod" },
        { name = "DJANGO_SETTINGS_MODULE", value = "backend.settings.prod" },
        { name = "AWS_SQS_REGION", value = "us-east-1" },
        { name = "AWS_ACCOUNT_ID", value = "272509770066" },
        { name = "SQS_QUEUE_NAME", value = "celery-prod-queue.fifo" },
        { name = "AWS_CELERY_ROLE_ARN", value = aws_iam_role.celery_worker_role.arn },
        { name = "DEBUG", value = "true" }, 
        { name = "AWS_STORAGE_BUCKET_NAME", value = "django-invoice-d4aa5bee" },
        { name = "USE_S3", value = "TRUE" }
      ],
      secrets = [
        { name = "AWS_ACCESS_KEY_ID", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/AWS_ACCESS_KEY_ID" },
        { name = "AWS_SECRET_ACCESS_KEY", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/AWS_SECRET_ACCESS_KEY" },
        { name = "POSTGRES_DB", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_DB" },
        { name = "POSTGRES_USER", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_USER" },
        { name = "POSTGRES_PASSWORD", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_PASSWORD" },
        { name = "POSTGRES_HOST", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_HOST" },
        { name = "POSTGRES_PORT", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/POSTGRES_PORT" }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = "/ecs/celery",
          awslogs-region        = "us-east-1",
          awslogs-stream-prefix = "celery"
        }
      }
    }
  ])
  tags = {
    environment = "development"
  }
}

# ✅ execution role (нужна для доступа к ECR, logs и т.п.)
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ✅ ECS Service
resource "aws_ecs_service" "django_service" {
  name                   = "django-service"
  cluster                = aws_ecs_cluster.django-cluster.id
  task_definition        = aws_ecs_task_definition.django-worker.arn
  launch_type            = "FARGATE"
  desired_count          = 1
  enable_execute_command = true

  network_configuration {
    subnets          = [aws_subnet.private1.id, aws_subnet.private2.id]
    assign_public_ip = false
    security_groups  = [aws_security_group.celery_sg.id]
  }
  load_balancer {
    target_group_arn = aws_alb_target_group.nginx_tg.arn
    container_name   = "django"
    container_port   = 8000
  }
  depends_on = [
    aws_alb_listener.nginx_https
  ]
}

###

resource "aws_ecs_service" "celery_service" {
  name                   = "celery-service"
  cluster                = aws_ecs_cluster.django-cluster.id
  task_definition        = aws_ecs_task_definition.celery-worker.arn
  launch_type            = "FARGATE"
  desired_count          = 1
  enable_execute_command = true

  network_configuration {
    subnets          = [aws_subnet.private1.id, aws_subnet.private2.id]
    assign_public_ip = false
    security_groups  = [aws_security_group.celery_sg.id]
  }
  # load_balancer {
  #   target_group_arn = aws_alb_target_group.nginx_tg.arn
  #   container_name   = "django"
  #   container_port   = 8000
  # }
  # depends_on = [
  #   aws_alb_listener.nginx_https
  # ]
}

resource "aws_alb" "nginx_alb" {
  name               = "nginx-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.public1.id, aws_subnet.public2.id]
  security_groups    = [aws_security_group.load-balancer.id]
}

resource "aws_alb_target_group" "nginx_tg" {
  name        = "nginx-target-group"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200"
  }
}

resource "aws_alb_listener" "nginx_https" {
  load_balancer_arn = aws_alb.nginx_alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate_validation.main.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.nginx_tg.arn
  }
}
resource "aws_cloudwatch_log_group" "nginx_log_group" {
  name              = "/ecs/nginx"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "migrate_log_group" {
  name              = "/ecs/migrate"
  retention_in_days = 7
}
resource "aws_cloudwatch_log_group" "celery_log_group" {
  name              = "/ecs/celery"
  retention_in_days = 7
}

resource "aws_security_group" "load-balancer" {
  name        = "load_balancer_security_group"
  description = "Controls access to the ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ✅ CloudWatch Logs
resource "aws_cloudwatch_log_group" "django_logs" {
  name              = "/ecs/django"
  retention_in_days = 7
}

resource "aws_iam_policy" "ssm_access" {
  name = "ecs-ssm-access"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter"
        ],
        Resource = [
          "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_ssm" {
  role       = aws_iam_role.celery_execution_role.name
  policy_arn = aws_iam_policy.ssm_access.arn
}

data "aws_caller_identity" "current" {}

resource "aws_iam_policy_attachment" "attach_ssm_exec" {
  name       = "attach-ssm-exec-role"
  roles      = [aws_iam_role.ecs_task_execution_role.name]
  policy_arn = aws_iam_policy.ssm_access.arn
}

