# Terraform

Infrastructure as Code (IaC) tools allow you to manage infrastructure **with configuration files** rather than through a graphical user interface. IaC allows you to build, change, and manage your infrastructure in a **safe**, **consistent**, and **repeatable** way by defining resource configurations that **you can version, reuse, and share**.

* Terraform can manage infrastructure on multiple cloud platforms.
* The human-readable configuration language helps you write infrastructure code quickly.
* Terraform's state allows you to track resource changes throughout your deployments.
* You can commit your configurations to version control to safely collaborate on infrastructure.

Terraform's configuration language is **declarative**, meaning that it describes the desired end-state for your infrastructure, in contrast to procedural programming languages that require step-by-step instructions to perform tasks. Terraform providers automatically calculate dependencies between resources to create or destroy them in the correct order.

To deploy infrastructure with Terraform:

* Scope - Identify the infrastructure for your project.
* Author - Write the configuration for your infrastructure.
* Initialize - Install the plugins Terraform needs to manage the infrastructure.
* Plan - Preview the changes Terraform will make to match your configuration.
* Apply - Make the planned changes.

## Instalation

Descargar Terraform desde la página oficial de HashiCorp y descomprimir.

ubico el archivo en `C:\Program Files\Terraform\terraform.exe` y creo la variable de entorno `C:\Program Files\Terraform`.
