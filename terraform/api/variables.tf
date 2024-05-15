variable "ami_id" {
  description = "The AMI ID to use for the instance."
  default     = "ami-08af887b5731562d3"
}

variable "instance_type" {
  description = "The type of instance to launch."
  default     = "t2.micro"
}

variable "container_image_url" {
  description = "The URL of the container image to be pulled and run"
  type        = string
}


# variable "key_name" {
#   description = "The key name of the AWS Key Pair to use for the instance."
# }
