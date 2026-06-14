from __future__ import annotations

import traceback
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from inventory_parser import __version__
from inventory_parser.character_column_order import (
    ColumnRosterEntry,
    build_column_roster,
    paths_for_roster_removal,
    save_character_column_order,
    saved_character_column_order,
)
from inventory_parser.cli import generate_workbook
from inventory_parser.export_bundle import release_export_memory
from inventory_parser.team_report import (
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
from inventory_parser.excel_theme import tier_bucket_legend_rows
from inventory_parser.output_paths import (
    team_inventory_filename,
    team_inventory_path,
    default_export_prefix_from_input_paths,
    is_auto_team_inventory_path,
)
from inventory_parser.package_data import asset_path
from inventory_parser.pill_button import ChipToggle, PillBadge, PillButton
from inventory_parser.slots import NON_VISIBLE_SLOTS, VISIBLE_SLOTS, SlotFilter
from inventory_parser.window_chrome import bind_dark_title_bar
from inventory_parser.gui_theme import (
    ACCENT as _ACCENT,
    ACCENT_EXCEL as _ACCENT_EXCEL,
    ACCENT_FILES as _ACCENT_FILES,
    ACCENT_OUTPUT as _ACCENT_OUTPUT,
    ACCENT_SLOTS as _ACCENT_SLOTS,
    BG as _BG,
    BG_INPUT as _BG_INPUT,
    BG_PANEL as _BG_PANEL,
    BG_RECESSED as _BG_RECESSED,
    FG as _FG,
    FG_MUTED as _FG_MUTED,
    INPUT_BORDER as _INPUT_BORDER,
    PANEL_BORDER as _PANEL_BORDER,
    SCROLL_THUMB as _SCROLL_THUMB,
    SCROLL_THUMB_ACTIVE as _SCROLL_THUMB_ACTIVE,
)

def _downloads_dir() -> Path:
    return Path.home() / "Downloads"


def _default_output_path(prefix: str | None = None) -> Path:
    return team_inventory_path(_downloads_dir(), prefix)


_HEADER_ICON_PX = 44
_TITLEBAR_ICON_PX = 16


def _scaled_icon_photo(root: tk.Misc, image: Image.Image, px: int) -> ImageTk.PhotoImage:
    w, h = image.size
    scale = px / max(w, h)
    resized = image.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized, master=root)


def _apply_app_icon(root: tk.Tk) -> tk.PhotoImage | None:
    """Set window/taskbar icon and return a larger image for the header row."""
    icon_file = asset_path("eq-icon.png")
    if not icon_file.is_file():
        return None
    try:
        base = Image.open(icon_file).convert("RGBA")
    except OSError:
        return None

    refs: list[ImageTk.PhotoImage] = []
    try:
        titlebar = _scaled_icon_photo(root, base, _TITLEBAR_ICON_PX)
        refs.append(titlebar)
        root.iconphoto(True, titlebar)
    except tk.TclError:
        pass

    header = _scaled_icon_photo(root, base, _HEADER_ICON_PX)
    refs.append(header)
    root._app_icon_refs = refs  # type: ignore[attr-defined]
    base.close()
    return header


def _apply_theme(root: tk.Tk, style: ttk.Style) -> None:
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=_BG)
    style.configure(".", background=_BG, foreground=_FG, font=("Segoe UI", 10))
    style.configure("TFrame", background=_BG)
    style.configure("TLabel", background=_BG, foreground=_FG)
    style.configure("Muted.TLabel", background=_BG, foreground=_FG_MUTED)
    style.configure("Panel.TLabel", background=_BG_PANEL, foreground=_FG_MUTED, font=("Segoe UI", 9))
    style.configure("Status.TLabel", background=_BG, foreground=_FG_MUTED)
    style.configure("StatusOk.TLabel", background=_BG, foreground=_ACCENT_EXCEL)

    style.configure(
        "TEntry",
        fieldbackground=_BG_RECESSED,
        foreground=_FG,
        bordercolor=_INPUT_BORDER,
        padding=(8, 6),
    )
    style.configure(
        "TCombobox",
        fieldbackground=_BG_RECESSED,
        foreground=_FG,
        bordercolor=_INPUT_BORDER,
        padding=(8, 6),
    )
    style.configure(
        "Main.TCombobox",
        fieldbackground=_BG_RECESSED,
        foreground=_FG,
        bordercolor=_INPUT_BORDER,
        arrowcolor=_FG,
        padding=(8, 6),
    )
    style.map(
        "Main.TCombobox",
        fieldbackground=[("readonly", _BG_RECESSED)],
        bordercolor=[("focus", _ACCENT_FILES), ("readonly", _INPUT_BORDER)],
    )
    style.map("TCombobox", fieldbackground=[("readonly", _BG_RECESSED)])

    style.configure(
        "Main.Vertical.TScrollbar",
        background=_SCROLL_THUMB,
        troughcolor=_BG_RECESSED,
        bordercolor=_BG_RECESSED,
        arrowcolor=_FG,
        darkcolor=_PANEL_BORDER,
        lightcolor=_SCROLL_THUMB,
    )
    style.map(
        "Main.Vertical.TScrollbar",
        background=[("active", _SCROLL_THUMB_ACTIVE)],
        arrowcolor=[("active", "#ffffff")],
    )

    _apply_picker_theme(style)


