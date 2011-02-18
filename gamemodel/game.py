#!/usr/bin/env python
# coding=utf8

from random import Random

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
	class TooManyPlayersException(Exception): pass
	class WrongPhaseException(Exception): pass
	player_colors = 'red', 'blue', 'green', 'orange', 'brown', 'white'

	def __init__(self, random_seed = None):
		self.board = None
		self.players = {}
		self.phase = 'init'
		self.initial_seed = random_seed
		self.random = Random(random_seed)

		self.turn = 0
		self.round = 0
		self.turn_order = None

	@property
	def current_player(self):
		if 'main' == self.phase:
			return self.turn_order[self.turn]
		elif 'setup' == self.phase:
			return self.turn_order[(-1-self.turn) if self.round%2 else self.turn]
		else:
			raise self.WrongPhaseException('No current player in %s phase.' % self.phase)

	def next_turn(self):
		self.turn = (self.turn + 1) % len(self.turn_order)
		if 0 == self.turn: self.round += 1


	def create_player(self, name, color = None):
		if not 'init' == self.phase: raise self.WrongPhaseException('The game has already started, joining not possible.')
		if len(self.players) == 4: raise self.TooManyPlayersException
		color = color or self.random.choice(self.colors_still_available())
		if color in self.players: raise self.ColorAlreadyTakenException('Color %s is already taken' % color)
		self.players[color] = Player(name, color)

	def colors_still_available(self):
		cs = []
		for col in self.player_colors:
			if col not in self.players: cs.append(col)
		return cs

	def initialize_board(self, *args, **kwargs):
		self.board = Board(self.random)
		self.board.generate_board(*args, **kwargs)
