# Language

## `terraform init [options]`

Initializes a working directory containing Terraform configuration files. This is the first command that should be run after writing a new Terraform configuration or cloning an existing one from version control.

## `terraform plan [options]`

creates an execution plan, which lets you preview the changes that Terraform plans to make to your infrastructure. By default, when Terraform creates a plan it:

* Reads the current state of any already-existing remote objects to make sure that the Terraform state is up-to-date.
* Compares the current configuration to the prior state and noting any differences.
* Proposes a set of change actions that should, if applied, make the remote objects match the configuration.

`terraform plan --out my_plan.plan` save the plan file (binary) that can be apply later

## `terraform apply [options] [plan file]` 

executes the actions proposed in a Terraform plan.

## `terraform destroy [options]`

convenient way to destroy all remote objects managed by a particular Terraform configuration.

This command is just a convenience alias for the following command: `terraform apply -destroy`.

For that reason, this command accepts most of the options that `terraform apply` accepts, although it does not accept a plan file argument and forces the selection of the "destroy" planning mode.

You can also create a speculative destroy plan, to see what the effect of destroying would be, by running the following command: `terraform plan -destroy`

This will run terraform plan in destroy mode, showing you the proposed destroy changes without executing them.

## `terraform show [options] [file]`

provide human-readable output from a state or plan file. This can be used to inspect a plan to ensure that the planned operations are expected, or to inspect the current state as Terraform sees it.

## `terraform fmt`

Da formato al archivo terraform para ser facilmente leible.

## `terraform validate`

validates the configuration files in a directory, referring only to the configuration and not accessing any remote services such as remote state, provider APIs, etc.

# Terraform block reference

```
terraform {
  required_providers {
    aws = {
      version = "~> 5"
      source = "hashicorp/aws"
    }
  }
  required_version = "~> 1.9"
}
```