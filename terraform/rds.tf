resource "random_password" "rds_password" {
  length  = 20
  special = true
}

resource "aws_ssm_parameter" "rds_password" {
  name        = "/django/dev/POSTGRES_PASSWORD"
  type        = "SecureString"
  value       = random_password.rds_password.result
  description = "Password for RDS PostgreSQL"
}

resource "aws_ssm_parameter" "postgres_db" {
  name  = "/django/dev/POSTGRES_DB"
  type  = "String"
  value = "education"
}

resource "aws_ssm_parameter" "postgres_user" {
  name  = "/django/dev/POSTGRES_USER"
  type  = "String"
  value = "edu"
}

resource "aws_ssm_parameter" "postgres_host" {
  name  = "/django/dev/POSTGRES_HOST"
  type  = "String"
  value = aws_db_instance.django.address
}

resource "aws_ssm_parameter" "postgres_port" {
  name  = "/django/dev/POSTGRES_PORT"
  type  = "String"
  value = "5432"
}
resource "aws_db_subnet_group" "rds_subnets" {
  name       = "rds-subnet-group"
  subnet_ids = [aws_subnet.private1.id, aws_subnet.private2.id]

  tags = {
    Name = "rds-subnet-group"
  }
}

resource "aws_db_instance" "django" {
  identifier              = "django-postgres-db"
  engine                  = "postgres"
  engine_version          = "17.5"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  max_allocated_storage   = 100
  db_subnet_group_name    = aws_db_subnet_group.rds_subnets.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  username                = "edu"
  password                = random_password.rds_password.result
  skip_final_snapshot     = true
  publicly_accessible     = false
  apply_immediately       = true
  deletion_protection     = false
  multi_az                = false

  tags = {
    Name        = "django-rds"
    Environment = "prod"
  }
}

resource "aws_security_group" "rds" {
  name        = "rds-security-group"
  description = "Allow PostgreSQL access from ECS Fargate"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    # security_groups = [aws_security_group.ecs_fargate.id] # доступ только с ECS
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds-security-group"
  }
}
