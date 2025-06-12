# ===============================
# ECS AUTOSCALER FOR DJANGO SERVICE (CPU + MEMORY)
# ===============================

resource "aws_appautoscaling_target" "django_scaling_target" {
  max_capacity       = 5
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.django-cluster.name}/${aws_ecs_service.django_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "django_cpu_policy" {
  name               = "django-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.django_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.django_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.django_scaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 60.0
    scale_in_cooldown  = 180
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "django_memory_policy" {
  name               = "django-memory-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.django_scaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.django_scaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.django_scaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 240
    scale_out_cooldown = 90
  }
}
