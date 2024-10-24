terraform {
  required_providers {
    aws = {
      version = ">= 5.60, < 6"
      source  = "hashicorp/aws"
    }
  }
  required_version = "~> 1.9"
}

provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  region = "us-east-2"
  alias  = "ohio"
}
