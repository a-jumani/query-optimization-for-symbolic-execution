#!/usr/bin/env python

from z3 import *
import time
import sys

'''
Records time spent in solving some path contraints of the GCD function.

@input
	reps		constraints up to reps levels of depth in the symbolic execution tree
	incremental	solver z3 will be used if incremental == True

@return
		[t_0, t_1, ...t_rep] where t_i is the time consumed in solving the path constraint of depth i
'''
def test(reps, incremental):

	# initial array for time-keeping
	t = []

	# initiate z3 objects
	a = BitVec("a", 32)
	s = Solver()

	# initiate the solver
	s.add(a != 0)

	for i in range(int(reps)):

		# solve the constraints and record the time
		time_start = time.time()
		stat = s.check()
		t.append(time.time() - time_start)

		# reset the solver if z3 is not to be used incrementally
		if not incremental:
			s_new = Solver()
			for j in s.assertions():
				s_new.add(j)
			s = s_new

		# adjust the same solver to represent path constraints of the next level of recursion
		s.add(LShR(a, i + 1) != 0)

	return t


'''
Run test multiple times

@input
	freq		number of times to run the test
	length		depth of the path constraints to reach to
	incremental	solver z3 will be used if incremental == True

@return			an array t such that t[i][j] is the time taken by the solver in the ith run for path constraint representing depth j
'''
def run_test(freq, length, incremental):

	# run test freq number of times
	result = []
	for i in range(freq):
		time_recorded = test(length, incremental)
		result.append(time_recorded)

	return result


'''
Average the results of running the test multiple times

@input
	results		array of results as given by run_test function

@return			an array t such that t[i] is the average time taken by the solver for path constraint representing depth i
'''
def avg_result(result):

	average = []
	depth = len(result[0])
	freq = len(result)

	# iterate over path constraints at depth i, sum the results and then average them
	for i in range(depth):
		total = 0
		for j in range(freq):
			total += result[j][i]

		average.append(total / freq)

	return average


'''
Run test multiple times

@input
	freq	number of times to run the test
	length	depth of the path constraints to reach to

@return		an array of average time consumed by the solver
'''
def main(freq, length):

	# get the average the results with incremental solving
	average_opt = avg_result(run_test(freq, length, True))
	print average_opt

	# get the average the results without incremental solving
	average_no_opt = avg_result(run_test(freq, length, False))
	print average_no_opt


if __name__ == '__main__':
	main(int(sys.argv[1]), int(sys.argv[2]))
