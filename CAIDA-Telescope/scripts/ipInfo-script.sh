
username="$1"
password="$2"

mc alias set twenteStorage https://storage.dacs.utwente.nl "${username}" "${password}"

root_folders=("country_asn" "rir" "rwhois" "standard_abuse" "standard_asn" "standard_carrier" "standard_company" "standard_location" "standard_privacy")


for root_folder in "${root_folders[@]}"; do
  echo "Working on: $root_folder"

  years=$(mc ls twenteStorage/feeds/ipinfo/"${root_folder}" | awk '{print $NF}' | grep -oE '^[0-9]{4}' | sort -n)
  latest_year=$(echo "$years" | tail -n 1)

  files=$(mc ls twenteStorage/feeds/ipinfo/"${root_folder}"/"${latest_year}")
  latest_file=$(echo "$files" | awk '{print $NF}' | sort | tail -n 1)

  download_path="twenteStorage/feeds/ipinfo/${root_folder}/${latest_year}/${latest_file}"
  destination_path="./database"

  mc cp "${download_path}" "${destination_path}"

  if [[ "${latest_file}" == *.gz ]]; then
    echo "Unpacking ${latest_file}..."
    gunzip -f "${destination_path}/${latest_file}"
    rm "${destination_path}/${latest_file}"
    echo "Unpacking finished: ${latest_file}"
  fi

  echo "Finished: ${root_folder}/${latest_year}/${latest_file}"

done
