NUM_PLAYERS=10


#sleep 2


for (( i=0; i<$NUM_PLAYERS; i++ ))
do
    python3 createtest.py
done

wait
