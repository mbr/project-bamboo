#!/usr/bin/env python
# coding=utf8

try: import unittest2 as unittest
except ImportError: import unittest

from gamemodel.game import *

class TestGame(unittest.TestCase):
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

	def test_game_starts_with_zero_players(self):
		self.assertEqual(0, len(self.game.players))

	def test_game_forbids_duplicate_colors(self):
		self.game.create_player('BrownOne', 'brown')

		with self.assertRaises(Game.ColorAlreadyTakenException):
			self.game.create_player('BrownTwo', 'brown')

	def test_game_starts_in_init_phase(self):
		self.assertEqual(self.game.phase, 'init')

	@unittest.skip('no functionality to change phase yet')
	def test_game_allows_plapyer_adding_only_in_init_phase(self):
		raise NotImplementedError

	def test_game_starts_with_no_players_and_board(self):
		self.assertIsNone(self.game.board)
		self.assertItemsEqual(self.game.players, [])

class TestPlayer(unittest.TestCase):
	def setUp(self):
		self.player = Player('TestPlayer', 'red')

	def test_player_starts_with_0_resources(self):
		for res in ['Ore', 'Lumber', 'Wool', 'Brick', 'Grain']:
			self.assertIn(res, self.player.resources)
			self.assertEqual(0, self.player.resources[res])