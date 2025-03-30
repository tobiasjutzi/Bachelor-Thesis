#
# Script based on https://github.com/thisni1s/telescope
#

# Authenticate
#source /home/limbo/.limbo_creds
#eval $(swift auth)

# get all available caps
#swift list telescope-ucsdnt-pcap-live > caps.txt

# filter caps
filter=$(<"$1")
filename="$2"
#while IFS= read -r p; do
while read p; do
  echo "Working on file: $p"
  outfile=$(echo "$p" | sed 's/[\/=]/-/g')
  foldername=$(echo "fol-${outfile%%.[^.]*}")
  cd ../workplace
  mkdir ${foldername}
  cd ./${foldername}
  tracesplit -m 1 --filter="${filter}" -c 1500000 pcapfile:swift://telescope-ucsdnt-pcap-live/${p} pcapfile:out-${outfile}

  cd ../../scripts
  echo "Docker start"
  sudo docker run -i --rm -v ./cfg:/cfg -v $(realpath ../workplace/${foldername}):/mnt zeek/zeek:latest zeek -C -r /mnt/out-${outfile} /cfg/cfg.zeek detect_filtered_trace=F Log::default_logdir=/mnt
  echo "Finished docker"
  # Filter conn.log: Behalte nur Zeilen mit ^d in der history Spalte
  awk 'NR<=7 {print; next} $16 ~ /\^d/ {print}' ../workplace/${foldername}/conn.log > ../workplace/${foldername}/conn_filtered.log
  mv ../workplace/${foldername}/conn_filtered.log ../workplace/${foldername}/conn.log

  # Behalte nur die relevanten Spalten in conn.log
  awk 'NR<=7 {print; next} {print $1, $3, $4, $5, $6, $7, $10, $12, $16}' OFS="\t" ../workplace/${foldername}/conn.log > ../workplace/${foldername}/conn_filtered.log
  mv ../workplace/${foldername}/conn_filtered.log ../workplace/${foldername}/conn.log

  echo "Finished filtering"

  mv ../workplace/${foldername}/conn.log ../workplace/${foldername}-conn.log
  mv ../workplace/${foldername}/notice.log ../workplace/${foldername}-notice.log
#  mv ../workplace/${foldername}/dns.log ../workplace/${foldername}-dns.log

  rm ../workplace/${foldername}/out-${outfile}
  rmdir ../workplace/${foldername}
  echo "Finished working on file: $p"

done < "../workplace/${filename}"

echo "Finished with file $filename"