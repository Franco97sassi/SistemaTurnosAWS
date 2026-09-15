terraform {
  backend "s3" {}
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

  default_tags {
    tags = {
      Application = "sistema-turnos"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_ecr_repository" "backend" {
  name                 = "sistema-turnos-api"
  image_tag_mutability = "IMMUTABLE_WITH_EXCLUSION"

  image_tag_mutability_exclusion_filter {
    filter      = "latest"
    filter_type = "WILDCARD"
  }

  image_scanning_configuration {
    scan_on_push = true
  }
}
