#!/usr/bin/env python
# coding=utf8

def signed_area(ps):
	sum = 0
	l = len(ps)
	for i in range(0,l):
		pi = ps[i]
		pj = ps[(i+1)%l]
		sum += pi[0]*pj[1] - pj[0]*pi[1]
	return 0.5 * sum


def is_counterclockwise(ps):
	a = signed_area(ps)
	assert(a != 0)
	return a > 0


class HexPosition(object):
	class IllegalPositionException(Exception): pass

	def __init__(self, r = 0, g = 0, b = 0):
		if not r+g+b == 0: raise self.IllegalPositionException()
		self._t = (r,g,b)

	def __repr__(self):
		return '%s(%d, %d, %d)' % (self.__class__.__name__, self.r, self.g, self.b)

	@property
	def r(self):
		return self._t[0]

	@property
	def g(self):
		return self._t[1]

	@property
	def b(self):
		return self._t[2]

	def __add__(self, h):
		return HexPosition(self._t[0] + h._t[0], self._t[1] + h._t[1], self._t[2] + h._t[2])

	def __sub__(self, h):
		return HexPosition(self._t[0] - h._t[0], self._t[1] - h._t[1], self._t[2] - h._t[2])

	def __lt__(self, o):
		return self._t < o

	def __le__(self, o):
		return self._t <= o

	def __eq__(self, o):
		return self._t == o

	def __ne__(self, o):
		return self._t != o

	def __gt__(self, o):
		return self._t > o

	def __ge__(self, o):
		return self._t >= o

	def __hash__(self):
		return hash(self._t)

	def norm(self):
		# uses p=inf metric from the origin as the norm
		return max(map(abs, self._t))

	def distance_to(self, h):
		return (self-h).norm()

	def get_projected_coords(self):
		# projects _unstretched_ onto a 2d surface.
		# to get proper coordinates for hex centers,
		# you need to apply f(x,y) |-> (3/2x, sqrt(3)/2y)
		return (self._t[0], self._t[1]-self._t[2])

	@classmethod
	def walk_circle(_class, start, m = None):
		"""starting at start, walk a circle around m, clockwise direction"""
		if None == m: m = _class.origin

		yield start
		if start == m: return

		r = start.distance_to(m)
		cur = None

		# get starting move
		for d in _class.directions:
			cand = start+d

			# check radius
			if cand.distance_to(m) == r:

				# determine if going from start to candidate is
				# is a clockwise motion relative to m
				if not is_counterclockwise([m.get_projected_coords(), start.get_projected_coords(), cand.get_projected_coords()]):
					cur = cand
					break

		# starting direction is the one from start to cur
		cdir_i = _class.directions.index(cur-start)

		while cur != start:
			# select proper direction
			while True:
				cand = cur+_class.directions[cdir_i]
				if cand.distance_to(m) != r:
					# time to change directions
					cdir_i = (cdir_i + 1) % len(_class.directions)
				else:
					break

			yield cur
			cur = cand

	@classmethod
	def walk_spiral(_class, r, direction, m = None):
		"""walk a spiral until radius r, starting in direction, around m"""
		if None == m: m = _class.origin

		start = m

		while start.distance_to(m) <= r:
			for p in _class.walk_circle(start, m): yield p
			start = p+direction

HexPosition.origin = HexPosition()
HexPosition.directions = map(lambda t: HexPosition(*t), [
                              (0,1,-1), # N
                              (1,0,-1), # NE
                              (1,-1,0), # SE
                              (0,-1,1), # S
                              (-1,0,1), # SW
                              (-1,1,0), # NW
                         ])
