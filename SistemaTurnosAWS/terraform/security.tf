resource "aws_security_group" "backend_sg" {
  name        = "turnos-backend-sg"
  description = "Allow HTTP traffic to backend"
  vpc_id      = aws_vpc.turnos_vpc.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
    description     = "FastAPI from ALB"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "turnos-backend-sg"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "turnos-rds-sg"
  description = "Managed by Terraform"
  vpc_id      = aws_vpc.turnos_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend_sg.id]
    description     = "Permitir PostgreSQL desde el backend"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "turnos-rds-sg"
  }
}