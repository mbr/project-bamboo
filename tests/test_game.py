#!/usr/bin/env python
# coding=utf8

from __future__ import with_statement
try: import unittest2 as unittest
except ImportError: import unittest

from gamemodel.game import *
from gamemodel.actions import *

from mock import Mock
import mock

class TestGameRandomGenerator(unittest.TestCase):
	def setUp(self):
		self.game = Game()

	def test_game_sets_up_random_generator(self):
		self.assertIsNotNone(self.game.random)


class TestGameInitPhase(unittest.TestCase):
	def setUp(self):
		self.game = Game()

	def test_colors_available_works(self):
		self.assertItemsEqual(['red', 'blue', 'green', 'orange', 'brown', 'white'], self.game.colors_still_available())

	def test_colors_available_removes_colors(self):
		self.game.create_player('somePlayer', 'red')
		self.assertItemsEqual(['blue', 'green', 'orange', 'brown', 'white'], self.game.colors_still_available())

		self.game.create_player('someOtherPlayer', 'orange')
		self.assertItemsEqual(['blue', 'green', 'brown', 'white'], self.game.colors_still_available())

	def test_create_player_choose_color(self):
		self.game.create_player('myPlayer')
		self.assertEqual(5, len(self.game.colors_still_available()))

	def test_create_player_adds_player(self):
		self.game.create_player('aPlayer')
		self.assertEqual(1, len(self.game.players))

	def test_create_player_allows_no_more_then_4_players(self):
		self.game.create_player('playerOne')
		self.game.create_player('playerTwo')
		self.game.create_player('playerThree')
		self.game.create_player('playerFour')
		with self.assertRaises(Game.TooManyPlayersException):
			self.game.create_player('playerFive')

	def test_game_starts_with_zero_players(self):
		self.assertEqual(0, len(self.game.players))

	def test_game_forbids_duplicate_colors(self):
		self.game.create_player('BrownOne', 'brown')

		with self.assertRaises(Game.ColorAlreadyTakenException):
			self.game.create_player('BrownTwo', 'brown')

	def test_game_starts_in_init_phase(self):
		self.assertEqual(self.game.phase, 'init')

	def test_game_allows_plapyer_adding_only_in_init_phase(self):
		self.game.create_player('playerOne')
		self.game.phase = 'setup'
		with self.assertRaises(Game.WrongPhaseException):
			self.game.create_player('playerTwo')

	def test_game_starts_with_no_players_and_board(self):
		self.assertIsNone(self.game.board)
		self.assertItemsEqual(self.game.players, [])

	def test_game_initialize_board_sets_up_board(self):
		self.game.initialize_board()
		self.assertIsNotNone(self.game.board)

	def test_game_passes_initialize_board_parameters(self):
		args = ['1', 2, 'three']
		kwargs = {'foo': 'bar'}

		with mock.patch('gamemodel.game.Board') as mockboard:
			self.game.initialize_board(*args, **kwargs)
			mockboard.assert_called()
			self.game.board.generate_board.assert_called_with(*args, **kwargs)

	def test_game_starts_with_no_turn_order(self):
		self.assertIsNone(self.game.turn_order)

	def test_game_starts_on_round0_turn0(self):
		self.assertEqual(self.game.turn, 0)
		self.assertEqual(self.game.round, 0)

	def test_current_player_throws_exception(self):
		with self.assertRaises(Game.WrongPhaseException):
			self.game.current_player


class TestGameSetupPhase(unittest.TestCase):
	def setUp(self):
		self.game = Game()

		# set-up three players
		self.game.create_player('playerOne', 'red')
		self.game.create_player('playerTwo')
		self.game.create_player('playerThree')

		# start the game
		start_game_action = StartGameAction('red')
		start_game_action.apply(self.game)

	def test_game_uses_setup_turn_order(self):
		self.assertEqual(self.game.current_player, self.game.turn_order[self.game.turn])
		player1 = self.game.current_player
		self.game.next_turn()
		self.assertEqual(self.game.current_player, self.game.turn_order[self.game.turn])
		player2 = self.game.current_player
		self.game.next_turn()
		self.assertEqual(self.game.current_player, self.game.turn_order[self.game.turn])
		player3 = self.game.current_player
		self.game.next_turn()

		# reverse order afterwards
		self.assertEqual(self.game.current_player, player3)
		self.game.next_turn()
		self.assertEqual(self.game.current_player, player2)
		self.game.next_turn()
		self.assertEqual(self.game.current_player, player1)


class TestGameMainPhase(unittest.TestCase):
	def setUp(self):
		self.game = Game()

		# set-up three players
		self.game.create_player('playerOne', 'red')
		self.game.create_player('playerTwo')
		self.game.create_player('playerThree')

		# start the game
		start_game_action = StartGameAction('red')
		start_game_action.apply(self.game)

	def test_game_uses_normal_turn_order(self):
		self.game.phase = 'main'
		self.assertEqual(self.game.current_player, self.game.turn_order[self.game.turn])
		player1 = self.game.current_player
		self.game.next_turn()

		self.assertEqual(self.game.current_player, self.game.turn_order[self.game.turn])
		player2 = self.game.current_player
		self.game.next_turn()

		self.assertEqual(self.game.current_player, self.game.turn_order[self.game.turn])
		player3 = self.game.current_player
		self.game.next_turn()

		self.assertEqual(self.game.current_player, player1)
		self.game.next_turn()
		self.assertEqual(self.game.current_player, player2)
		self.game.next_turn()
		self.assertEqual(self.game.current_player, player3)
		self.game.next_turn()
		self.assertEqual(self.game.current_player, player1)
		self.game.next_turn()
		self.assertEqual(self.game.current_player, player2)
		self.game.next_turn()
		self.assertEqual(self.game.current_player, player3)

	def test_turns_and_rounds_are_counted(self):
		self.game.phase = 'main'
		self.assertEqual(0, self.game.round)
		self.assertEqual(0, self.game.turn)
		self.game.next_turn()

		self.assertEqual(0, self.game.round)
		self.assertEqual(1, self.game.turn)
		self.game.next_turn()

		self.assertEqual(0, self.game.round)
		self.assertEqual(2, self.game.turn)
		self.game.next_turn()

		self.assertEqual(1, self.game.round)
		self.assertEqual(0, self.game.turn)
		self.game.next_turn()

		self.assertEqual(1, self.game.round)
		self.assertEqual(1, self.game.turn)
		self.game.next_turn()

		self.assertEqual(1, self.game.round)
		self.assertEqual(2, self.game.turn)
		self.game.next_turn()

		self.assertEqual(2, self.game.round)
		self.assertEqual(0, self.game.turn)
		self.game.next_turn()


class TestPlayer(unittest.TestCase):
	def setUp(self):
		self.player = Player('TestPlayer', 'red')

	def test_player_starts_with_0_resources(self):
		for res in ['Ore', 'Lumber', 'Wool', 'Brick', 'Grain']:
			self.assertIn(res, self.player.resources)
			self.assertEqual(0, self.player.resources[res])
