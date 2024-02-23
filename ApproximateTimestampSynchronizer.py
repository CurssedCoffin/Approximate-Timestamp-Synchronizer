# Author: CurssedCoffin
# Github repo: https://github.com/CurssedCoffin

import itertools
from natsort import natsorted

class ApproximateTimestampSynchronizer:
    """
    ApproximateTimestampSynchronizer Filter Class
    Example:
        from ApproximateTimestampSynchronizer import ApproximateTimestampSynchronizer
        t1 = [1, 2, 3, 4]
        t2 = [1.0001, 2.0001, 3.0001]
        tolerance = 0.1
        ts = ApproximateTimestampSynchronizer([t1, t2], tolerance)
        sync_results, sync_unsynced, unsynced_count = ts.sync_results, ts.sync_unsynced, ts.unsynced_count
        # sync_results: [(1, 1.0001), (2, 2.0001), (3, 3.0001)]
        # sync_unsynced: [4, []]
        # unsynced_count: 1
    ======================
    Args:
        msg_sequences (list): list of lists of messages, like [  [msg1, msg1, ...], [msg2, ...], ...   ]
        tolerance (int or float): the maximum time difference between the messages to be synchronized
    Functions:
        * get_stamp_from_msg: get the timestamp from the message
        * callback: the callback function
        
        run: run the synchronization
        registerCallback: register a callback function
        signalMessage: signal the message to the callback function
        add: add a message to the queue
    """
    def __init__(self, msg_sequences: list, tolerance):
        # init params
        self.registerCallback(self.callback)
        self.msg_sequences = msg_sequences
        self.queues = [{} for msg_sequence in self.msg_sequences] # stores {stamp: msg}
        self.latest_stamps = [0 for msg_sequence in self.msg_sequences]
        self.tolerance = tolerance
        
        # save results
        self.sync_results = []
        self.sync_unsynced = [[] for msg_sequence in self.msg_sequences]
        self.unsynced_count = 0
        
        self.run()
    
    def get_stamp_from_msg(self, msg):
        return msg
    
    def callback(self, *args):
        self.sync_results.append(args)
    
    def run(self):
        for queue_index, (msg_sequence, queue) in enumerate(zip(self.msg_sequences, self.queues)):
            for msg in natsorted(msg_sequence):
                self.add(msg, queue, queue_index)
        
        for queue_index, queue in enumerate(self.queues):
            for stamp, msg in queue.items():
                self.sync_unsynced[queue_index].append(msg)
                self.unsynced_count += 1
    
    def registerCallback(self, _callback, *args):
        self.callbacks = {}
        conn = len(self.callbacks)
        self.callbacks[conn] = (_callback, args)
        return conn

    def signalMessage(self, *msg):
        for (_callback, args) in self.callbacks.values():
            _callback(*(msg + args))
    
    def add(self, msg, my_queue, my_queue_index=None):
        stamp = self.get_stamp_from_msg(msg)
        my_queue[stamp] = msg

        if my_queue_index is None:
            search_queues = self.queues
        else:
            search_queues = self.queues[:my_queue_index] + \
                self.queues[my_queue_index+1:]
        
        # sort and leave only reasonable stamps for synchronization
        stamps = []
        for queue in search_queues:
            topic_stamps = []
            for s in queue:
                stamp_delta = abs(s - stamp)
                if stamp_delta > self.tolerance:
                    continue  # far over the tolerance
                topic_stamps.append((s, stamp_delta))
            if not topic_stamps:
                return
            topic_stamps = sorted(topic_stamps, key=lambda x: x[1])
            stamps.append(topic_stamps)
        for vv in itertools.product(*[next(iter(zip(*s))) for s in stamps]):
            vv = list(vv)
            # insert the new message
            if my_queue_index is not None:
                vv.insert(my_queue_index, stamp)
            qt = list(zip(self.queues, vv))
            if ( ((max(vv) - min(vv)) < self.tolerance) and
                (len([1 for q,t in qt if t not in q]) == 0) ):
                msgs = [q[t] for q,t in qt]
                self.signalMessage(*msgs)
                for q,t in qt:
                    del q[t]
                break  # fast finish after the synchronization
