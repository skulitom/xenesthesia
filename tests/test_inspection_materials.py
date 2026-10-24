"""Guard sign masks, charger subparts and the stock-material off path."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from inspection_materials import STATIONS, station_material, sign_material
from surface_motion import tokens
from surface_shaders import patch_shader


class InspectionMaterialTests(unittest.TestCase):
    def test_charger_parts_keep_authored_glow_alpha_and_share_shape_clock(self):
        for name in STATIONS:
            flags = '$translucent 1 $envmap env_cubemap' if 'glass' in name else '$selfillum 1'
            source = 'VertexLitGeneric { $basetexture charger '+flags+' }'
            out = station_material(name, source, tokens)
            self.assertTrue(out.startswith(source[:-1]))
            self.assertIn('"sineMin" "1003.004000" "sineMax" "1003.045000"', out)
            self.assertIn('"sinePeriod" "7.300000"', out)
            self.assertNotIn('EntityRandom', out)
            self.assertNotIn('EntityOrigin', out)
            self.assertEqual([t[0].strip('"').lower() for t in tokens(out)].count('proxies'), 1)
        self.assertIsNone(station_material('materials/models/props_lab/glass.vmt', source, tokens))

    def test_charger_refuses_unreviewed_bump_path_or_authored_animation(self):
        for param in ('$bumpmap normal', '$phong 1', 'Proxies { Sine { } }'):
            with self.assertRaises(ValueError):
                station_material(sorted(STATIONS)[0], 'VertexLitGeneric { $basetexture a '+param+' }', tokens)

    def test_signs_reuse_existing_image_and_preserve_alpha_and_fallback(self):
        original = ('LightmappedGeneric { $basetexture "Decals/warning" $translucent 1 '
                    '$decal 1 $vertexalpha 1 DX8 { $fallbackmaterial old/sign } } // end')
        out = sign_material('materials/decals/decalsigndanger001a.vmt', original, tokens)
        self.assertTrue(out.startswith(original[:original.rfind('}')]))
        self.assertTrue(out.endswith('} // end'))
        self.assertIn('"$detail" "Decals/warning"', out)
        self.assertIn('"$detailblendmode" "0"', out)  # retail RGB-only MOD2X
        self.assertIn('"$detailtint" "[.5 .5 .5]"', out)  # white paper stays neutral
        self.assertIn('"$detailscale" "-1338"', out)
        self.assertIn('"Clamp"', out)
        # Source Clamp preserves the destination's type. First write it with
        # Sine (SetFloatValue), otherwise an integer initial zero eats the fade.
        self.assertLess(out.index('"resultVar" "$detailblendfactor"'), out.index('"Clamp"'))
        self.assertIn('"Clamp" { "srcVar1" "$detailblendfactor"', out)
        self.assertNotIn('EntityRandom', out)

    def test_model_sign_has_separate_detail_transform(self):
        out = sign_material('materials/models/props_c17/streetsigns_composite01.vmt',
                            'VertexLitGeneric { $basetexture signs }', tokens)
        self.assertNotIn('$basetexturetransform', out)
        self.assertIn('"resultVar" "$detailtexturetransform"', out)
        self.assertNotIn('-1338', out)

    def test_special_signs_and_unrelated_decals_are_not_taken_over(self):
        for param in ('$detail authored', '$basetexturetransform identity', '$bumpmap normal',
                      'Proxies { Sine { resultVar $alpha } }'):
            self.assertIsNone(sign_material('materials/props/signwarning001b.vmt',
                                           'LightmappedGeneric { $basetexture a '+param+' }', tokens))
        self.assertIsNone(sign_material('materials/decals/blood.vmt',
                                       'LightmappedGeneric { $basetexture blood }', tokens))

    def test_world_and_flashlight_restore_base_before_sampling(self):
        root = Path(__file__).resolve().parents[1] / 'artifacts/private/surface-sdk-clean'
        for name in ('lightmappedgeneric_vs20.fxc', 'lightmappedgeneric_flashlight_vs20.fxc'):
            out = patch_shader(name, (root/name).read_bytes().decode('cp1252'))
            code = out[out.index('if (XenSignEcho'):]
            self.assertLess(code.index('= o.baseTexCoord.xy'), code.index('o.baseTexCoord.xy = v.vBaseTexCoord.xy'))
            self.assertIn('XenWorldColourUV(worldPos)', out)


if __name__ == '__main__':
    unittest.main()
