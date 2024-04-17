#!/bin/bash

echo "Run,Core,Cache,Hits,Misses,Missrate";
for i in $@; 
do 
	cat ${i} | grep "rate\|L1D\|L2\|L3\|Hits\|Misses" |sed ':a;N;$!ba;s/Hits:                                0\n//g' | sed ':a;N;$!ba;s/Misses:                              0//g' |sed 's/ //g'  | sed ':a;N;$!ba;s/\nHits:/,/g' | sed ':a;N;$!ba;s/\nMisses:/,/g' |sed ':a;N;$!ba;s/\nMissrate:/,/g' | sed ':a;N;$!ba;s/\nLocalmissrate:/,/g'| sed ':a;N;$!ba;s/D(size=65536,assoc=4,block=256,LRU)stats://g' | sed ':a;N;$!ba;s/(size=8388608,assoc=16,block=256,LRU,inclusive)stats://g' | sed ':a;N;$!ba;s/(size=268435456,assoc=16,block=256,LRU,inclusive)stats://g' | sed ':a;N;$!ba;s/(size=536870912,assoc=16,block=256,LRU,inclusive)stats://g' | sed 's/L1/,L1/g' | sed ':a;N;$!ba;s/\nC/appname,/g' | sed 's/L2/appname,,L2/g' | sed '$ d' | sed 's/%//g' |sed 's/ //g' | sed "s/appname/$(basename ${i})/g"  ;
done

