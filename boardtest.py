#!/usr/bin/env python
# coding=utf8

import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject
from direct.actor.Actor import Actor
from direct.task import Task
from pandac.PandaModules import AmbientLight, Spotlight, PerspectiveLens, DirectionalLight, AntialiasAttrib, WindowProperties
from panda3d.core import VBase4, Vec3, Vec4, Mat4, Point3, TransformState, Material, ConfigVariableInt, ConfigVariableBool, ConfigVariableString, CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay, CollisionPlane, GeomNode, Texture, TextureStage, Plane, BitMask32
from math import pi, sqrt, cos, sin

from gamemodel.board import *
from gamemodel.hexgrid import *
from gamemodel.tiles import *
from gamemodel.game import *
import random

def align_to_vector(v):
	"""Given a vector v, calculates the non-scaling transformation matrix
	   that would point the x-axis along it, assuming they share the same z.

	   Important: Modifies v in place!
	   """

	v[2] = 0
	v.normalize()

	m = Mat4(v[0], v[1], 0, 0,
			 -v[1],  v[0], 0, 0,
			 0,       0, 1, 0,
			 0,       0, 0, 1)
	return m


def draw_debugging_arrow(base, v_from, v_to):
	arrowModel = base.loader.loadModel('models/debuggingArrow')
	mat = align_to_vector(v_to-v_from)
	arrowModel.setTransform(TransformState.makeMat(mat))
	arrowModel.setPos(*v_from)
	arrowModel.reparentTo(base.render)

	return arrowModel


class SimpleTileset(object):
	def __init__(self, base, tileset_path = 'tilesets/simple/'):
		self.base = base
		self.tileset_path = tileset_path

	def get_chip_model(self, number):
		chipModel = self.base.loader.loadModel(self.tileset_path + 'models/chip')
		tex = self.load_texture('textures/chip%d.png' % number)
		chipModel.find('**/chip').setTexture(tex, 1)
		return chipModel

	def get_city_model(self):
		return self.base.loader.loadModel(self.tileset_path + 'models/city')

	def get_harbor_model(self):
		return self.base.loader.loadModel(self.tileset_path + 'models/harbor')

	def get_player_texture(self, player):
		return self.load_texture('textures/player%s.png' % player.color.capitalize())

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
		tex = self.load_texture('textures/%s.jpeg' % texname)
		tileModel.find('**/tile').setTexture(tex, 1)

		chip_offset = Vec3(0,0,0.001)

		return (tileModel, chip_offset)

	def load_texture(self, subpath):
		tex = self.base.loader.loadTexture(self.tileset_path + subpath)
		tex.setMinfilter(Texture.FTLinearMipmapLinear) # FIXME: refactor/combine
		                                               #        load_texture methods
		tex.setAnisotropicDegree(2)
		return tex


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
			tileModel.setTag('pickable', 'True')

			# load and place chip
			if tile.number:
				chipModel = self.tileset.get_chip_model(tile.number)
				chipModel.setPos(chip_offset)
				chipModel.reparentTo(tileModel)
				chipModel.setTag('pickable', 'False')

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
				cityModel.setTag('pickable', 'True')

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
				roadModel.setTag('pickable', 'True')

		# place robber
		if self.board.robber:
			robberModel = self.tileset.get_robber_model()
			robberModel.setPos(*self.get_tile_coordinates(self.board.robber))
			robberModel.reparentTo(base.render)
			robberModel.setTag('pickable', 'True')

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
					harborModel.setTag('pickable', 'True')
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


class HandRenderer(object):
	def __init__(self, base, player, card_size = 0.2, width = 0.5, card_x_overlap = 0.2, card_y_overlap = 0.8):
		self.base = base
		self.player = player

		aspect_ratio = self.base.getAspectRatio()
		self.card_size = card_size # a card size of 1 makes it 2/3 of the screen high
		                           # cards have a ration of 1:1.555

		self.width = width         # width is percentage of screen width
		                           # wider screen => more cards displayed

		self.card_x_overlap = card_x_overlap # percentage of card that overlaps onto next
		self.card_y_overlap = card_y_overlap

		card_x_offset = (1-card_x_overlap)*card_size
		card_y_offset = (1.555-card_y_overlap)*card_size

		# num cards to render
		num_cards = sum(player.resources.values())

		# the 2d coordinate system is x in [-aspect,aspect] left-to-right,
		# y in [-1,1] bottom-to-top
		cards_per_row = int(((aspect_ratio*2)*width-card_size) / card_x_offset)

		# the hand offset
		hand_width = card_size + (min(num_cards, cards_per_row)-1) * card_x_offset if num_cards else 0
		x_offset = aspect_ratio-hand_width
		y_offset = -1 # draw from the bottom

		resource_index = 0
		for resource, amount in sorted(player.resources.iteritems()):
			for i in xrange(0, amount): # arrangement depends on order in tree
				cardModel = self.load_card_model(resource)
				cardModel.setScale(self.card_size, self.card_size, self.card_size)
				cardModel.setPos(
					# x - left/right
					x_offset + card_x_offset * (resource_index%cards_per_row),
					# y - ignored
					0,
					# z - "intuitive" y
					y_offset + card_y_offset * (resource_index/cards_per_row)
				)

				# control render order, first card should also be the one
				# on the front
				cardModel.setBin("fixed", -resource_index)

				# the behaviour of aspect2d is a bit strange,
				# rotating the card always causes it be face-up
				cardModel.reparentTo(self.base.aspect2d)

				resource_index += 1

	def load_card_model(self, face):
		facepart = face[0].lower() + face[1:]
		model = self.base.loader.loadModel('models/cardModel')
		tex = self.load_texture('textures/%sCard.png' % facepart)

		# apply texture
		model.setTexture(tex, 1)

		return model

	def load_texture(self, path):
		tex = self.base.loader.loadTexture(path)
		tex.setMinfilter(Texture.FTLinearMipmapLinear) # FIXME: refactor/combine
		                                               #        load_texture methods
		tex.setAnisotropicDegree(2)
		return tex


