import unittest

from coffee.cli import CLI

class Test_CLI (unittest.TestCase):

    def test_smoke (self):
        CLI()
