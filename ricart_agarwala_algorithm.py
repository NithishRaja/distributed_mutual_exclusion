####
# Implementation of ricart agarwala algorithm for mutual exclusion
#
#

# Dependencies
from mpi4py import MPI
import threading, time, random
# Local Dependencies
from helpers.lamport_clock import LamportClock

# Initialise locks
lc_lock = threading.Lock()
wl_lock = threading.Lock()
wc_lock = threading.Lock()
pr_lock = threading.Lock()

# Initialise clock
lc = LamportClock()
# Initialise count
wait_list = []
# Intialise flag
want_cs = False
pr = []

# Initialise MPI framework
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

for it in range(0, size):
    if it == 0:
        pr.append(1)
    elif it == rank:
        pr.append(1)
    else:
        pr.append(0)

log_file = open("log_"+str(rank)+".txt", "w")

def listen_to_process(process_id):
    while True:
        data = comm.recv(source=process_id, tag=0)
        if data == -1:
            break
        elif data[0] == "request":
            wc_lock.acquire()
            temp_flag = want_cs
            wc_lock.release()
            lc_lock.acquire()
            curr_time = lc.get_time()
            lc_lock.release()
            if temp_flag == True:
                if curr_time < data[1]:
                    wl_lock.acquire()
                    wait_list.append(process_id)
                    wl_lock.release()
                else:
                    comm.send(["response", curr_time, rank], dest=process_id, tag=0)
            else:
                comm.send(["response", curr_time, rank], dest=process_id, tag=0)
        elif data[0] == "response":
            pr_lock.acquire()
            pr[process_id] = 1
            pr_lock.release()
            #print("rank: ", rank, " pr: ", pr)



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
    no_of_cs = 2 
    #if rank > size/2:
    #    no_of_cs = 8 
  

    while no_of_cs > 0:
        # Reset flags
        wc_lock.acquire()
        want_cs = False
        wc_lock.release()
        wl_lock.acquire()
        wait_list = []
        wl_lock.release()
        pr_lock.acquire()
        for it in range(1, size):
            if it != rank:
                pr[it] = 0
        pr_lock.release()

        # Check if need to enter CS now
        temp = random.uniform(0,1)
        if temp >= 0 and temp <= 1:
            wc_lock.acquire()
            want_cs = True
            wc_lock.release()
            res_time_start = time.time()
            # Get timestamp
            lc_lock.acquire()
            curr_time = lc.get_time()
            lc_lock.release()
            # Send requests
            for it in range(1, size):
                if it != rank:
                    comm.send(["request", curr_time], dest=it, tag=0)
            # Wait for response
            while True:
                # Check if cs is available
                temp = 0
                pr_lock.acquire()
                for it in range(size):
                    temp = temp + pr[it]
                pr_lock.release()
                if temp == size:
                    # Update no_of_cs
                    no_of_cs = no_of_cs - 1
                    break


            # Send response to waiting processes
            wl_lock.acquire()
            #for process in wait_list:
            #    comm.send(["response", curr_time, rank], dest=process, tag=0)
            for it in range(1, size):
                if it != rank:
                    comm.send(["response", curr_time, rank], dest=it, tag=0)
            wl_lock.release()
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
