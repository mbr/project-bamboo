#!/usr/bin/env python
# coding=utf8

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from pandac.PandaModules import AmbientLight
from panda3d.core import VBase4, Vec3, Vec4, Mat4, TransformState
from math import pi, sqrt, acos

from gamemodel import *
import random

def align_to_vector(v):
	"""Given a vector v, calculates the non-scaling transformation matrix
	   that would point the x-axis along it, assuming they share the same z"""

	# get the 2d part, normalize
	v2d = Vec3(v)
	v2d[2] = 0

	v2d_n = Vec3(v2d)
	v2d_n.normalize()

	m = Mat4(v2d_n[0],  -v2d[1], 0, 0,
			   v2d[1], v2d_n[0], 0, 0,
					0,        0, 1, 0,
					0,        0, 0, 1)
	print "align"
	print m
	return m

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

			# load and place chip
			if tile.number:
				chipModel = base.loader.loadModel('blender/chiptest')
				chipModel.setScale(0.2, 0.2, 0.2) # oops
				chipModel.setPos(*self.get_tile_coordinates(pos))
				tex = base.loader.loadTexture('textures/chip_%d.png' % tile.number)
				chipModel.setTexture(tex, 1)
				chipModel.reparentTo(base.render)

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
				roadModel = base.loader.loadModel('blender/roadtest')

				# get coordinates
				co_s, co_t = map(self.get_node_coordinates, e)

				# align
				mat = align_to_vector(co_t-co_s)
				roadModel.setTransform(TransformState.makeMat(mat))

				roadModel.setPos(co_s)
				roadModel.reparentTo(base.render)

		# place robber
		if self.board.robber:
			robberModel = base.loader.loadModel('blender/robbertest.egg')
			robberModel.setPos(*self.get_tile_coordinates(self.board.robber))
			robberModel.reparentTo(base.render)

	def get_tile_model_filename(self, tile):
		return 'tiles/%s' % tile.__class__.__name__

	def get_tile_coordinates(self, pos):
		x, y = pos.get_projected_coords()
		return Vec3(x*self.x_stretch, y*self.y_stretch, self.z_plane)

	def get_node_coordinates(self, node_id):
		a, b, c = map(self.get_tile_coordinates, node_id)
		return Vec3((a[0]+b[0]+c[0])/3., (a[1]+b[1]+c[1])/3., (a[2]+b[2]+c[2])/3.)


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
