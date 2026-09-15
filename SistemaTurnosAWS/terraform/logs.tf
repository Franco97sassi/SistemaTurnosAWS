resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/turnos-backend"
  retention_in_days = 7

  tags = {
    Name = "turnos-backend-logs"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_targets" {
  alarm_name          = "turnos-unhealthy-targets"
  alarm_description   = "Alerts when the backend has unhealthy ECS targets"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  treat_missing_data  = "breaching"

  dimensions = {
    LoadBalancer = aws_lb.turnos_alb.arn_suffix
    TargetGroup  = aws_lb_target_group.backend_tg.arn_suffix
  }
}
