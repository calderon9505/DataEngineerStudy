resource "aws_vpc" "vpc_virginia" {
  cidr_block = var.virginia_cidr
  tags = {
    Name = "VPC_VIRGINIA"
    env  = "Dev"
  }
}

# Se crea un recurso en una region diferente porque se usa un provider diferente
# Tambien se podría tener un stack diferente de terra y usar allá el provider deseado
resource "aws_vpc" "vpc_ohio" {
  cidr_block = var.ohio_cidr
  tags = {
    Name = "VPC_OHIO"
    env  = "Dev"
  }
  provider = aws.ohio
}
