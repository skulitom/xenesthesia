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
            self.assertIn(Path(name).suffix, {'.vmt','.vcs','.cfg'})
            self.assertNotIn(Path(name).name, {'autoexec.cfg','config.cfg','gameinfo.txt'})
            if name.endswith('.cfg'):
                lines = [x.strip() for x in read(name).decode('ascii').splitlines()
                         if not x.strip().startswith('//')]
                commands = [x.split()[0] for x in lines if x and not x.startswith('echo ')]
                self.assertNotIn('sv_cheats', commands)
                self.assertNotIn('host_writeconfig', commands)
                if name.endswith('xen_keys.cfg'):
                    self.assertEqual([x for x in lines if x.startswith('bind ')],
                                     ['bind F4 "exec xen_toggle"'])
                else:
                    self.assertNotIn('bind', commands)

    def test_compiled_shader_and_both_postprocess_paths(self):
        _, read = read_vpk(ROOT/'content.vpk')
        data = read('shaders/fxc/xenesthesia_ps20b.vcs')
        version,total,dynamic,flags,centroid,static,crc = struct.unpack_from('<7I',data)
        self.assertEqual((version,total,dynamic,static),(6,1,1,2))
        self.assertNotEqual(crc,0)
        self.assertGreater(len(data),100)
        a = read('materials/dev/bloomadd.vmt')
        b = read('materials/dev/engine_post.vmt')
        self.assertEqual(a,b)
        self.assertIn(b'"$pixshader" "xenesthesia_ps20"',a)
        self.assertIn(b'"CurrentTime"',a)
        self.assertIn(b'"$texture2" "_rt_SmallFB1"',a)

if __name__ == '__main__':
    unittest.main()
