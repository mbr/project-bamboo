#!/usr/bin/env python
# coding=utf8

import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from direct.actor.Actor import Actor
from direct.task import Task
from pandac.PandaModules import AmbientLight, Spotlight, PerspectiveLens, DirectionalLight, AntialiasAttrib, WindowProperties
from panda3d.core import VBase4, Vec3, Vec4, Mat4, TransformState, Material, ConfigVariableInt, ConfigVariableBool, ConfigVariableString
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

	m = Mat4(v2d_n[0],  -v2d_n[1], 0, 0,
			   v2d_n[1], v2d_n[0], 0, 0,
					0,        0, 1, 0,
					0,        0, 0, 1)
	m.invertInPlace()
	return m


def draw_debugging_arrow(base, v_from, v_to):
	arrowModel = base.loader.loadModel('models/debuggingArrow')
	mat = align_to_vector(v_to-v_from)
	arrowModel.setTransform(TransformState.makeMat(mat))
	arrowModel.setPos(*v_from)
	arrowModel.reparentTo(base.render)


class SimpleTileset(object):
	def __init__(self, base, tileset_path = 'tilesets/simple/'):
		self.base = base
		self.tileset_path = tileset_path

	def get_chip_model(self, number):
		chipModel = self.base.loader.loadModel(self.tileset_path + 'models/chip')
		return chipModel

	def get_city_model(self):
		return self.base.loader.loadModel(self.tileset_path + 'models/city')

	def get_harbor_model(self):
		return self.base.loader.loadModel(self.tileset_path + 'models/harbor')

	def get_player_texture(self, player):
		return self.base.loader.loadTexture(self.tileset_path + 'textures/player%s.png' % player.color.capitalize())

	def get_road_model(self):
		return self.base.loader.loadModel(self.tileset_path + 'models/road')

	def get_robber_model(self):
		return self.base.loader.loadModel(self.tileset_path + 'models/robber')

	def get_tile_model_with_chip_offset(self, tile):
		# load generic tile
		tileModel = self.base.loader.loadModel(self.tileset_path + 'models/genericTile')

		# texture
		texname = tile.__class__.__name__
		texname = texname[0].lower() + texname[1:]
		tex = self.base.loader.loadTexture(self.tileset_path + 'textures/%s.jpeg' % texname)
		tileModel.find('**/tile').setTexture(tex, 1)

		chip_offset = Vec3(0,0,0.001)

		return (tileModel, chip_offset)


class BoardRenderer(object):
	def __init__(self, base, board, tileset = None, x_stretch = 3/2., y_stretch = sqrt(3)/2., z_plane = 0):
		self.base = base
		self.board = board
		self.tileset = tileset or SimpleTileset(base)
		self.x_stretch = x_stretch
		self.y_stretch = y_stretch
		self.z_plane = 0

		# we get s == 1 by using to tile-scaling
		# the projection of the tile uses integers, multiplying by
		# x and y stretch should result in correct coordinates
		for pos, tile in board.tiles.iteritems():
			# load model
			(tileModel, chip_offset) = self.tileset.get_tile_model_with_chip_offset(tile)

			# calculate position
			tile_coordinates = self.get_tile_coordinates(pos)
			tileModel.setPos(*tile_coordinates)

			# load and place chip
			if tile.number:
				chipModel = self.tileset.get_chip_model(tile.number)
				chipModel.setPos(chip_offset)
				chipModel.reparentTo(tileModel)

			# render
			tileModel.reparentTo(base.render)

		# handle graph nodes
		for n in self.board.network.nodes_iter():
			building = self.board.network.node[n].get('building',None)
			if building == 'city':
				cityModel = self.tileset.get_city_model()
				self.apply_player_texture(cityModel, self.board.network.node[n]['player'])
				cityModel.setH(random.random()*360) # rotation randomly
				cityModel.setPos(*self.get_node_coordinates(n))
				cityModel.reparentTo(base.render)

		# handle graph edges
		for e in self.board.network.edges_iter():
			if 'road' in self.board.network.edge[e[0]][e[1]]:
				roadModel = self.tileset.get_road_model()
				self.apply_player_texture(roadModel, self.board.network.edge[e[0]][e[1]]['player'])

				# get coordinates
				co_s, co_t = map(self.get_node_coordinates, e)

				# align
				mat = align_to_vector(co_t-co_s)
				roadModel.setTransform(TransformState.makeMat(mat))

				roadModel.setPos(co_s)
				roadModel.reparentTo(base.render)

		# place robber
		if self.board.robber:
			robberModel = self.tileset.get_robber_model()
			robberModel.setPos(*self.get_tile_coordinates(self.board.robber))
			robberModel.reparentTo(base.render)

		# place harbors
		try:
			coast_nodes = self.board.walk_coast()
			while True:
				node_id = coast_nodes.next()
				if 'harbor' in self.board.network.node[node_id]:
					# harbors should appear in pairs
					node_id2 = coast_nodes.next()
					assert(self.board.network.node[node_id]['harbor'] == self.board.network.node[node_id2]['harbor'])

					# harbor edge
					h1, h2 = self.get_node_coordinates(node_id), self.get_node_coordinates(node_id2)
					harborModel = self.tileset.get_harbor_model()

					# rotate harbor
					mat = align_to_vector(h2-h1)
					harborModel.setTransform(TransformState.makeMat(mat))

					harborModel.setPos(h1)
					harborModel.reparentTo(base.render)
		except StopIteration:
			pass

	def get_tile_coordinates(self, pos):
		x, y = pos.get_projected_coords()
		return Vec3(x*self.x_stretch, y*self.y_stretch, self.z_plane)

	def get_node_coordinates(self, node_id):
		a, b, c = map(self.get_tile_coordinates, node_id)
		return Vec3((a[0]+b[0]+c[0])/3., (a[1]+b[1]+c[1])/3., (a[2]+b[2]+c[2])/3.)

	def apply_player_texture(self, model, player, player_index = 0):
		# load texture
		tex = self.tileset.get_player_texture(player)

		for path in model.findAllMatches('**/playerColor%d*' % player_index):
			path.setTexture(tex)


