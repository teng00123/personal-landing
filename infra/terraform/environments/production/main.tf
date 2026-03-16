# infra/terraform/environments/production/main.tf

terraform {
  required_version = ">= 1.5"

  backend "s3" {
    bucket         = "personal-landing-tfstate"
    key            = "production/terraform.tfstate"
    region         = "ap-southeast-1"
    encrypt        = true
    dynamodb_table = "personal-landing-tflock"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region"   { default = "ap-southeast-1" }
variable "ami_id"       { description = "Ubuntu 22.04 AMI" }
variable "key_name"     { description = "SSH key pair" }
variable "vpc_id"       {}
variable "subnet_id"    {}
variable "allowed_ssh_cidrs" {
  type    = list(string)
  default = []
}

module "server" {
  source = "../../modules/server"

  env           = "production"
  instance_type = "t3.medium"
  ami_id        = var.ami_id
  key_name      = var.key_name
  vpc_id        = var.vpc_id
  subnet_id     = var.subnet_id
  allowed_ssh_cidrs = var.allowed_ssh_cidrs
}

output "public_ip"   { value = module.server.public_ip }
output "instance_id" { value = module.server.instance_id }
