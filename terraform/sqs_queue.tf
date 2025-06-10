# DLQ очередь
# DLQ FIFO очередь
resource "aws_sqs_queue" "celery_dlq" {
  name                        = "celery-dlq.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
}


# Основная очередь Celery
resource "aws_sqs_queue" "celery_queue" {
  name                        = "celery-prod-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.celery_dlq.arn
    maxReceiveCount     = 5
  })

  tags = {
    Environment = "prod"
    App         = "celery"
  }
}

# Разрешение на редрайв
resource "aws_sqs_queue_redrive_allow_policy" "allow_redrive" {
  queue_url = aws_sqs_queue.celery_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.celery_queue.arn]
  })
}

# IAM Role
resource "aws_iam_role" "celery_role" {
  name = "celery-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com" # или ec2.amazonaws.com если ты на EC2
      },
      Action = "sts:AssumeRole"
    }]
  })
}

# Политика с доступом к SQS
resource "aws_iam_policy" "celery_sqs_policy" {
  name = "celery-sqs-access"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl",
          "sqs:ChangeMessageVisibility",
          "sqs:ListQueues"
        ],
        Resource = [
          aws_sqs_queue.celery_queue.arn,
          aws_sqs_queue.celery_dlq.arn
        ]
      }
    ]
  })
}

# Присоединение политики к роли
resource "aws_iam_role_policy_attachment" "celery_policy_attachment" {
  role       = aws_iam_role.celery_role.name
  policy_arn = aws_iam_policy.celery_sqs_policy.arn
}
