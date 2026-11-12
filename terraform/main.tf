terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source = "hashicorp/aws", version = "~> 5.0"
    }
    archive = {
      source = "hashicorp/archive", version = "~> 2.0"
    }

  }
}

provider "aws" {
  region  = "eu-south-2"
  profile = var.aws_profile
}
provider "aws" {
  alias   = "ireland"
  region  = "eu-west-1"
  profile = var.aws_profile
}
provider "aws" {
  alias   = "virginia"
  region  = "us-east-1"
  profile = var.aws_profile
}
provider "aws" {
  alias   = "tokyo"
  region  = "ap-northeast-1"
  profile = var.aws_profile
}
