#!/usr/bin/env bash

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
        find . -type f -name "main.tf" \
        -execdir terraform init \; -execdir terraform 0.12upgrade -yes \; -execdir touch terraform_0.12_ready \;
    else
        if terraform init && terraform 0.12upgrade -yes; then
            touch terraform_0.12_ready
        else
            echo "Couldn't upgrade $i to Terraform 0.12"
        fi
    fi
else
    echo "Exiting"
    exit
fi
