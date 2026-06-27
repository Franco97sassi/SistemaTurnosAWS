resource "aws_db_subnet_group" "turnos" {
  name = "turnos-db-subnet-group"

  subnet_ids = [
    aws_subnet.public_subnet_1.id,
    aws_subnet.public_subnet_2.id
  ]

  tags = {
    Name = "Turnos DB Subnet Group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier        = "turnos-postgres"
  allocated_storage = 20
  engine            = "postgres"
  engine_version    = "17"
  instance_class    = "db.t3.micro"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.turnos.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  publicly_accessible = false
  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "turnos-postgres"
  }
}