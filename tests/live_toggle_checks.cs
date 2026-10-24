using System;
using System.IO;

internal class ToggleChecks
{
    static void Check(bool value, string why) { if (!value) throw new Exception(why); }
    static int Main(string[] args)
    {
        string root = args[0], state = Path.Combine(root, "state"), mount = Path.Combine(root, "mount"), cfg = Path.Combine(root, "cfg");
        Directory.CreateDirectory(Path.Combine(state, "off"));
        Directory.CreateDirectory(Path.Combine(mount, "materials"));
        Directory.CreateDirectory(cfg);
        foreach (string d in new[] { state, mount }) File.WriteAllText(Path.Combine(d, ".xenesthesia-owned"), "Xenesthesia live toggle v1");
        File.WriteAllText(Path.Combine(state, "off", "example.vmt"), "original bytes");
        File.WriteAllText(Path.Combine(mount, "materials", "example.vmt"), "animated bytes");
        using (var live = new LiveToggle(state, mount, cfg))
        {
            string first = live.Request;
            Check(File.ReadAllText(Path.Combine(cfg, "xen_toggle.cfg")).Contains("\necho\necho " + first),
                  "Request must begin on a fresh log line after unterminated game output");
            Check(!live.Handle("] echo " + first), "Console input echo must not count as a request");
            Check(live.Enabled, "Spurious toggle");
            Check(live.Handle(first), "Request ignored");
            Check(!live.Enabled, "Off not recorded");
            Check(File.ReadAllText(Path.Combine(mount, "materials", "example.vmt")) == "original bytes", "Off did not restore exact bytes");
            Check(File.ReadAllText(Path.Combine(cfg, "xen_toggle_reply_a.cfg")).Contains("mat_reloadallmaterials"), "No refresh acknowledgement");
            Check(File.ReadAllText(Path.Combine(cfg, "xen_toggle_reply_b.cfg")).StartsWith("// Pending;"), "Next answer was stale");
            Check(!live.Handle(first), "Duplicate request toggled again");
            Check(live.Handle(live.Request), "On ignored");
            Check(File.ReadAllText(Path.Combine(mount, "materials", "example.vmt")) == "animated bytes", "On bytes changed");
            Check(File.ReadAllText(Path.Combine(cfg, "xen_toggle_reply_a.cfg")).StartsWith("// Pending;"), "Reused slot did not reset");
            live.Handle(live.Request);
            Check(!live.Enabled, "Third toggle failed");
        }
        Check(File.ReadAllText(Path.Combine(state, "on", "example.vmt")) == "animated bytes", "Exit did not retain on state");
        Check(!Directory.Exists(Path.Combine(mount, "materials")), "Loose overrides survived game exit");
        Check(File.ReadAllText(Path.Combine(cfg, "xen_toggle.cfg")) == LiveToggle.Missing, "No safe offline response");
        // Simulate an unexpected destination: it must remain untouched and the
        // mounted tree must stay intact rather than being partially replaced.
        using (var live = new LiveToggle(state, mount, cfg))
        {
            Directory.CreateDirectory(Path.Combine(state, "on"));
            File.WriteAllText(Path.Combine(state, "on", "keep.txt"), "keep me");
            live.Handle(live.Request);
            Check(live.Enabled, "Failed swap changed state");
            Check(File.ReadAllText(Path.Combine(state, "on", "keep.txt")) == "keep me", "Unexpected content overwritten");
            Check(File.ReadAllText(Path.Combine(mount, "materials", "example.vmt")) == "animated bytes", "Failed swap lost materials");
            File.Delete(Path.Combine(state, "on", "keep.txt"));
            Directory.Delete(Path.Combine(state, "on"));
        }
        Console.WriteLine("Toggle protocol, exact restoration, stale replies, failure rollback and cleanup passed.");
        return 0;
    }
}
