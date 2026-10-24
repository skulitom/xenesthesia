// Original Xenesthesia companion, MIT. No hooks, injection or game memory access.
// F5 asks through the native console log; the response is an ordinary game cfg.
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading;

internal sealed class LiveToggle : IDisposable
{
    const string Bind = "bind F5 \"exec xen_toggle; xen_toggle_begin\"\n";
    internal const string Missing = "alias xen_toggle_begin \"\"\necho Xenesthesia: launch with the preview launcher to use F5.\n" + Bind;
    readonly string stateRoot, mountRoot, cfgRoot;
    readonly string token = Guid.NewGuid().ToString("N");
    readonly FileStream ownership;
    internal bool Enabled = true;
    string slot = "a";

    internal LiveToggle(string state, string mount, string cfg)
    {
        stateRoot = Path.GetFullPath(state);
        mountRoot = Path.GetFullPath(mount);
        cfgRoot = Path.GetFullPath(cfg);
        foreach (string root in new[] { stateRoot, mountRoot })
            if (File.ReadAllText(Path.Combine(root, ".xenesthesia-owned")).Trim() != "Xenesthesia live toggle v1")
                throw new InvalidOperationException("Unowned toggle directory: " + root);
        ownership = new FileStream(Path.Combine(stateRoot, "companion.lock"), FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None);
        string mounted = Path.Combine(mountRoot, "materials");
        if (!Directory.Exists(mounted) && Directory.Exists(Path.Combine(stateRoot, "on")))
            Directory.Move(Path.Combine(stateRoot, "on"), mounted);
        if (!Directory.Exists(mounted))
            throw new InvalidOperationException("Run prepare-live-toggle.py with the game closed first.");
        if (!Directory.Exists(Path.Combine(stateRoot, "off")) && Directory.Exists(Path.Combine(stateRoot, "on")))
        {
            // Recover an interrupted previous OFF session before accepting input.
            Enabled = false;
            SwitchMaterials(true);
        }
        if (!Directory.Exists(Path.Combine(stateRoot, "off"))) throw new IOException("Missing original materials.");
        File.WriteAllText(Path.Combine(stateRoot, "companion.pid"), Process.GetCurrentProcess().Id.ToString());
        WriteCfg("xen_wait_timeout", "alias xen_wait_continue \"\"\necho Xenesthesia toggle timed out. Restart the companion before trying again.\n" + Bind);
        PrepareRequest();
        WriteState();
    }

    void WriteCfg(string name, string value)
    {
        // Readers see a complete old or new file, never a partial console script.
        string path = Path.Combine(cfgRoot, name + ".cfg");
        string temp = path + ".tmp";
        File.WriteAllText(temp, value, new UTF8Encoding(false));
        for (int attempt = 0; ; ++attempt)
        {
            try
            {
                if (File.Exists(path)) File.Replace(temp, path, null);
                else File.Move(temp, path);
                break;
            }
            catch (IOException) { if (attempt == 39) throw; Thread.Sleep(10); }
        }
    }

    internal string Request { get { return "XENESTHESIA_REQUEST_" + token + "_" + slot; } }

    void PrepareRequest()
    {
        WriteCfg("xen_toggle_reply_" + slot, "// Pending; return without recursing into another exec.\n");
        var request = new StringBuilder("bind F5 \"\"\nalias xen_read_reply \"exec xen_toggle_reply_" + slot + "\"\nalias xen_wait_continue xen_wait_next\nalias xen_toggle_begin xw0\n");
        for (int i = 0; i < 40; ++i)
        {
            string next = i == 39 ? "exec xen_wait_timeout" : "xw" + (i + 1);
            request.Append("alias xw" + i + " \"alias xen_wait_next " + (i == 39 ? "xen_timeout" : next) + "; wait 30; xen_read_reply; xen_wait_continue\"\n");
        }
        // Some native console diagnostics omit their trailing newline. Flush
        // an empty line first so our exact request cannot join that output.
        request.Append("alias xen_timeout \"exec xen_wait_timeout\"\necho\necho " + Request + "\n");
        // The key binding calls xen_toggle_begin AFTER exec returns. Valve's
        // exec evaluates nested files synchronously, so starting the wait chain
        // inside that file would recurse rather than yield to the next frame.
        WriteCfg("xen_toggle", request.ToString());
    }

