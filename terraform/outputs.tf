
output "vpc_id" {
  value = aws_vpc.main.id
}

output "infrastructure_instance_id" {
  value = aws_instance.infrastructure.id
}

output "infrastructure_public_ip" {
  value = aws_instance.infrastructure.public_ip
}

output "cicd_instance_id" {
  value = aws_instance.cicd.id
}

output "cicd_public_ip" {
  value = aws_instance.cicd.public_ip
}
