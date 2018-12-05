# Atlas Connection Analysis Tool

The MongoDB Atlas Real Time monitor will show you how many connections are established:

![connections](images/connections.png)

Behind the scenes Atlas is running `db.currentOp(true).inprog.length` to get this number.

This tools aims to provide more detail about the source of those connections by mapping the client address from the operation to the IP Whitelist entry in Atlas. If you don't open your cluster to the world (0.0.0.0/0) and take care to document your IP Whitelist entries, this tool may provide some value.

As a prerequisite, you must have already [Configured Atlas API Access](https://docs.atlas.mongodb.com/configure-api-access/) for which you'll need to provide this tool your user name and API key.

To use the tool, you need to populate a [params.py](params.py) file with your credentials:

```
# Input parameters

# Atlas API
project_id = '<Project ID found under Atlas Project Settings>'
user = '<User Name>'
password = '<API Key>'

# Atlas DB
conn_string = '<Application connection string provided by the Atlas UI>'
database = 'analysis'
```
The `analysis` database is used to run some aggregation queries against the combined results. Feel free to name it whatever you like. 

Once the parameters are in place, running the tool will produce output like the following:

```
python analyze_conn.py

MongoDB Atlas Connection Analysis Tool

Their are 7 whitelist entries
Their are 81 current operations

Active Operations:11
Dormant Operations:70

            ==== Active Whitelist Connections (1) ====
 Connection Source                             Connections
 Brian Leonard's Home Office                            1

            ==== Active System Connections (10) ====
 Connection Source                             Connections
 System                                                 3
 WT RecordStoreThread: local.oplog.rs                   1
 ReplBatcher                                            1
 monitoring keys for HMAC                               1
 watchdogMonitor                                        1
 watchdogCheck                                          1
 NoopWriter                                             1
 rsSync                                                 1

            ==== Dormant Whitelist Connections (23) ====
 Connection Source                             Connections
 ION App Team                                          14
 Brian Leonard's Home Office                            9

            ==== Dormant System Connections (47) ====
 Connection Source                             Connections
 System                                                27
 repl writer worker 2                                   1
 clientcursormon                                        1
 ApplyBatchFinalizerForJournal                          1
 repl writer worker 14                                  1
 replication-1                                          1
 initandlisten                                          1
 ftdc                                                   1
 SessionKiller                                          1
 rsBackgroundSync                                       1
 replexec-5859                                          1
 repl writer worker 4                                   1
 WTOplogJournalThread                                   1
 LogicalSessionCacheReap                                1
 replexec-5863                                          1
 WTJournalFlusher                                       1
 repl writer worker 1                                   1
 TTLMonitor                                             1
 SyncSourceFeedback                                     1
 WTCheckpointThread                                     1
 LogicalSessionCacheRefresh                             1

Analysis Complete
```


