####
# Implementation of lamport algorithm for mutual exclusion
#
#

# Dependencies
from mpi4py import MPI
import threading, time, random
# Local Dependencies
from helpers.priority_queue import PriorityQueue
from helpers.lamport_clock import LamportClock

# Initialise locks
lc_lock = threading.Lock()
pq_lock = threading.Lock()
pr_lock = threading.Lock()

# Initialise clock
lc = LamportClock()
# Initialise Queue
pq = PriorityQueue()
# Initialise count
pr = []

# Initialise MPI framework
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

for it in range(size):
    if it == 0:
        pr.append(1)
    elif it == rank:
        pr.append(1)
    else:
        pr.append(0)

log_file = open("log_"+str(rank)+".txt", "w")
   

def listen_to_process(process_id):
    global pr
    while True:
        data = comm.recv(source=process_id, tag=0)
        if data == -1:
            break
        elif data[0] == "request":
            # Add request to queue
            pq_lock.acquire()
            pq.insert(data[1], process_id)
            pq_lock.release()
            # Respond with current timestamp
            lc_lock.acquire()
            res = lc.get_time()
            lc_lock.release()
            comm.send(["response", res], dest=process_id, tag=0)
        elif data[0] == "response":
            # Compare timestamps
            lc_lock.acquire()
            curr_time = lc.get_time()
            lc_lock.release()
            if curr_time <= data[1]:
                pr[process_id] = 1
            # Call function to check and execute CS
            #execute_cs()
        elif data[0] == "release":
            pq_lock.acquire()
            pq.remove_by_id(process_id)
            pq_lock.release()
            # Compare timestamps
            lc_lock.acquire()
            curr_time = lc.get_time()
            lc_lock.release()
            if curr_time <= data[1]:
                pr[process_id] = 1
            # Call function to check and execute cs
            #execute_cs()



if rank == 0:
    start_time = time.time()
    # Start execution
    for it in range(1, size):
        init_msg = 1
        comm.send(init_msg, dest=it, tag=0)

    # Listen for completion
    for it in range(1, size):
        msg = comm.recv(source=it, tag=0)

    # Send termination message
    for it in range(1, size):
        term_msg = -1
        comm.send(term_msg, dest=it, tag=0)
    end_time = time.time()
    # Wait for response
    for it in range(1, size):
        term_msg = comm.recv(source=it, tag=0)
    print("Total time: ", end_time - start_time)
    log_file.write("Total time: "+str(end_time - start_time)+"\n")
else:
    # Wait for init message
    init_msg = comm.recv(source=0, tag=0)

    # Initialise threads
    threadArr = [ None ]
    for it in range(1, size):
        if it != rank:
            threadArr.append( threading.Thread(target=listen_to_process, args=[int(it)]) )
        else:
            threadArr.append( None )
    # Start threads
    for it in range(1, size):
        if it != rank:
            threadArr[it].start()

    # Begin computation
    thro_start_time = time.time()
    # Temporarily hard coding
    no_of_cs = 4
    #if rank > size/2:
    #    no_of_cs = 6
    while no_of_cs > 0:
        
        # Check if need to enter CS now
        temp = random.uniform(0,1)
        if temp >= 0 and temp <= 1:
            # Reset flags
            pr_lock.acquire()
            for it in range(1, size):
                if it != rank:
                    pr[it] = 0
            pr_lock.release()
            lc_lock.acquire()
            curr_time = lc.get_time()
            lc_lock.release()
            pq_lock.acquire()
            pq.insert(curr_time, rank)
            pq_lock.release()
            res_time_start = time.time()
            print("rank: ", rank, " cs: ", no_of_cs, " clock: ", lc.get_time(), " queue: ", pq.get_queue())
            # Send request to enter CS
            for it in range(1, size):
                if it != rank:
                    comm.send(["request", curr_time], dest=it, tag=0)
            # Wait till CS is executed
            while True:

                # Check if cs is available
                temp = 0
                pr_lock.acquire()
                for it in range(size):
                    temp = temp + pr[it]
                pr_lock.release()
                if temp == size:
                    pq_lock.acquire()
                    top = pq.get_head()
                    pq_lock.release()
                    if top[1] == rank:
                        # Send release message
                        for it in range(1, size):
                            if it != rank:
                                comm.send(["release", curr_time+1, rank], dest=it, tag=0)
                        # Remove from queue
                        pq_lock.acquire()
                        pq.remove_by_id(rank)
                        pq_lock.release()
                        # Update no of cs required
                        no_of_cs = no_of_cs - 1
                        break
            res_time_end = time.time()
            print("rank: ", rank, " cs: ", no_of_cs, " r_time: ", res_time_end - res_time_start)
            log_file.write("rank: "+str(rank)+" cs: "+str(no_of_cs)+" r_time: "+str(res_time_end - res_time_start)+"\n")
        # Increment clock
        lc_lock.acquire()
        lc.increment()
        lc_lock.release()

    thro_end_time = time.time()
    print("rank: ", rank, " t_time: ", thro_end_time - thro_start_time)
    log_file.write("rank: "+str(rank)+" t_time: "+str(thro_end_time - thro_start_time)+"\n")

    # Send completion message
    lc_lock.acquire()
    lc.update(10000)
    lc_lock.release()
    msg = "complete"
    comm.send(msg, dest=0, tag=0)

    # Wait for termination message
    term_msg = comm.recv(source=0, tag=0)
    # Forward termination message to all processes
    for it in range(1, size):
        if it != rank:
            term_msg = -1
            comm.send(term_msg, dest=it, tag=0)

    # Wait for all threads to exit
    for it in range(1, size):
        if it != rank:
            threadArr[it].join()
    # Reply to termination message
    term_msg = -1
    comm.send(term_msg, dest=0, tag=0)

log_file.close()
