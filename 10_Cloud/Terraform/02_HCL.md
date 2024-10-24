# HCL (Hashicorp Configuration Language)

* **Legibilidad**: HCL utiliza una sintaxis clara que se asemeja a JSON pero es más fácil de leer y escribir, lo que facilita la comprensión y el mantenimiento del código.
* **Declarativo**: Permite a los usuarios declarar el estado deseado de la infraestructura. Terraform se encarga de gestionar los cambios necesarios para alcanzar ese estado.
* **Soporte para módulos**: HCL permite crear módulos, que son conjuntos reutilizables de configuraciones, lo que facilita la organización y modularidad del código.
* **Integración**: HCL se integra perfectamente con Terraform y otras herramientas de HashiCorp, lo que lo convierte en una opción popular para la infraestructura como código.

la estructura básica de un bloque de terraform es la siguiente:

```terraform
block_type "provider_resource" "resource_name" {
    # Arguments
}
```

En la página [Terraform Registry](https://registry.terraform.io/) se encuentran todos los providers y toda la documentación.

# Files and Directories

* Code in the Terraform language is stored in plain text files with the `.tf` file extension.
* Files containing Terraform code are often called **configuration files**.
* A **module** is a collection of `.tf` and/or `.tf.json` files kept together in a directory.
  * A Terraform module only consists of the top-level configuration files in a directory; nested directories are treated as completely separate modules, and are not automatically included in the configuration.
  * Terraform evaluates all of the configuration files in a module, effectively treating the entire module as a single document. Separating various blocks into different files is purely for the convenience of readers and maintainers, and has no effect on the module's behavior.
  * A Terraform module can use module calls to explicitly include other modules into the configuration. These child modules can come from local directories (nested in the parent module's directory, or anywhere else on disk), or from external sources like the Terraform Registry.