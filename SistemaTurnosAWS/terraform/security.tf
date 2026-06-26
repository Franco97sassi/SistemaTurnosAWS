resource "aws_security_group" "api_sg" {
  name        = "turnos-api-sg"
  description = "Security Group de la API"
  vpc_id      = aws_vpc.turnos_vpc.id

  ingress {
    description = "HTTP API"
    from_port = 5432
    to_port   = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "turnos-api-sg"
  }
}