"""Validate the release bytes and guard against unintended game/config changes."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from vpk import read_vpk

class PackageTests(unittest.TestCase):
    def test_archive_contains_exact_manifest_bytes(self):
        manifest = json.loads((ROOT/'artifacts/build-manifest.json').read_text())
        entries, read = read_vpk(ROOT/'content.vpk')
        self.assertEqual(set(entries), set(manifest))
        for name, digest in manifest.items():
            body = read(name)
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest, name)
            self.assertEqual(body, (ROOT/'content'/name).read_bytes(), name)

    def test_content_only_and_opt_in_binding(self):
        entries, read = read_vpk(ROOT/'content.vpk')
        for name in entries:
            self.assertIn(Path(name).suffix, {'.vmt','.vcs','.cfg','.vtf','.txt'})
            if name.endswith('.txt'):
                self.assertIn(name, {'xenesthesia/licenses/valve-sdk-license.txt',
                                    'xenesthesia/licenses/valve-sdk-thirdpartylegalnotices.txt'})
            if name.endswith('.vtf'):
                self.assertIn(name, {'materials/xenesthesia/prism.vtf',
                                     'materials/xenesthesia/weave.vtf',
                                     'materials/xenesthesia/eddy_normal.vtf'})
            self.assertNotIn(Path(name).name, {'autoexec.cfg','config.cfg','gameinfo.txt'})
            if name.endswith('.cfg'):
                lines = [x.strip() for x in read(name).decode('ascii').splitlines()
                         if not x.strip().startswith('//')]
                commands = [x.split()[0] for x in lines if x and not x.startswith('echo ')]
                self.assertNotIn('sv_cheats', commands)
                self.assertNotIn('host_writeconfig', commands)
                if name.endswith('xen_keys.cfg'):
                    self.assertEqual([x for x in lines if x.startswith('bind ')],
                                     ['bind F4 "exec xen_help"'])
                else:
                    self.assertNotIn('bind', commands)

    def test_surface_colour_texture_and_retired_camera_hooks(self):
        entries, read = read_vpk(ROOT/'content.vpk')
        self.assertNotIn('materials/dev/bloomadd.vmt',entries)
        self.assertNotIn('materials/dev/engine_post.vmt',entries)
        self.assertNotIn('shaders/fxc/xenesthesia_ps20b.vcs',entries)
        data = read('materials/xenesthesia/prism.vtf')
        signature,major,minor,header,width,height,flags,frames,start = struct.unpack_from('<4sIIIHHIHH',data)
        self.assertEqual((signature,major,minor,header),(b'VTF\0',7,2,80))
        self.assertEqual((width,height,frames,start),(64,64,128,0))
        self.assertEqual(flags,2)  # wrap and trilinear; no alpha/no forced clamping
        bump,fmt,mips,low_fmt,low_w,low_h,depth = struct.unpack_from('<fIBiBBH',data,48)
        self.assertEqual((fmt,mips,low_fmt,low_w,low_h,depth),(2,7,-1,0,0,1))
        self.assertEqual(len(data),80 + frames*3*sum(4**i for i in range(mips)))
        largest = 64*64*3
        self.assertNotEqual(data[-largest:],data[-2*largest:-largest])

    def test_experimental_npc_shader_layout_and_markers(self):
        _, read = read_vpk(ROOT/'content.vpk')
        for version,total,dynamic,static in [('20',96,24,3),('30',32,16,2)]:
            header = struct.unpack_from('<6I',read(f'shaders/fxc/vortwarp_vs{version}.vcs'))
            self.assertEqual(header,(6,total,dynamic,0,0,static))
        from npc_pulse import MATERIALS, PATCH, ANCHOR
        self.assertIn('if (g_Time >= 2.0)',PATCH)
        self.assertEqual(PATCH.count(ANCHOR),1)
        for name in MATERIALS:
            source = read(name).decode()
            self.assertTrue(source.startswith('"VortWarp"'))
            self.assertIn('"sineMin" "2.04" "sineMax" "2.75"',source)
            self.assertNotIn('TextureTransform',source)
        self.assertIn(b'SOURCE 1 SDK LICENSE',read('xenesthesia/licenses/valve-sdk-license.txt'))

    def test_world_and_generic_shader_combo_contracts(self):
        _, read = read_vpk(ROOT/'content.vpk')
        layouts = {
            'lightmappedgeneric_vs20': (2048, 8, 65),
            'lightmappedgeneric_flashlight_vs20': (32, 2, 17),
            'vertexlit_and_unlit_generic_vs20': (98304, 192, 145),
            'vertexlit_and_unlit_generic_vs30': (65536, 128, 145),
            'vertexlit_and_unlit_generic_bump_vs20': (192, 24, 5),
            'vertexlit_and_unlit_generic_bump_vs30': (128, 16, 5),
        }
        for name, (total, dynamic, static) in layouts.items():
            self.assertEqual(struct.unpack_from('<6I', read(f'shaders/fxc/{name}.vcs')),
                             (6, total, dynamic, 0, 0, static), name)

if __name__ == '__main__':
    unittest.main()
