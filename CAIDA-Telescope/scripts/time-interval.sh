#!/bin/bash

# read interval-limits file
interval_file="$1"
IFS=','

# read stark and end boundaries
start_line=$(grep "^start:" "$interval_file" | sed 's/start: //')
end_line=$(grep "^end:" "$interval_file" | sed 's/end: //')

# extract start and end values
read start_year start_month start_day start_hour <<< $(echo "$start_line")
read end_year end_month end_day end_hour <<< $(echo "$end_line")

# calculate Unix start and end timestamp
start_timestamp=$(date -d "$start_year-$start_month-$start_day $start_hour:00:00" +%s)
end_timestamp=$(date -d "$end_year-$end_month-$end_day $end_hour:00:00" +%s)

#create temp-caps.txt
touch ../workplace/temp-caps.txt


# lop throw filename file
while IFS= read -r line; do
    # extract time values
    year=$(echo "$line" | grep -oP "year=\K\d+")
    month=$(echo "$line" | grep -oP "month=\K\d+")
    day=$(echo "$line" | grep -oP "day=\K\d+")
    hour=$(echo "$line" | grep -oP "hour=\K\d+")

    # calculate Unix timestamp
    line_timestamp=$(date -d "$year-$month-$day $hour:00:00" +%s)

    # check if fileName is in the interval
    if [ "$line_timestamp" -ge "$start_timestamp" ] && [ "$line_timestamp" -le "$end_timestamp" ]; then
        echo "$line" >> ../workplace/temp-caps.txt
    fi
done < ../workplace/caps_all.txt

# delete temp-caps.txt
cp ../workplace/temp-caps.txt ../workplace/caps_all.txt
rm ../workplace/temp-caps.txt