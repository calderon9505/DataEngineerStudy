# Identity and Access Management


# User

IAM Identity with **long-term** credentials that is used to interact with AWS in an account.
The users have attach one or more policys.


# User group

Collection of users.


# Role

IAM Identity with **short-term** credentials. Is similar to a user but without password or access keys.

If a user is assigned to a role, access keys are created dynamically and provided to the user temporarily. That is to say, **gives up** his own permissions and instead takes on the permissions of the role.

Se crean roles y se asignan a las distintas aplicaciones (códigos) para que tengan acceso a los recursos específicos que requiera la aplicación.

En términos de ADL, tengo mi usuario sebastian.calderon (con ninguna policy o alguna policy que desconozco). Dicho usuario tiene acceso a distintas cuentas (Data Lake account, Data Lake Stage, Data Lake Production, ASL Sandbox, etc) a las cuales puedo acceder con distintos roles (data-bbog-dataengineers-dev, data-commons-dataengineers-dev, adl-shared-access-dev)

# Policy

Object (JSON document) that defines **permissions**.

- effect
- actions
- resources
- optional conditions

> Any actions or resources that are not explicitly allowed are denied by default

```json
{
    "Version": "2012-10-17",
    "Statement": {
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
    }
}

```

El campo de **Resource** he visto que tiene el siguiente orden

```
arn:aws:<service>:<region>:<account>:<resource>
```

The region portion is blank when the service is global.

You can organize IAM users into IAM groups and attach a policy to a group. In that case, individual users still have their own credentials, but all the users in a group have the permissions that are attached to the group.

## Identity-based and resource-based policies

Identity-based policies are permissions policies that you attach to an IAM identity, such as an IAM user, group, or role. Resource-based policies are permissions policies that you attach to a resource such as an Amazon S3 bucket or an IAM role trust policy.