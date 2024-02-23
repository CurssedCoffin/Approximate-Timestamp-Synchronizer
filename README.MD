# Example:
```python
    from ApproximateTimestampSynchronizer import ApproximateTimestampSynchronizer
    t1 = [1, 2, 3, 4]
    t2 = [1.0001, 2.0001, 3.0001]
    tolerance = 0.1
    ts = ApproximateTimestampSynchronizer([t1, t2], tolerance)
    sync_results, sync_unsynced, unsynced_count = ts.sync_results, ts.sync_unsynced, ts.unsynced_count
    # sync_results: [(1, 1.0001), (2, 2.0001), (3, 3.0001)]
    # sync_unsynced: [4, []]
    # unsynced_count: 1
```

# Args:
    msg_sequences (list): List of lists of messages, like [  [msg1, msg1, ...], [msg2, ...], ...   ]

    tolerance (int or float): The maximum time difference between the messages to be synchronized
# Functions:
    * get_stamp_from_msg: get the timestamp from the message
    * callback: the callback function
    ** Both function can be re-written for custom input and output

    run: Run the synchronization
    registerCallback: Register a callback function
    signalMessage: Signal the message to the callback function
    add: Add a message to the queue and do sync