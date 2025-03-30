#!/bin/bash

if [ -z "$1" ]; then
    echo "Bitte ein Verzeichnis als Parameter angeben."
    exit 1
fi

target_dir="../../data/raw/cloud_merged_pcap/descriptor"

for dir in "$1"/*/; do
    if [ -d "$dir" ]; then
        dir_name=$(basename "$dir")

        for file in "$dir"descriptor-*; do
            if [ -f "$file" ]; then
                target_file="$target_dir/descriptor-$dir_name"

                cp "$file" "$target_file"
            fi
        done
    fi
done

echo "Kopieren abgeschlossen."
