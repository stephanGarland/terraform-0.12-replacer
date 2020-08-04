#!/usr/bin/env bash

if [[ ! $(terraform version | grep v0.12) ]]; then
    echo "The 0.12upgrade tool is only available in Terraform >= 0.12.x"
    echo "Please switch to Terraform 0.12.x"
    exit 1
fi

printf "WARNING: This will recursively upgrade everything in \n$(pwd) with no confirmations.\n\n"
read -p  "Continue? Only 'yes' will be accepted to confirm: "
if [[ $REPLY == [Yy]es ]]; then
    find . -type f -name "Makefile" \
        -execdir pwd \; -execdir make init \; -execdir terraform 0.12upgrade -yes \; -execdir touch terraform_0.12_ready \;
    readarray NO_MAKEFILE < <(find . -type f -not -name "terraform_0.12_ready" -exec dirname {} \; | grep -Ev ".terraform|.terragrunt-cache" | sort -u)
    for i in ${FILES[@]}; do
        if [[ -e main.tf ]]; then
            pwd && terraform init $i && terraform 0.12upgrade -yes
        fi
    done
else
    echo "Exiting"
    exit
fi
