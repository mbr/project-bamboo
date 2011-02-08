#!/usr/bin/env python
# coding=utf8

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from pandac.PandaModules import AmbientLight
from panda3d.core import VBase4
from math import pi, sqrt

from gamemodel import *

class TileLayout(object):
	def __init__(self, base, board, x_stretch = 3/2., y_stretch = sqrt(3)/2.):
		self.board = board
		self.x_stretch = x_stretch
		self.y_stretch = y_stretch

		# we get s == 1 by using to tile-scaling
		# the projection of the tile uses integers, multiplying by
		# x and y stretch should result in correct coordinates
		for pos, tile in board.tiles.iteritems():
			# load model
			tileModel = base.loader.loadModel(self.get_tile_model_filename(tile))

			# calculate position
			x, y = pos.get_projected_coords()
			tileModel.setPos(x * self.x_stretch, y * self.y_stretch, 0)

			# render
			tileModel.reparentTo(base.render)

	def get_tile_model_filename(self, tile):
		return 'tiles/%s' % tile.__class__.__name__


class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# generate a new board
		board = Board()
		board.generate_board()
		print board

		TileLayout(self, board)

		tileModel = base.loader.loadModel('models/City.egg')
		tileModel.setPos(0,0,0)
		tileModel.reparentTo(self.render)

		# ambient light, so we can see colors on models
		alight = AmbientLight('alight')
		alight.setColor(VBase4(1, 1, 1, 1))
		alnp = render.attachNewNode(alight)
		render.setLight(alnp)


base = MyApp()
base.run()
