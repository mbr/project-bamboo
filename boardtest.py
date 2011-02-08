#!/usr/bin/env python
# coding=utf8

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from pandac.PandaModules import AmbientLight
from panda3d.core import VBase4
from math import pi, sqrt

from gamemodel import *

def crossproduct(a, b):
	return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])


def dotproduct(a, b):
	return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


class TileLayout(object):
	def __init__(self, base, board):
		self.board = board

		sqrt3 = sqrt(3)
		# we get s == 1 by using to tile-scaling
		# formulas taken from http://stackoverflow.com/questions/2459402/hexagonal-grid-coordinates-to-pixel-coordinates
		for (a,b,c), tile in board.tiles.iteritems():
			# load model
			tileModel = base.loader.loadModel(self.get_tile_model_filename(tile))

			# calculate position
			x = 3/2.*a
			y = (b-c)*sqrt3/2
			tileModel.setPos(x, y, 0)

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

		# create 3d model
#		for pos, tile in b.tiles.iteritems():
#			print "pos",tile

		TileLayout(self, board)


		tileModel = base.loader.loadModel('models/City.egg')
		tileModel.setPos(0,0,0)
		tileModel.reparentTo(self.render)

		alight = AmbientLight('alight')
		alight.setColor(VBase4(1, 1, 1, 1))
		alnp = render.attachNewNode(alight)
		render.setLight(alnp)
#		self.camera.setPos(0, 0, 20)

		# control camera
#		self.camera.setHpr(0, -90, 0)
#		self.disableMouse()


base = MyApp()
base.run()
