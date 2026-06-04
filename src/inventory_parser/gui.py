from __future__ import annotations

import traceback
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from inventory_parser import __version__
from inventory_parser.character_column_order import (
    ColumnRosterEntry,
    build_column_roster,
    paths_for_roster_removal,
    save_character_column_order,
    saved_character_column_order,
)
from inventory_parser.cli import generate_workbook
from inventory_parser.crew_report import (
    FolderCharacterChoice,
    discover_folder_character_choices,
)
from inventory_parser.achievement_files import collect_achievement_paths
from inventory_parser.missing_spells import (
    bindings_include_personas,
    discover_persona_bindings,
    split_input_paths,
)
from inventory_parser.eq_servers import server_display_name
from inventory_parser.evolver import EVOLVER_LABEL
from inventory_parser.excel_theme import GEAR_SET_FILLS
from inventory_parser.gear_sets import GEAR_SETS_NEWEST_FIRST
from inventory_parser.output_paths import (
    crew_inventory_filename,
    crew_inventory_path,
    default_export_prefix_from_input_paths,
    is_auto_crew_inventory_path,
)
from inventory_parser.slots import NON_VISIBLE_SLOTS, VISIBLE_SLOTS, SlotFilter

_FILE_TYPES = [
    ("Inventory, MissingSpells & Achievements", "*-Inventory.txt;*-MissingSpells.txt;*-Achievements.txt"),
    ("Inventory & MissingSpells", "*-Inventory.txt;*-MissingSpells.txt"),
    ("Inventory dumps", "*-Inventory.txt"),
    ("MissingSpells logs", "*-MissingSpells.txt"),
    ("Achievement dumps", "*-Achievements.txt"),
    ("Text files", "*.txt"),
    ("All files", "*.*"),
]

def _downloads_dir() -> Path:
    return Path.home() / "Downloads"


def _default_output_path(prefix: str | None = None) -> Path:
    return crew_inventory_path(_downloads_dir(), prefix)


# Dark base
_BG = "#121214"
_BG_PANEL = "#1e1e24"
_BG_INPUT = "#282830"
_FG = "#e8eaef"
_FG_MUTED = "#9ca3b4"

# Section accents (echo Excel gear tiers)
_ACCENT_FILES = "#5b8fd9"
_ACCENT_SLOTS = "#5cb8a8"
_ACCENT_OUTPUT = "#c9a227"
_ACCENT_EXCEL = "#3d9b5c"
_ACCENT_EXCEL_ACTIVE = "#2f7a47"
_ACCENT_DANGER = "#c45c5c"
_ACCENT_DANGER_ACTIVE = "#a04848"

# Card label colors per section
_CARD_STYLES: dict[str, tuple[str, str]] = {
    "files": ("Files.TLabelframe", _ACCENT_FILES),
    "slots": ("Slots.TLabelframe", _ACCENT_SLOTS),
    "output": ("Output.TLabelframe", _ACCENT_OUTPUT),
}


def _apply_theme(root: tk.Tk, style: ttk.Style) -> None:
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=_BG)
    style.configure(".", background=_BG, foreground=_FG, font=("Segoe UI", 10))
    style.configure("TFrame", background=_BG)
    style.configure("TLabel", background=_BG, foreground=_FG)
    style.configure("Title.TLabel", background=_BG, foreground=_ACCENT_FILES, font=("Segoe UI", 18, "bold"))
    style.configure("Muted.TLabel", background=_BG, foreground=_FG_MUTED)
    style.configure("Panel.TLabel", background=_BG_PANEL, foreground=_FG_MUTED)
    style.configure("Status.TLabel", background=_BG_PANEL, foreground=_ACCENT_SLOTS)
    style.configure("StatusOk.TLabel", background=_BG_PANEL, foreground=_ACCENT_EXCEL)

    for name, accent in _CARD_STYLES.values():
        style.configure(name, background=_BG_PANEL, bordercolor=accent)
        style.configure(f"{name}.Label", background=_BG_PANEL, foreground=accent, font=("Segoe UI", 10, "bold"))

    style.configure("TButton", padding=(10, 6), background="#35353d", foreground=_FG)
    style.map("TButton", background=[("active", "#454550")])

    style.configure("Primary.TButton", padding=(10, 6))
    style.map(
        "Primary.TButton",
        background=[("active", "#4a7ec4"), ("!disabled", "#3d6fad")],
        foreground=[("!disabled", "#ffffff")],
    )

    style.configure("Secondary.TButton", padding=(10, 6))
    style.map(
        "Secondary.TButton",
        background=[("active", "#4a9e92"), ("!disabled", "#3d857a")],
        foreground=[("!disabled", "#ffffff")],
    )

    style.configure("Danger.TButton", padding=(10, 6))
    style.map(
        "Danger.TButton",
        background=[("active", _ACCENT_DANGER_ACTIVE), ("!disabled", _ACCENT_DANGER)],
        foreground=[("!disabled", "#ffffff")],
    )

    style.configure("Accent.TButton", padding=(18, 11), font=("Segoe UI", 11, "bold"))
    style.map(
        "Accent.TButton",
        background=[("active", _ACCENT_EXCEL_ACTIVE), ("!disabled", _ACCENT_EXCEL)],
        foreground=[("!disabled", "#ffffff")],
    )

    style.configure("TEntry", fieldbackground=_BG_INPUT, foreground=_FG, bordercolor="#454550")
    style.configure("TCombobox", fieldbackground=_BG_INPUT, foreground=_FG, bordercolor="#454550")
    style.map("TCombobox", fieldbackground=[("readonly", _BG_INPUT)])
    _apply_picker_theme(style)


