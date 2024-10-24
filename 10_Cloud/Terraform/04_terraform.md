# Terraform

Terraform puede crear **por defecto** hasta 10 recursos en paralelo.

agregar la extension HashiCorp Terraform en vs code y `File > Preferences > Settings` activar el **Format On Save** y en Default Formatter poner HashiCorp Terraform. Esta extensión usa el comando `terraform fmt` para formatear automaticamente al guardar. El comando `terraform validate` validate el archivo de configuración, pero solo valida que la sintaxis sea correcta, no formatea nada.

La carpeta `.terraform` contiene las versiones de los providers usados

## Terraform Constrainst

| required version  | meaning                                           | considerations                                                   |
| ----------------- | ------------------------------------------------- | ---------------------------------------------------------------- |
| `1.8.0`           | Only Terraform v1.8.0 exactly                     | To upgrade Terraform, first edit the `required _version` setting |
| `>= 1.8`          | Any Terraform v1.8.0 or grater                    |
| `~= 1.8.0`        | Any Terraform v1.8.x                              | Minor version updates are intended to be non-disruptive          |
| `>= 1.5, < 2.0.0` | Terraform v1.8.0 or greater, but less than v2.0.0 | avoids major version updates                                     |