    void SwitchMaterials(bool enabled)
    {
        if (Enabled == enabled) return;
        string current = Path.Combine(mountRoot, "materials");
        string saved = Path.Combine(stateRoot, Enabled ? "on" : "off");
        string incoming = Path.Combine(stateRoot, enabled ? "on" : "off");
        // Both directories are prepared and owned. Rename only these exact
        // directories; never delete or traverse unrelated custom content.
        if (Directory.Exists(saved) || !Directory.Exists(incoming))
            throw new IOException("Unexpected material state; refusing to replace it.");
        MoveMaterials(current, saved);
        try { MoveMaterials(incoming, current); }
        catch { MoveMaterials(saved, current); throw; }
        Enabled = enabled;
        WriteState();
    }

    static void MoveMaterials(string source, string destination)
    {
        for (int attempt = 0; ; ++attempt)
        {
            try { Directory.Move(source, destination); return; }
            catch (IOException) { if (attempt == 39) throw; Thread.Sleep(10); }
        }
    }

    void WriteState()
    {
        File.WriteAllText(Path.Combine(stateRoot, "state.txt"), Enabled ? "on" : "off");
    }

    internal bool Handle(string line)
    {
        if (line.Trim() != Request) return false;
        string answered = slot;
        try
        {
            SwitchMaterials(!Enabled);
            slot = slot == "a" ? "b" : "a";
            PrepareRequest();
            // Next slot is pending before this acknowledgement is visible.
            // A stale answer can therefore never satisfy the next keypress.
            WriteCfg("xen_toggle_reply_" + answered,
                "alias xen_wait_continue \"\"\nmat_reloadallmaterials\necho Xenesthesia visuals " + (Enabled ? "ON" : "OFF") + ".\n" + Bind);
        }
        catch (Exception e)
        {
            File.AppendAllText(Path.Combine(stateRoot, "errors.log"), DateTime.UtcNow + " " + e + "\n");
            slot = answered == "a" ? "b" : "a";
            PrepareRequest();
            WriteCfg("xen_toggle_reply_" + answered, "alias xen_wait_continue \"\"\necho Xenesthesia toggle failed. See companion errors.log.\n" + Bind);
        }
        return true;
    }

    public void Dispose()
    {
        try
        {
            SwitchMaterials(true);
            // Leave no loose material overrides after the game exits. Ordinary
            // launches and Workshop disable/uninstall then behave normally.
            MoveMaterials(Path.Combine(mountRoot, "materials"), Path.Combine(stateRoot, "on"));
            WriteCfg("xen_toggle", Missing);
        }
        finally { ownership.Dispose(); }
    }

    static int Main(string[] args)
    {
        try
        {
            if (args.Length != 5) throw new ArgumentException("Usage: live-toggle STATE MOUNT CFG LOG GAME_PID");
            var game = Process.GetProcessById(Int32.Parse(args[4]));
            if (game.ProcessName != "hl2") throw new ArgumentException("Target must be the running Half-Life 2 process.");
            long position = File.Exists(args[3]) ? new FileInfo(args[3]).Length : 0;
            using (var live = new LiveToggle(args[0], args[1], args[2]))
            {
                string pending = "";
                while (!game.HasExited)
                {
                    if (File.Exists(args[3]))
                    {
                        using (var stream = new FileStream(args[3], FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
                        {
                            if (stream.Length < position) { position = 0; pending = ""; }
                            stream.Position = position;
                            using (var reader = new StreamReader(stream))
                            {
                                pending += reader.ReadToEnd();
                                position = stream.Position;
                            }
                        }
                        int end;
                        while ((end = pending.IndexOf('\n')) >= 0)
                        {
                            live.Handle(pending.Substring(0, end));
                            pending = pending.Substring(end + 1);
                        }
                        if (pending.Length > 65536) pending = "";
                    }
                    Thread.Sleep(50);
                }
            }
            return 0;
        }
        catch (Exception e)
        {
            if (args.Length > 0 && Directory.Exists(args[0]))
                File.AppendAllText(Path.Combine(args[0], "errors.log"), DateTime.UtcNow + " " + e + "\n");
            return 1;
        }
    }
}
