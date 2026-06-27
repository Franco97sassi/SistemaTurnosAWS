resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/turnos-backend"
  retention_in_days = 7

  tags = {
    Name = "turnos-backend-logs"
  }
}