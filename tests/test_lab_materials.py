"""Guard the alpha boundary, authored tank setup, and looping normal data."""
import math
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import lab_materials as lab
import lab_textures as texture
from surface_motion import animate, tokens
from vpk import read_vpk


class LabMaterialTests(unittest.TestCase):
    def test_carpet_overlays_keep_exact_base_uvs_and_alpha(self):
        source = 'LightmappedGeneric { $basetexture carpet $translucent 1 $decal 1 $vertexalpha 1 }'
        for name in lab.RUGS | lab.RUNNERS:
            out = animate(name, source)
            self.assertIsNotNone(out, name)
            self.assertTrue(out.startswith(source[:-1]))
            self.assertNotIn('TextureTransform', out)
            self.assertNotIn('EntityRandom', out)
            self.assertIn('"AnimatedTexture"', out)
        self.assertIsNone(animate('materials/overlays/stain.vmt', source))

    def test_contiguous_runner_pieces_share_world_colour(self):
        for name in lab.RUNNERS:
            out = animate(name, 'LightmappedGeneric { $basetexture runner $decal 1 }')
            self.assertIn('"$detailscale" "-1337.000"', out)
            self.assertIn('"animatedTextureFrameRate" "8.000"', out)

    def test_tank_replaces_only_normal_animation_and_scroll(self):
        original = '''Refract { $model 1 $refractamount .2 $refracttint "{255 200 110}"
        $normalmap dev/water_normal $refracttinttexture original/tint $bluramount 1
        Refract_DX60 { $fallbackmaterial original/dx60 }
        Proxies {
          AnimatedTexture { animatedtexturevar $dudvmap animatedtextureframerate 30 }
          AnimatedTexture { animatedtexturevar $normalmap animatedtextureframerate 30 }
          TextureScroll { texturescrollvar $bumptransform texturescrollrate .05 }
        } }'''
        out = lab.tank_material(lab.TANK, original, tokens)
        for retained in ('$model 1', '$refracttinttexture original/tint', '$bluramount 1',
                         'Refract_DX60 { $fallbackmaterial original/dx60 }',
                         'animatedtexturevar $dudvmap animatedtextureframerate 30'):
            self.assertIn(retained, out)
        self.assertIn('animatedtexturevar $normalmap animatedtextureframerate "16"', out)
        self.assertNotIn('TextureScroll', out)
        self.assertNotIn('EntityRandom', out)
        self.assertIsNone(lab.tank_material('materials/other_glass.vmt', original, tokens))

    def test_colour_border_neutral_and_time_loop_exact(self):
        for u, v in ((0, .5), (1, .5), (.5, 0), (.5, 1)):
            for phase in (0, 1, 2, 3):
                self.assertEqual(texture.weave_colour(u, v, phase), (128, 128, 128))
        self.assertEqual(texture.pixels(0), texture.pixels(texture.WEAVE_FRAMES))
        self.assertEqual(texture.pixels(0, True), texture.pixels(texture.EDDY_FRAMES, True))
        self.assertNotEqual(texture.pixels(0), texture.pixels(16))

    def test_eddy_spatial_seams_unit_normals_and_opaque_alpha(self):
        for p in (0, .7, 2.8):
            for v in (0, .1, .35, .9):
                self.assertEqual(texture.eddy_normal(0, v, p), texture.eddy_normal(1, v, p))
                self.assertEqual(texture.eddy_normal(v, 0, p), texture.eddy_normal(v, 1, p))
        data, size = texture.pixels(17, True), texture.SIZE
        while True:
            for i in range(0, len(data), 4):
                n = [x/127.5-1 for x in data[i:i+3]]
                self.assertAlmostEqual(math.sqrt(sum(x*x for x in n)), 1, delta=.008)
                self.assertEqual(data[i+3], 255)
            if size == 1:
                break
            data = texture.normal_downsample(data, size)
            size //= 2

    def test_packaged_texture_layout_and_frames(self):
        root = Path(__file__).resolve().parents[1]
        _, read = read_vpk(root/'content.vpk')
        for name, frames, flags, fmt, channels in [('weave', 128, 0xE, 2, 3),
                                                   ('eddy_normal', 256, 0x82, 0, 4)]:
            data = read(f'materials/xenesthesia/{name}.vtf')
            self.assertEqual(struct.unpack_from('<HHIHH', data, 16), (64, 64, flags, frames, 0))
            self.assertEqual(struct.unpack_from('<IBiBBH', data, 52), (fmt, 7, -1, 0, 0, 1))
            self.assertEqual(len(data), 80+frames*channels*sum(4**i for i in range(7)))


if __name__ == '__main__':
    unittest.main()
