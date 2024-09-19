from prod import TextFormatter
import unittest

class TestTextFormatter(unittest.TestCase):

    def test_center_word(self):
        t = TextFormatter()
        t.set_line_width(10)
        self.assertEqual("   todo   ",  t.center_word("todo"))     

if __name__ == '__main__':
    unittest.main()