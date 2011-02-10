import pdb
#!/usr/bin/env python
# coding=utf8

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import VBase4, Mat4, Vec4, TransformState
from pandac.PandaModules import AmbientLight

# this file is intented as a quick reference, in case
# anyone forgets on how to do matrix transformation
# acrobatics in panda3d

class MyApp(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# ambient light, so we can see colors on models
		alight = AmbientLight('alight')
		alight.setColor(VBase4(1, 1, 1, 1))
		alnp = render.attachNewNode(alight)
		render.setLight(alnp)

		# this piece of code loads a model, and places it at (1,3,0)
		# it will be visible as soon as the program is started
		self.cityModel = self.loader.loadModel('models/City.egg')
		self.cityModel.setPos(1, 3, 0)

		# reparenting to "render" causes it to be displayed (render is the
		# root of the object tree
		self.cityModel.reparentTo(self.render)

		self.taskMgr.add(self.move_city, "move_city")

	def move_city(self, task):
		# moves the city, using the transformation matrix

		# first, get the current transformation matrix
		# getTransform() returns a TransformState, which is a higher level
		# abstraction of our matrix
		# getMat() retrieves the inner matrix. the returned matrix is const
		# though
		oldmat = self.cityModel.getTransform().getMat()

		# oldmat ist a const Mat4, we need one we can manipulate
		newmat = Mat4(oldmat)

		# the matrices in Panda3d are suitable for row-vector multiplication, that is
		# vector * Matrix (same as opengl). the bottom row (3) is therefore the
		# translation in xyzt order
		#
		# replace it with a different one, we want to move the value of
		# time, which is the number of seconds passed since starting this task
		newmat.setRow(3, Vec4(1-task.time, 3, 0, 1))

		# we need to create a new TransformState from the matrix, and set it
		# to apply the transformation
		self.cityModel.setTransform(TransformState.makeMat(newmat))

		return Task.cont

base = MyApp()
base.run()
