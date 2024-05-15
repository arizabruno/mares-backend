resource "aws_iam_policy" "ec2_connect" {
  name        = "EC2-Instance-Connect-Policy"
  description = "Allow sending SSH public key to EC2 Instance Connect"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "ec2-instance-connect:SendSSHPublicKey",
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role" "ec2_connect_role" {
  name = "EC2InstanceConnectRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole",
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_connect_attach" {
  role       = aws_iam_role.ec2_connect_role.name
  policy_arn = aws_iam_policy.ec2_connect.arn
}

resource "aws_iam_instance_profile" "ec2_connect_profile" {
  name = "EC2InstanceConnectProfile"
  role = aws_iam_role.ec2_connect_role.name
}

resource "aws_iam_role_policy_attachment" "ecr_read_only_attach" {
  role       = aws_iam_role.ec2_connect_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}
