resource "aws_instance" "mares_api_instance" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  # key_name               = var.key_name
  security_groups        = [aws_security_group.ssh_access.name, aws_security_group.mares_api_sg.name]
  iam_instance_profile   = aws_iam_instance_profile.ec2_connect_profile.name

  user_data = <<-EOF
                #!/bin/bash
                sudo apt-get update
                sudo apt-get install -y awscli docker.io
                sudo usermod -aG docker ubuntu

                # Log in to Amazon ECR
                aws ecr get-login-password --region sa-east-1 | sudo docker login --username AWS --password-stdin ${var.container_image_url}

                # Run Docker container
                sudo docker run -d -p 8080:8080 ${var.container_image_url}
                EOF


  tags = {
    Name = "MaresAPIInstance"
  }
}
