resource "aws_security_group" "alb_sg" {
  name        = "turnos-alb-sg"
  description = "Allow HTTP traffic to ALB"
  vpc_id      = aws_vpc.turnos_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from Internet"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "turnos-alb-sg"
  }
}

resource "aws_lb" "turnos_alb" {
  name               = "turnos-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]

  subnets = [
    aws_subnet.public_subnet_1.id,
    aws_subnet.public_subnet_2.id
  ]

  tags = {
    Name = "turnos-alb"
  }
}

resource "aws_lb_target_group" "backend_tg" {
  name        = "turnos-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.turnos_vpc.id
  target_type = "ip"

  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    Name = "turnos-backend-tg"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.turnos_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend_tg.arn
  }
}