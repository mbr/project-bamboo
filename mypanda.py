#!/usr/bin/env python
# coding=utf8

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

from itertools import product

import warnings
warnings.filterwarnings('ignore')
import networkx as nx
import random

class Tile(object):
	def __str__(self):
		return '<%s>' % self.__class__.__name__


class MountainTile(Tile):
	pass


class ForestTile(Tile):
	pass


class PastureTile(Tile):
	pass


class DesertTile(Tile):
	pass


class FieldsTile(Tile):
	pass


class HillsTile(Tile):
	pass


STANDARD_BOARD_TILES = {
	MountainTile: 3,
	HillsTile: 3,
	DesertTile: 1,
	ForestTile: 4,
	PastureTile: 4,
	FieldsTile: 4,
}


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


TILE_DIRECTIONS = [(0, 1, -1),
		        (1, 0, -1),
		        (1, -1, 0),
		        (0, -1, 1),
		        (-1, 0, 1),
		        (-1, 1, 0)]


def add_pos(p1, p2):
	return p1[0]+p2[0], p1[1]+p2[1], p1[2]+p2[2]


class Board(object):
	def __init__(self):
		# tiles have cube-coordinates: (x,y,z) with x+y+z == 0
		self.tiles = {}
		self.network = nx.Graph()

	def __str__(self):
		s = "Board\n=====\n"
		for pos in self.tiles.iteritems():
			s += "%s\t%s\n" % pos
		return s

	def generate_board(self, setup):
		stack = TileStack(setup)

		# no floating point arithmetic, please
		l = len(stack.tiles)-1
		r = 0
		while l > 0:
			r += 1
			l -= r*6

		rs = range(-r, r+1)
		positions = [t for t in product(rs,rs,rs) if sum(t) == 0]

		for pos in positions:
			self.tiles[pos] = stack.get_random_tile()()

		for pos, tile in self.tiles.iteritems():
			nodes = []
			for i in range(0,len(TILE_DIRECTIONS)):
				p1, p2 = TILE_DIRECTIONS[i], TILE_DIRECTIONS[(i+1)%len(TILE_DIRECTIONS)]
				node_id = tuple(sorted([add_pos(pos, p1), add_pos(pos, p2), pos]))
				print node_id

				# add node
				self.network.add_node(node_id)
				nodes.append(node_id)
			print

			# add connecting edges
			for i in range(0, len(nodes)):
				self.network.add_edge(nodes[i], nodes[(i+1)%len(nodes)])

		print "generated network %d nodes, %d edges" % (self.network.number_of_nodes(), self.network.number_of_edges())


class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# environment
#		self.environ = self.loader.loadModel('models/environment')
#		self.environ.reparentTo(self.render)
#		self.environ.setScale(0.25, 0.25, 0.25)
#		self.environ.setPos(-8, 42, 0)

		# load a model
		self.pandaActor = Actor('models/panda-model')

		# attach to render
#		self.pandaActor.setScale(0.005, 0.005, 0.0010)
		self.pandaActor.reparentTo(self.render)

#		self.pandaActor.loop('walk')

#base = MyApp()
#base.run()

b = Board()
b.generate_board(STANDARD_BOARD_TILES)
print b
