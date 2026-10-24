"""Exercise the real Windows companion protocol against disposable files."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CSC = Path('C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe')


class LiveToggleTests(unittest.TestCase):
    @unittest.skipUnless(CSC.exists(), 'Windows .NET Framework compiler required')
    def test_companion_protocol_and_rollback(self):
        with tempfile.TemporaryDirectory(prefix='xen-toggle-test-') as temp:
            exe = Path(temp)/'checks.exe'
            subprocess.run([str(CSC), '/nologo', '/main:ToggleChecks', '/out:'+str(exe),
                            str(ROOT/'tools/live_toggle.cs'), str(ROOT/'tests/live_toggle_checks.cs')],
                           check=True, capture_output=True)
            subprocess.run([str(exe), temp], check=True, capture_output=True)
