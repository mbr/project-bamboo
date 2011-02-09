#!/usr/bin/env python
# coding=utf8

import random
import networkx

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


class Tile(object):
	resource = None
	number = None
	def __str__(self):
		return '<%s(%s): %s>' % (self.__class__.__name__, self.resource, self.number)


class MountainTile(Tile):
	resource = 'Ore'
	pass


class ForestTile(Tile):
	resource = 'Lumber'
	pass


class PastureTile(Tile):
	resource = 'Wool'
	pass


class DesertTile(Tile):
	pass


class FieldsTile(Tile):
	resource = 'Grain'
	pass


class HillsTile(Tile):
	resource = 'Brick'
	pass


class EmptyTile(Tile):
	pass


STANDARD_BOARD_TILES = {
	MountainTile: 3,
	HillsTile: 3,
	DesertTile: 1,
	ForestTile: 4,
	PastureTile: 4,
	FieldsTile: 4,
}

STANDARD_BOARD_CHIPS = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]


class TileStack(object):
	def __init__(self, initial_tiles):
		self.tiles = []
		for tile, count in initial_tiles.iteritems():
			for i in range(0,count):
				self.tiles.append(tile)

	def get_random_tile(self):
		return self.tiles.pop(random.randint(0,len(self.tiles)-1))


class Board(object):
	def __init__(self):
		# tiles have cube-coordinates: (x,y,z) with x+y+z == 0
		self.tiles = {}
		self.network = networkx.Graph()
		self.dice_map = {}
		self.robber = None

	def __str__(self):
		s = "Board\n=====\n"
		for pos in self.tiles.iteritems():
			s += "%s\t%s\n" % pos
		return s

	def generate_board(self, setup = STANDARD_BOARD_TILES, chips = STANDARD_BOARD_CHIPS):
		stack = TileStack(setup)

		# determine board radius
		l = len(stack.tiles)-1
		r = 0
		while l > 0:
			r += 1
			l -= r*6

		# we will walk from the inside to the outside, so reverse
		# the chip order
		chipstack = chips[:]

		# spiral walk to create board
		# use a random direction
		for pos in HexPosition.walk_spiral(r, random.choice(HexPosition.directions)):
			# first, put down tile
			self.tiles[pos] = stack.get_random_tile()()
			self.tiles[pos].position = pos

			# then place a chip on top, if it's not a desert
			if self.tiles[pos].resource:
				self.tiles[pos].number = chipstack.pop()
			else:
				# place robber on desert at start
				self.robber = pos

			# for easy lookup, register in dice_map
			self.dice_map.setdefault(self.tiles[pos].number, []).append(self.tiles[pos])

		# create network on top of tiles
		for pos, tile in self.tiles.iteritems():
			nodes = []
			for i in range(0,len(HexPosition.directions)):
				p1, p2 = HexPosition.directions[i], HexPosition.directions[(i+1)%len(HexPosition.directions)]
				node_id = tuple(sorted([pos+p1, pos+p2, pos]))

				# add node
				self.network.add_node(node_id)
				nodes.append(node_id)

			# add connecting edges
			for i in range(0, len(nodes)):
				self.network.add_edge(nodes[i], nodes[(i+1)%len(nodes)])

		print "generated network %d nodes, %d edges" % (self.network.number_of_nodes(), self.network.number_of_edges())

	def node_available(self, node_id):
		if 'building' in self.network.node[node_id]: return False

		# check if neighbours have buildings
		for n in self.network.neighbors(node_id):
			if 'building' in self.network.node[n]: return False
		return True
