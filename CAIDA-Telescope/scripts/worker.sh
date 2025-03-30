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
  cd ../scan-workplace
  mkdir ${foldername}
  cd ./${foldername}
  tracesplit -m 1 --filter="${filter}" -c 1000000 pcapfile:swift://telescope-ucsdnt-pcap-live/${p} pcapfile:out-${outfile}

  cd ../../scripts
  sudo docker run -i --rm -v ./cfg:/cfg -v $(realpath ../scan-workplace/${foldername}):/mnt zeek/zeek:latest zeek -C -r /mnt/out-${outfile} /cfg/scan-cfg.zeek detect_filtered_trace=F Log::default_logdir=/mnt

  # Behalte nur die relevanten Spalten in conn.log
  awk 'NR<=7 {print; next} {print $1, $3, $4, $5, $6, $7, $10, $12, $16}' OFS="\t" ../scan-workplace/${foldername}/conn.log > ../scan-workplace/${foldername}/conn_filtered.log
  mv ../scan-workplace/${foldername}/conn_filtered.log ../scan-workplace/${foldername}/conn.log

  awk 'NR<=8 {print; next} {print $1, $11, "\"" $12 "\"", $13, $14, $15}' OFS="\t" "../scan-workplace/${foldername}/notice.log" > "../scan-workplace/${foldername}/notice_filtered.log"
  mv "../scan-workplace/${foldername}/notice_filtered.log" "../scan-workplace/${foldername}/notice.log"


  mv ../scan-workplace/${foldername}/conn.log ../scan-workplace/${foldername}-conn.log
  mv ../scan-workplace/${foldername}/notice.log ../scan-workplace/${foldername}-notice.log
#  mv ../scan-workplace/${foldername}/dns.log ../scan-wocatrkplace/${foldername}-dns.log

  rm ../scan-workplace/${foldername}/out-${outfile}
  rmdir ../scan-workplace/${foldername}
  echo "Finished working on file: $p"

done < "../scan-workplace/${filename}"

echo "Finished with file $filename"


# mit 25a 5min 15p 5min
# 262 fol-datasource-ucsd-nt-year-2025-month-01-day-20-hour-16-ucsd-nt-notice.log 56K
# 999238 fol-datasource-ucsd-nt-year-2025-month-01-day-20-hour-16-ucsd-nt-conn.log 104 M

# mit 100a 5min 25p 5min
# 999238 fol-datasource-ucsd-nt-year-2025-month-01-day-20-hour-16-ucsd-nt-conn.log 12K
# 192 fol-datasource-ucsd-nt-year-2025-month-01-day-20-hour-16-ucsd-nt-notice.log 65M
