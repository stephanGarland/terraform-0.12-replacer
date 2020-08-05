#!/usr/bin/env bash

printf "Checking in $(pwd) and all subdirectories for missing terraform_0.12_ready\n\n"
for i in **/; do
    if [[ ! -e $i/terraform_0.12_ready ]] && [[ $(ls $i*.tf | wc -l) -ge 1 ]] 2>/dev/null; then 
        echo $i
    fi
done
