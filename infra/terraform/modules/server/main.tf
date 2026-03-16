# infra/terraform/modules/server/main.tf
# 通用服务器模块（支持 AWS EC2 / 腾讯云 CVM）

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ── 变量 ─────────────────────────────────────────────────

variable "env"            { description = "环境名称 (staging/production)" }
variable "instance_type"  { description = "实例类型"; default = "t3.small" }
variable "ami_id"         { description = "AMI ID" }
variable "key_name"       { description = "SSH 密钥对名称" }
variable "vpc_id"         { description = "VPC ID" }
variable "subnet_id"      { description = "Subnet ID" }
variable "app_port"       { description = "应用端口"; default = 8000 }
variable "allowed_ssh_cidrs" {
  description = "允许 SSH 的 CIDR 列表"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# ── 安全组 ────────────────────────────────────────────────

resource "aws_security_group" "app" {
  name        = "personal-landing-${var.env}"
  description = "Personal Landing ${var.env} security group"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "personal-landing-${var.env}"
    Environment = var.env
    ManagedBy   = "terraform"
  }
}

# ── EC2 实例 ──────────────────────────────────────────────

resource "aws_instance" "app" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.app.id]
  subnet_id              = var.subnet_id

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    env = var.env
  }))

  root_block_device {
    volume_size = var.env == "production" ? 40 : 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name        = "personal-landing-${var.env}"
    Environment = var.env
    ManagedBy   = "terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ── 弹性 IP ───────────────────────────────────────────────

resource "aws_eip" "app" {
  instance = aws_instance.app.id
  domain   = "vpc"

  tags = {
    Name        = "personal-landing-${var.env}-eip"
    Environment = var.env
    ManagedBy   = "terraform"
  }
}

# ── 输出 ──────────────────────────────────────────────────

output "public_ip"     { value = aws_eip.app.public_ip }
output "instance_id"   { value = aws_instance.app.id }
output "security_group_id" { value = aws_security_group.app.id }
