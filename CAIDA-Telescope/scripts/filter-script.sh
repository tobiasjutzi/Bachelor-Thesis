#
# Script based on https://github.com/thisni1s/telescope
#

# Authenticate
source /home/limbo/.limbo_creds
eval $(swift auth)

# Switch to working dir
cd /home/limbo/swift-scripts/scripts

filter="$1"
intervalLimits="$2"

# clear caps_all.txt
> ../scan-workplace/caps_all.txt

# get all available caps
swift list telescope-ucsdnt-pcap-live > ../scan-workplace/caps_all.txt

# filter caps_all
bash scan-time-interval.sh "scan-intervalLimints.txt"
wait

# move old log files
mv ../scan-workplace/*.log ../scan-logs/
rm ../scan-workplace/cap_*

while [ -s "../scan-workplace/caps_all.txt" ]; do
   # build the caps file
   head -n 8 ../scan-workplace/caps_all.txt > ../scan-workplace/caps.txt # ersten 8 Zeilen von caps_all als/in caps.txt speichern
   mv ../scan-workplace/caps_all.txt ../scan-workplace/caps_all.txt.old # caps_all wird als cap_all old gespeichert
   tail -n +9 ../scan-workplace/caps_all.txt.old > ../scan-workplace/caps_all.txt # alle Zeilen ab 8 werden als caps_all gespeichert

   cd ../scan-workplace
   split --number=l/8 --additional-suffix=.txt --numeric-suffixes caps.txt cap_ # teilt caps.txt in 8 gleich große Dateien auf (also jede Datei genau
   cd ../scripts
   # 1 Zeile erzeugt dann 8 Dateien nach dem Schema cap_00.txt cap_01.txt... )

   for i in {0..7}; do
       filename="cap_0${i}.txt"
       echo "Starting worker for file: ${filename}"
       bash worker.sh "${filter}" ${filename} &
   done
   wait
done
wait

echo "Done!"