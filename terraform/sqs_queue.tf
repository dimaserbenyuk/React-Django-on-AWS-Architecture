####################
# Celery SQS Queues
####################

resource "aws_sqs_queue" "celery_dlq" {
  name                          = "celery-dlq.fifo"
  fifo_queue                    = true
  content_based_deduplication   = true
}

resource "aws_sqs_queue" "celery_queue" {
  name                          = "celery-prod-queue.fifo"
  fifo_queue                    = true
  content_based_deduplication   = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.celery_dlq.arn,
    maxReceiveCount     = 5
  })

  tags = {
    Environment = "prod"
    App         = "celery"
  }
}

resource "aws_sqs_queue_redrive_allow_policy" "allow_redrive" {
  queue_url = aws_sqs_queue.celery_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns   = [aws_sqs_queue.celery_queue.arn]
  })
}

###############################
# IAM Role 1: ECS Task executes
###############################

resource "aws_iam_role" "celery_execution_role" {
  name = "celery-execution-role"

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

# Позволяем этой роли ассаумить celery_worker_role
resource "aws_iam_policy" "allow_assume_celery_worker_role" {
  name = "allow-assume-celery-worker-role"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "sts:AssumeRole",
        Resource = aws_iam_role.celery_worker_role.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_assume_role" {
  role       = aws_iam_role.celery_execution_role.name
  policy_arn = aws_iam_policy.allow_assume_celery_worker_role.arn
}

#########################################
# IAM Role 2: Target Celery Worker Role
#########################################

resource "aws_iam_role" "celery_worker_role" {
  name = "celery-worker-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        AWS = aws_iam_role.celery_execution_role.arn
      },
      Action = "sts:AssumeRole"
    }]
  })
}

# Политика доступа к очередям
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

resource "aws_iam_role_policy_attachment" "attach_sqs_to_worker_role" {
  role       = aws_iam_role.celery_worker_role.name
  policy_arn = aws_iam_policy.celery_sqs_policy.arn
}