def _apply_picker_theme(style: ttk.Style) -> None:
    """Styles for the folder character picker dialog."""
    style.configure(
        "Picker.TCombobox",
        fieldbackground=_BG_INPUT,
        foreground=_FG,
        background="#454550",
        bordercolor=_ACCENT_FILES,
        lightcolor="#606070",
        darkcolor="#35353d",
        arrowsize=16,
        arrowcolor=_FG,
        padding=(8, 6),
    )
    style.map(
        "Picker.TCombobox",
        fieldbackground=[("readonly", _BG_INPUT), ("disabled", _BG_PANEL)],
        foreground=[("readonly", _FG), ("disabled", _FG_MUTED)],
        background=[("readonly", "#454550"), ("active", "#5a5a68")],
        arrowcolor=[("readonly", _FG), ("active", "#ffffff"), ("disabled", _FG_MUTED)],
        bordercolor=[("focus", _ACCENT_FILES), ("readonly", _ACCENT_FILES)],
    )
    style.configure(
        "Picker.TCheckbutton",
        background=_BG_PANEL,
        foreground=_FG,
        focuscolor=_ACCENT_FILES,
        padding=(2, 4),
    )
    style.map(
        "Picker.TCheckbutton",
        background=[("active", "#2a2a32")],
        foreground=[("disabled", _FG_MUTED)],
    )
    style.configure(
        "Picker.Horizontal.TScrollbar",
        background="#454550",
        troughcolor=_BG_INPUT,
        bordercolor=_BG_INPUT,
        arrowcolor=_FG,
        darkcolor="#35353d",
        lightcolor="#606070",
    )
    style.map(
        "Picker.Horizontal.TScrollbar",
        background=[("active", "#5a5a68")],
        arrowcolor=[("active", "#ffffff")],
    )
    style.configure(
        "Picker.Vertical.TScrollbar",
        background="#454550",
        troughcolor=_BG_INPUT,
        bordercolor=_BG_INPUT,
        arrowcolor=_FG,
        darkcolor="#35353d",
        lightcolor="#606070",
    )
    style.map(
        "Picker.Vertical.TScrollbar",
        background=[("active", "#5a5a68")],
        arrowcolor=[("active", "#ffffff")],
    )
    style.configure(
        "PickerPanel.TLabel",
        background=_BG,
        foreground=_FG_MUTED,
    )


