# Existen 4 formas de definir las variables de manera indirecta cuando 
# estas se crean pero se dejan vacías.
# si existe en una, no se miran las demás:
# 1. parámetros por lineas de comandos
#   terraform plan --var virginia_cidr="10.10.0.0/16"
#   terraform plan --var-file xxx.tfvars
# 2. Se usa un archivo de variables terraform
#   - xxx.auto.tfvars
#   - xxx.auto.tfvars.json
#   - terraform.tfvars
#   - terraform.tfvars.json
# 3. variables de entorno cuyo nombre inicie con TF_VAR_
#   export TF_VAR_ohio_cidr="10.20.0.0/16"
# 5. se piden el valor por terminal

variable "virginia_cidr" {
}

variable "ohio_cidr" {
}

# Tipos de variables
# string, number, bool, any(defecto)

variable "test_variable" {
  default     = "my_var"
  description = "my description"
  type        = string
  sensitive   = true
}

# Existen conversiones automáticas de variables
# string <---> number
# string <---> bool

# Las variables de tipo listas deben ser todas del mismo tipo
# y pueden admitir valores repetidos
variable "list_variable" {
  default     = ["10.10.0.0/16", "10.20.0.0/16"]
  description = "my list"
  type        = list(string)
}

# Las variables de tipo Map con de clave-valor
variable "map_variable" {
  default = {
    "virginia" = "10.10.0.0/16"
    "ohio"     = "10.20.0.0/16"
  }
  description = "my list"
  type        = map(string)
}

# Las variables de tipo set no admite elementos repetidos
# A difenrencia de las listas, No se accede a elementos puntuales de un set 
# su uso es poco común
# se accede a cada elemento usando la funcion for_each 
variable "set_variable" {
  default     = ["10.10.0.0/16", "10.20.0.0/16"]
  description = "my list"
  type        = list(string)
}

# Las variables de tipo Object permite crear variables que tienen campos
# de distintos tipos
variable "object_variable" {
  type = object({
    name     = string
    cantidad = number
    cidrs    = list(string)
    enable   = bool
  })

  default = {
    name     = "my object"
    cantidad = 1
    cidrs    = ["10.10.0.0/16", "10.20.0.0/16"]
    enable   = true
  }
}

# las variables de tipo Tupla son iguales a las listas
# pero pueden tener elementos de distinto tipo
variable "tuple_variable" {
  type    = tuple([string, number, bool])
  default = ["ohio", 2, false]
}
