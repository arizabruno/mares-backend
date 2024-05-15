variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "mares"
}

variable "db_username" {
  description = "The master username for the database"
  type        = string
}

variable "db_password" {
  description = "The password for the master database user"
  type        = string
}
