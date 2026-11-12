variable "aws_profile" {
  type    = string
  default = "terraform"
}
variable "allowed_cidr" {
  type        = string
  description = "Your current public IPv4 in /32 CIDR format. Never use 0.0.0.0/0."
  validation {
    condition     = can(cidrhost(var.allowed_cidr, 0)) && endswith(var.allowed_cidr, "/32")
    error_message = "Specify a single IPv4 address as x.x.x.x/32."

  }
}
variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}
