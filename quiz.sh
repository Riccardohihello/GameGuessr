#!/bin/bash

python3 Server.py &

sleep 1

for i in {1..4}
do
   python3 Client.py &
done

read -p "premere invio nel terminale per tgerminare i client"

pkill -f Server.py Client.py

