#!/bin/bash
if [[ ! $(terraform version | grep v0.12) ]]; then
    echo "The 0.12upgrade tool is only available in Terraform >= 0.12.x"
    echo "Please switch to Terraform 0.12.x"
    exit 1
fi
printf "WARNING: This will recursively upgrade everything in \n$(pwd) with no confirmations.\n\n"
read -p  "Continue? Only 'yes' will be accepted to confirm: "
if [[ $REPLY == [Yy]es ]]; then
    ls $(pwd)/*/ >/dev/null 2>&1
    if [[ $? == 0 ]]; then
        for i in $(ls); do
            echo $i && terraform init $i &&  terraform 0.12upgrade -yes $i && touch $i/terraform_0.12_ready
        done
        for i in $(ls); do
            if [[ ! -f $i/terraform_0.12_ready ]]; then
                echo "Couldn't upgrade $i to Terraform 0.12"
            fi
        done
    else
        terraform init && terraform 0.12upgrade -yes && touch terraform_0.12_ready
        if [[ ! -f terraform_0.12_ready ]]; then
            printf "\nCouldn't upgrade to Terraform 0.12\n"
        fi
    fi
else
    echo "Exiting"
fi
