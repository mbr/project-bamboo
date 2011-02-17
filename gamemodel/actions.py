#!/usr/bin/env python
# coding=utf8

class BaseAction(object):
	def is_legal(self, game):
		raise NotImplementedError
