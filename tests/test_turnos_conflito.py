"""Unit tests for Streamlit shift overlap without initializing Streamlit or Neon."""
import ast
import pathlib
import unittest
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = (ROOT / "app.py").read_text(encoding="utf-8")
tree = ast.parse(source)
normalizer = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=="normalizar_turno_convocacao")
overlap_def = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=="turnos_se_sobrepoem")
only = ast.Module(body=[normalizer, overlap_def], type_ignores=[])
scope = {
    "normalizar": lambda s: "".join(c for c in unicodedata.normalize("NFD", str(s).upper()) if unicodedata.category(c) != "Mn")
}
exec(compile(only, str(ROOT / "app.py"), "exec"), scope)
overlap = scope["turnos_se_sobrepoem"]

class TestShiftOverlap(unittest.TestCase):
    def test_integral_and_night_do_not_overlap(self):
        for a, b in [("Integral", "Noite"), ("Noite", "Integral")]:
            with self.subTest(a=a,b=b):
                self.assertFalse(overlap(a,b))
    def test_daytime_integral_blocks_morning_and_afternoon(self):
        for a,b in [("Integral","Manhã"), ("Manhã","Integral"), ("Integral","Tarde"), ("Tarde","Integral")]:
            with self.subTest(a=a,b=b):
                self.assertTrue(overlap(a,b))
    def test_same_shift_still_blocks(self):
        for a in ["Integral","Manhã","Tarde","Noite"]:
            with self.subTest(shift=a):
                self.assertTrue(overlap(a,a))
    def test_distinct_partial_shifts_coexist(self):
        for a,b in [("Manhã","Tarde"),("Manhã","Noite"),("Tarde","Noite")]:
            with self.subTest(a=a,b=b):
                self.assertFalse(overlap(a,b))

if __name__ == "__main__":
    unittest.main()
