resource "aws_ecr_repository" "turnos_api" {
  name = "sistema-turnos-api"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "sistema-turnos-api"
  }
}