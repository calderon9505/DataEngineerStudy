# Identity and Access Management


# User

IAM Identity with **long-term** credentials that is used to interact with AWS in an account.
The users have attach one or more policys.


# User group

Collection of users.


# Role

IAM Identity with **short-term** credentials. Is similar to a user but without password or access keys.

If a user is assigned to a role, access keys are created dynamically and provided to the user termporarily. That is to say, **gives up** his own permissions and instead takes on the permissions of the role.

Se crean roles y se asignan a las distintas aplicaciones (códigos) para que tengan acceso a los recursos específicos que requiera la aplicación.

En términos de ADL, tengo mi usuario sebastian.calderon (con ninguna policy o alguna policy que desconozco). Dicho usuario tiene acceso a distintas cuentas (Data Lake account, Data Lake Stage, Data Lake Production, ASL Sandbox, etc) a las cuales puedo acceder con distintos roles (data-bbog-dataengineers-dev, data-commons-dataengineers-dev, adl-shared-access-dev)

# Policy

Object (JSON document) that defines permissions.

- effect
- actions
- resources
- optional conditions

> Any actions or resources that are not explicitly allowed are denied by default

```json
// who/what is authorized
"Sid" : "Stmt1351674984"
"Effect": "Allow",
// which tasks are allowed
"Action": [
    "s3:DeleteObject",
    "s3:GetObject",
],
// which conditions need to be met for authorization
"Condition": {
    "IpAddress": {
        "aws:SourceIP": "10.14.8.0/24"
    }
}
// Resources to which authorized tasks are performed
"Resource": [
    "arn:aws:s3:::dataeng-landing-zone/*",
    "arn:aws:s3:::dataeng-landing-zone",
]
```

Las policys se asignan a un usuario o a un grupo.
