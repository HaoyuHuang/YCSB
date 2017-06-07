#!/bin/bash

source machines.sh

# maven cleanup
mvn clean

# copy it over
for client in ${CLIENT_IPS[@]}
do
	scp -r ~/ycsb/YCSB $client:~/ycsb/
	ssh $client "cd ~/ycsb/YCSB && mvn -pl com.yahoo.ycsb:mongodb-binding -am clean package"
	ssh $client "cd ~/ycsb/YCSB && mvn -pl com.yahoo.ycsb:redis-binding -am clean package"
done

# re-install the project locally.
mvn -pl com.yahoo.ycsb:redis-binding -am clean package
mvn -pl com.yahoo.ycsb:mongodb-binding -am clean package

# copy CAMPServer over.
#for cache in ${CACHE_IPS[@]}
#do
#	scp -r ~/Desktop/EW/CAMPServer $cache:~/Desktop/EW/
#done

# copy redis server.
#for cache in ${CACHE_IPS[@]}
#do
#	echo "Copy redis server "$cache
#	scp -r ~/redis-3.2.8 $cache:~/
#	ssh $cache "mkdir -p ~/Dropbox"
#	scp ~/Dropbox/redis.conf $cache:~/Dropbox
#done
