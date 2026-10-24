"""Guard selective deformation and preservation of authored material behavior."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from human_pulse import material, patch_shader
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

    def test_enemy_pulses_preserve_native_shading_and_masks(self):
        source = 'VertexLitGeneric { $basetexture enemy $bumpmap normal $phong 1 $selfillum 1 $alphatest 1 }'
        for folder, marker in [('combine_soldier', 1002), ('police', 1000),
                               ('zombie_fast', 1001), ('zombie_poison', 1001),
                               ('headcrab_black', 1001), ('antlion', 1001), ('antlion_guard', 1001)]:
            out = material(f'materials/models/{folder}/test.vmt', source, tokens)
            self.assertTrue(out.startswith(source[:-1]))
            self.assertIn(f'translate {marker} 0', out)
            self.assertNotIn('VortWarp', out)
        self.assertIsNone(material('materials/models/police/glint.vmt', source, tokens))

    def test_pickups_keep_markings_glow_and_get_geometry(self):
        from human_pulse import PICKUPS
        for name in PICKUPS:
            source = 'VertexLitGeneric { $basetexture kit $selfillum 1 $envmapmask mask }'
            out = material(name, animate(name, source), tokens)
            self.assertIn('translate 1003 0', out)
            self.assertIn('$selfillum 1', out)
            self.assertIn('$envmapmask mask', out)
            self.assertIn('xenesthesia/prism', out)
            self.assertNotIn('EntityRandom', out)

    def test_shared_antlion_gib_materials_are_safe_for_static_props(self):
        out = material('materials/models/antlion/antlionhigh_sheet.vmt',
                       'VertexLitGeneric { $basetexture antlion }', tokens)
        self.assertNotIn('EntityRandom', out)
        self.assertIn('translate 1001 0', out)

    def test_armoured_head_mask_uses_rest_pose_not_world_height(self):
        from surface_shaders import patch_shader as patch_generic
        root = Path(__file__).resolve().parents[1]/'artifacts/private'
        for name, folder, patch in [
            ('skin_vs20.fxc', 'npc-sdk-clean', patch_shader),
            ('vertexlit_and_unlit_generic_vs20.fxc', 'surface-sdk-clean', patch_generic),
            ('vertexlit_and_unlit_generic_bump_vs20.fxc', 'surface-sdk-clean', patch_generic)]:
            out = patch(name, (root/folder/name).read_bytes().decode('cp1252'))
            if '_bump_' not in name:
                self.assertLess(out.index('vPosition.xyz *= 1.0'), out.index('\n\tSkinPosition'))
            self.assertIn('smoothstep(52.0, 61.0, v.vPos.z)', out)
            self.assertIn('xenHuman && xenMarker < 1002.0', out)

    def test_glasses_keep_original_alpha_and_lighting(self):
        for name, source in [
            ('glassesfront_walter', 'VertexLitGeneric { $basetexture front $envmapmask mask }'),
            ('glass2', 'UnlitGeneric { $basetexture glass $translucent 1 $additive 1 }')]:
            out = material(f'materials/models/kleiner/{name}.vmt', source, tokens)
            self.assertIsNotNone(out)
            self.assertTrue(out.startswith(source[:-1]))
            self.assertNotIn('$phong', out)
            self.assertNotIn('$basemapalphaphongmask', out)
            self.assertIn('translate 1000 0', out)

    def test_eye_flashlight_deformation_does_not_require_intro_combo(self):
        # Regression: this branch was once misplaced in material(), causing
        # the compiler to silently erase the generic INTRO-only eye patch.
        source = ('#include "common_vs_fxc.h"\n'
                  'const float4 cLightPosition : register( SHADER_SPECIFIC_CONST_0 );\n'
                  'VS_OUTPUT main() {\n\t// Transform into projection space\nreturn o; }')
        out = patch_shader('eyes_flashlight_vs20.fxc', source)
        self.assertNotIn('#if INTRO', out)
        self.assertIn('XenHumanPulseWorld(worldPos, xenEyeUp.xyz, xenEyeUp.w - 2.0)', out)
        self.assertIn('xenEyeUp : register( SHADER_SPECIFIC_CONST_7 )', out)

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
