import unittest

from hollerith.encoding import hash, last_chunk_as_bcd


class HashTest(unittest.TestCase):

    def test_last_chunk_as_bcd(self):
        # Test cases with expected results
        self.assertEqual( last_chunk_as_bcd(""), 0o60606060606 ) # _ _ _ _ _ _)
        self.assertEqual( last_chunk_as_bcd("X") , 0o67606060606 ) # X _ _ _ _ _
        self.assertEqual( last_chunk_as_bcd("HERE") , 0o302551256060 ) # H E R E _ _
        self.assertEqual( last_chunk_as_bcd("ALWAYS") , 0o214366217062 ) # A L W A Y S
        self.assertEqual( last_chunk_as_bcd("INVENTED") , 0o25246060606 ) # E D _ _ _ _
        self.assertEqual( last_chunk_as_bcd("123456ABCDEF") , 0o212223242526 ) # A B C D E F


    def test_real_world_cases(self):
        # Test cases from real-world scenarios
        self.assertEqual(hash(0o214366217062, 7), 14)
        self.assertEqual(hash(0o302551256060, 2), 3)
        self.assertEqual(hash(0o423124626060, 2), 1)
        self.assertEqual(hash(0o633144256060, 2), 0)

    def test_other_cases(self):
        # Other hypothetical test cases
        self.assertEqual(hash(0o777777777777, 7), 0x70)
        self.assertEqual(hash(0o777777777777, 15), 0x7F00)
        self.assertEqual(hash(0x555555555, 15), 0x46E3)
        self.assertEqual(hash(0xF0F0F0F0F, 15), 0x7788)
        self.assertEqual(hash(0o214366217062, 15), 0x70EE)
        self.assertEqual(hash(0o633144256060, 15), 0x252E)
        self.assertEqual(hash(0, 7), 0)

if __name__ == '__main__':
    unittest.main()