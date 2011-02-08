#!/usr/bin/env python
# coding=utf8

import unittest
from gamemodel import *
from math import sqrt

class TestGeometryFunctions(unittest.TestCase):
	def test_signed_area(self):
		triangle = [(0,0), (1,0), (0,1)]

		self.assertEqual(0.5, signed_area(triangle))
		triangle.reverse()
		self.assertEqual(-0.5, signed_area(triangle))

	def test_is_counterclockwise(self):
		ccw_t = [(0,0), (1,0), (0,1)]
		cw_t = [(1,1), (1,0), (0,0), (0,1)]

		self.assertTrue(is_counterclockwise(ccw_t))
		self.assertFalse(is_counterclockwise(cw_t))


class TestHexPosition(unittest.TestCase):
	def test_hex_position_validates_position(self):
		def cm():
			HexPosition(1,0,0)

		self.assertRaises(Exception, cm)

	def test_hex_position_addition(self):
		a = HexPosition(5, -5, 0)
		b = HexPosition(2, 2, -4)
		c = a+b

		self.assertEqual(7, c.r)
		self.assertEqual(-3, c.g)
		self.assertEqual(-4, c.b)

	def test_hex_position_substraction(self):
		a = HexPosition(0, 1, -1)
		b = HexPosition(2, -6, 4)

		c = a-b

		self.assertEqual(-2, c.r)
		self.assertEqual(7, c.g)
		self.assertEqual(-5, c.b)

	def test_hex_position_defaults(self):
		h = HexPosition()
		self.assertEqual(0, h.r)
		self.assertEqual(0, h.g)
		self.assertEqual(0, h.b)

	def test_hex_position_norm(self):
		h = HexPosition()
		self.assertEqual(0, h.norm())

		g = HexPosition(4,-3,-1)
		self.assertEqual(4, g.norm())

	def test_hex_position_distance(self):
		h = HexPosition(-1,1,0)
		g = HexPosition(2,-1,-1)
		x = HexPosition(0,1,-1)

		self.assertEqual(3, h.distance_to(g))
		self.assertEqual(3, g.distance_to(h))

		self.assertEqual(0, h.distance_to(h))
		self.assertEqual(0, h.distance_to(h))

		self.assertEqual(1, x.distance_to(h))
		self.assertEqual(2, x.distance_to(g))

	def test_hex_position_radius_is_origin_distance(self):
		return # DISABLED
		g = HexPosition(-3,6,-3)
		h = HexPosition(3,-3,0)
		i = HexPosition(-1,-1,2)
		self.assertEqual(g.distance_to(HexPosition()), g.get_radius())
		self.assertEqual(h.distance_to(HexPosition()), h.get_radius())
		self.assertEqual(i.distance_to(HexPosition()), i.get_radius())

	def test_hex_positions_test_equality(self):
		g = HexPosition()
		h = HexPosition()

		self.assertEqual(g, h)

		i = HexPosition(-2,2,0)
		j = HexPosition(-2,2,0)

		self.assertEqual(i,j)

		self.assertNotEqual(HexPosition(-2,0,2), i)

	def test_hex_position_hash_matches_tuple(self):
		ts = [(1,2,-3), (0,1,-1), (0,0,0), (-3,6,-3)]

		for t in ts:
			self.assertEqual(hash(t),hash(HexPosition(*t)))

	def test_hex_position_sorting(self):
		unsor = [HexPosition(-1,3,-2), HexPosition(2,-1,-1), HexPosition(-1,2,-1)]
		sor = [HexPosition(-1,2,-1), HexPosition(-1,3,-2), HexPosition(2,-1,-1)]

		unsor.sort()

		self.assertEqual(sor, unsor)

	def test_hex_position_generators(self):
		return # DISABLED
		circle0 = set([HexPosition()])
		circle1 = set(map(lambda t: HexPosition(*t), [(0, 1, -1), (1, 0, -1), (1, -1, 0), (0, -1, 1), (-1, 0, 1), (-1, 1, 0)]))

		circle0_1 = circle0.copy()
		circle0_1.update(circle1)

		self.assertEqual(circle0, set(HexPosition.circle(0)))
		self.assertEqual(circle1, set(HexPosition.circle(1)))

		self.assertEqual(circle0_1, set(HexPosition.circle(1, True)))

	def test_hex_position_2d_game_projection(self):
		g = HexPosition(-2,1,1)
		h = HexPosition()
		i = HexPosition(2,-1,-1)
		j = HexPosition(0,1,-1)

		self.assertEqual((-2,0), g.get_projected_coords())
		self.assertEqual((0,0), h.get_projected_coords())
		self.assertEqual((2,0), i.get_projected_coords())
		self.assertEqual((0,2), j.get_projected_coords())

	def test_circle_walk(self):
		circle0 = map(lambda t: HexPosition(*t), [(0,0,0)])
		circle1 = map(lambda t: HexPosition(*t), [(0,1,-1), (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0)])
		circle2 = map(lambda t: HexPosition(*t), [(0,2,-2), (1,1,-2), (2,0,-2), (2,-1,-1), (2,-2,0), (1,-2,1), (0,-2,2), (-1,-1,2), (-2,0,2), (-2,1,1), (-2,2,0), (-1,2,-1)])

		# circles around origin
		def list_rotations(l):
			for i in range(0,len(l)):
				yield l[i:] + l[:i]

		for rot in list_rotations(circle1):
			self.assertEqual(list(HexPosition.walk_circle(rot[0])), rot)

		for rot in list_rotations(circle2):
			self.assertEqual(list(HexPosition.walk_circle(rot[0])), rot)

		# circles around a different tile
		m1 = HexPosition(2,-2,0)
		circle1_m1 = map(lambda a: a+m1, circle1)
		circle2_m1 = map(lambda a: a+m1, circle2)

		for rot in list_rotations(circle1_m1):
			self.assertEqual(list(HexPosition.walk_circle(rot[0], m1)), rot)

		for rot in list_rotations(circle2_m1):
			self.assertEqual(list(HexPosition.walk_circle(rot[0], m1)), rot)

if '__main__' == __name__:
	unittest.main()
