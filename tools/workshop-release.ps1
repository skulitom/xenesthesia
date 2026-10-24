param([ValidateSet('inspect','subscribe','gallery','publish')][string]$Action = 'inspect')
$ErrorActionPreference = 'Stop'
if ([IntPtr]::Size -ne 4) { throw 'Run with 32-bit Windows PowerShell for the installed HL2 Steam API.' }
# Development verification only. Uses the installed game's official Steamworks
# library and the already signed-in local client. Never ships in the addon.
$env:SteamAppId = '220'
$env:SteamGameId = '220'
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class XenWorkshop {
    const string Dll = @"D:\Steam\steamapps\common\Half-Life 2\bin\steam_api.dll";
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    public static extern int SteamAPI_InitFlat(StringBuilder error);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    public static extern void SteamAPI_Shutdown();
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    public static extern void SteamAPI_RunCallbacks();
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    public static extern IntPtr SteamAPI_SteamUGC_v020();
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    public static extern IntPtr SteamAPI_SteamUtils_v010();
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    public static extern ulong SteamAPI_ISteamUGC_StartItemUpdate(IntPtr self, uint app, ulong item);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    [return: MarshalAs(UnmanagedType.I1)]
    public static extern bool SteamAPI_ISteamUGC_SetItemVisibility(IntPtr self, ulong update, int visibility);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl, CharSet=CharSet.Ansi)]
    [return: MarshalAs(UnmanagedType.I1)]
    public static extern bool SteamAPI_ISteamUGC_SetItemDescription(IntPtr self, ulong update, string description);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl, CharSet=CharSet.Ansi)]
    [return: MarshalAs(UnmanagedType.I1)]
    public static extern bool SteamAPI_ISteamUGC_AddItemPreviewFile(IntPtr self, ulong update, string file, int type);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl, CharSet=CharSet.Ansi)]
    public static extern ulong SteamAPI_ISteamUGC_SubmitItemUpdate(IntPtr self, ulong update, string note);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    [return: MarshalAs(UnmanagedType.I1)]
    public static extern bool SteamAPI_ISteamUtils_IsAPICallCompleted(IntPtr self, ulong call, [MarshalAs(UnmanagedType.I1)] out bool failed);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    [return: MarshalAs(UnmanagedType.I1)]
    public static extern bool SteamAPI_ISteamUtils_GetAPICallResult(IntPtr self, ulong call, out SubmitResult result, int size, int callback, [MarshalAs(UnmanagedType.I1)] out bool failed);
    // Valve's source-sdk-2013/public/steam/isteamugc.h: callback 3400 + 4.
    // steamclientpublic.h uses pack(8) on Windows, including 32-bit Windows.
    [StructLayout(LayoutKind.Sequential, Pack=8)]
    public struct SubmitResult {
        public int result;
        [MarshalAs(UnmanagedType.I1)] public bool needsAgreement;
        public ulong item;
    }
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    public static extern uint SteamAPI_ISteamUGC_GetItemState(IntPtr self, ulong item);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    public static extern ulong SteamAPI_ISteamUGC_SubscribeItem(IntPtr self, ulong item);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    [return: MarshalAs(UnmanagedType.I1)]
    public static extern bool SteamAPI_ISteamUGC_DownloadItem(IntPtr self, ulong item, [MarshalAs(UnmanagedType.I1)] bool priority);
    [DllImport(Dll, CallingConvention=CallingConvention.Cdecl)]
    [return: MarshalAs(UnmanagedType.I1)]
    public static extern bool SteamAPI_ISteamUGC_GetItemInstallInfo(IntPtr self, ulong item, out ulong size, StringBuilder folder, uint capacity, out uint timestamp);
}
'@
$errorText = New-Object Text.StringBuilder 1024
$init = [XenWorkshop]::SteamAPI_InitFlat($errorText)
if ($init -ne 0) { throw "Steam API initialization failed ($init): $errorText" }
try {
    $ugc = [XenWorkshop]::SteamAPI_SteamUGC_v020()
    if ($ugc -eq [IntPtr]::Zero) { throw 'Steam UGC interface unavailable.' }
    # Restrict mutations to this task's one already-created Workshop item.
    $project = Split-Path -Parent $PSScriptRoot
    $proof = Get-Content -LiteralPath (Join-Path $project 'artifacts\workshop-item.json') -Raw | ConvertFrom-Json
    [UInt64]$item = $proof.published_file_id
    if ($item -eq 0 -or $item -eq 3822268020 -or $proof.title -notlike 'Xenesthesia*') { throw 'This helper is restricted to the Xenesthesia item recorded by this task.' }
    if ($Action -eq 'publish' -or $Action -eq 'gallery') {
        $project = Split-Path -Parent $PSScriptRoot
        $proof = Get-Content -LiteralPath (Join-Path $project 'artifacts\workshop-item.json') -Raw | ConvertFrom-Json
        if (-not $proof.subscription_verified) { throw 'Downloaded-only runtime verification must pass before publication.' }
        $receiptPath = Join-Path $project ("artifacts\workshop-" + $Action + ".json")
        if (Test-Path -LiteralPath $receiptPath) { throw 'Publication already attempted: inspect its receipt and current Steam state before another mutation.' }
        $description = Get-Content -LiteralPath (Join-Path $project 'artifacts\workshop-description.txt') -Raw
        if ($description -match '[^\x00-\x7f]') { throw 'This helper currently requires ASCII text for ANSI marshaling.' }
        $update = [XenWorkshop]::SteamAPI_ISteamUGC_StartItemUpdate($ugc, 220, $item)
        if ($update -eq [UInt64]::MaxValue) { throw 'Invalid update handle.' }
        if ($Action -eq 'publish' -and -not [XenWorkshop]::SteamAPI_ISteamUGC_SetItemVisibility($ugc, $update, 0)) { throw 'Could not set Public visibility.' }
        if (-not [XenWorkshop]::SteamAPI_ISteamUGC_SetItemDescription($ugc, $update, $description)) { throw 'Could not set description.' }
        foreach ($name in $(if ($Action -eq 'gallery') { @('carpet.jpg','canals.jpg','storefront.jpg') } else { @() })) {
            $preview = Join-Path $project ('artifacts\release\gameplay\' + $name)
            $media = Get-Content -LiteralPath (Join-Path $project 'artifacts\release\gameplay-media.json') -Raw | ConvertFrom-Json
            if ($media.generated_art_used -or $media.runtime_sha256 -ne $proof.runtime_sha256) { throw 'Media does not describe the approved runtime.' }
            if ((Get-FileHash -LiteralPath $preview -Algorithm SHA256).Hash -ne $media.images.$name.sha256) { throw "Unverified gameplay screenshot: $name" }
            if ((Get-Item -LiteralPath $preview).Length -ge 1000000) { throw "Steam preview is too large: $name" }
            if (-not [XenWorkshop]::SteamAPI_ISteamUGC_AddItemPreviewFile($ugc, $update, $preview, 0)) { throw "Could not add preview: $name" }
        }
        $call = [XenWorkshop]::SteamAPI_ISteamUGC_SubmitItemUpdate($ugc, $update, 'Xenesthesia initial release: gentle surface motion, flowing prismatic colours and subtle character pulses. Current native gameplay screenshots.')
        if ($call -eq 0) { throw 'Update submission returned no request handle.' }
        $receipt = [ordered]@{ item=$item; update=$update; call=$call; submitted_utc=[DateTime]::UtcNow.ToString('o'); status='pending' }
        $receipt | ConvertTo-Json | Set-Content -LiteralPath $receiptPath -Encoding UTF8
        $utils = [XenWorkshop]::SteamAPI_SteamUtils_v010()
        $deadline = [DateTime]::UtcNow.AddSeconds(55)
        $failed = $false
        do {
            [XenWorkshop]::SteamAPI_RunCallbacks()
            $completed = [XenWorkshop]::SteamAPI_ISteamUtils_IsAPICallCompleted($utils, $call, [ref]$failed)
            if ($completed) { break }
            Start-Sleep -Milliseconds 100
        } while ([DateTime]::UtcNow -lt $deadline)
        if (-not $completed -or $failed) { throw 'Publication is pending or failed: inspect the saved receipt; do not blindly resubmit.' }
        $result = New-Object XenWorkshop+SubmitResult
        $size = [Runtime.InteropServices.Marshal]::SizeOf($result)
        if ($size -ne 16) { throw "Unexpected callback size: $size" }
        $received = [XenWorkshop]::SteamAPI_ISteamUtils_GetAPICallResult($utils, $call, [ref]$result, $size, 3404, [ref]$failed)
        $receipt.status = 'completed'
        $receipt.received = $received
        $receipt.failed = $failed
        $receipt.result = $result.result
        $receipt.needs_agreement = $result.needsAgreement
        $receipt.returned_item = $result.item
        $receipt | ConvertTo-Json | Set-Content -LiteralPath $receiptPath -Encoding UTF8
        $receipt | ConvertTo-Json
        if (-not $received -or $failed -or $result.result -ne 1 -or $result.item -ne $item) { throw 'Steam did not confirm successful publication.' }
        if ($result.needsAgreement) { throw 'The owner must accept the Workshop agreement in Steam.' }
    }
    if ($Action -eq 'subscribe') {
        $call = [XenWorkshop]::SteamAPI_ISteamUGC_SubscribeItem($ugc, $item)
        if ($call -eq 0) { throw 'Subscribe request was not accepted.' }
        Write-Output "Subscription request handle: $call"
        $deadline = [DateTime]::UtcNow.AddSeconds(60)
        $downloadRequested = $false
        do {
            [XenWorkshop]::SteamAPI_RunCallbacks()
            $state = [XenWorkshop]::SteamAPI_ISteamUGC_GetItemState($ugc, $item)
            if (($state -band 1) -and -not $downloadRequested) {
                $downloadRequested = [XenWorkshop]::SteamAPI_ISteamUGC_DownloadItem($ugc, $item, $true)
            }
            if (($state -band 5) -eq 5 -and ($state -band 56) -eq 0) { break }
            Start-Sleep -Milliseconds 100
        } while ([DateTime]::UtcNow -lt $deadline)
    }
    [XenWorkshop]::SteamAPI_RunCallbacks()
    $state = [XenWorkshop]::SteamAPI_ISteamUGC_GetItemState($ugc, $item)
    [UInt64]$size = 0
    [UInt32]$timestamp = 0
    $folder = New-Object Text.StringBuilder 4096
    $installed = [XenWorkshop]::SteamAPI_ISteamUGC_GetItemInstallInfo($ugc, $item, [ref]$size, $folder, 4096, [ref]$timestamp)
    [pscustomobject]@{ item=$item; state=$state; subscribed=[bool]($state -band 1); installed=$installed; size=$size; folder=$folder.ToString(); timestamp=$timestamp } | ConvertTo-Json
    if ($Action -eq 'subscribe' -and ((-not ($state -band 1)) -or (-not $installed))) { throw 'Subscription/download has not completed; inspect the existing request before retrying.' }
} finally {
    [XenWorkshop]::SteamAPI_Shutdown()
}
