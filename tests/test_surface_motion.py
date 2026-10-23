"""Check that material generation preserves source behaviour and safe exclusions."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from surface_motion import animate, tokens


class SurfaceMotionTests(unittest.TestCase):
    def test_preserves_shader_parameters_and_nested_fallback(self):
        original = 'LightmappedGeneric { "$basetexture" "brick/test" "$surfaceprop" "brick" "DX8" { "$detail" "detail/test" } } // trailing comment'
        out = animate('materials/brick/test.vmt', original)
        self.assertIsNotNone(out)
        self.assertTrue(out.startswith(original[:original.rfind('}')]))
        self.assertTrue(out.endswith('} // trailing comment'))
        self.assertIn('"TextureTransform"', out)
        self.assertIn('"$xen_scale[0]"', out)
        self.assertNotIn('EntityRandom', out)

    def test_world_blend_shares_supported_base_transform(self):
        out = animate('materials/nature/test.vmt', 'WorldVertexTransition { $basetexture a $basetexture2 b $bumpmap n $bumpmap2 m }')
        self.assertNotIn('$basetexturetransform2', out)
        self.assertIn('"resultVar" "$basetexturetransform"', out)
        self.assertIn('"resultVar" "$bumptransform2"', out)

    def test_weapons_have_entity_phase_and_preserve_emissive_mask(self):
        out = animate('materials/models/weapons/v_pistol/test.vmt', 'VertexLitGeneric { $basetexture pistol $selfillum 1 $bumpmap normal }')
        self.assertIn('EntityRandom', out)
        self.assertIn('$selfillum 1', out)
        self.assertIn('"resultVar" "$bumptransform"', out)

    def test_skips_special_materials_and_existing_animation(self):
        for extra in ['Proxies { Sine { resultVar $alpha } }', '$alphatest 1', '$translucent 1', '$basetexturetransform "center .5 .5 scale 2 2"']:
            self.assertIsNone(animate('materials/brick/test.vmt', 'LightmappedGeneric { $basetexture test '+extra+' }'))
        for name in ['materials/vgui/test.vmt', 'materials/decals/test.vmt', 'materials/models/humans/test.vmt']:
            self.assertIsNone(animate(name, 'LightmappedGeneric { $basetexture test }'))

    def test_static_props_do_not_use_entity_only_proxy(self):
        out = animate('materials/models/props_c17/crate.vmt', 'VertexLitGeneric { $basetexture crate }')
        self.assertIsNotNone(out)
        self.assertNotIn('EntityRandom', out)

    def test_comments_do_not_change_eligibility_and_phase_is_stable(self):
        source = '// Proxies { }\nLightmappedGeneric { $basetexture test /* $alphatest 1 */ }'
        a = animate('materials/brick/a.vmt', source)
        self.assertIsNotNone(a)
        self.assertEqual(a, animate('materials/brick/a.vmt', source))
        self.assertNotEqual(a, animate('materials/brick/b.vmt', source))
        self.assertIsNone(animate('materials/brick/a.vmt', source + ' }'))


if __name__ == '__main__':
    unittest.main()
