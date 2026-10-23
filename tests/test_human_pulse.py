"""Guard selective deformation and preservation of authored material behavior."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from human_pulse import material
from surface_motion import tokens, animate
from prism_texture import frame_pixels, FRAMES


class HumanPulseTests(unittest.TestCase):
    def test_named_human_retains_skin_and_one_proxy_block(self):
        name = 'materials/models/alyx/alyx_faceandhair.vmt'
        original = 'VertexLitGeneric { $basetexture face $phong 1 $phongboost 6 }'
        coloured = animate(name, original)
        out = material(name, coloured, tokens)
        self.assertTrue(out.startswith('VertexLitGeneric'))
        self.assertIn('$phongboost 6', out)
        self.assertIn('xenesthesia/prism', out)
        self.assertIn('translate 1000 0', out)
        self.assertEqual([x[0].strip('"').lower() for x in tokens(out)].count('proxies'), 1)

    def test_eye_and_mouth_keep_specialized_shaders(self):
        for shader in ('eyes', 'Teeth'):
            out = material('materials/models/alyx/test.vmt', shader+' { $basetexture face }', tokens)
            self.assertTrue(out.startswith(shader))
            self.assertIn('"$intro" "1"', out)
            self.assertIn('"sineMax" "2.16"', out)

    def test_static_props_and_authored_warp_are_excluded(self):
        source = 'VertexLitGeneric { $basetexture test }'
        self.assertIsNone(material('materials/models/props_lab/crate.vmt', source,tokens))
        self.assertIsNone(material('materials/models/alyx/emptool_sheet.vmt',source,tokens))
        self.assertIsNone(material('materials/models/alyx/test.vmt',source[:-1]+' $warpparam .5 }',tokens))

    def test_colour_animation_closes_loop_and_changes_shapes(self):
        self.assertEqual(frame_pixels(0), frame_pixels(FRAMES))
        # A global hue rotation preserves pairwise RGB distances. Moving lobes
        # change those distances, which distinguishes flow from hue cycling.
        frames = [frame_pixels(x) for x in (0, FRAMES//4)]
        changes = []
        for a,b in [(150,500),(1200,3100),(700,900)]:
            distances = [sum((f[3*a+c]-f[3*b+c])**2 for c in range(3)) for f in frames]
            changes.append(abs(distances[0]-distances[1]))
        self.assertGreater(max(changes),1000)


if __name__ == '__main__':
    unittest.main()
