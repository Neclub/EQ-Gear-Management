# Troubleshooting

| Problem | What to do |
|---------|------------|
| “Add at least one *-Inventory.txt” | Spell files alone are not enough — add inventory files. |
| GUI window is blank or fails to start | Install the [WebView2 runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (Evergreen bootstrapper). |
| Spell tabs empty | Confirm spell file names match `Name_server-CLASS-MissingSpells.txt` and character names match inventory files. |
| Achievement tabs empty | Confirm achievement file names match `Name_server-Achievements.txt` and character/server match inventory files. |
| Include chips are grayed out | No inventory files in the roster yet. |
| “Permission denied” / save failed | Close the workbook in Excel and try again. |
| Generate Report error dialog | Read the message (it stays until **OK**). Common causes: Excel has the file open, no inventory files, or a network/catalog fetch failed. Details of the last run — including what was served from cache vs fetched from EQ Resource/raidloot, and fetch problems — are in `%LOCALAPPDATA%\EQGM\last_report.log`. |
| Wrong characters in columns | Each inventory file should be one character; check filenames. |
| Type 7/8 Augs sheets missing or empty | Leave the **Type 7/8 Augs** chip on; first generate seeds from the GitHub prebuilt cache (needs network), then reuses `%LOCALAPPDATA%\EQGM\`. Use **1.35.7** or newer if the catalog was empty — older searches mixed `augslot` with `augtype` and returned no rows. |
| Type 7/8 note says to move an aug, but **Upgrade to** is blank | Use **1.30.3** or newer and regenerate the report. Older builds marked that donor hole as BiS. |
| Type 5 Augs sheet missing or empty | Leave the **Type 5 Augs** chip on; sockets and aug stats use the same `%LOCALAPPDATA%\EQGM\` cache as Type 7/8 (first generate may seed from GitHub). |
| Type 18/19 Augs sheet missing or empty | Leave the **Type 18/19 Augs** chip on; first generate seeds from GitHub, later runs reuse `%LOCALAPPDATA%\EQGM\`. |
| Raid BiS sheet missing or slots look empty | Leave the **Raid BiS** chip on; first generate seeds from GitHub, later runs reuse `%LOCALAPPDATA%\EQGM\`. |
| Raid BiS suggests an item your class cannot wear | Use **1.35.4** or newer and regenerate. Older caches treated jewelry with no class list as wearable by everyone. |
| Raid BiS paperdoll shows `PAL Chest` (or similar) instead of an icon | Use **1.35.5** or newer and regenerate. Older caches kept armor catalog stubs and skipped hydrating names, stats, and icons. |
| Stale or wrong catalog / aug / Raid BiS data after an update | **Help → Clear Cache**, then Generate Report (re-seeds from GitHub, then fetches true misses into `%LOCALAPPDATA%\EQGM\`). |
| HTML looks outdated after an update | Regenerate the report. |
| Installer or update asks for administrator permission | Expected — the app installs under Program Files. Allow UAC, finish the wizard, then open EQ Gear Management from the Start Menu if it does not relaunch. |
| Update download fails | Check network access to GitHub. **Help → Check for Updates** again, or download `EQGM-install-x.y.z.exe` from [Releases](https://github.com/Neclub/EQ-Gear-Management/releases) and run it manually. |
| Still using an old portable `EQGM-x.y.z.exe` | Install once from the latest Release (`EQGM-install-x.y.z.exe`). Settings in `%LOCALAPPDATA%\EQGM\` carry over. You can delete the old portable exe afterward. |
| Uninstall left settings behind | By design. Uninstall removes Program Files and shortcuts; `%LOCALAPPDATA%\EQGM\` (settings and caches) stays. Delete that folder manually if you want a clean slate. |

More help: [[Getting Started]], [[In-Game Output Files]], [[Setup Screen]].

Download: [Releases](https://github.com/Neclub/EQ-Gear-Management/releases) · Product page: [neclub.github.io/EQ-Gear-Management](https://neclub.github.io/EQ-Gear-Management/)