def _show_gear_tiers_help(parent: tk.Tk) -> None:
    """Modal help window: gear tier colors and slot visibility."""
    win = tk.Toplevel(parent)
    win.title("Help — Gear tiers & colors")
    win.configure(bg=_BG)
    win.transient(parent)
    win.grab_set()
    win.minsize(480, 420)
    win.geometry("520x480")

    outer = tk.Frame(win, bg=_BG, padx=16, pady=14)
    outer.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        outer,
        text="Gear tier colors",
        bg=_BG,
        fg=_ACCENT_FILES,
        font=("Segoe UI", 14, "bold"),
    ).pack(anchor="w")

    tk.Label(
        outer,
        text="Newest at top. Item cells in Excel use these colors when the name matches.",
        bg=_BG,
        fg=_FG_MUTED,
        font=("Segoe UI", 9),
        wraplength=460,
        justify=tk.LEFT,
    ).pack(anchor="w", pady=(4, 10))

    list_frame = tk.Frame(outer, bg=_BG_PANEL, padx=8, pady=8)
    list_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(list_frame, bg=_BG_PANEL, highlightthickness=0, borderwidth=0)
    scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
    inner = tk.Frame(canvas, bg=_BG_PANEL)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def add_legend_row(parent_frame: tk.Frame, hex_color: str, label_text: str) -> None:
        row = tk.Frame(parent_frame, bg=_BG_PANEL, pady=4)
        row.pack(fill=tk.X, anchor="w")
        tk.Label(row, text="  ", bg=f"#{hex_color}", width=3, relief=tk.FLAT).pack(
            side=tk.LEFT, padx=(0, 10), ipady=8
        )
        tk.Label(
            row,
            text=label_text,
            bg=_BG_PANEL,
            fg=_FG,
            font=("Segoe UI", 10),
            anchor="w",
            justify=tk.LEFT,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    add_legend_row(inner, GEAR_SET_FILLS["evolver"], EVOLVER_LABEL)
    tk.Label(
        inner,
        text=(
            "Equipped items whose dump includes the final augment row: "
            "Ear-Slot6 (and similar), Primary-Slot5. "
            "Purple overrides tier color."
        ),
        bg=_BG_PANEL,
        fg=_FG_MUTED,
        font=("Segoe UI", 9),
        wraplength=440,
        justify=tk.LEFT,
    ).pack(anchor="w", padx=(0, 0), pady=(0, 8))

    for gear_set in GEAR_SETS_NEWEST_FIRST:
        add_legend_row(inner, GEAR_SET_FILLS[gear_set.key], gear_set.label)

    notes = (
        "Unlisted items (e.g. Legacies Lost, Selenelion) have no tier color in Excel.\n\n"
        "Excel legend: Crew gear sheet, A26–A35 (Evolver + gear tiers).\n\n"
        "Item names link to EQ Resource using the ID from your inventory dump."
    )
    tk.Label(
        outer,
        text=notes,
        bg=_BG,
        fg=_FG_MUTED,
        font=("Segoe UI", 9),
        wraplength=460,
        justify=tk.LEFT,
    ).pack(anchor="w", pady=(12, 8))

    tk.Label(
        outer,
        text="Visible vs non-visible slots",
        bg=_BG,
        fg=_ACCENT_SLOTS,
        font=("Segoe UI", 11, "bold"),
    ).pack(anchor="w", pady=(4, 4))

    vis_text = (
        "Visible (on character model):\n  "
        + ", ".join(VISIBLE_SLOTS)
        + "\n\nNon-visible:\n  "
        + ", ".join(NON_VISIBLE_SLOTS)
        + "\n\nUse the Visibility column in Excel to filter, or Slots → visible / non_visible when exporting."
    )
    tk.Label(
        outer,
        text=vis_text,
        bg=_BG,
        fg=_FG,
        font=("Segoe UI", 9),
        wraplength=460,
        justify=tk.LEFT,
    ).pack(anchor="w")

    ttk.Button(outer, text="Close", command=win.destroy).pack(anchor="e", pady=(14, 0))

    win.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - win.winfo_width()) // 2
    y = parent.winfo_y() + (parent.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{max(x, 0)}+{max(y, 0)}")


def _show_folder_character_picker(
    parent: tk.Tk,
    folder: Path,
    choices: list[FolderCharacterChoice],
) -> list[FolderCharacterChoice] | None:
    """Modal checkbox dialog to pick characters from a scanned folder."""
    selected: list[FolderCharacterChoice] | None = None

    win = tk.Toplevel(parent)
    win.title("Select characters")
    win.configure(bg=_BG)
    win.transient(parent)
    win.grab_set()
    win.minsize(520, 580)
    win.geometry("560x620")

    win.columnconfigure(0, weight=1)
    win.rowconfigure(1, weight=1)

    header = tk.Frame(win, bg=_BG, padx=16, pady=14)
    header.grid(row=0, column=0, sticky="ew")
    header.columnconfigure(0, weight=1)

    tk.Label(
        header,
        text="Characters in folder",
        bg=_BG,
        fg=_ACCENT_FILES,
        font=("Segoe UI", 14, "bold"),
    ).grid(row=0, column=0, sticky="w")
    tk.Label(
        header,
        text=str(folder),
        bg=_BG,
        fg=_FG_MUTED,
        font=("Segoe UI", 9),
        wraplength=500,
        justify=tk.LEFT,
    ).grid(row=1, column=0, sticky="w", pady=(4, 4))
    tk.Label(
        header,
        text="Choose which characters to add. Spell files in SpellData are grouped with each character.",
        bg=_BG,
        fg=_FG,
        font=("Segoe UI", 9),
        wraplength=500,
        justify=tk.LEFT,
    ).grid(row=2, column=0, sticky="w")

    body = tk.Frame(win, bg=_BG, padx=16, pady=8)
    body.grid(row=1, column=0, sticky="nsew")
    body.columnconfigure(0, weight=1)
    body.rowconfigure(2, weight=1)

    servers = sorted({c.server for c in choices}, key=str.casefold)
    server_labels = {slug: server_display_name(slug) for slug in servers}
    server_filter_var = tk.StringVar(value="All servers")

    filter_panel = tk.Frame(body, bg=_ACCENT_FILES, padx=1, pady=1)
    filter_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    filter_inner = tk.Frame(filter_panel, bg=_BG_INPUT, padx=10, pady=8)
    filter_inner.pack(fill=tk.X)
    filter_inner.columnconfigure(1, weight=1)
    ttk.Label(filter_inner, text="Server", style="PickerPanel.TLabel").grid(
        row=0, column=0, sticky="w", padx=(0, 10)
    )
    server_values = ["All servers"] + [
        f"{server_labels[slug]} ({slug})" if server_labels[slug] != slug else slug
        for slug in servers
    ]
    server_combo = ttk.Combobox(
        filter_inner,
        textvariable=server_filter_var,
        values=server_values,
        state="readonly",
        width=32,
        style="Picker.TCombobox",
    )
    server_combo.grid(row=0, column=1, sticky="ew")

    tk.Label(
        body,
        text="Characters",
        bg=_BG,
        fg=_ACCENT_SLOTS,
        font=("Segoe UI", 10, "bold"),
    ).grid(row=1, column=0, sticky="w", pady=(0, 6))

    list_shell = tk.Frame(body, bg=_ACCENT_SLOTS, padx=1, pady=1)
    list_shell.grid(row=2, column=0, sticky="nsew")
    list_shell.columnconfigure(0, weight=1)
    list_shell.rowconfigure(0, weight=1)

    list_frame = tk.Frame(list_shell, bg=_BG_PANEL, padx=8, pady=8)
    list_frame.grid(row=0, column=0, sticky="nsew")
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)

    canvas = tk.Canvas(list_frame, bg=_BG_PANEL, highlightthickness=0, borderwidth=0)
    scroll = ttk.Scrollbar(
        list_frame,
        orient=tk.VERTICAL,
        command=canvas.yview,
        style="Picker.Vertical.TScrollbar",
    )
    inner = tk.Frame(canvas, bg=_BG_PANEL)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)

    def _resize_inner(event: tk.Event) -> None:
        canvas.itemconfigure(canvas_window, width=event.width)

    canvas.bind("<Configure>", _resize_inner)
    canvas.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")

    list_height = min(360, max(180, min(len(choices), 10) * 52))
    canvas.configure(height=list_height)

    def _file_summary(choice: FolderCharacterChoice) -> str:
        parts: list[str] = []
        if choice.inventory_paths:
            parts.append(
                f"{len(choice.inventory_paths)} inventory"
                if len(choice.inventory_paths) != 1
                else "1 inventory"
            )
        if choice.spell_paths:
            parts.append(
                f"{len(choice.spell_paths)} MissingSpells"
                if len(choice.spell_paths) != 1
                else "1 MissingSpells"
            )
        if choice.achievement_paths:
            parts.append(
                f"{len(choice.achievement_paths)} Achievements"
                if len(choice.achievement_paths) != 1
                else "1 Achievements"
            )
        return " · ".join(parts) if parts else "No files"

    vars_by_choice: list[tuple[FolderCharacterChoice, tk.BooleanVar]] = []
    row_frames: list[tk.Frame] = []
    for choice in choices:
        var = tk.BooleanVar(value=True)
        vars_by_choice.append((choice, var))
        row = tk.Frame(inner, bg=_BG_PANEL, pady=4)
        row.pack(fill=tk.X, anchor="w")
        row_frames.append(row)
        ttk.Checkbutton(
            row,
            text=choice.display_name,
            variable=var,
            style="Picker.TCheckbutton",
        ).pack(anchor="w")
        tk.Label(
            row,
            text=_file_summary(choice),
            bg=_BG_PANEL,
            fg=_FG_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
            justify=tk.LEFT,
        ).pack(anchor="w", padx=(22, 0))

    def _selected_server_slug() -> str | None:
        value = server_filter_var.get().strip()
        if value == "All servers":
            return None
        if value.endswith(")") and " (" in value:
            return value.rsplit(" (", 1)[1][:-1]
        return value

    def apply_server_filter(_event: tk.Event | None = None) -> None:
        slug = _selected_server_slug()
        for (choice, _var), row in zip(vars_by_choice, row_frames, strict=True):
            visible = slug is None or choice.server.casefold() == slug.casefold()
            if visible:
                row.pack(fill=tk.X, anchor="w")
            else:
                row.pack_forget()
        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    server_combo.bind("<<ComboboxSelected>>", apply_server_filter)

    def visible_choices() -> list[tuple[FolderCharacterChoice, tk.BooleanVar]]:
        slug = _selected_server_slug()
        if slug is None:
            return vars_by_choice
        return [
            (choice, var)
            for choice, var in vars_by_choice
            if choice.server.casefold() == slug.casefold()
        ]

    def set_all(value: bool) -> None:
        for _choice, var in visible_choices():
            var.set(value)

    footer_wrap = tk.Frame(win, bg=_ACCENT_FILES, padx=2, pady=2)
    footer_wrap.grid(row=2, column=0, sticky="ew")
    footer = tk.Frame(footer_wrap, bg=_BG_PANEL, padx=14, pady=12)
    footer.pack(fill=tk.X)

    btn_row = ttk.Frame(footer)
    btn_row.pack(side=tk.LEFT)
    ttk.Button(btn_row, text="Select all", command=lambda: set_all(True)).pack(side=tk.LEFT)
    ttk.Button(btn_row, text="Select none", command=lambda: set_all(False)).pack(
        side=tk.LEFT, padx=(8, 0)
    )

    def cancel() -> None:
        win.destroy()

    def confirm() -> None:
        nonlocal selected
        picked = [choice for choice, var in visible_choices() if var.get()]
        if not picked:
            messagebox.showwarning(
                "Inventory Parser",
                "Select at least one character to add.",
                parent=win,
            )
            return
        selected = picked
        win.destroy()

    action_row = ttk.Frame(footer)
    action_row.pack(side=tk.RIGHT)
    ttk.Button(action_row, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=(8, 0))
    ttk.Button(action_row, text="Add selected", style="Primary.TButton", command=confirm).pack(
        side=tk.RIGHT
    )

    win.update_idletasks()
    req_w = max(win.winfo_reqwidth(), 560)
    req_h = max(win.winfo_reqheight(), 620)
    x = parent.winfo_x() + max((parent.winfo_width() - req_w) // 2, 0)
    y = parent.winfo_y() + max((parent.winfo_height() - req_h) // 2, 0)
    win.geometry(f"{req_w}x{req_h}+{max(x, 0)}+{max(y, 0)}")
    win.wait_window()
    return selected


def _show_about(parent: tk.Tk) -> None:
    messagebox.showinfo(
        "About Inventory Parser",
        f"Inventory Parser {__version__}\n\n"
        "Build crew gear Excel workbooks from EverQuest\n"
        "/outputfile inventory and missingspells dumps.\n\n"
        "Sheets: Crew gear, Gear T-Level, Missing Runes, Spell List.",
        parent=parent,
    )


def _build_help_menu(root: tk.Tk) -> None:
    menubar = tk.Menu(root)
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(
        label="Gear tier colors…",
        command=lambda: _show_gear_tiers_help(root),
    )
    help_menu.add_separator()
    help_menu.add_command(
        label=f"About Inventory Parser {__version__}…",
        command=lambda: _show_about(root),
    )
    menubar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menubar)


def _accent_card(parent: ttk.Frame, title: str, card_key: str, **grid_kw) -> ttk.LabelFrame:
    frame_style, stripe_color = _CARD_STYLES[card_key]
    wrap = tk.Frame(parent, bg=stripe_color, padx=2, pady=2)
    wrap.grid(**grid_kw)
    inner = ttk.Frame(wrap)
    inner.pack(fill=tk.BOTH, expand=True)
    lf = ttk.LabelFrame(inner, text=f" {title} ", style=frame_style, padding=10)
    lf.pack(fill=tk.BOTH, expand=True)
    return lf


def main() -> None:
    root = tk.Tk()
    root.title(f"Inventory Parser {__version__}")
    root.minsize(680, 520)
    root.geometry("820x640")

    style = ttk.Style(root)
    _apply_theme(root, style)
    _build_help_menu(root)

    pad = {"padx": 12, "pady": 8}
    file_list: list[str] = []

    output_var = tk.StringVar(value=str(_default_output_path()))
    slots_var = tk.StringVar(value="all")

    def _refresh_output_default() -> None:
        """Set output path from inputs when empty or still using an auto-generated name."""
        prefix = default_export_prefix_from_input_paths([Path(p) for p in file_list])
        current = output_var.get().strip()
        if not current or is_auto_crew_inventory_path(current):
            output_var.set(str(_default_output_path(prefix)))
    include_spells_var = tk.BooleanVar(value=False)
    include_achievements_var = tk.BooleanVar(value=False)
    also_html_var = tk.BooleanVar(value=False)
    spells_cb_ref: list[ttk.Checkbutton] = []
    achievements_cb_ref: list[ttk.Checkbutton] = []
    status_var = tk.StringVar(value="Add inventory dump files to begin.")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frm = ttk.Frame(root, padding=16)
    frm.grid(row=0, column=0, sticky="nsew")
    frm.columnconfigure(0, weight=1)
    frm.rowconfigure(1, weight=1)

    header = ttk.Frame(frm)
    header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
    ttk.Label(header, text=f"Inventory Parser {__version__}", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        header,
        text="Crew gear workbook · color-coded tiers · EQ Resource links",
        style="Muted.TLabel",
    ).pack(anchor="w", pady=(2, 0))

    files_outer = tk.Frame(frm, bg=_ACCENT_FILES, padx=2, pady=2)
    files_outer.grid(row=1, column=0, sticky="nsew", **pad)
    files_outer.columnconfigure(0, weight=1)
    files_outer.rowconfigure(0, weight=1)

    files_inner = ttk.Frame(files_outer)
    files_inner.pack(fill=tk.BOTH, expand=True)
    files_lf = ttk.LabelFrame(
        files_inner,
        text=" Crew characters (column order) ",
        style="Files.TLabelframe",
        padding=10,
    )
    files_lf.pack(fill=tk.BOTH, expand=True)
    files_lf.columnconfigure(0, weight=1)
    files_lf.rowconfigure(0, weight=1)

    lb_frame = ttk.Frame(files_lf)
    lb_frame.grid(row=0, column=0, sticky="nsew")
    lb_frame.columnconfigure(0, weight=1)
    lb_frame.rowconfigure(0, weight=1)

    listbox = tk.Listbox(
        lb_frame,
        selectmode=tk.EXTENDED,
        activestyle="none",
        bg=_BG_INPUT,
        fg=_FG,
        selectbackground=_ACCENT_FILES,
        selectforeground="#ffffff",
        highlightthickness=1,
        highlightbackground="#454550",
        highlightcolor=_ACCENT_FILES,
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    listbox.grid(row=0, column=0, sticky="nsew")
    scroll = ttk.Scrollbar(lb_frame, orient=tk.VERTICAL, command=listbox.yview)
    scroll.grid(row=0, column=1, sticky="ns")
    listbox.configure(yscrollcommand=scroll.set)

    ttk.Label(
        files_lf,
        text="Top character = first column in Excel and HTML. Use Move up / Move down to prioritize.",
        style="Muted.TLabel",
    ).grid(row=2, column=0, sticky="w", pady=(8, 0))

    roster: list[ColumnRosterEntry] = []

    def _split_file_list() -> tuple[list[Path], list[Path], list[Path]]:
        paths = [Path(p) for p in file_list]
        return split_input_paths(paths)

    def _persona_discovery_for_list():
        inv_paths, spell_paths, _achievement_paths = _split_file_list()
        return discover_persona_bindings(inv_paths, spell_paths=spell_paths)

    def refresh_spell_checkbox() -> None:
        if not spells_cb_ref:
            return
        cb = spells_cb_ref[0]
        if not file_list:
            include_spells_var.set(False)
            cb.configure(state=tk.DISABLED)
            return
        discovery = _persona_discovery_for_list()
        cb.configure(state=tk.NORMAL)
        include_spells_var.set(any(b.spell_path for b in discovery.bindings))

    def refresh_achievement_checkbox() -> None:
        if not achievements_cb_ref:
            return
        cb = achievements_cb_ref[0]
        if not file_list:
            include_achievements_var.set(False)
            cb.configure(state=tk.DISABLED)
            return
        inv_paths, _spell_paths, achievement_paths = _split_file_list()
        discovered = collect_achievement_paths(inv_paths, achievement_paths or None)
        cb.configure(state=tk.NORMAL)
        include_achievements_var.set(bool(achievement_paths or discovered))

    def update_status() -> None:
        n = len(file_list)
        status_lbl.configure(style="Status.TLabel")
        if n == 0:
            status_var.set("Add inventory, MissingSpells, or achievement files to begin.")
            return
        inv_paths, spell_paths, achievement_paths = _split_file_list()
        parts: list[str] = []
        if inv_paths:
            parts.append(f"{len(inv_paths)} inventory")
        if spell_paths:
            parts.append(f"{len(spell_paths)} MissingSpells")
        if achievement_paths:
            parts.append(f"{len(achievement_paths)} Achievements")
        summary = ", ".join(parts) if parts else f"{n} files"
        if n == 1:
            status_var.set(f"{Path(file_list[0]).name} ({summary})")
        else:
            status_var.set(f"{n} files ({summary})")
        if include_spells_var.get():
            discovery = _persona_discovery_for_list()
            spell_bindings = [b for b in discovery.bindings if b.spell_path]
            if spell_bindings:
                label = (
                    "persona"
                    if bindings_include_personas(discovery.bindings)
                    else "character"
                )
                plural = "s" if len(spell_bindings) != 1 else ""
                status_var.set(
                    f"{status_var.get()} · {len(spell_bindings)} spell {label}{plural}"
                )
            if discovery.warnings:
                status_var.set(f"{status_var.get()} · {len(discovery.warnings)} warning(s)")
        if include_achievements_var.get():
            inv_paths, _spell_paths, achievement_paths = _split_file_list()
            discovered = collect_achievement_paths(inv_paths, achievement_paths or None)
            ach_count = len(achievement_paths) if achievement_paths else len(discovered)
            if ach_count:
                label = "achievement file" if ach_count == 1 else "achievement files"
                status_var.set(f"{status_var.get()} · {ach_count} {label}")

    def rebuild_roster(*, preserve_order: bool = True) -> None:
        nonlocal roster
        saved = saved_character_column_order() if preserve_order else [entry.persona_key for entry in roster]
        roster = build_column_roster(file_list, saved)
        refresh_listbox()

    def refresh_listbox() -> None:
        listbox.delete(0, tk.END)
        for entry in roster:
            listbox.insert(tk.END, entry.display_name)
        update_status()

    def add_paths(paths: list[str]) -> None:
        added = False
        for raw in paths:
            p = str(Path(raw).resolve())
            if p not in file_list:
                file_list.append(p)
                added = True
        if not added:
            return
        file_list.sort(key=str.casefold)
        rebuild_roster()
        refresh_spell_checkbox()
        refresh_achievement_checkbox()
        _refresh_output_default()

    def move_selected(delta: int) -> None:
        selection = listbox.curselection()
        if len(selection) != 1:
            return
        index = selection[0]
        new_index = index + delta
        if new_index < 0 or new_index >= len(roster):
            return
        roster[index], roster[new_index] = roster[new_index], roster[index]
        save_character_column_order([entry.persona_key for entry in roster])
        refresh_listbox()
        listbox.selection_set(new_index)
        listbox.see(new_index)

    def browse_files() -> None:
        paths = filedialog.askopenfilenames(
            title="Select inventory dumps, MissingSpells logs, and/or achievement files",
            filetypes=_FILE_TYPES,
        )
        if paths:
            add_paths(list(paths))

    def browse_folder() -> None:
        folder = filedialog.askdirectory(
            title="Folder with inventory dumps, MissingSpells logs, and/or achievement files"
        )
        if not folder:
            return
        folder_path = Path(folder)
        choices = discover_folder_character_choices(folder_path)
        if not choices:
            messagebox.showinfo(
                "Inventory Parser",
                f"No *-Inventory.txt, *-MissingSpells.txt, or *-Achievements.txt files found in:\n{folder}",
            )
            return
        picked = _show_folder_character_picker(root, folder_path, choices)
        if not picked:
            return
        paths: list[str] = []
        for choice in picked:
            paths.extend(str(p) for p in choice.paths)
        add_paths(paths)

    def remove_selected() -> None:
        indices = listbox.curselection()
        if not indices:
            return
        removing = [roster[index] for index in indices]
        drop_paths = paths_for_roster_removal(removing, roster, file_list)
        if drop_paths:
            file_list[:] = [path for path in file_list if path not in drop_paths]
        rebuild_roster()
        _refresh_output_default()

    def clear_all() -> None:
        if not file_list:
            return
        if messagebox.askyesno("Inventory Parser", "Remove all characters from the list?"):
            file_list.clear()
            rebuild_roster()
            _refresh_output_default()

    btn_row = ttk.Frame(files_lf)
    btn_row.grid(row=1, column=0, sticky="ew", pady=(10, 0))
    add_files_btn = ttk.Button(btn_row, text="Add files…", style="Primary.TButton", command=browse_files)
    add_files_btn.pack(side=tk.LEFT, padx=(0, 8))
    add_folder_btn = ttk.Button(
        btn_row, text="Add folder…", style="Secondary.TButton", command=browse_folder
    )
    add_folder_btn.pack(side=tk.LEFT, padx=(0, 8))
    remove_btn = ttk.Button(btn_row, text="Remove selected", command=remove_selected)
    remove_btn.pack(side=tk.LEFT, padx=(0, 8))
    move_up_btn = ttk.Button(btn_row, text="Move up", command=lambda: move_selected(-1))
    move_up_btn.pack(side=tk.LEFT, padx=(0, 8))
    move_down_btn = ttk.Button(btn_row, text="Move down", command=lambda: move_selected(1))
    move_down_btn.pack(side=tk.LEFT, padx=(0, 8))
    clear_btn = ttk.Button(btn_row, text="Clear all", style="Danger.TButton", command=clear_all)
    clear_btn.pack(side=tk.LEFT)
    file_action_buttons = (
        add_files_btn,
        add_folder_btn,
        remove_btn,
        move_up_btn,
        move_down_btn,
        clear_btn,
    )

    options = ttk.Frame(frm)
    options.grid(row=2, column=0, sticky="ew", pady=(4, 0))
    options.columnconfigure(1, weight=1)

    slots_lf = _accent_card(options, "Slots", "slots", row=0, column=0, sticky="nsw", padx=(0, 10))
    ttk.Label(slots_lf, text="Include", style="Panel.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
    ttk.Combobox(
        slots_lf,
        textvariable=slots_var,
        values=("all", "visible", "non_visible"),
        state="readonly",
        width=16,
    ).grid(row=0, column=1, sticky="w")
    ttk.Label(
        slots_lf,
        text="Visible = model slots first in sheet",
        style="Panel.TLabel",
    ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

    spells_cb = ttk.Checkbutton(
        slots_lf,
        text="Include missing spells (Rk. III runes)",
        variable=include_spells_var,
        command=update_status,
    )
    spells_cb.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))
    spells_cb.configure(state=tk.DISABLED)
    spells_cb_ref.append(spells_cb)

    achievements_cb = ttk.Checkbutton(
        slots_lf,
        text="Include achievements (collections & summary)",
        variable=include_achievements_var,
        command=update_status,
    )
    achievements_cb.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
    achievements_cb.configure(state=tk.DISABLED)
    achievements_cb_ref.append(achievements_cb)

    html_cb = ttk.Checkbutton(
        slots_lf,
        text="Also generate HTML report",
        variable=also_html_var,
    )
    html_cb.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

    out_lf = _accent_card(options, "Output", "output", row=0, column=1, sticky="ew")
    out_lf.columnconfigure(1, weight=1)

    def browse_output() -> None:
        p = filedialog.asksaveasfilename(
            title="Save Excel workbook",
            defaultextension=".xlsx",
            initialdir=str(_downloads_dir()),
            initialfile=crew_inventory_filename(
                default_export_prefix_from_input_paths([Path(p) for p in file_list])
            ),
            filetypes=[("Excel workbook", "*.xlsx"), ("All files", "*.*")],
        )
        if p:
            output_var.set(p)

    ttk.Label(out_lf, text="Excel file", style="Panel.TLabel").grid(
        row=0, column=0, sticky="w", padx=(0, 8)
    )
    ttk.Entry(out_lf, textvariable=output_var).grid(row=0, column=1, sticky="ew")
    ttk.Button(out_lf, text="Browse…", style="Secondary.TButton", command=browse_output).grid(
        row=0, column=2, padx=(8, 0)
    )

    action_wrap = tk.Frame(frm, bg=_ACCENT_EXCEL, padx=0, pady=2)
    action_wrap.grid(row=3, column=0, sticky="ew", pady=(12, 0))
    action_bar = tk.Frame(action_wrap, bg=_BG_PANEL, padx=14, pady=12)
    action_bar.pack(fill=tk.X)
    action_bar.columnconfigure(0, weight=1)

    status_lbl = ttk.Label(action_bar, textvariable=status_var, style="Status.TLabel")
    status_lbl.grid(row=0, column=0, sticky="w")

    def run_export() -> None:
        paths = [Path(p) for p in file_list]
        out = output_var.get().strip()
        inv_paths, _spell_paths, _achievement_paths = split_input_paths(paths)
        if not inv_paths:
            messagebox.showwarning(
                "Inventory Parser",
                "Add at least one *-Inventory.txt file (MissingSpells alone is not enough).",
            )
            return
        if not out:
            messagebox.showwarning("Inventory Parser", "Choose where to save the Excel file.")
            return

        gen_btn.configure(state=tk.DISABLED)
        for btn in file_action_buttons:
            btn.configure(state=tk.DISABLED)
        status_lbl.configure(style="Status.TLabel")
        status_var.set(
            "Building workbook and HTML…"
            if also_html_var.get()
            else "Building workbook…"
        )

        def work() -> None:
            try:
                raw_slots = slots_var.get().strip() or "all"
                slot_filter: SlotFilter = (
                    raw_slots if raw_slots in ("all", "visible", "non_visible") else "all"
                )
                saved, warnings, html_saved = generate_workbook(
                    paths,
                    Path(out),
                    slot_filter=slot_filter,
                    include_spells=include_spells_var.get(),
                    include_achievements=include_achievements_var.get(),
                    also_html=also_html_var.get(),
                    character_column_order=[entry.persona_key for entry in roster],
                )
                msg = f"Saved:\n{saved}"
                if html_saved is not None:
                    msg += f"\n{html_saved}"
                if warnings:
                    msg += "\n\n" + "\n".join(warnings)

                def done_ok() -> None:
                    status_lbl.configure(style="StatusOk.TLabel")
                    status_var.set(f"Done — {saved.name}")
                    messagebox.showinfo(f"Inventory Parser {__version__}", msg)
                    gen_btn.configure(state=tk.NORMAL)
                    for btn in file_action_buttons:
                        btn.configure(state=tk.NORMAL)

                root.after(0, done_ok)
            except Exception:
                err = traceback.format_exc()

                def done_err() -> None:
                    status_lbl.configure(style="Status.TLabel")
                    status_var.set("Export failed.")
                    messagebox.showerror("Inventory Parser", err)
                    gen_btn.configure(state=tk.NORMAL)
                    for btn in file_action_buttons:
                        btn.configure(state=tk.NORMAL)

                root.after(0, done_err)

        threading.Thread(target=work, daemon=True).start()

    gen_btn = ttk.Button(
        action_bar,
        text="  Generate Excel  ",
        style="Accent.TButton",
        command=run_export,
    )
    gen_btn.grid(row=0, column=1, sticky="e", padx=(12, 0))

    root.mainloop()


if __name__ == "__main__":
    main()
