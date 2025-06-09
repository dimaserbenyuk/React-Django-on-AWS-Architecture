# ============================
# ECS FARGATE + Django WORKER
# ============================

resource "aws_ecs_cluster" "celery_cluster" {
  name = "django-cluster"
}

resource "aws_ecs_task_definition" "celery_worker" {
  family                   = "django-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.celery_role.arn # ✅ используем роль из sqs.tf

  container_definitions = jsonencode([
    {
      name      = "django"
      image     = "272509770066.dkr.ecr.us-east-1.amazonaws.com/django-backend:latest"
      essential = true
      command   = ["python", "manage.py", "runserver"]
      environment = [
        { name = "DJANGO_ENV", value = "prod" },
        { name = "DJANGO_SETTINGS_MODULE", value = "backend.settings.prod" }
      ]
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

# ❌ УДАЛИ ЭТО! дублирует celery_role из sqs.tf
# resource "aws_iam_role" "celery_task_role" {
#   ...
# }

# ✅ ECS Service
resource "aws_ecs_service" "django_service" {
  name            = "django-service"
  cluster         = aws_ecs_cluster.celery_cluster.id
  task_definition = aws_ecs_task_definition.celery_worker.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = [aws_subnet.public1.id, aws_subnet.public2.id]
    assign_public_ip = true
    security_groups  = [aws_security_group.celery_sg.id]
  }
}

# ✅ CloudWatch Logs
resource "aws_cloudwatch_log_group" "django_logs" {
  name              = "/ecs/django"
  retention_in_days = 7
}
