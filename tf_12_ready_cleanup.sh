#!/usr/bin/env bash

read -p  "Do you want to delete all tf_0.12_ready files? Only 'yes' will be accepted to confirm: "
if [[ $REPLY == [Yy]es ]]; then
    find . -type f -name "terraform_0.12_ready" -size 0 -exec rm {} \;
else
    echo "Exiting"
fi