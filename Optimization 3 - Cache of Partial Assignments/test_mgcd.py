from z3 import *
import os, time


'''
Compares time spent in solving queries with and without partial counter-example cache hits of the modified GCD function.

@input
	reps	constraints or copying up to reps levels of depth in the symbolic execution tree

@return
		average time spent copying
'''
def test(reps):

	time_cache = []
	cache_hit = []
	time_no_cache = []

	# create solver
	a = BitVec("a", 32)
	b = BitVec("b", 32)
	c = BitVec("c", 32)
	solver = Solver()
	solver.add(a != 0, b != 0, c != 0)
	solver.check()

	# obtain solution
	a_sol = solver.model()[a]
	b_sol = solver.model()[b]
	c_sol = solver.model()[c]

	# initial expressions for solver predicate manipulation
	x = a
	y = b

	for i in range(reps):

		print "Rep: " + str(i)

		# add the new constraint and adjust for constraints for next depth
		solver.add(x % y != 0, c - (i + 1) != 0)
		x, y = y, x % y

		# translate the solver
		Cont = Context()
		s_new = solver.translate(Cont)

		# add partial cached solution (b and c only) and time the solving
		tstart = time.time()
		s_new.push()
		s_new.add( b.translate(Cont) == b_sol.translate(Cont), c.translate(Cont) == c_sol.translate(Cont) )
		if not s_new.check() == sat:
			cache_hit.append(0)
			s_new.pop()
			s_new.check()
		else:
			cache_hit.append(1)
		tend = time.time()
		time_cache.append(tend - tstart)

		# time the solution of the first solver
		tstart = time.time()
		solver.check()
		tend = time.time()
		time_no_cache.append(tend - tstart)

		# update the solution cache
		a_sol = solver.model()[a]
		b_sol = solver.model()[b]
		c_sol = solver.model()[c]

	print time_cache
	print time_no_cache
	print cache_hit

	return None


if __name__ == '__main__':
	test(20)