def _apply_picker_theme(style: ttk.Style) -> None:
    """Styles for the folder character picker dialog."""
    style.configure(
        "Picker.TCombobox",
        fieldbackground=_BG_RECESSED,
        foreground=_FG,
        background=_SCROLL_THUMB,
        bordercolor=_ACCENT_FILES,
        lightcolor=_SCROLL_THUMB,
        darkcolor=_PANEL_BORDER,
        arrowsize=16,
        arrowcolor=_FG,
        padding=(8, 6),
    )
    style.map(
        "Picker.TCombobox",
        fieldbackground=[("readonly", _BG_RECESSED), ("disabled", _BG_PANEL)],
        foreground=[("readonly", _FG), ("disabled", _FG_MUTED)],
        background=[("readonly", _SCROLL_THUMB), ("active", _SCROLL_THUMB_ACTIVE)],
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
        background=_SCROLL_THUMB,
        troughcolor=_BG_RECESSED,
        bordercolor=_BG_RECESSED,
        arrowcolor=_FG,
        darkcolor=_PANEL_BORDER,
        lightcolor=_SCROLL_THUMB,
    )
    style.map(
        "Picker.Horizontal.TScrollbar",
        background=[("active", _SCROLL_THUMB_ACTIVE)],
        arrowcolor=[("active", "#ffffff")],
    )
    style.configure(
        "Picker.Vertical.TScrollbar",
        background=_SCROLL_THUMB,
        troughcolor=_BG_RECESSED,
        bordercolor=_BG_RECESSED,
        arrowcolor=_FG,
        darkcolor=_PANEL_BORDER,
        lightcolor=_SCROLL_THUMB,
    )
    style.map(
        "Picker.Vertical.TScrollbar",
        background=[("active", _SCROLL_THUMB_ACTIVE)],
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
        text="Semantic tier buckets. Team Gear and Gear T-Level use the same cell colors.",
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

    for fill, label_text in tier_bucket_legend_rows():
        add_legend_row(inner, fill.fgColor.rgb[-6:], label_text)

    tk.Label(
        inner,
        text=(
            "Evolver: equipped items whose dump includes the final augment row "
            "(Ear-Slot6, Primary-Slot5, etc.). Tier is resolved first; Evolver only "
            "when the item has no recognized tier pattern."
        ),
        bg=_BG_PANEL,
        fg=_FG_MUTED,
        font=("Segoe UI", 9),
        wraplength=440,
        justify=tk.LEFT,
    ).pack(anchor="w", padx=(0, 0), pady=(8, 0))

    notes = (
        "Unlisted items (e.g. Legacies Lost, Selenelion) show as red (???).\n\n"
        "Excel legend: Team gear sheet, A26–A30.\n\n"
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

    PillButton(outer, text="Close", command=win.destroy).pack(anchor="e", pady=(14, 0))

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
    PillButton(btn_row, text="Select all", command=lambda: set_all(True)).pack(side=tk.LEFT)
    PillButton(btn_row, text="Select none", command=lambda: set_all(False)).pack(
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
    PillButton(action_row, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=(8, 0))
    PillButton(action_row, text="Add selected", variant="primary", command=confirm).pack(
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
        "Build team gear Excel workbooks from EverQuest\n"
        "/outputfile inventory and missingspells dumps.\n\n"
        "Sheets: Team gear, Gear T-Level, Missing Runes, Missing Spells.",
        parent=parent,
    )


def _popup_help_menu(root: tk.Tk, anchor: tk.Widget) -> None:
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(
        label="Gear tier colors…",
        command=lambda: _show_gear_tiers_help(root),
    )
    menu.add_separator()
    menu.add_command(
        label=f"About Inventory Parser {__version__}…",
        command=lambda: _show_about(root),
    )
    try:
        menu.tk_popup(anchor.winfo_rootx(), anchor.winfo_rooty() + anchor.winfo_height())
    finally:
        menu.grab_release()


def _panel_card(parent: ttk.Frame, title: str, **grid_kw) -> tk.Frame:
    """Subtle bordered panel with section title."""
    wrap = tk.Frame(parent, bg=_PANEL_BORDER, padx=1, pady=1)
    wrap.grid(**grid_kw)
    inner = tk.Frame(wrap, bg=_BG_PANEL)
    inner.pack(fill=tk.BOTH, expand=True)
    title_bar = tk.Frame(inner, bg=_BG_PANEL)
    title_bar.pack(fill=tk.X, padx=12, pady=(10, 4))
    tk.Label(
        title_bar,
        text=title,
        bg=_BG_PANEL,
        fg=_ACCENT,
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor="w")
    body = tk.Frame(inner, bg=_BG_PANEL)
    body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
    return body


def main() -> None:
    root = tk.Tk()
    root.title(f"Inventory Parser v{__version__}")
    root.minsize(680, 520)
    root.geometry("820x640")

    style = ttk.Style(root)
    _apply_theme(root, style)
    bind_dark_title_bar(root, background=_BG, foreground=_FG)
    header_icon = _apply_app_icon(root)

    pad = {"padx": 12, "pady": 8}
    file_list: list[str] = []

    output_var = tk.StringVar(value=str(_default_output_path()))
    slots_var = tk.StringVar(value="all")

    def _refresh_output_default() -> None:
        """Set output path from inputs when empty or still using an auto-generated name."""
        prefix = default_export_prefix_from_input_paths([Path(p) for p in file_list])
        current = output_var.get().strip()
        if not current or is_auto_team_inventory_path(current):
            output_var.set(str(_default_output_path(prefix)))
    include_spells_var = tk.BooleanVar(value=False)
    include_achievements_var = tk.BooleanVar(value=False)
    also_html_var = tk.BooleanVar(value=True)
    spells_cb_ref: list[ChipToggle] = []
    achievements_cb_ref: list[ChipToggle] = []
    status_var = tk.StringVar(value="Ready • No files loaded")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frm = ttk.Frame(root, padding=(16, 10, 16, 16))
    frm.grid(row=0, column=0, sticky="nsew")
    frm.columnconfigure(0, weight=1)
    frm.rowconfigure(1, weight=1)

    header = tk.Frame(frm, bg=_BG)
    header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    header.columnconfigure(0, weight=1)

    header_top = tk.Frame(header, bg=_BG)
    header_top.grid(row=0, column=0, sticky="ew")
    header_top.columnconfigure(0, weight=1)

    title_row = tk.Frame(header_top, bg=_BG)
    title_row.grid(row=0, column=0, sticky="w")
    if header_icon is not None:
        tk.Label(title_row, image=header_icon, bg=_BG).pack(side=tk.LEFT, padx=(0, 12))
    else:
        tk.Label(
            title_row,
            text="EQ",
            bg=_BG_INPUT,
            fg=_ACCENT,
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=3,
        ).pack(side=tk.LEFT, padx=(0, 12))
    tk.Label(
        title_row,
        text="Inventory Parser",
        bg=_BG,
        fg=_FG,
        font=("Segoe UI", 15, "bold"),
    ).pack(side=tk.LEFT)
    PillBadge(title_row, f"v{__version__}").pack(side=tk.LEFT, padx=(10, 0))

    help_btn = tk.Label(
        header_top,
        text="Help",
        bg=_BG,
        fg=_ACCENT,
        font=("Segoe UI", 9),
        cursor="hand2",
    )
    help_btn.grid(row=0, column=1, sticky="e", padx=(8, 0))
    help_btn.bind("<Button-1>", lambda _e: _popup_help_menu(root, help_btn))
    help_btn.bind("<Enter>", lambda _e: help_btn.configure(fg=_FG))
    help_btn.bind("<Leave>", lambda _e: help_btn.configure(fg=_ACCENT))

    ttk.Label(
        header,
        text="Team gear workbook • color-coded tiers • EQ Resource links",
        style="Muted.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(6, 0), padx=(56, 0))

    files_body = _panel_card(frm, "Team characters", row=1, column=0, sticky="nsew", **pad)
    files_body.columnconfigure(0, weight=1)
    files_body.rowconfigure(0, weight=1)

    list_shell = tk.Frame(files_body, bg=_PANEL_BORDER, padx=1, pady=1)
    list_shell.grid(row=0, column=0, sticky="nsew")
    list_shell.columnconfigure(0, weight=1)
    list_shell.rowconfigure(0, weight=1)

    lb_frame = tk.Frame(list_shell, bg=_BG_RECESSED)
    lb_frame.grid(row=0, column=0, sticky="nsew")
    lb_frame.columnconfigure(0, weight=1)
    lb_frame.rowconfigure(0, weight=1)

    listbox = tk.Listbox(
        lb_frame,
        selectmode=tk.EXTENDED,
        activestyle="none",
        bg=_BG_RECESSED,
        fg=_FG,
        selectbackground=_ACCENT_FILES,
        selectforeground="#ffffff",
        highlightthickness=1,
        highlightbackground=_INPUT_BORDER,
        highlightcolor=_ACCENT_FILES,
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    listbox.grid(row=0, column=0, sticky="nsew")
    scroll = ttk.Scrollbar(
        lb_frame,
        orient=tk.VERTICAL,
        command=listbox.yview,
        style="Main.Vertical.TScrollbar",
    )
    scroll.grid(row=0, column=1, sticky="ns")
    listbox.configure(yscrollcommand=scroll.set)

    empty_state = tk.Frame(lb_frame, bg=_BG_RECESSED)
    empty_state.grid(row=0, column=0, columnspan=2, sticky="nsew")
    empty_state.columnconfigure(0, weight=1)
    empty_state.rowconfigure(0, weight=1)
    empty_inner = tk.Frame(empty_state, bg=_BG_RECESSED)
    empty_inner.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(
        empty_inner,
        text="📁",
        bg=_BG_RECESSED,
        fg=_FG_MUTED,
        font=("Segoe UI", 28),
    ).pack()
    tk.Label(
        empty_inner,
        text="Add inventory dump files to begin",
        bg=_BG_RECESSED,
        fg=_FG_MUTED,
        font=("Segoe UI", 10),
    ).pack(pady=(8, 0))

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
            status_var.set("Ready • No files loaded")
            empty_state.grid()
            return
        empty_state.grid_remove()
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
            status_var.set(f"Ready • {Path(file_list[0]).name} ({summary})")
        else:
            status_var.set(f"Ready • {n} files ({summary})")
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
                    f"{status_var.get()} • {len(spell_bindings)} spell {label}{plural}"
                )
            if discovery.warnings:
                status_var.set(f"{status_var.get()} • {len(discovery.warnings)} warning(s)")
        if include_achievements_var.get():
            inv_paths, _spell_paths, achievement_paths = _split_file_list()
            discovered = collect_achievement_paths(inv_paths, achievement_paths or None)
            ach_count = len(achievement_paths) if achievement_paths else len(discovered)
            if ach_count:
                label = "achievement file" if ach_count == 1 else "achievement files"
                status_var.set(f"{status_var.get()} • {ach_count} {label}")

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

    btn_col = tk.Frame(files_body, bg=_BG_PANEL, width=138)
    btn_col.grid(row=0, column=1, sticky="ns", padx=(12, 0))
    btn_col.grid_propagate(False)

    _btn_w = 130

    eq_folder_btn = PillButton(
        btn_col,
        text="EQ Folder",
        icon="📁",
        variant="primary",
        command=browse_folder,
        width=_btn_w,
    )
    eq_folder_btn.pack(fill=tk.X, pady=(0, 10))

    util_grid = tk.Frame(btn_col, bg=_BG_PANEL)
    util_grid.pack(fill=tk.X)
    util_grid.columnconfigure(0, weight=1)
    util_grid.columnconfigure(1, weight=1)

    _ghost_w = 62
    move_up_btn = PillButton(
        util_grid, text="Up", icon="↑", variant="ghost", command=lambda: move_selected(-1), width=_ghost_w
    )
    move_up_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 4))
    remove_btn = PillButton(
        util_grid, text="Remove", icon="⊖", variant="ghost", command=remove_selected, width=_ghost_w
    )
    remove_btn.grid(row=0, column=1, sticky="ew", pady=(0, 4))
    move_down_btn = PillButton(
        util_grid, text="Down", icon="↓", variant="ghost", command=lambda: move_selected(1), width=_ghost_w
    )
    move_down_btn.grid(row=1, column=0, sticky="ew", padx=(0, 4))
    clear_btn = PillButton(
        util_grid, text="Clear", icon="🗑", variant="ghost", command=clear_all, width=_ghost_w
    )
    clear_btn.grid(row=1, column=1, sticky="ew")
    file_action_buttons = (
        eq_folder_btn,
        remove_btn,
        move_up_btn,
        move_down_btn,
        clear_btn,
    )

    options = ttk.Frame(frm)
    options.grid(row=2, column=0, sticky="ew", pady=(8, 0))
    options.columnconfigure(0, weight=1)
    options.columnconfigure(1, weight=1)

    slots_body = _panel_card(options, "Slots", row=0, column=0, sticky="nsew", padx=(0, 6))
    slots_body.columnconfigure(0, weight=1)
    ttk.Combobox(
        slots_body,
        textvariable=slots_var,
        values=("all", "visible", "non_visible"),
        state="readonly",
        style="Main.TCombobox",
    ).grid(row=0, column=0, sticky="ew", ipady=2)

    chips_row = tk.Frame(slots_body, bg=_BG_PANEL)
    chips_row.grid(row=1, column=0, sticky="w", pady=(10, 0))

    spells_chip = ChipToggle(
        chips_row,
        "Spells",
        include_spells_var,
        icon="★",
        command=update_status,
    )
    spells_chip.pack(side=tk.LEFT, padx=(0, 6))
    spells_chip.configure(state=tk.DISABLED)
    spells_cb_ref.append(spells_chip)

    achievements_chip = ChipToggle(
        chips_row,
        "Achievements",
        include_achievements_var,
        icon="🏆",
        command=update_status,
    )
    achievements_chip.pack(side=tk.LEFT, padx=(0, 6))
    achievements_chip.configure(state=tk.DISABLED)
    achievements_cb_ref.append(achievements_chip)

    ChipToggle(chips_row, "HTML", also_html_var, icon="</>").pack(side=tk.LEFT)

    out_body = _panel_card(options, "Output Folder", row=0, column=1, sticky="nsew", padx=(6, 0))
    out_body.columnconfigure(0, weight=1)

    def browse_output() -> None:
        p = filedialog.asksaveasfilename(
            title="Save Excel workbook",
            defaultextension=".xlsx",
            initialdir=str(_downloads_dir()),
            initialfile=team_inventory_filename(
                default_export_prefix_from_input_paths([Path(p) for p in file_list])
            ),
            filetypes=[("Excel workbook", "*.xlsx"), ("All files", "*.*")],
        )
        if p:
            output_var.set(p)

    ttk.Entry(out_body, textvariable=output_var, style="TEntry").grid(row=0, column=0, sticky="ew", ipady=4)
    PillButton(out_body, text="Browse…", variant="secondary", command=browse_output).grid(
        row=0, column=1, padx=(8, 0)
    )

    action_bar = tk.Frame(frm, bg=_BG, padx=14, pady=12)
    action_bar.grid(row=3, column=0, sticky="ew", pady=(12, 0))
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
            finally:
                release_export_memory()

        threading.Thread(target=work, daemon=True).start()

    gen_btn = PillButton(
        action_bar,
        text="Generate Report",
        variant="accent",
        command=run_export,
    )
    gen_btn.grid(row=0, column=1, sticky="e", padx=(12, 0))

    root.mainloop()


if __name__ == "__main__":
    main()
