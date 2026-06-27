output "vpc_id" {
  value = aws_vpc.turnos_vpc.id
}

output "public_subnet_1_id" {
  value = aws_subnet.public_subnet_1.id
}

output "public_subnet_2_id" {
  value = aws_subnet.public_subnet_2.id
}

output "backend_security_group_id" {
  value = aws_security_group.backend_sg.id
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "rds_port" {
  value = aws_db_instance.postgres.port
}

output "alb_dns_name" {
  value = aws_lb.turnos_alb.dns_name
}

output "backend_url" {
  value = "http://${aws_lb.turnos_alb.dns_name}"
}


output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}

output "frontend_website_endpoint" {
  value = aws_s3_bucket_website_configuration.frontend.website_endpoint
}

output "cloudfront_url" {
  value = aws_cloudfront_distribution.frontend.domain_name
}