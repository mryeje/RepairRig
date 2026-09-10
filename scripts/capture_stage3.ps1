param([string]$Output='E:\RepairRig\renders\stage3_visible.png')
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class RepairRigWindow {
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd,int nCmdShow);
[DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd,out RECT r);
public struct RECT { public int Left,Top,Right,Bottom; }
}
"@
$p=Get-Process -Id 30904
[RepairRigWindow]::ShowWindow($p.MainWindowHandle,3) | Out-Null
[RepairRigWindow]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
$r=New-Object RepairRigWindow+RECT
[RepairRigWindow]::GetWindowRect($p.MainWindowHandle,[ref]$r) | Out-Null
$b=New-Object Drawing.Bitmap ($r.Right-$r.Left),($r.Bottom-$r.Top)
$g=[Drawing.Graphics]::FromImage($b)
$g.CopyFromScreen($r.Left,$r.Top,0,0,$b.Size)
$b.Save($Output,[Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $b.Dispose()
