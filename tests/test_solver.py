import unittest
from pathlib import Path

from solve_cgl import load_cost_matrix, solve_instance, validate_sequence


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class TestCGLSolver(unittest.TestCase):
    def test_cgl17_matrix_shape(self):
        C = load_cost_matrix(DATA / "cgl_17.txt")
        self.assertEqual(C.shape, (17, 17))

    def test_cgl17_exact_solution(self):
        result = solve_instance(DATA / "cgl_17.txt", mip_gap=0.0)
        self.assertEqual(result["status"], "OPTIMAL")
        self.assertTrue(result["proven_optimal"])
        self.assertTrue(result["valid_sequence"])
        self.assertAlmostEqual(result["validated_cost"], 4422.0, places=7)
        self.assertEqual(len(result["sequence"]), 17)

    def test_reference_sequence_validation(self):
        C = load_cost_matrix(DATA / "cgl_17.txt")
        seq = [2, 0, 1, 3, 4, 5, 6, 7, 16, 8, 9, 11, 14, 13, 10, 12, 15]
        valid, cost, message = validate_sequence(C, seq)
        self.assertTrue(valid, message)
        self.assertAlmostEqual(cost, 4422.0, places=7)


if __name__ == "__main__":
    unittest.main()
