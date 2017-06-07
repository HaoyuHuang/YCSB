#!/bin/bash

source machines.sh

YCSB="~/ycsb/YCSB"
ARCHIVE="/home/hieun/Desktop/archive"
RESULT="/home/hieun/Desktop/results"

#ycsb_client="mongodb-mc-redlease"
ycsb_client="mongodb"
modes=( ["normal"]="9000,10000" )   # dbfail mode (no dbfail for this exp)
AR="10"
TIME="300"

# select cache mode
cache_mode="wb"
cache_mode="wt"
cache_mode="wa"

function join_by { local IFS="$1"; shift; caches="$*"; }

caches=( "${CACHE_IPS[@]/%/:11211}" )
join_by , ${caches[@]}

for workload in "workloada_1M" "workloadb_1M"
do
  for thread in 1 2 4 8 16 32 64
  do
    echo "Client: $ycsb_client"
    echo "Time: $TIME"
    echo "Client IPs: ${CLIENT_IPS[@]}"
    echo "Cache IPs: ${CACHE_IPS[@]}"
    echo "Cache Mode: $cache_mode"
    echo "Workload: $workload"
    echo "# Thread: $thread"

    # reset mongo
    java -jar ExpRestart.jar restartFC $MONGO_IP hieun /home/hieun/Desktop/mongo/ /home/hieun/Desktop/mongo_ycsb_1m/ back
    #mongo --host $MONGO_IP --port 27017 < mongoscript.js
    #ssh $MONGO_IP "sudo service mongod restart"

    sleep 2

    # restart cache
    for CACHE_IP in ${CACHE_IPS[@]}
    do
      echo "Restart cache "$CACHE_IP
      ssh $CACHE_IP "killall twemcache"
      ssh $CACHE_IP "killall redis-server"
      ssh $CACHE_IP "killall memcached"
    done

    # warm up for 100 secs
    for CLIENT_IP in ${CLIENT_IPS[@]}
    do
      cmd="bin/ycsb run $ycsb_client -P workloads/$workload -jvm-args \"-Xmx12g -XX:+UseG1GC -XX:+UseStringDeduplication\" -p mongodb.url=mongodb://$MONGO_IP:27017 -p mongo.database=ycsb -p cacheservers=$caches -p numcacheservers=1 -s -threads $thread -p maxexecutiontime=100 -p fullwarmup=true -p dbfail=${modes[$m]} -p numarworker=$AR -p cachemode=$cache_mode"
      echo $cmd
      ssh $CLIENT_IP "cd $YCSB && $cmd > $RESULT/run_$CLIENT_IP 2>&1 &" &    
    done

    sleepTime=120
    echo "Sleep for "$sleepTime
    sleep $sleepTime

    # start stats
    bash "startstats.sh"

    # run multi-clients
    for CLIENT_IP in ${CLIENT_IPS[@]}
    do
      cmd="bin/ycsb run $ycsb_client -P workloads/$workload -jvm-args \"-Xmx12g -XX:+UseG1GC -XX:+UseStringDeduplication\" -p mongodb.url=mongodb://$MONGO_IP:27017 -p mongo.database=ycsb -p cacheservers=$caches -p numcacheservers=1 -s -threads $thread -p maxexecutiontime=$TIME -p fullwarmup=true -p dbfail=${modes[$m]} -p numarworker=$AR -p cachemode=$cache_mode"
      echo $cmd
      ssh $CLIENT_IP "cd $YCSB && $cmd > $RESULT/run_$CLIENT_IP 2>&1 &" &    
    done

    sleepTime=$((TIME+20))
    echo "Sleep for "$sleepTime
    sleep $sleepTime

    # get cache stats
    for CACHE_IP in ${CACHE_IPS[@]}
    do
      { sleep 2; echo "stats"; sleep 2; echo "stats slabs"; sleep 2; echo "quit"; sleep 1; } | telnet $CACHE_IP 11211 > $RESULT/$CACHE_IP"cachestats.txt"
    done

    # collec stats
    bash "copystats.sh"

    folder="wb-mongoonly-$workload-th$thread"
    mkdir -p $ARCHIVE/$folder
    mv $RESULT/* $ARCHIVE/$folder/
    eval "java -jar graph.jar $ARCHIVE/$folder $CACHE_IP $MONGO_IP $CLIENT_IP"
  done
done
