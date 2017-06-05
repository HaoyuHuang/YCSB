package com.yahoo.ycsb.db;

import static com.yahoo.ycsb.db.TardisYCSBConfig.NUM_EVENTUAL_WRITE_LOGS;
import static com.yahoo.ycsb.db.TardisYCSBConfig.STATS_EW_WORKER_TIME_BETWEEN_CHECKING_EW;
import static com.yahoo.ycsb.db.TardisYCSBConfig.getEWLogKey;

import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;

import org.apache.log4j.Logger;

import com.meetup.memcached.MemcachedClient;
import com.meetup.memcached.SockIOPool;

public class EWStatsWatcher implements Callable<Void> {
	private final MemcachedClient memcachedClient;

	private boolean isRunning = true;

	private final Logger logger = Logger.getLogger(EWStatsWatcher.class);

	public EWStatsWatcher() {
		super();
		this.memcachedClient = new MemcachedClient(TardisYCSBConfig.BENCHMARK);
	}

	public EWStatsWatcher(MemcachedClient client) {
		this.memcachedClient = client;
	}

	@Override
	public Void call() throws Exception {

		System.out.println("Start EWStatsWatcher...");

		String[] EWs = new String[NUM_EVENTUAL_WRITE_LOGS];
		for (int i = 0; i < EWs.length; i++) {
			EWs[i] = getEWLogKey(i);
		}

		while (isRunning) {

			try {
				Map<String, Object> ewList = memcachedClient.getMulti(EWs);
				
				int cnt = 0;
				for (String ew: ewList.keySet()) {
				  String val = (String) ewList.get(ew);
					Set<String> dirtyUserIds = MemcachedSetHelper.convertSet(val);
					cnt += dirtyUserIds.size();
				}

				System.out.println("Remaining dirty docs: "+cnt);
				try {
					Thread.sleep(STATS_EW_WORKER_TIME_BETWEEN_CHECKING_EW);
				} catch (Exception e) {
					logger.error("sleep got interrupted", e);
				}
			} catch (Exception e) {
				System.out.println("EW failed");
				e.printStackTrace();
			}
		}
		return null;
	}

	public void shutdown() {
		isRunning = false;
		logger.info("shutdown EW stats watcher");
	}

	public static void main(String[] args) {
		String[] serverlist = { "127.0.0.1:11211" };
		SockIOPool pool = SockIOPool.getInstance("BG");
		if (!pool.isInitialized()) {
			pool.setServers(serverlist);

			pool.setInitConn(100);
			pool.setMinConn(1);
			pool.setMaxConn(100);
			pool.setMaintSleep(20);

			pool.setNagle(false);
			pool.initialize();
		}

		// get client instance
		MemcachedClient mc = new MemcachedClient("BG");
		Map<String, Long> stats = (Map<String, Long>) mc.statsSlabs().values().iterator().next();
		System.out.println(stats);
		EWStatsWatcher w = new EWStatsWatcher();
		Executors.newFixedThreadPool(1).submit(w);
	}
}
