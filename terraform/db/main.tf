provider "aws" {
  region = "sa-east-1"
}

resource "aws_db_instance" "mares_db" {
  identifier           = "mares-db-instance"
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "16.1"
  instance_class       = "db.t3.micro"
  db_name              = var.db_name
  username             = var.db_username
  password             = var.db_password
  parameter_group_name = "default.postgres16"
  skip_final_snapshot  = true
  publicly_accessible  = true

  vpc_security_group_ids = [aws_security_group.mares_rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.mares_db_subnet_group.name
}

resource "aws_db_subnet_group" "mares_db_subnet_group" {
  name       = "mares-db-subnet-group"
  subnet_ids = [aws_subnet.mares_public_subnet_a.id, aws_subnet.mares_public_subnet_b.id]

  tags = {
    Name = "mares-db-subnet-group"
  }
}

resource "aws_security_group" "mares_rds_sg" {
  name        = "mares-rds-sg"
  description = "Allow RDS access from anywhere"
  vpc_id      = aws_vpc.mares_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
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
    Name = "mares-rds-sg"
  }
}
