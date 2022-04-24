# Mutual exclusion algorithms

## Running code

* To run a particular algorithm use the following command
```
mpiexec -n <no_of_processes> python <algo_name>_algorithm.py
```
* Separate log files are created for each process
* Log files contain response time for each process and total time of execution

## Editing code

* Code for the mutual exclusion algorithms are present in `root` directory of repo
* Code for lamport clock and priority queue is present inside `helpers` directory

### Testing code

* Unittests are available for all helper functionalities
* To execute unittests, run `python <helper_functionality>.unittest.py`
