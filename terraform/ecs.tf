# ============================
# ECS FARGATE + Django WORKER
# ============================

resource "aws_ecs_cluster" "celery_cluster" {
  name = "django-cluster"
  tags = {
    environment = "development"
  }
}

resource "aws_ecs_task_definition" "celery_worker" {
  family                   = "django-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.celery_role.arn

  container_definitions = jsonencode([
    {
      name      = "django"
      image     = "272509770066.dkr.ecr.us-east-1.amazonaws.com/django-backend:latest"
      essential = true
      command      = ["python", "manage.py", "runserver", "0.0.0.0:8000"]
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]
      environment = [
        { name = "DJANGO_ENV", value = "dev" },
        { name = "DJANGO_SETTINGS_MODULE", value = "backend.settings.dev" }
      ],
      secrets = [
        { name = "SECRET_KEY", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SECRET_KEY" },
        { name = "DJANGO_SU_NAME", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SU_NAME" },
        { name = "DJANGO_SU_EMAIL", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SU_EMAIL" },
        { name = "DJANGO_SU_PASSWORD", valueFrom = "arn:aws:ssm:us-east-1:${data.aws_caller_identity.current.account_id}:parameter/django/dev/SU_PASSWORD" }
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
    # {
    #   name         = "nginx"
    #   image        = "272509770066.dkr.ecr.us-east-1.amazonaws.com/django-nginx:latest"
    #   essential    = true
    #   cpu          = 10
    #   memory       = 128
    #   portMappings = [{ containerPort = 80, protocol = "tcp" }]
    #   dependsOn    = [{ containerName = "django", condition = "START" }]
    #   logConfiguration = {
    #     logDriver = "awslogs",
    #     options = {
    #       awslogs-group         = "/ecs/nginx",
    #       awslogs-region        = "us-east-1",
    #       awslogs-stream-prefix = "nginx"
    #     }
    #   }
    # }
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
  cluster                = aws_ecs_cluster.celery_cluster.id
  task_definition        = aws_ecs_task_definition.celery_worker.arn
  launch_type            = "FARGATE"
  desired_count          = 1
  enable_execute_command = true

  network_configuration {
    subnets          = [aws_subnet.public1.id, aws_subnet.public2.id]
    assign_public_ip = true
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
  role       = aws_iam_role.celery_role.name
  policy_arn = aws_iam_policy.ssm_access.arn
}

data "aws_caller_identity" "current" {}

resource "aws_iam_policy_attachment" "attach_ssm_exec" {
  name       = "attach-ssm-exec-role"
  roles      = [aws_iam_role.ecs_task_execution_role.name]
  policy_arn = aws_iam_policy.ssm_access.arn
}
