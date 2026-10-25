"""Classic NPC materials also render after their owning entity disappears."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from npc_pulse import MATERIALS, material
from surface_motion import tokens


class ClassicPulseTests(unittest.TestCase):
    def test_entityless_render_keeps_clock_without_entity_callbacks(self):
        original = 'VertexLitGeneric { "$basetexture" "classic" "$bumpmap" "normal" }'
        for name in MATERIALS:
            with self.subTest(material=name):
                result = material(name, original, tokens(original))
                values = [t[0].strip('"').lower() for t in tokens(result)]
                self.assertNotIn('entityrandom', values)
                self.assertNotIn('entityorigin', values)
                self.assertEqual(values.count('proxies'), 1)
                self.assertIn('"$basetexture" "classic"', result)
                self.assertIn('"$bumpmap" "normal"', result)
                self.assertIn('"sinePeriod" "4.7"', result)
                self.assertIn('"sineMin" "2.04" "sineMax" "2.75"', result)
                self.assertIn('"resultVar" "$warpparam"', result)


if __name__ == '__main__':
    unittest.main()
