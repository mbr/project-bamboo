#!/usr/bin/env python
# coding=utf8

from __future__ import with_statement
try: import unittest2 as unittest
except ImportError: import unittest
from mock import Mock
import mock

from gamemodel.game import Game
from gamemodel.actions import *

class TestBaseAction(unittest.TestCase):
	def setUp(self):
		self.action = BaseAction()
		self.mgame = Mock()

	def test_base_action_has_assert_legal_method(self):
		with self.assertRaises(NotImplementedError):
			self.action.assert_legal(self.mgame)

	def test_base_action_has_apply_unchecked_method(self):
		with self.assertRaises(NotImplementedError):
			self.action.apply_unchecked(self.mgame)

	def test_base_action_apply_checks_and_applies(self):
		with mock.patch('gamemodel.actions.BaseAction.apply_unchecked'):
			with mock.patch('gamemodel.actions.BaseAction.assert_legal'):
				mgame = Mock()
				self.action.apply(mgame)
				self.action.assert_legal.assert_called_with(mgame)
				self.action.apply_unchecked.assert_called_with(mgame)


class TestPlayerActionMixin(object):
	def test_valid_player_is_enforced_by_subclass(self):
		# convention: self.game must be a valid game
		#             and self.action a legal action
		self.action.assert_legal(self.game)
		del self.game.players[self.action.player]
		with self.assertRaises(IllegalActionException):
			self.action.assert_legal(self.game)


class TestPlayerAction(unittest.TestCase, TestPlayerActionMixin):
	def setUp(self):
		self.game = Game()
		self.game.create_player('bluePlayer', 'blue')
		self.action = PlayerAction('blue')

	def test_constructor_sets_player(self):
		pa = PlayerAction('red')
		self.assertEqual(pa.player, 'red')

	def test_existing_player_is_enforced(self):
		game = Game()
		pa = PlayerAction('red')
		with self.assertRaises(IllegalActionException):
			pa.assert_legal(game)
		game.create_player('redPlayer', 'red')
		pa.assert_legal(game)


class TestStartGameAction(unittest.TestCase, TestPlayerActionMixin):
	def setUp(self):
		self.game = Game()
		self.game.create_player('playerOne', 'red')
		self.game.create_player('playerTwo')
		self.game.create_player('playerThree')
		self.action = StartGameAction('red')

	def test_start_game_action_initializes_board(self):
		self.action.apply_unchecked(self.game)
		self.assertIsNotNone(self.game.board)

	def test_start_game_action_starts_game(self):
		self.action.apply_unchecked(self.game)
		self.assertEqual('setup', self.game.phase)

	def test_start_game_action_assert_legal_on_init(self):
		self.action.assert_legal(self.game)
		self.action.apply_unchecked(self.game)
		with self.assertRaises(IllegalActionException):
			self.action.assert_legal(self.game)

	def test_start_game_sets_up_turn_order(self):
		self.assertIsNone(self.game.turn_order)
		self.action.apply_unchecked(self.game)
		self.assertIsNotNone(self.game.turn_order)

	def test_start_game_action_is_not_legal_for_less_then_three_players(self):
		for i in range(0,3):
			game = Game()
			for n in range(0,i):
				game.create_player('Player %d' % n)
			with self.assertRaises(IllegalActionException):
				self.action.assert_legal(game)
