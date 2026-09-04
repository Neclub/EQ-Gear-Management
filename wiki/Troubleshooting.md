# Troubleshooting

| Problem | What to do |
|---------|------------|
| “Add at least one *-Inventory.txt” | Spell files alone are not enough — add inventory files. |
| GUI window is blank or fails to start | Install the [WebView2 runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) (Evergreen bootstrapper). |
| Spell tabs empty | Confirm spell file names match `Name_server-CLASS-MissingSpells.txt` and character names match inventory files. |
| Achievement tabs empty | Confirm achievement file names match `Name_server-Achievements.txt` and character/server match inventory files. |
| Include chips are grayed out | No inventory files in the roster yet. |
| “Permission denied” / save failed | Close the workbook in Excel and try again. |
| Wrong characters in columns | Each inventory file should be one character; check filenames. |
| Type 7/8 Augs sheets missing or empty | Leave the **Type 7/8 Augs** chip on; the first run needs network access to EQ Resource (later runs use `%LOCALAPPDATA%\EQGM\` cache). |
| Type 7/8 note says to move an aug, but **Upgrade to** is blank | Use **1.30.3** or newer and regenerate the report. Older builds marked that donor hole as BiS. |
| Type 5 Augs sheet missing or empty | Leave the **Type 5 Augs** chip on; sockets and aug stats use the same `%LOCALAPPDATA%\EQGM\` cache as Type 7/8 (first run may need network). |
| Type 18/19 Augs sheet missing or empty | Leave the **Type 18/19 Augs** chip on; the first run needs network access to EQ Resource (later runs use `%LOCALAPPDATA%\EQGM\` cache). |
| Raid BiS sheet missing or slots look empty | Leave the **Raid BiS** chip on; the first run needs network access to EQ Resource (later runs use `%LOCALAPPDATA%\EQGM\` cache). |
| Raid BiS suggests an item your class cannot wear | Use **1.35.4** or newer and regenerate. Older caches treated jewelry with no class list as wearable by everyone. |
| HTML looks outdated after an update | Regenerate the report. |
| Warning: “Failed to remove temporary directory …_MEI…” | Harmless packaging cleanup from the single-file `.exe`. Windows (or antivirus) sometimes keeps a handle open after exit, so PyInstaller cannot delete its extract folder. Click **OK** and keep working. You can delete leftover `_MEI*` folders under `%TEMP%` when EQGM is closed. It is unrelated to reading your EverQuest folder. |

More help: [[Getting Started]], [[In-Game Output Files]], [[Setup Screen]].

Download: [Releases](https://github.com/Neclub/EQ-Gear-Management/releases) · Product page: [neclub.github.io/EQ-Gear-Management](https://neclub.github.io/EQ-Gear-Management/)
