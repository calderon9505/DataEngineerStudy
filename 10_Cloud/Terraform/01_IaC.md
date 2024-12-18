# Enfoques de la IaC

## Declarative:

La IaC declarativa permite al desarrollador describir los recursos y la configuración que componen el estado final de un sistema deseado. A continuación, la solución de IaC crea este sistema a partir del código de infraestructura. Esto hace que la IaC declarativa sea fácil de usar, siempre que el desarrollador sepa qué componentes y configuraciones necesita para ejecutar su aplicación.

The desired **end state** of the infrastructure is described. The system takes care of **matching** that state with the actual infrastructure.

Examples: Terraform, AWS CloudFormation.

## Imperative:

La IaC imperativa permite al desarrollador describir todos los pasos para configurar los recursos y llegar al sistema y al estado de ejecución deseados. Si bien no es tan sencillo escribir la IaC imperativa como la IaC declarativa, el enfoque imperativo se hace necesario en las implementaciones de infraestructuras complejas. Esto es especialmente cierto cuando el orden de los eventos es crítico.

Tthe exact **steps** or actions that need to be executed to reach a desired state are specified. The focus is on "how" to do things.

Examples: Ansible, Chef, Puppet (though some of these tools can also use a declarative approach).

# Tipos de IaC

## Configuration (orientado a la configuración)

Este tipo se centra en definir y gestionar la configuración del software y los sistemas operativos en la infraestructura. Se utiliza para instalar aplicaciones, gestionar configuraciones y asegurar que todos los servidores y servicios estén correctamente configurados.

Suele complementarse con herramientas de aprovisionamiento.

Ejemplos: *Ansible, Puppet*

## Templates (orientado a servidores)

Las plantillas son archivos de configuración que definen la infraestructura en un formato estructurado, como JSON o YAML. Estas plantillas especifican los recursos que se deben crear y sus configuraciones.

Es un enfoque común en entornos de nube.

Ejemplos: *AWS CloudFormation, Azure Resource Manager*

## Provisioning

Aunque se entrelaza con otros tipos, el aprovisionamiento se refiere específicamente al proceso de crear y configurar recursos de infraestructura. Es el primer paso antes de aplicar configuraciones de software.

Es IaC declarativo, con recursos inmutables. Es decir, si cambio algo que es crítico en un recurso, se destruye el recurso antiguo y se crea uno nuevo.

Ejemplos: *Terraform, AWS CloudFormation*