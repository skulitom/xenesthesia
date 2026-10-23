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

    def test_skips_translucent_and_interface_materials(self):
        for extra in ['$translucent 1', '$decal 1', '$additive 1']:
            self.assertIsNone(animate('materials/brick/test.vmt', 'LightmappedGeneric { $basetexture test '+extra+' }'))
        for name in ['materials/vgui/test.vmt', 'materials/decals/test.vmt', 'materials/models/humans/test.vmt']:
            self.assertIsNone(animate(name, 'LightmappedGeneric { $basetexture test }'))

    def test_existing_animation_is_merged_without_moving_its_uvs(self):
        authored = 'Sine { resultVar $alpha sineMin .7 sineMax 1 }'
        out = animate('materials/models/props_lab/computer.vmt',
                      'UnlitGeneric { $basetexture test Proxies { '+authored+' } }')
        self.assertIn(authored, out)
        self.assertEqual([t[0].strip('"').lower() for t in tokens(out)].count('proxies'), 1)
        self.assertIn('"AnimatedTexture"', out)
        self.assertNotIn('TextureTransform', out)

    def test_cutout_and_face_colour_preserve_uv_and_alpha(self):
        for name,extra in [('materials/models/weapons/v_rpg/rpg.vmt','$alphatest 1'),
                           ('materials/models/humans/face.vmt','')]:
            out = animate(name, 'VertexLitGeneric { $basetexture test '+extra+' }')
            self.assertIn('"$detailblendmode" "0"', out)
            self.assertNotIn('TextureTransform', out)
            self.assertNotIn('EntityRandom', out)
            if extra:
                self.assertIn(extra, out)

    def test_authored_detail_layer_is_not_replaced(self):
        source = 'LightmappedGeneric { $basetexture test $detail original/detail }'
        out = animate('materials/brick/test.vmt',source)
        self.assertIn('$detail original/detail', out)
        self.assertNotIn('xenesthesia/prism',out)

    def test_standard_micrograin_replaced_without_duplicate_keys(self):
        source = 'LightmappedGeneric { $basetexture a $detail "detail\\plaster_detail_01" $detailscale 4 }'
        out = animate('materials/plaster/test.vmt',source)
        values = [t[0].strip('"').lower() for t in tokens(out)]
        self.assertEqual(values.count('$detailscale'),1)
        self.assertIn('"$detailframe" "0"',out)
        self.assertNotIn('plaster_detail_01',out)
        self.assertIn('"-1337.000"',out)

    def test_world_colour_shares_coordinates_and_clock_across_materials(self):
        for name in ('brick/a', 'concrete/b', 'wood/c'):
            out = animate(f'materials/{name}.vmt', 'LightmappedGeneric { $basetexture test }')
            self.assertIn('"$detailscale" "-1337.000"', out)
            self.assertIn('"animatedTextureFrameRate" "8.000"', out)
        model = animate('materials/models/props_lab/crate.vmt', 'VertexLitGeneric { $basetexture test }')
        self.assertIn('"$detailscale" "1.000"', model)
        self.assertNotIn('-1337', model)

    def test_static_props_do_not_use_entity_only_proxy(self):
        out = animate('materials/models/props_c17/crate.vmt', 'VertexLitGeneric { $basetexture crate }')
        self.assertIsNotNone(out)
        self.assertNotIn('EntityRandom', out)
        world_weapon = animate('materials/models/weapons/w_pistol/test.vmt', 'VertexLitGeneric { $basetexture pistol }')
        self.assertNotIn('EntityRandom', world_weapon)

    def test_small_world_motion_has_bounded_harmonics(self):
        import re
        out = animate('materials/brick/test.vmt', 'LightmappedGeneric { $basetexture test }')
        waves = re.findall(r'"Sine" \{ "sinePeriod" "([^"]+)" "sineMin" "([^"]+)" "sineMax" "([^"]+)"', out)
        self.assertEqual(len(waves), 10)
        limits = [0.0012, 0.0012, 0.0035, 0.0035, 0.006]
        for i, limit in enumerate(limits):
            a, b = waves[i*2:i*2+2]
            self.assertGreater(float(a[0]), 7.9)
            self.assertGreater(float(b[0]), float(a[0]) * 1.6)
            total = (float(a[2])-float(a[1])+float(b[2])-float(b[1]))/2
            self.assertAlmostEqual(total, limit, places=6)

    def test_comments_do_not_change_eligibility_and_phase_is_stable(self):
        source = '// Proxies { }\nLightmappedGeneric { $basetexture test /* $alphatest 1 */ }'
        a = animate('materials/brick/a.vmt', source)
        self.assertIsNotNone(a)
        self.assertEqual(a, animate('materials/brick/a.vmt', source))
        self.assertNotEqual(a, animate('materials/brick/b.vmt', source))
        self.assertIsNone(animate('materials/brick/a.vmt', source + ' }'))


if __name__ == '__main__':
    unittest.main()
