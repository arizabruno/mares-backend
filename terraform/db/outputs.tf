output "rds_endpoint" {
  value = aws_db_instance.mares_db.endpoint
}

output "vpc_id" {
  value = aws_vpc.mares_vpc.id
}

output "subnet_a_id" {
  value = aws_subnet.mares_public_subnet_a.id
}

output "subnet_b_id" {
  value = aws_subnet.mares_public_subnet_b.id
}
