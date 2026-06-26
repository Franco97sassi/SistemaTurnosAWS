resource "aws_iam_role" "ecs_task_role" {

  name = "turnos-ecs-role"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = "ecs-tasks.amazonaws.com"

        }

        Action = "sts:AssumeRole"

      }

    ]

  })

}


resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {

  role = aws_iam_role.ecs_task_role.name

  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"

}