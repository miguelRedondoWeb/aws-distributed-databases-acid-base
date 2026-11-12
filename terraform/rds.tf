data "aws_vpc" "default" {
  default = true
}
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_subnet" "all" {
  for_each = toset(data.aws_subnets.default.ids)
  id       = each.value
}

resource "aws_security_group" "mysql" {
  name_prefix = "ej7-mysql-"
  description = "Ejercicio 7 MySQL: access restricted to one student IP"
  vpc_id      = data.aws_vpc.default.id
  ingress {
    description = "MySQL from student IP only"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]

  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]

  }
}
resource "aws_db_subnet_group" "mysql" {
  name       = "ej7-mysql-subnets"
  subnet_ids = data.aws_subnets.default.ids
}
resource "aws_db_instance" "bank" {
  identifier                  = "ej7-banco-mysql"
  engine                      = "mysql"
  instance_class              = var.db_instance_class
  allocated_storage           = 20
  storage_type                = "gp2"
  storage_encrypted           = true
  multi_az                    = true
  db_name                     = "banco"
  username                    = "adminmysql"
  manage_master_user_password = true
  publicly_accessible         = true
  vpc_security_group_ids      = [aws_security_group.mysql.id]
  db_subnet_group_name        = aws_db_subnet_group.mysql.name
  backup_retention_period     = 0
  skip_final_snapshot         = true
  deletion_protection         = false
  apply_immediately           = true
  tags = {
    Project = "IFCD0078-Ejercicio7", Environment = "lab"
  }
}
output "rds_endpoint" {
  value = aws_db_instance.bank.address
}
output "rds_identifier" {
  value = aws_db_instance.bank.identifier
}