class MyApp(ShowBase, DirectObject.DirectObject):
	def __init__(self):
		ShowBase.__init__(self)

		# generate a new game
		game = Game()
		game.create_player('Player One')
		game.create_player('Player Two')
		game.create_player('Player Three')

		# place some random cities
		for player in game.players.values():
			while True:
				n = random.choice(game.board.network.nodes())
				if game.board.node_available(n):
					game.board.network.node[n]['building'] = 'city'
					game.board.network.node[n]['player'] = player

					# place a random road
					m = random.choice(game.board.network.neighbors(n))
					game.board.network.edge[n][m]['road'] = True
					game.board.network.edge[n][m]['player'] = player
					break

		BoardRenderer(self, game.board)

		# setup some 3-point lighting for the whole board
		lKey = DirectionalLight('lKey')
		lKey.setColor(VBase4(0.9,0.9,0.9,1))
		lKeyNode = render.attachNewNode(lKey)
		lKeyNode.setH(-63)
		lKeyNode.setP(-60)
		lKeyNode.setR(-30)
		render.setLight(lKeyNode)

		lFill = DirectionalLight('lFill')
		lFill.setColor(VBase4(0.4,0.4,0.4,1))
		lFillNode = render.attachNewNode(lFill)
		lFillNode.setH(27)
		lFillNode.setP(-15)
		lFillNode.setR(-30)
		render.setLight(lFillNode)

		lBack = DirectionalLight('lBack')
		lBack.setColor(VBase4(0.3,0.3,0.3,1))
		lBackNode = render.attachNewNode(lBack)
		lBackNode.setH(177)
		lBackNode.setP(-20)
		lBackNode.setR(0)
		render.setLight(lBackNode)

		lBelow = DirectionalLight('lBelow')
		lBelow.setColor(VBase4(0.4,0.4,0.4,1))
		lBelowNode = render.attachNewNode(lBelow)
		lBelowNode.setH(0)
		lBelowNode.setP(90)
		lBelowNode.setR(0)
		render.setLight(lBelowNode)

		self.accept('a', self.on_toggle_anti_alias)
		self.accept('q', self.on_quit)

	def on_toggle_anti_alias(self):
		if AntialiasAttrib.MNone != render.getAntialias():
			render.setAntialias(AntialiasAttrib.MNone)
			print "anti-aliasing disabled"
		else:
			render.setAntialias(AntialiasAttrib.MAuto)
			print "anti-aliasing enabled"

	def on_quit(self):
		sys.exit(0)

# set some configuration
ConfigVariableBool("show-frame-rate-meter").setValue(True)

base = MyApp()

base.on_toggle_anti_alias()
base.run()
