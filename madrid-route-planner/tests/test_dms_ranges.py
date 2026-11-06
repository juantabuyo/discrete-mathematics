"""Proposed regression tests: physically impossible degrees/minutes/seconds are rejected."""
import unittest

import street_map


class DmsRanges(unittest.TestCase):
    def test_valid_coordinates_are_unchanged(self):
        self.assertEqual(street_map.dms_to_decimal("40°25'30''N"), 40.425)
        self.assertEqual(street_map.dms_to_decimal("3°42'13.6''W"), -3.7037778)
        self.assertEqual(street_map.dms_to_decimal("90°00'00''N"), 90.0)
        self.assertEqual(street_map.dms_to_decimal("180°00'00''E"), 180.0)

    def test_impossible_values_raise_value_error(self):
        for coordinate in ("90°99'99''N", "91°00'00''S", "181°00'00''E", "40°60'00''N", "40°00'60''N"):
            with self.subTest(coordinate=coordinate), self.assertRaises(ValueError):
                street_map.dms_to_decimal(coordinate)


if __name__ == '__main__':
    unittest.main()
