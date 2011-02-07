#!/usr/bin/env python
# coding=utf8

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from math import pi, sqrt

from itertools import product

import warnings
warnings.filterwarnings('ignore')
import networkx as nx
import random

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


STANDARD_BOARD_TILES = {
	MountainTile: 3,
	HillsTile: 3,
	DesertTile: 1,
	ForestTile: 4,
	PastureTile: 4,
	FieldsTile: 4,
}

STANDARD_BOARD_CHIPS = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]

TILE_DIRECTIONS = [(0, 1, -1),
		        (1, 0, -1),
		        (1, -1, 0),
		        (0, -1, 1),
		        (-1, 0, 1),
		        (-1, 1, 0)]

class EmptyTile(Tile):
	pass


class TileStack(object):
	def __init__(self, initial_tiles):
		self.tiles = []
		for tile, count in initial_tiles.iteritems():
			for i in range(0,count):
				self.tiles.append(tile)

	def get_random_tile(self):
		return self.tiles.pop(random.randint(0,len(self.tiles)-1))


def crossproduct(a, b):
	return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])


def dotproduct(a, b):
	return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def add_pos(p1, p2):
	return p1[0]+p2[0], p1[1]+p2[1], p1[2]+p2[2]


def dist_pos(p1, p2):
	return (abs(p1[0]-p2[0])+abs(p1[1]-p2[1])+abs(p1[2]-p2[2]))/2


def radius_of_pos(p1):
	return dist_pos( (0,0,0), p1 )


# walk all tiles, from a random corner of the tile map
# circular in one direction, going inwards one step
# until the center is reached
def spiral_walk(start):
	previous = start
	preprevious = None
	relax = False
	yield start

	for cr in range(radius_of_pos(start), 0, -1):
		# compile a list of possible positions
		rs = range(-cr, cr+1)

		# FIXME: ensure proper ccw or cw orientation
		positions = [t for t in product(rs,rs,rs) if sum(t) == 0 and radius_of_pos(t) == cr and t != previous]

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
		self.network = nx.Graph()
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

class TileLayout(object):
	def __init__(self, base, board):
		self.board = board

		# determine size
		tileModel = base.loader.loadModel('test')

		sqrt3 = sqrt(3)
		# we get s == 1 by using to tile-scaling
		# formulas taken from http://stackoverflow.com/questions/2459402/hexagonal-grid-coordinates-to-pixel-coordinates
		for (a,b,c), tile in board.tiles.iteritems():
			# load model
			tileModel = base.loader.loadModel(self.get_tile_model_filename(tile))

			# scale automatically
			min_bounds, max_bounds = tileModel.getTightBounds()
			d_x = max_bounds[0]-min_bounds[0]
			d_y = max_bounds[1]-min_bounds[1]
			self.tilescale = 1./d_y

			# calculate position
			x = 3/2.*a/sqrt3
			y = 0.5*(b-c)
			tileModel.setPos(x, y, 0)

			# set scaling
			tileModel.setScale(self.tilescale,self.tilescale,self.tilescale)

			# render
			tileModel.reparentTo(base.render)

		print "scale",self.tilescale

	def get_tile_model_filename(self, tile):
		return 'tiles/%s' % tile.__class__.__name__


class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# generate a new board
		board = Board()
		board.generate_board()
		print board

		# create 3d model
#		for pos, tile in b.tiles.iteritems():
#			print "pos",tile

		TileLayout(self, board)


#		self.camera.setPos(0, 0, 20)

		# control camera
#		self.camera.setHpr(0, -90, 0)
#		self.disableMouse()


base = MyApp()
base.run()

