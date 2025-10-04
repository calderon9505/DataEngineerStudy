## Terraform

sudo yum install -y yum-utils shadow-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum install terraform

## aws

viene instalada por defecto

aws configure
se crean credenciales únicas

## github

git config --global user.name "Sebastian Calderon terraform"
git config --global user.email "calderon950527@gmail.com"
eval "$(ssh-agent -s)"
ssh-keygen -t rsa -b 4096 -C "calderon950527@gmail.com"
ssh-add ~/.ssh/id_rsa
git clone git@github.com:calderon9505/DataEngineerStudy.git