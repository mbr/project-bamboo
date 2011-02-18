#!/usr/bin/env python
# coding=utf8

class IllegalActionException(Exception): pass

class BaseAction(object):
	def assert_legal(self, game):
		raise NotImplementedError

	def apply_unchecked(self, game):
		raise NotImplementedError

	def apply(self, game):
		self.assert_legal(game)
		self.apply_unchecked(game)

class PlayerAction(BaseAction):
	def __init__(self, player):
		self.player = player

	def assert_legal(self, game):
		if not self.player in game.players: raise IllegalActionException('Player %s not in the game.' % self.player)


class StartGameAction(PlayerAction):
	def apply_unchecked(self, game):
		# initialize the board
		game.initialize_board()
		game.phase = 'setup'
		game.turn_order = game.players.keys()
		game.random.shuffle(game.turn_order)

	def assert_legal(self, game):
		super(StartGameAction, self).assert_legal(game)

		# check for correct phase
		if not 'init' == game.phase: raise IllegalActionException('Can only start in init phase.')

		if len(game.players) < 3: raise IllegalActionException('At least 3 players are needed to start the game.')
