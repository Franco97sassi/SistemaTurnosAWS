terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  required_version = ">= 1.6"
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

resource "aws_ecr_repository" "backend" {
  name                 = "sistema-turnos-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
