from z3 import *
import os, time
from multiprocessing import Array


'''
Records time spent in forking while solving some path contraints of the LOG function.

@input
	reps	constraints or forks up to reps levels of depth in the symbolic execution tree

@return
		average time spent forking
'''
def test_fork(reps):

	# set up variables to record time
	forking_time = 0
	parent_solving_time = [0.0]*reps
	child_solving_time = Array('d', [0.0]*reps)

	# create and initialize the solver
	a = BitVec("a", 32)
	solver = Solver()
	solver.add(a != 0)
	solver.check()

	for i in range(reps):

		fork_tstart = time.time()

		# fork a child process
		pid = os.fork()

		# add next constraint in the parent process
		if pid:

			# recording forking time
			fork_tend = time.time()
			forking_time += fork_tend - fork_tstart

			# recording solving time
			solve_tstart = time.time()
			solver.add(LShR(a, i + 1) != 0)
			solver.check()
			solve_tend = time.time()
			parent_solving_time[i] = solve_tend - solve_tstart

		# add negation of next constraint in the child process
		else:

			# record solving time
			solving_tstart = time.time()
			solver.add(LShR(a, i + 1) == 0)
			solver.check()
			solving_tend = time.time()
			child_solving_time[i] = solving_tend - solving_tstart
			sys.exit(0)

	try:
		while True:
			os.waitpid(0, 0)
	except:
		return forking_time + sum(parent_solving_time) + sum(child_solving_time)


'''
Records time spent in copying solver while solving some path contraints of the LOG function.

@input
	reps	constraints or copying up to reps levels of depth in the symbolic execution tree

@return
		average time spent copying
'''
def test_copy(reps):

	acc_time = 0

	# create solver
	a = BitVec("a", 32)
	solver = Solver()
	solver.add(a != 0)
	solver.check()

	for i in range(reps):

		time_start = time.time()

		# translate the solver
		c = Context()
		s_new = solver.translate(c)

		# add constraints and solve the two solvers
		solver.add(LShR(a, i + 1) != 0)
		solver.check()
		s_new.add(LShR(a.translate(c), i + 1) == 0)
		s_new.check()

		# record time
		time_end = time.time()
		acc_time += time_end - time_start

	return acc_time


'''
Run a test multiple times

@input
	test	test function to run
	freq	number of times to run the test
	length	depth of the path constraints to reach to

@return		an average time consumed by the state splitting used in the test
'''
def run_test(test, freq, length):
	total = 0.0
	for i in range(freq):
		total += test(length)
	return total / freq


'''
Run a test multiple times

@input
	test	test function to run
	freq	number of times to run the test
	length	depth of the path constraints to reach to

@return		an array of average time consumed by the solver
'''
def main(freq, length):

	# run forking test
	print run_test(test_fork, freq, length)

	# run copying test
	print run_test(test_copy, freq, length)


if __name__ == '__main__':
	main(int(sys.argv[1]), int(sys.argv[2]))
