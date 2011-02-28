#!/usr/bin/env python
# coding=utf8

from tiles import *
import networkx

from hexgrid import HexPosition

class Board(object):
	def __init__(self, random):
		# tiles have cube-coordinates: (x,y,z) with x+y+z == 0
		self.tiles = {}
		self.network = networkx.Graph()
		self.dice_map = {}
		self.robber = None
		self.random = random

	def __str__(self):
		s = "Board\n=====\n"
		for pos, tile in self.tiles.iteritems():
			s += "%s\t%s" % (pos, tile)
			if pos == self.robber: s += " robber!"
			s += "\n"
		return s

	def generate_board(self, setup = STANDARD_BOARD_TILES, chips = STANDARD_BOARD_CHIPS):
		stack = TileStack(self.random, setup)

		# determine board radius
		l = len(stack.tiles)-1
		r = 0
		while l > 0:
			r += 1
			l -= r*6
		self.radius = r

		# we will walk from the inside to the outside, so reverse
		# the chip order
		chipstack = chips[:]

		# spiral walk to create board
		# use a random direction
		for pos in HexPosition.walk_spiral(r, self.random.choice(HexPosition.directions)):
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

		def harbor_placement():
			# 1, 1, 2, 1, 1, 2, ...
			order = (True, True, False) * 2 + (True, True, False, False)

			# start with 1
			i = 3
			while True:
				yield order[i]
				i = (i+1)%len(order)

		harbor_place = harbor_placement()
		harbors = STANDARD_HARBORS[:]

		# disable this to not shuffle harbors
		self.random.shuffle(harbors)

		prev = False
		for node_id in self.walk_coast():
			if harbor_place.next():
				if not prev: harbor = harbors.pop(0)
				self.network.node[node_id]['harbor'] = harbor
				prev = True
			else:
				prev = False

	def walk_coast(self):
		"""walk along the coast, radius r"""
		# starting top right tile, top node
		start_tile = HexPosition(self.radius+1, 0, -self.radius-1)
		starting_node = tuple(sorted((start_tile, start_tile+HexPosition.directions[-1], start_tile+HexPosition.directions[-2])))

		yield starting_node
		node_id = starting_node
		prev_node = node_id

		# try all neighbours
		candidates = self.network.neighbors(node_id)
		while candidates:
			n = candidates.pop()

			# if we visited it just before, skip it
			if prev_node == n: continue

			# end once we reach the start again
			if starting_node == n: break

			# must be a node on the coast, i.e. bordering on at least one land (r-1) and sea (r) tile
			sea, land = False, False
			for tile_pos in n:
				distance = tile_pos.distance_to(HexPosition.origin)
				if distance >= self.radius+1: sea = True
				else: land = True

			# if it's not a coastal node, skip it
			if not sea or not land:
				continue

			# it's a non-visited coastal node - move on to it
			prev_node = node_id
			node_id = n
			yield node_id

			# start with the next set of neighbours
			candidates = self.network.neighbors(node_id)

	def node_available(self, node_id):
		if 'building' in self.network.node[node_id]: return False

		# check if neighbours have buildings
		for n in self.network.neighbors(node_id):
			if 'building' in self.network.node[n]: return False
		return True

	def count_buildings(self):
		"""count the number of settlements/cities, returns a tuple of
		(settlements, cities), each being a dictionary of counts for
		each player"""
		settlements = defaultdict(lambda: 0)
		cities = defaultdict(lambda: 0)

		for n in self.network.nodes_iter():
			building = self.network.node[n].get('building', None)
			if 'city' == building:
				cities[self.network.node[n]['player']] += 1
			elif 'settlement' == building:
				settlements[self.network.node[n]['player']] += 1

			self.network.node[n]

		return (settlements, cities)

	def update_building(self, node_id, player, building):
		self.network.node[node_id]['player'] = player
		self.network.node[node_id]['building'] = building

	def node_resource_iter(self, player, node_id):
		for tile_pos in node_id:
			yield self.tiles[tile_pos].resource
