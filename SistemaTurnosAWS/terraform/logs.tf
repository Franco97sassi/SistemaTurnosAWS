resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/turnos-backend"
  retention_in_days = var.environment == "production" ? 30 : 7

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

  alarm_actions = var.alarm_email == "" ? [] : [aws_sns_topic.operational_alerts[0].arn]
}

resource "aws_sns_topic" "operational_alerts" {
  count = var.alarm_email == "" ? 0 : 1
  name  = "turnos-operational-alerts"
}

resource "aws_sns_topic_subscription" "alarm_email" {
  count     = var.alarm_email == "" ? 0 : 1
  topic_arn = aws_sns_topic.operational_alerts[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

resource "aws_cloudwatch_dashboard" "operations" {
  dashboard_name = "turnos-${var.environment}"
  dashboard_body = jsonencode({
    widgets = [{
      type = "metric", x = 0, y = 0, width = 12, height = 6,
      properties = {
        title = "API health and latency", region = var.region, stat = "Average", period = 300,
        metrics = [
          ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.turnos_alb.arn_suffix],
          [".", "HTTPCode_Target_5XX_Count", ".", ".", { stat = "Sum", yAxis = "right" }]
        ]
      }
    }, {
      type = "metric", x = 12, y = 0, width = 12, height = 6,
      properties = {
        title = "ECS utilization", region = var.region, stat = "Average", period = 300,
        metrics = [
          ["AWS/ECS", "CPUUtilization", "ServiceName", aws_ecs_service.backend.name, "ClusterName", aws_ecs_cluster.turnos.name],
          [".", "MemoryUtilization", ".", ".", ".", "."]
        ]
      }
    }]
  })
}
