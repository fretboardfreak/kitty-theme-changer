#!/bin/bash

profile_list=$1
if [[ ! -f ${profile_list} ]]; then
    echo "Please provide profiles file";
    exit 1;
fi

for profile in $(cat ${profile_list}); do
    echo $profile;
    kitty-theme -T $profile;
    read -p "enter to continue";
done
