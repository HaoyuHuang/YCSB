import os
from pprint import pprint
import sys
import json
import math
# import statistics

def average(a):
	return sum(a) / len(a)

def avg(a):
	if len(a) == 0:
		return 999999
	max_a = max(a)
	a.remove(max_a)
	min_a = min(a)
	a.remove(min_a)
	return sum(a) / len(a)

def print_exp4a_stats(workloads, columns, stats, out, outputlen):
	# row = "time,invalidate+no-migration,refill+no-migration,invalidate+migrate-new,refill+migrate-new,refill+migrate-all\n"
	row = "time"
	for column in columns:
		row += ","
		row += column
	row += "\n"
	data=columns

	# row = "time,refill+no-migration,invalidate+migrate-new,refill+migrate-new,refill+migrate-all\n"
	# data=["refill+no-migration" , "invalidate+migrate-new" , "refill+migrate-new", "refill+migrate-all"]
	base=0
	for i in range(outputlen):
		row += str(i + base)
		row += ","
		for config in data:
			row += str(workloads[config][stats][i])
			row += ","
		row += "\n"

	text_file = open(out, "w")
	text_file.write(row)
	text_file.close()
	print stats
	print row

def parse_exp4a(eval_result, workload, thread):
	workloads = {}
	for d in os.listdir(eval_result):
		if "exp" not in d:
			continue
		if workload not in d:
			continue
		if thread not in d:
			continue
		if "_1200" not in d:
			continue
		# new-paper-expmotiv-migration-workloadb1-coord-NORMAL-clientconfig-5_cache-coorconfig-5_cache_migrate_to_100s-5-clients-200-threads-tr-10000000-600-z
		method=d.split('-')[10]

		methods=["5_cache_normal", "5_cache_migrate_to_10s" , "5_cache_migrate_to_100s" , "5_cache_migrate_from"]
		if "5_cache_normal" in method:
			method="No-Migration"
		elif "5_cache_migrate_to_10s" in method:
			method="10s-Early-Migration"
		elif "5_cache_migrate_to_100s" in method:
			method="100s-Early-Migration"
		elif "5_cache_migrate_from" in method :
			method="Migration"
			

		
		print method

		workloads[method] = {}
		workloads[method]["cache"] = []
		workloads[method]["read-avg"] = []
		workloads[method]["read-p90"] = []
		workloads[method]["update-avg"] = []
		workloads[method]["update-p90"] = []
		workloads[method]["thpt"] = []
		workloads[method]["restore_cache"] = 0
		workloads[method]["data"] = {}

		cache = open(eval_result + '/' + d + '/cachehit.out').readlines()
		cache_hits = []
		for i in range(1, len(cache)):
			hits = cache[i].replace('\n', '').split(',')
			hs = 0.0
			for hit in hits:
				if hit is '':
					continue
				hs += float(hit)
			cache_hits.append(hs / (len(hits) - 1))

		thpt_text = open(eval_result + '/' + d + '/clienth1-throughput.out').readlines()
		thpt = []
		for i in range(1, len(thpt_text)):
			thpt.append(int(thpt_text[i].replace('\n', '')))
		

		for client in [7, 8, 9, 10]:
			thpt_text = open(eval_result + '/' + d + '/clienth{}-throughput.out'.format(client)).readlines()
			for i in range(1, len(thpt_text)):
				if i < len(thpt):
					thpt[i] += int(thpt_text[i].replace('\n', ''))

		read = open(eval_result + '/' + d + '/clienth1-read-latency.out').readlines()
		update = open(eval_result + '/' + d + '/clienth1-update-latency.out').readlines()
		
		start = 150

		for i in range(start, start + 300, 1):
			offset=i-2
			workloads[method]["cache"].append(str(cache_hits[i]))
			workloads[method]["read-avg"].append(read[offset].split(',')[0])
			workloads[method]["read-p90"].append(read[offset].split(',')[1])
			workloads[method]["thpt"].append(str(thpt[offset]))
			if "workloada" in workload or "workloadb" in workload:
				workloads[method]["update-avg"].append(update[offset].split(',')[0])
				workloads[method]["update-p90"].append(update[offset].split(',')[1])

		# print start
		end=-1
		prev_cache_hits = []
		for i in range(start-10, start+5, 1):
			hit = float(cache[i].split(',')[0])
			if hit != -1 or hit != 0:
				prev_cache_hits.append(hit)
		prev_cache_hit=sum(prev_cache_hits) / len(prev_cache_hits)
		print prev_cache_hit

		for i in range(start + 10, len(cache), 1):
			hit = float(cache[i].split(',')[0])
			if hit != -1 and end == -1:
				end = i
			if hit == 100:
				continue
			if hit >= prev_cache_hit:
				# print i
				# print end
				workloads[method]["restore_cache"] = i - end
				break
			elif end != -1:
				workloads[method]["restore_cache"] = i - end

		data = json.load(open(eval_result + '/' + d + '/stats-h1-metrics.out'))
		workloads[method]["data"] = data

	file="{}/{}-{}-".format(eval_result, workload, thread)
	file += "{}"
	if "workloada" in workload or "workloadb" in workload:
		methods=["No-Migration", "Migration" , "10s-Early-Migration" , "100s-Early-Migration"]

	outputlen=200
	
	print_exp4a_stats(workloads, methods, "cache", file.format("cache.csv"), outputlen)
	print_exp4a_stats(workloads, methods, "thpt", file.format("thpt.csv"), outputlen)
	print_exp4a_stats(workloads, methods, "read-avg", file.format("read-avg.csv"), outputlen)
	print_exp4a_stats(workloads, methods, "read-p90", file.format("read-p90.csv"), outputlen)
	if "workloada" in workload or "workloadb" in workload:
		print_exp4a_stats(workloads, methods, "update-avg", file.format("update-avg.csv"), outputlen)
		print_exp4a_stats(workloads, methods, "update-p90", file.format("update-p90.csv"), outputlen)
	
	# print "method,restore_cache,replay-duration,recover-duration,migrate-duration,dirty-keys,refill-dirty-keys,refill_percentage,all-keys,new-keys,new-keys-percentage,migrate-keys,migrate_percentage"
	
	# for method in methods:
	# 	data=workloads[method]["data"]["recovery"]["h2:11211"]
	# 	replay_duration = data.get("replay-duration", 0)
	# 	recover_duration = data.get("recover-duration", 0)
	# 	migrate_duration = recover_duration - replay_duration
	# 	dirty_keys=data.get("num-dirty-keys", 0)
	# 	refill_dirty_keys=data.get("num-migrated-dirty-keys", 0)
	# 	all_keys=data.get("num-all-keys", 0)
	# 	new_keys=data.get("num-new-keys", 0)
	# 	migrated_keys=data.get("num-migrate-success", 0)
	# 	refill_percentage=0
	# 	if dirty_keys != 0:
	# 		refill_percentage=float(refill_dirty_keys) * 100 / float(dirty_keys)

	# 	new_keys_percentage=0
	# 	migrate_percentage=0
	# 	if new_keys != 0:
	# 		migrate_percentage = float(migrated_keys) * 100 / float(new_keys)
	# 		new_keys_percentage = float(new_keys) * 100 / float(all_keys)
	# 	elif all_keys != 0:
	# 		migrate_percentage = float(migrated_keys) * 100 / float(all_keys)

	# 	line=method
	# 	line+=","
	# 	line+=str(workloads[method]["restore_cache"])
	# 	line+=","
	# 	line+=str(replay_duration)
	# 	line+=","
	# 	line+=str(recover_duration)
	# 	line+=","
	# 	line+=str(migrate_duration)
	# 	line+=","
	# 	line+=str(dirty_keys)
	# 	line+=","
	# 	line+=str(refill_dirty_keys)
	# 	line+=","
	# 	line+=str(refill_percentage)
	# 	line+=","
	# 	line+=str(all_keys)
	# 	line+=","
	# 	line+=str(new_keys)
	# 	line+=","
	# 	line+=str(new_keys_percentage)
	# 	line+=","
	# 	line+=str(migrated_keys)
	# 	line+=","
	# 	line+=str(migrate_percentage)
	# 	print line

def get(table, keys):
	for i in range(len(keys)):
		if keys[i] in table:
			table = table[keys[i]]
		else:
			return 0
	return table

def median(lst):
	if len(lst) == 0:
		return -1
	sortedLst = sorted(lst)
	lstLen = len(lst)
	index = (lstLen - 1) / 2
	return sortedLst[index]

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/float(n) # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def stddev(data, ddof=0):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
    	return 0
        # raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5
	# return 0

parse_exp4a("/Users/haoyuh/Documents/PhdUSC/Migration/results-migration", "workloadb1", "40-threads")

