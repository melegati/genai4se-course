import unittest
from convert_units import convert

class TestConvert(unittest.TestCase):

    def test_inches_to_centimeters(self):
        self.assertEqual(5.08, convert("2in", "cm"))  

    def test_centimeters_to_inches(self):
        self.assertEqual(10, convert("25.4cm", "in"))

    def test_yards_to_meters(self):
        self.assertEqual(9.144, convert("10yd", "m"))

    def test_meters_to_yards(self):
        self.assertEqual(10.9361, convert("10m", "yd"))  


if __name__ == '__main__':
    unittest.main()