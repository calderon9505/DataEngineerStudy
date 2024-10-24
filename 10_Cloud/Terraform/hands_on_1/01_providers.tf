# bloque para crear recurso con provider local
resource "local_file" "productos" {
  content  = "lista de productos del proximo mes"
  filename = "productos-${random_string.sufijo[count.index].id}.txt"
  count    = 3
}

# bloque para crear recurso con provider random
# se debe realizar nuevamente el terraform init
# porque se está usando un nuevo provider
resource "random_string" "sufijo" {
  length  = 4
  special = false
  upper   = false
  numeric = false
  count   = 3
}