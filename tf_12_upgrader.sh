#!/usr/bin/env bash

if [[ ! $(terraform version | grep v0.12) ]]; then
    echo "The 0.12upgrade tool is only available in Terraform >= 0.12.x"
    echo "Please switch to Terraform 0.12.x"
    exit 1
fi

printf "WARNING: This will recursively upgrade everything in \n$(pwd) with no confirmations.\n\n"
read -p  "Continue? Only 'yes' will be accepted to confirm: "
if [[ $REPLY == [Yy]es ]]; then
    #find . -type f -name "Makefile" \
    #    -execdir pwd \; -execdir make init \; -execdir terraform 0.12upgrade -yes \; -execdir touch terraform_0.12_ready \;
    for i in $(find . -type f -name "main.tf" -exec dirname {} \;); do
        if [[ ! -e $i/terraform_0.12_ready ]] && [[ ! $i == .terraform ]] && [[ ! $i == .terragrunt-cache ]]; then
            # For files using Terragrunt, comment out the remote bucket so we can init and upgrade
            # You could also put the init into a conditional, and pass it `backend=false`
            printf "\n$i\n"
            # 0.12upgrade doesn't accept a path as an argument, have to be inside the directory
            cd $i
            if [[ $(sed -n 2p main.tf) =~ 'backend "s3" {}' ]]; then
                sed -i '1,3 s/^/#/' main.tf
            fi
            terraform init && terraform 0.12upgrade -yes && touch terraform_0.12_ready
            # Remove the comments
            if [[ $(sed -n 2p main.tf) =~ 'backend "s3" {}' ]]; then
                sed -i '1,3 s/^##//' main.tf
            fi
            cd -
        fi
    done
    
else
    echo "Exiting"
fi
