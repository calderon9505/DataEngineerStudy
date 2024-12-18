resource "aws_s3_bucket" "proveedores" {
  bucket = "bucket-from-terra-sca"

  tags = {
    Name        = "bucket-from-terra-sca"
    Owner       = "Sebastian Calderon"
    Environment = "Dev"
  }
}
