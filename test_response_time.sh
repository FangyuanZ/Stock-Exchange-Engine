NUM_PLAYERS=180

start=$(date +%s)

#sleep 2

for (( i=0; i<$NUM_PLAYERS; i++ ))
do
    python3 createtest.py
done

end=$(date +%s)
time=$(( $end - $start ))
echo $time

wait



#finish_time=`date --date='0 days ago' "+%Y-%m-%d %H:%M:%S"`
#duration=$(($(($(date +%s -d "$finish_time")-$(date +%s -d "$start_time")))))
#echo "this shell script execution duration: $duration"
