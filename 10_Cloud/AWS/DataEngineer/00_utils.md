# Policies and permissions

A **policy** is an object in AWS that, when associated with an identity or resource, defines their **permissions**. 

## Identity-based policies and resource-based policies

When you create a permissions policy to restrict access to a resource, you can choose an identity-based policy or a resource-based policy.

Una política basada en recursos (resource-based policy) es una política de permisos que se adjunta al recurso, no a la identidad. El recurso declara quién puede usarlo.

La diferencia se ve mejor en contraste:

|                      | identity-based                   | resource-based                            |
|----------------------|----------------------------------|-------------------------------------------|
| Se adjunta a         | Usuario, grupo o rol IAM         | El recurso (bucket, cola, clave KMS, bus) |
| Dice                 | "Este rol puede leer ese bucket" | "Esta cuenta puede leerme"                |
| Elemento `Principal` | No lo tiene (está implícito)     | Obligatorio                               |
| Se gestiona desde    | La cuenta de la identidad        | La cuenta del recurso                     |


> El indicador infalible: si la política tiene un bloque `Principal`, es basada en recurso. Si no lo tiene, es basada en identidad.

Ejemplo: Una bucket policy que permite a otra cuenta leer tu data lake:

```json
{
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "PermitirLecturaCuentaAnalitica",
        "Effect": "Allow",
        "Principal": { "AWS": "arn:aws:iam::222222222222:root" },
        "Action": ["s3:GetObject", "s3:ListBucket"],
        "Resource": [
        "arn:aws:s3:::mi-data-lake",
        "arn:aws:s3:::mi-data-lake/curated/*"
        ]
    }]
}
```
Esa política vive en el bucket, en la cuenta 111111111111. El dueño del bucket controla el acceso sin tocar nada en la otra cuenta.

Cómo se evalúan juntas?

* **Dentro de la misma cuenta**: basta con que una de las dos permita la acción. Es una unión.

* **Entre cuentas distintas**: se necesitan ambas. La cuenta B debe tener una política de identidad que permita la acción, y el recurso en la cuenta A debe tener una política que permita a la cuenta B. Si falta cualquiera de las dos, se deniega.

* Un Deny explícito siempre gana, venga de donde venga. Y por encima de todo esto operan los SCPs de Organizations y los permission boundaries, que solo pueden restringir, nunca otorgar.

Solo algunos servicios las soportan. Los que importan en data engineering:

- **S3 bucket policies**: el caso canónico. Acceso cross-account a un data lake, forzar que las consulas a los objetos vengan cifradas, forzar TLS, restringir por VPC endpoint.
- **KMS key policies**: caso especial e importante. A diferencia del resto, la key policy es obligatoria — sin ella, ninguna política de IAM por sí sola da acceso a la clave. Si compartes datos cifrados entre cuentas, tienes que otorgar permiso tanto en el bucket como en la clave KMS. Olvidar la clave es un error clásico y una pregunta típica.
- **Glue Data Catalog resource policy**: para compartir el catálogo entre cuentas.
- **SQS y SNS**: permitir que otro servicio o cuenta publique o consuma.
- **Lambda resource policy**: lo que se crea automáticamente cuando configuras un trigger. Permite al servicio invocarte.
- **EventBridge event bus policy**: para recibir eventos de otras cuentas.
- **CloudWatch Logs resource policy**: para que otra cuenta o servicio escriba en tus log groups.
- **Secrets Manager**: acceso cross-account a un secreto.

> Dato aparte: la trust policy de un rol IAM es técnicamente una política basada en recurso. Por eso lleva `Principal` — define quién puede asumir el rol.

¿Para qué se usan realmente? Dos casos dominan:

1. Acceso cross-account. Es la razón principal de su existencia.
2. Dar acceso a un service principal. Cuando permites que `glue.amazonaws.com` o `firehose.amazonaws.com` escriba en tu bucket, eso va en la bucket policy.

> Un matiz para tu examen: en arquitecturas de data lake, AWS empuja hacia Lake Formation en lugar de gestionar bucket policies a mano. Lake Formation te da permisos a nivel de tabla, columna, fila y celda sobre el Glue Data Catalog, en lugar de permisos a nivel de prefijo de S3. Si una pregunta habla de gobernanza fina o filtrado por columnas, la respuesta es Lake Formation, no una bucket policy.





---
---

# AWS STS (Security Token Service)

AWS STS es un servicio que entrega credenciales de seguridad temporales y de privilegios limitados. En lugar de usar credenciales permanentes (como las access keys de un usuario IAM), obtienes credenciales que expiran después de un tiempo definido. Esas credenciales temporales constan de 3 elementos:

- AccessKeyId
- SecretAccessKey
- SessionToken ← este es el diferenciador clave respecto a credenciales permanentes

El principio central es no distribuir credenciales de larga duración. Las credenciales temporales:

- Expiran automáticamente (de 15 minutos hasta 12 horas, según el caso) → si se filtran, el daño es limitado.
- No se almacenan con el usuario/servicio; se solicitan bajo demanda.
- Permiten acceso entre cuentas y federación sin crear usuarios IAM permanentes.

Las operaciones principales de STS

| Operación                 | Cuándo se usa                                                                        |
| ------------------------- | ------------------------------------------------------------------------------------ |
| AssumeRole                | Asumir un rol IAM (dentro de la misma cuenta o cross-account). La más común.         |
| AssumeRoleWithWebIdentity | Federación con proveedores externos (Google, Facebook, Cognito, OIDC como EKS/IRSA). |
| AssumeRoleWithSAML        | Federación empresarial con SAML 2.0 (Active Directory, Okta).                        |
| GetSessionToken           | Credenciales temporales para un usuario IAM, típicamente con MFA.                    |
| GetFederationToken        | Federación para usuarios sin IAM propio.                                             |
| GetCallerIdentity         | Devuelve quién eres (cuenta, ARN, user ID). Útil para depurar.                       |


El concepto clave: **AssumeRole**. Este es el que más debes dominar. El flujo es:

1. Una identidad (usuario, servicio, otra cuenta) llama a sts:AssumeRole
2. STS verifica:
    - La TRUST POLICY del rol (¿quién puede asumirlo?)
    - El permiso sts:AssumeRole del que llama
3. STS devuelve credenciales temporales
4. La identidad usa esas credenciales con los permisos del ROL (no los suyos)

Punto crítico para el examen: un rol IAM tiene dos políticas:
- Trust policy (política de confianza) → quién puede asumir el rol (el principal).
- Permissions policy (política de permisos) → qué puede hacer quien asume el rol.

Ambas deben permitir la acción. Esto es causa frecuente de errores en escenarios de examen.

Relevancia para Data Engineering (DEA-C01):

1. **cross-account access data** — Ejemplo típico: un job de Glue o un cluster EMR en la Cuenta A necesita leer un bucket S3 en la Cuenta B. Se crea un rol en la Cuenta B que la Cuenta A asume vía STS.

2. **Service roles** — Glue, EMR, Lambda, Redshift, Kinesis Firehose: todos asumen un service role (usando STS por detrás) para acceder a recursos. Por eso defines un IAM Role y no access keys en estos servicios.

3. **Redshift Spectrum** / COPY desde S3 — Redshift asume un rol IAM para leer/escribir en S3. Verás la cláusula IAM_ROLE en comandos COPY/UNLOAD.

4. **Lake Formation** — usa credenciales temporales (vended credentials) para dar acceso granular y temporal a los datos del data lake.

5. EMR / EKS con IRSA — AssumeRoleWithWebIdentity + OIDC para que los pods/jobs obtengan permisos sin credenciales estáticas.
