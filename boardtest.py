#!/usr/bin/env python
# coding=utf8

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from pandac.PandaModules import AmbientLight
from panda3d.core import VBase4
from math import pi, sqrt, acos

from gamemodel import *
import random

def norm(v):
	return sqrt(v[0]**2+v[1]**2+v[2]**2)

class BoardRenderer(object):
	def __init__(self, base, board, x_stretch = 3/2., y_stretch = sqrt(3)/2., z_plane = 0):
		self.board = board
		self.x_stretch = x_stretch
		self.y_stretch = y_stretch
		self.z_plane = 0

		# we get s == 1 by using to tile-scaling
		# the projection of the tile uses integers, multiplying by
		# x and y stretch should result in correct coordinates
		for pos, tile in board.tiles.iteritems():
			# load model
			tileModel = base.loader.loadModel(self.get_tile_model_filename(tile))

			# calculate position
			tileModel.setPos(*self.get_tile_coordinates(pos))

			# render
			tileModel.reparentTo(base.render)

		# handle graph nodes
		for n in self.board.network.nodes_iter():
			building = self.board.network.node[n].get('building',None)
			if building == 'city':
				cityModel = base.loader.loadModel('models/City.egg')
				cityModel.setPos(*self.get_node_coordinates(n))
				cityModel.reparentTo(base.render)

		# handle graph edges
		for e in self.board.network.edges_iter():
			if 'road' in self.board.network.edge[e[0]][e[1]]:
				roadModel = base.loader.loadModel('models/Road.egg')
				roadModel.setH(self.get_edge_angle(e) * 180/pi)
				roadModel.setPos(*self.get_edge_coordinates(e))
				roadModel.reparentTo(base.render)

	def get_tile_model_filename(self, tile):
		return 'tiles/%s' % tile.__class__.__name__

	def get_tile_coordinates(self, pos):
		x, y = pos.get_projected_coords()
		return x*self.x_stretch, y*self.y_stretch, self.z_plane

	def get_node_coordinates(self, node_id):
		a, b, c = map(self.get_tile_coordinates, node_id)
		return (a[0]+b[0]+c[0])/3., (a[1]+b[1]+c[1])/3., (a[2]+b[2]+c[2])/3.

	def get_edge_coordinates(self, edge):
		a, b = map(self.get_node_coordinates, edge)
		return (a[0]+b[0])/2., (a[1]+b[1])/2., (a[2]+b[2])/2.

	def get_edge_vector(self, edge):
		a, b = map(self.get_node_coordinates, edge)
		if b[1] < a[1]: a, b = b, a # always go from bottom to top
		return b[0]-a[0], b[1]-a[1], b[2]-a[2]

	def get_edge_angle(self, edge):
		v = self.get_edge_vector(edge)
		return acos(v[0]+self.z_plane/norm(v))


class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# generate a new board
		board = Board()
		board.generate_board()
		print board

		# place some random cities
		for i in range(0,4):
			while True:
				n = random.choice(board.network.nodes())
				if board.node_available(n):
					board.network.node[n]['building'] = 'city'

					# place a random road
					m = random.choice(board.network.neighbors(n))
					board.network.edge[n][m]['road'] = True
					break

		BoardRenderer(self, board)

		# ambient light, so we can see colors on models
		alight = AmbientLight('alight')
		alight.setColor(VBase4(1, 1, 1, 1))
		alnp = render.attachNewNode(alight)
		render.setLight(alnp)


base = MyApp()
base.run()
