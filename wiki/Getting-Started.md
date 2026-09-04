# Getting Started

**Requirements:** Windows 10/11 with **[WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)** (Microsoft Edge runtime — usually already installed).

## 1. Get output files in-game

On each character, run in EverQuest chat:

| Command | What it creates |
|---------|-----------------|
| `/outputfile inventory` | Required — `Name_server-Inventory.txt` |
| `/outputfile inventory CHR_Server-CLASS-Inventory.txt` | Optional — persona inventory (`Name_server-CLASS-Inventory.txt`). A hotkey per persona is suggested. |
| `/outputfile missingspells` | Optional — spell and rune tabs |
| `/outputfile achievements` | Optional — achievement tabs |

EQ writes those files to the root of your **EverQuest** folder (not the Logs subfolder). Details: [[In-Game Output Files]].

## 2. Run the app

1. Download **`EQGM-x.y.z.exe`** from [Releases](https://github.com/Neclub/EQ-Gear-Management/releases).
2. Double-click the `.exe` to open it.

Windows may show a SmartScreen or antivirus warning. Download only from the GitHub **Releases** page above, then **More info → Run anyway** if asked. Details: [[Troubleshooting]].

If a newer GitHub Release exists, a popup shows the current and newest versions and asks whether to download. **Yes** opens the official GitHub download in your browser; the app does not install or run the file.

## 3. Generate the report

1. Click **EQ Folder** and pick the root of your EverQuest folder; select which characters to import.
2. Drag names in **Team characters** to set column order if you want. Adjust **Export options** on the right if needed. Under **Gear tier colors**, click a swatch to customize Team Gear / Gear T-Level colors — they persist the next time you open the app. **Browse…** under **Output folder** picks where to save; the file is always named `{Server}_Team Inventory.xlsx` (or `{Character}_…` for a single character).
3. Choose **Excel**, **HTML**, or **Both**, then click **Generate Report**.

<p align="center">
  <img src="https://neclub.github.io/EQ-Gear-Management/img/eqgm-setup.png" alt="EQ Gear Management setup screen" width="720">
</p>

Output: `{Server}_Team Inventory.xlsx` (and `{Server}_Team_Inventory.html` if HTML is included). When HTML is included, the report opens in your default browser. The setup screen stays open.

If Excel already has the file open, the app saves as `Team Inventory_1.xlsx`, etc.

More on the UI: [[Setup Screen]]. Reading each section: [[Gear]], [[Spells]], [[Augs]], [[Quests and Achievements]], [[HTML Report]]. Stuck? [[Troubleshooting]].
