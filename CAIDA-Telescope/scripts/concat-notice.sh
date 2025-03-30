#!/bin/sh
#
# Script based on https://github.com/thisni1s/telescope
#

output_file="concat-notice.log"

# Remove the output file if it already exists
[ -f "$output_file" ] && rm "$output_file"

head -n 1 fol-datasource-ucsd-nt-year-2025-month-01-day-20-hour-16-ucsd-nt-notice.log >> "$output_file"

# Loop through all CSV files in the current directory
for file in *notice.log; do
    echo "Working on $file"
    # Skip the loop iteration if the file is the output file itself
    [ "$file" = "$output_file" ] && continue

    # Skip the loop iteration if the file is empty
    [ ! -s "$file" ] && continue

    # Append the contents of the file without the header to the output file
    tail -n +2 "$file" >> "$output_file"
done

echo "Concatenation complete. Output saved to $output_file"

