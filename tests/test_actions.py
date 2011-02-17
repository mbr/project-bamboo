#!/usr/bin/env python
# coding=utf8

try: import unittest2 as unittest
except ImportError: import unittest
from mock import Mock

from gamemodel.actions import *

class TestBaseAction(unittest.TestCase):
	def setUp(self):
		self.action = BaseAction()
		self.mgame = Mock()

	def test_base_action_has_is_legal_method(self):
		with self.assertRaises(NotImplementedError):
			self.action.is_legal(self.mgame)