class MyApp(ShowBase, DirectObject.DirectObject):
	def __init__(self):
		ShowBase.__init__(self)

		# generate a new game
		game = Game()
		game.create_player('Player One')
		game.create_player('Player Two')
		game.create_player('Player Three')

		game.initialize_board()

		# place some random cities
		for player in game.players.values():
			# give the player some random resources
			for resource in player.resources:
				player.resources[resource] = random.randint(0,8)
			while True:
				n = random.choice(game.board.network.nodes())
				if game.board.node_available(n):
					game.board.update_building(n, player, 'city')

					# place a random road
					m = random.choice(game.board.network.neighbors(n))
					game.board.network.edge[n][m]['road'] = True
					game.board.network.edge[n][m]['player'] = player
					break

		self.board_renderer = BoardRenderer(self, game.board)
		self.hand_renderer = HandRenderer(self, game.players.values()[0])

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
		self.mouse_controlled = True
		self.on_toggle_mouse_control()
		self.accept('m', self.on_toggle_mouse_control)
		self.accept('q', self.on_quit)

		# onto-board selection collision test
		select_mask = BitMask32(0x100)
		self.select_ray = CollisionRay()
		select_node = CollisionNode('mouseToSurfaceRay')
		select_node.setFromCollideMask(select_mask)
		select_node.addSolid(self.select_ray)
		select_np = self.camera.attachNewNode(select_node)

		self.select_queue = CollisionHandlerQueue()
		self.select_traverser = CollisionTraverser()
		self.select_traverser.addCollider(select_np, self.select_queue)

		# create a plane that only collides with the mouse ray
		select_plane = CollisionPlane(Plane(Vec3(0,0,1), Point3(0,0,0)))

		# add plane to render
		self.select_node = CollisionNode('boardCollisionPlane')
		self.select_node.setCollideMask(select_mask)
		self.select_node.addSolid(select_plane)
		self.select_plane_np = self.render.attachNewNode(self.select_node)

		self.debug_select = draw_debugging_arrow(self, Vec3(0,0,0), Vec3(0,1,0))

		self.taskMgr.add(self.update_mouse_target, "mouseTarget")
		self.taskMgr.add(self.update_debug_arrow, "updateDebugArrow")

	def on_toggle_anti_alias(self):
		if AntialiasAttrib.MNone != render.getAntialias():
			render.setAntialias(AntialiasAttrib.MNone)
			print "anti-aliasing disabled"
		else:
			render.setAntialias(AntialiasAttrib.MAuto)
			print "anti-aliasing enabled"

	def on_toggle_mouse_control(self):
		if self.mouse_controlled:
			self.disableMouse()
			self.taskMgr.add(self.spin_camera_task, "spinCameraTask")
		else: self.enableMouse()

		self.mouse_controlled = not self.mouse_controlled

	def spin_camera_task(self, task):
		height = 9
		distance = 15
		speed = 1./16
		angle = (task.time*speed) * 2 * pi

		self.camera.setPos(distance*cos(angle), distance*-sin(angle), height)
		self.camera.lookAt(0,0,0)

		if self.mouse_controlled: return Task.done
		return Task.cont

	def update_mouse_target(self, task):
		if not base.mouseWatcherNode.hasMouse():
			self.mouse_target = None
			return Task.cont

		# setup ray through camera position and mouse position (on camera plane)
		mouse_pos = base.mouseWatcherNode.getMouse()
		self.select_ray.setFromLens(self.board_renderer.base.camNode, mouse_pos.getX(), mouse_pos.getY())

		self.select_traverser.traverse(self.board_renderer.base.render)

		# abort if there's no collision
		if not self.select_queue.getNumEntries(): return Task.cont

		collision = self.select_queue.getEntry(0)
		self.mouse_board_collision = collision.getSurfacePoint(collision.getIntoNodePath())
		self.mouse_target = 'board'

		return Task.cont

	def update_debug_arrow(self, task):
		if self.mouse_target:
			self.debug_select.setPos(self.mouse_board_collision)
		return Task.cont

	def on_pick(self):
		if not self._update_pick_ray(): return

		# traverse scene graph and determine nearest selection (if pickable)
		self.pick_traverser.traverse(self.board_renderer.base.render)
		self.pick_queue.sortEntries()
		if not self.pick_queue.getNumEntries(): return
		node = self.pick_queue.getEntry(0).getIntoNodePath().findNetTag('pickable')
		if node.isEmpty() or node.getTag('pickable') == 'False': return

		# add some color
		ts = TextureStage('ts')
		ts.setMode(TextureStage.MModulate)
		colors = list(Game.player_colors)
		colors.remove('white')
		node.setTexture(ts, self.board_renderer.tileset.load_texture('textures/player%s.png' % random.choice(colors).capitalize()))

	def on_quit(self):
		sys.exit(0)

# set some configuration
ConfigVariableBool("show-frame-rate-meter").setValue(True)

base = MyApp()

base.on_toggle_anti_alias()
base.run()
