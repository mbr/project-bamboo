#!/usr/bin/env python
# coding=utf8

import random

from board import Board

class Player(object):
	def __init__(self, name, color):
		self.name = name
		self.color = color
		self.resources = {
			'Ore': 0,
			'Lumber': 0,
			'Wool': 0,
			'Grain': 0,
			'Brick': 0
		}


class Game(object):
	class ColorAlreadyTakenException(Exception): pass
	player_colors = 'red', 'blue', 'green', 'orange', 'brown', 'white'

	def __init__(self):
		self.board = Board()
		self.board.generate_board()
		self.players = {}

	def create_player(self, name, color = None):
		color = color or random.choice(self.colors_still_available())
		if color in self.players: raise self.ColorAlreadyTakenException('Color %s is already taken' % color)
		self.players[color] = Player(name, color)

	def colors_still_available(self):
		cs = []
		for col in self.player_colors:
			if col not in self.players: cs.append(col)
		return cs
