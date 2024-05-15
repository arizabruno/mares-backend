output "instance_public_ip" {
  value = aws_instance.mares_api_instance.public_ip
}

output "instance_public_dns" {
  value = aws_instance.mares_api_instance.public_dns
}

output "api_url" {
  value = "http://${aws_instance.mares_api_instance.public_ip}:8080"
}
