#!/usr/bin/env python
# coding=utf8

from itertools import product
import random

# nx imports some legacy code
import warnings
with warnings.catch_warnings():
	warnings.filterwarnings('ignore', module = '(networkx|matplotlib).*')
	import networkx

TILE_DIRECTIONS = [(0, 1, -1),
		        (1, 0, -1),
		        (1, -1, 0),
		        (0, -1, 1),
		        (-1, 0, 1),
		        (-1, 1, 0)]

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

	def __cmp__(self, h):
		return cmp(self._t, h._t)

	def __hash__(self):
		return hash(self._t)

	def norm(self):
		# uses 3d manhattan metric from the origin as the norm
		return max(map(abs, self._t))

	def distance_to(self, h):
		return (self-h).norm()

	#def get_radius(self):
	#	return self.norm()

	def get_projected_coords(self):
		# projects _unstretched_ onto a 2d surface.
		# to get proper coordinates for hex centers,
		# you need to apply f(x,y) |-> (3/2x, sqrt(3)/2y)
		return (self._t[0], self._t[1]-self._t[2])

#	@classmethod
#	def circle(_class, radius, fill = False):
#		rs = range(-radius,radius+1)
#		gen = (HexPosition(*t) for t in product(rs,rs,rs) if sum(t) == 0)
#		if fill: return (h for h in gen if h.get_radius() <= radius)
#		else: return (h for h in gen if h.get_radius() == radius)

	@classmethod
	def walk_circle(_class, start, m = None):
		if m == None: m = self.origin
		r = start.distance_to(m)

		yield start
		cur = None

		# get starting move
		for d in self.directions:
			cand = start+d

			# check radius
			if cand.distance_to(m) == r:

				# determine if going from start to candidate is
				# is a clockwise motion relative to m
				if not is_counterclockwise([m.get_projected_coords(), start.get_projected_coords(), cand.get_projected_coords()]):
					cur = cand
					break

		assert(cur) # sanity check
		yield cur

		# starting direction is the one from start to cur
		cdir_i = self.directions.index(cur-start)

		while cur != start:
			cand = cur+self.directions[cdir_i]
			if cand.distance_to(m) != r:
				# time to change directions
				cdir_i = (cdir_i + 1) % len(self.directions)
				continue
			yield cand
			cur = cand


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


# walk all tiles, from a random corner of the tile map
# circular in one direction, going inwards one step
# until the center is reached
def spiral_walk(start):
	previous = start
	preprevious = None
	relax = False
	yield start

	for cr in range(start.radius(), 0, -1):
		# FIXME: ensure proper ccw or cw orientation
		positions = [p for p in HexPosition.circle(cr) if p != previous]

		while positions:
			# remove the position closest to the start position
			i = 0
			while True:
				pos = positions[i]
				if 1 == dist_pos(previous, pos):
					if not preprevious or 2 == dist_pos(preprevious, pos):
						current = positions.pop(i)
						yield current
						preprevious = previous
						previous = current
						break
					elif relax:
						current = positions.pop(i)
						yield current
						# keep preprevious
						relax = False
						previous = current
				i += 1

				if i == len(positions):
					# we're tried all and found no way to continue - this happens when we start on a non-edge
					# tile and the condition 2 == dist_pos(preprevious, pos) cannot be satisfied

					# relax conditions and try again
					relax = True
					#raise Exception('cannot spiral walk from this starting point')
					i = 0

	yield (0,0,0)


class Board(object):
	def __init__(self):
		# tiles have cube-coordinates: (x,y,z) with x+y+z == 0
		self.tiles = {}
		self.network = networkx.Graph()
		self.dice_map = {}

	def __str__(self):
		s = "Board\n=====\n"
		for pos in self.tiles.iteritems():
			s += "%s\t%s\n" % pos
		return s

	def generate_board(self, setup = STANDARD_BOARD_TILES, chips = STANDARD_BOARD_CHIPS):
		stack = TileStack(setup)

		# no floating point arithmetic, please
		l = len(stack.tiles)-1
		r = 0
		while l > 0:
			r += 1
			l -= r*6

		rs = range(-r, r+1)
		positions = [t for t in product(rs,rs,rs) if sum(t) == 0]

		# create all tiles
		for pos in positions:
			self.tiles[pos] = stack.get_random_tile()()
			self.tiles[pos].position = pos

		# create network on top of tiles
		for pos, tile in self.tiles.iteritems():
			nodes = []
			for i in range(0,len(TILE_DIRECTIONS)):
				p1, p2 = TILE_DIRECTIONS[i], TILE_DIRECTIONS[(i+1)%len(TILE_DIRECTIONS)]
				node_id = tuple(sorted([add_pos(pos, p1), add_pos(pos, p2), pos]))

				# add node
				self.network.add_node(node_id)
				nodes.append(node_id)

			# add connecting edges
			for i in range(0, len(nodes)):
				self.network.add_edge(nodes[i], nodes[(i+1)%len(nodes)])

		print "generated network %d nodes, %d edges" % (self.network.number_of_nodes(), self.network.number_of_edges())

		# generate all possible starting positions
		possible_starts = [t for t in product(rs,rs,rs) if sum(t) == 0 and abs(t[0]) in (0,r) and abs(t[1]) in (0,r) and abs(t[2]) in (0,r)]

		# distribute chips
		chipstack = chips[:]
		for pos in spiral_walk(random.choice(possible_starts)):
			if self.tiles[pos].resource: self.tiles[pos].number = chipstack.pop(0)

			# for easy lookup, register in dice_map
			self.dice_map.setdefault(self.tiles[pos].number, []).append(self.tiles[pos])
