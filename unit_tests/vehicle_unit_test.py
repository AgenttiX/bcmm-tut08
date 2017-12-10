import mapgrid
import vehicle

import numpy as np
import unittest


class VehicleTest(unittest.TestCase):
    def test_history_error_generation(self):
        m = mapgrid.generate_map(10, 10)
        v = vehicle.Vehicle(m)

        history_colors = v.history()[:, 1]
        for i in range(10):
            history_err_colors = v.history_error_one()[:, 1]
            diff = np.sum(history_colors != history_err_colors)
            self.assertEqual(diff, 1)


if __name__ == "__main__":
    unittest.main()
