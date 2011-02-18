#!/usr/bin/env python
# coding=utf8

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

# this order is the same as when using frames
# to get the variable tile based order, simply shuffle
STANDARD_HARBORS = ['3to1', 'Brick', 'Lumber', '3to1', 'Grain', 'Ore', '3to1', 'Sheep', '3to1']

class TileStack(object):
	def __init__(self, random, initial_tiles):
		self.tiles = []
		for tile, count in initial_tiles.iteritems():
			for i in range(0,count):
				self.tiles.append(tile)
		self.random = random

	def get_random_tile(self):
		return self.tiles.pop(self.random.randint(0,len(self.tiles)-1))
