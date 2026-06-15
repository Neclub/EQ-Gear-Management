/* Inventory Parser — HTML setup page */

const state = {
  filePaths: [],
  roster: [],
  selectedRoster: new Set(),
  includeSpells: false,
  includeAchievements: false,
  alsoHtml: true,
  generating: false,
};

const $ = (id) => document.getElementById(id);

function api(method, ...args) {
  if (!window.pywebview || !pywebview.api || !pywebview.api[method]) {
    return Promise.reject(new Error("App API not available."));
  }
  return Promise.resolve(pywebview.api[method](...args));
}

function showToast(message, isError = false) {
  const el = $("toast");
  el.textContent = message;
  el.classList.toggle("error", isError);
  el.classList.remove("hidden");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => el.classList.add("hidden"), 6000);
}

function showModal(html) {
  $("modalRoot").innerHTML = `<div class="modal-backdrop" id="modalBackdrop">${html}</div>`;
  const backdrop = $("modalBackdrop");
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) closeModal();
  });
}

function closeModal() {
  $("modalRoot").innerHTML = "";
}

function toggleChip(el, on) {
  el.classList.toggle("on", on);
}

async function initApp() {
  try {
    const info = await api("get_version");
    $("versionBadge").textContent = `v${info.version}`;
    if (info.logoDataUri) $("logo").src = info.logoDataUri;
  } catch (_) {
    $("versionBadge").textContent = "";
  }
  bindEvents();
  refreshUI();
}

function bindEvents() {
  $("helpBtn").addEventListener("click", (e) => {
    e.stopPropagation();
    $("helpMenu").classList.toggle("hidden");
  });
  document.addEventListener("click", () => $("helpMenu").classList.add("hidden"));
  $("helpMenu").addEventListener("click", (e) => e.stopPropagation());

  $("helpTiers").addEventListener("click", () => {
    $("helpMenu").classList.add("hidden");
    showHelpTiers();
  });
  $("helpAbout").addEventListener("click", async () => {
    $("helpMenu").classList.add("hidden");
    const info = await api("get_version");
    showModal(`
      <div class="modal">
        <div class="modal-header"><h2>About Inventory Parser</h2></div>
        <div class="modal-body">
          <p>Version ${info.version}</p>
          <p style="margin-top:12px;color:var(--muted);font-size:12px">
            Builds team Excel workbooks and optional HTML reports from EverQuest
            /outputfile inventory, spell, and achievement dumps.
          </p>
          <p style="margin-top:8px;font-size:12px">Sheets: Team Gear, Gear T-Level, Missing Runes,
          Missing Spells, Rune Inventory, Unmade Gear, achievements, and more.</p>
        </div>
        <div class="modal-footer"><button type="button" class="btn" id="modalClose">Close</button></div>
      </div>`);
    $("modalClose").addEventListener("click", closeModal);
  });

  $("btnFolder").addEventListener("click", browseFolder);
  $("btnUp").addEventListener("click", () => moveRoster(-1));
  $("btnDown").addEventListener("click", () => moveRoster(1));
  $("btnRemove").addEventListener("click", removeSelected);
  $("btnClear").addEventListener("click", clearAll);
  $("btnBrowse").addEventListener("click", browseOutput);
  $("btnGenerate").addEventListener("click", generateReport);

  $("chipSpells").addEventListener("click", () => {
    if ($("chipSpells").disabled) return;
    state.includeSpells = !state.includeSpells;
    toggleChip($("chipSpells"), state.includeSpells);
    updateStatus();
  });
  $("chipAchievements").addEventListener("click", () => {
    if ($("chipAchievements").disabled) return;
    state.includeAchievements = !state.includeAchievements;
    toggleChip($("chipAchievements"), state.includeAchievements);
    updateStatus();
  });
  $("chipHtml").addEventListener("click", () => {
    state.alsoHtml = !state.alsoHtml;
    toggleChip($("chipHtml"), state.alsoHtml);
  });
}

async function browseFolder() {
  try {
    const folder = await api("pick_folder");
    if (!folder) return;
    const data = await api("discover_folder_choices", folder);
    if (!data.choices.length) {
      showToast(`No inventory, spell, or achievement files found in:\n${folder}`, true);
      return;
    }
    showFolderPicker(data);
  } catch (err) {
    showToast(String(err), true);
  }
}

function showFolderPicker(data) {
  const serverOptions = ['<option value="">All servers</option>']
    .concat(data.servers.map((s) => `<option value="${escapeAttr(s.slug)}">${escapeHtml(s.label)} (${escapeHtml(s.slug)})</option>`))
    .join("");

  const rows = data.choices.map((c, i) => `
    <label class="picker-item" data-server="${escapeAttr(c.server)}" data-index="${i}">
      <input type="checkbox" checked data-index="${i}">
      <div class="picker-body">
        <div class="char-card-host" data-choice-index="${i}"></div>
        ${c.summary ? `<div class="picker-summary">${escapeHtml(c.summary)}</div>` : ""}
      </div>
    </label>`).join("");

  showModal(`
    <div class="modal wide">
      <div class="modal-header">
        <h2>Characters in folder</h2>
        <div class="path">${escapeHtml(data.folder)}</div>
        <p style="margin:8px 0 0;font-size:12px;color:var(--muted)">Choose which characters to add. Spell files in SpellData are grouped with each character.</p>
      </div>
      <div class="modal-body">
        <div class="picker-filter">
          <div class="field-label">Server</div>
          <select id="pickerServer">${serverOptions}</select>
        </div>
        <div class="field-label">Characters</div>
        <div class="picker-list" id="pickerList">${rows}</div>
        <div class="toolbar" style="margin-top:10px">
          <button type="button" class="btn btn-secondary" id="pickerAll">Select all</button>
          <button type="button" class="btn btn-secondary" id="pickerNone">Select none</button>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" id="pickerCancel">Cancel</button>
        <button type="button" class="btn btn-primary" id="pickerAdd">Add selected</button>
      </div>
    </div>`);

  data.choices.forEach((c, i) => {
    const host = document.querySelector(`.char-card-host[data-choice-index="${i}"]`);
    if (!host) return;
    host.appendChild(
      ClassVisuals.createCard({
        character: c.character,
        classAbbr: c.classAbbr,
        server: c.server,
        serverDisplay: c.serverDisplay,
      })
    );
  });

  const visiblePickerItems = () =>
    Array.from(document.querySelectorAll(".picker-item:not(.hidden-row)"));

  const filterRows = () => {
    const slug = $("pickerServer").value;
    document.querySelectorAll(".picker-item").forEach((row) => {
      const match = !slug || row.dataset.server.toLowerCase() === slug.toLowerCase();
      row.classList.toggle("hidden-row", !match);
    });
  };
  $("pickerServer").addEventListener("change", filterRows);

  $("pickerAll").addEventListener("click", () => {
    visiblePickerItems().forEach((row) => {
      row.querySelector("input").checked = true;
    });
  });
  $("pickerNone").addEventListener("click", () => {
    visiblePickerItems().forEach((row) => {
      row.querySelector("input").checked = false;
    });
  });
  $("pickerCancel").addEventListener("click", closeModal);
  $("pickerAdd").addEventListener("click", () => {
    const selected = [];
    visiblePickerItems().forEach((row) => {
      const cb = row.querySelector("input");
      if (!cb || !cb.checked) return;
      const idx = Number(cb.dataset.index);
      selected.push(data.choices[idx]);
    });
    if (!selected.length) {
      showToast("Select at least one character.", true);
      return;
    }
    const newPaths = [];
    selected.forEach((c) => newPaths.push(...c.paths));
    addPaths(newPaths);
    closeModal();
  });
}

async function addPaths(paths) {
  let added = false;
  for (const raw of paths) {
    if (!state.filePaths.includes(raw)) {
      state.filePaths.push(raw);
      added = true;
    }
  }
  if (!added) return;
  state.filePaths.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base" }));
  await rebuildRoster();
  await refreshToggles();
  await refreshOutputDefault();
  refreshUI();
}

async function rebuildRoster() {
  if (!state.filePaths.length) {
    state.roster = [];
    return;
  }
  state.roster = await api("build_roster", state.filePaths);
}

async function refreshToggles() {
  const spellsBtn = $("chipSpells");
  const achBtn = $("chipAchievements");
  if (!state.filePaths.length) {
    state.includeSpells = false;
    state.includeAchievements = false;
    spellsBtn.disabled = true;
    achBtn.disabled = true;
    toggleChip(spellsBtn, false);
    toggleChip(achBtn, false);
    return;
  }
  const spellInfo = await api("spell_bindings", state.filePaths);
  const achInfo = await api("achievement_info", state.filePaths);
  spellsBtn.disabled = false;
  achBtn.disabled = false;
  state.includeSpells = spellInfo.hasSpells;
  state.includeAchievements = achInfo.hasAchievements;
  toggleChip(spellsBtn, state.includeSpells);
  toggleChip(achBtn, state.includeAchievements);
}

async function refreshOutputDefault() {
  const current = $("outputPath").value;
  const next = await api("default_output_path", state.filePaths, current);
  $("outputPath").value = next;
}

function renderRoster() {
  const list = $("rosterList");
  list.innerHTML = "";
  const servers = new Set(state.roster.map((e) => (e.server || "").toLowerCase()));
  const showServer = servers.size > 1;
  state.roster.forEach((entry, idx) => {
    const li = document.createElement("li");
    li.className = "roster-item";
    li.dataset.index = String(idx);
    if (state.selectedRoster.has(idx)) li.classList.add("selected");
    li.appendChild(
      ClassVisuals.createCard({
        character: entry.character,
        classAbbr: entry.classAbbr,
        server: showServer ? entry.server : null,
      })
    );
    li.addEventListener("click", (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (state.selectedRoster.has(idx)) state.selectedRoster.delete(idx);
        else state.selectedRoster.add(idx);
      } else {
        state.selectedRoster.clear();
        state.selectedRoster.add(idx);
      }
      renderRoster();
    });
    list.appendChild(li);
  });
  $("emptyState").classList.toggle("hidden", state.roster.length > 0);
}

async function moveRoster(delta) {
  if (state.selectedRoster.size !== 1) return;
  const index = [...state.selectedRoster][0];
  const newIndex = index + delta;
  if (newIndex < 0 || newIndex >= state.roster.length) return;
  const tmp = state.roster[index];
  state.roster[index] = state.roster[newIndex];
  state.roster[newIndex] = tmp;
  state.selectedRoster.clear();
  state.selectedRoster.add(newIndex);
  await api("save_roster_order", state.roster.map((e) => e.personaKey));
  renderRoster();
}

async function removeSelected() {
  if (!state.selectedRoster.size) return;
  const removing = [...state.selectedRoster].map((i) => state.roster[i]);
  const removingKeys = removing.map((e) => e.personaKey);
  const dropPaths = await api("paths_for_removal", removingKeys, state.roster, state.filePaths);
  state.filePaths = state.filePaths.filter((p) => !dropPaths.includes(p));
  state.selectedRoster.clear();
  await rebuildRoster();
  await refreshToggles();
  await refreshOutputDefault();
  refreshUI();
}

async function clearAll() {
  if (!state.filePaths.length) return;
  if (!confirm("Remove all characters from the list?")) return;
  state.filePaths = [];
  state.roster = [];
  state.selectedRoster.clear();
  await refreshToggles();
  refreshUI();
}

async function browseOutput() {
  try {
    const name = await api("default_output_filename", state.filePaths);
    const path = await api("pick_output_file", name);
    if (path) $("outputPath").value = path;
  } catch (err) {
    showToast(String(err), true);
  }
}

async function updateStatus() {
  const status = $("status");
  status.classList.remove("ok");
  if (!state.filePaths.length) {
    status.textContent = "Ready • No files loaded";
    return;
  }
  const split = await api("split_paths", state.filePaths);
  const parts = [];
  if (split.inventory.length) parts.push(`${split.inventory.length} inventory`);
  if (split.spells.length) parts.push(`${split.spells.length} MissingSpells`);
  if (split.achievements.length) parts.push(`${split.achievements.length} Achievements`);
  const summary = parts.join(", ") || `${state.filePaths.length} files`;
  let text = state.filePaths.length === 1
    ? `Ready • ${basename(state.filePaths[0])} (${summary})`
    : `Ready • ${state.filePaths.length} files (${summary})`;

  if (state.includeSpells) {
    const spellInfo = await api("spell_bindings", state.filePaths);
    if (spellInfo.spellCount) {
      const label = spellInfo.usePersonaLabel ? "persona" : "character";
      const plural = spellInfo.spellCount !== 1 ? "s" : "";
      text += ` • ${spellInfo.spellCount} spell ${label}${plural}`;
    }
    if (spellInfo.warnings.length) {
      text += ` • ${spellInfo.warnings.length} warning(s)`;
    }
  }
  if (state.includeAchievements) {
    const achInfo = await api("achievement_info", state.filePaths);
    if (achInfo.achievementCount) {
      const label = achInfo.achievementCount === 1 ? "achievement file" : "achievement files";
      text += ` • ${achInfo.achievementCount} ${label}`;
    }
  }
  status.textContent = text;
}

function setGenerating(on) {
  state.generating = on;
  $("btnGenerate").disabled = on;
  $("btnFolder").disabled = on;
  $("btnUp").disabled = on;
  $("btnDown").disabled = on;
  $("btnRemove").disabled = on;
  $("btnClear").disabled = on;
  $("btnBrowse").disabled = on;
}

async function generateReport() {
  if (state.generating) return;
  const outputPath = $("outputPath").value.trim();
  const split = await api("split_paths", state.filePaths);
  if (!split.inventory.length) {
    showToast("Add at least one *-Inventory.txt file (MissingSpells alone is not enough).", true);
    return;
  }
  if (!outputPath) {
    showToast("Choose where to save the Excel file.", true);
    return;
  }

  setGenerating(true);
  $("status").classList.remove("ok");
  $("status").textContent = state.alsoHtml ? "Building workbook and HTML…" : "Building workbook…";

  const config = {
    paths: state.filePaths,
    outputPath,
    slotFilter: $("slotFilter").value,
    includeSpells: state.includeSpells,
    includeAchievements: state.includeAchievements,
    alsoHtml: state.alsoHtml,
    characterColumnOrder: state.roster.map((e) => e.personaKey),
  };

  try {
    await api("generate_report", config);
  } catch (err) {
    setGenerating(false);
    showToast(String(err), true);
    $("status").textContent = "Export failed.";
  }
}

window.onGenerateComplete = async function (result) {
  setGenerating(false);
  if (!result.ok) {
    $("status").textContent = "Export failed.";
    const msg = result.traceback || result.error || "Export failed.";
    showToast(msg, true);
    return;
  }
  $("status").classList.add("ok");
  $("status").textContent = `Done — ${basename(result.xlsx)}`;

  let msg = `Saved:\n${result.xlsx}`;
  if (result.html) msg += `\n${result.html}`;
  if (result.warnings && result.warnings.length) {
    msg += "\n\n" + result.warnings.join("\n");
  }
  showToast(msg.replace(/\n/g, " • "));

  if (result.reportPayload) {
    try {
      await api("show_report", result.reportPayload);
    } catch (err) {
      showToast(`Report saved but viewer failed: ${err}`, true);
    }
  }
};

function refreshUI() {
  renderRoster();
  updateStatus();
}

async function showHelpTiers() {
  const data = await api("tier_legend");
  const rows = data.rows.map((r) => `
    <div class="legend-row">
      <div class="legend-swatch" style="background:#${r.color}"></div>
      <span>${escapeHtml(r.label)}</span>
    </div>`).join("");

  showModal(`
    <div class="modal wide">
      <div class="modal-header"><h2>Gear tier colors</h2></div>
      <div class="modal-body">
        <p style="color:var(--muted);font-size:12px;margin-top:0">Semantic tier buckets. Team Gear and Gear T-Level use the same cell colors.</p>
        ${rows}
        <p style="margin-top:12px;font-size:12px;color:var(--muted)">
          Evolver: equipped items whose dump includes the final augment row. Tier is resolved first;
          Evolver only when the item has no recognized tier pattern.
        </p>
        <p style="font-size:12px;color:var(--muted)">Unlisted items show as red (???). Item names link to EQ Resource.</p>
        <p style="margin-top:16px;font-weight:600">Visible vs non-visible slots</p>
        <p style="font-size:12px">Visible: ${data.visibleSlots.join(", ")}</p>
        <p style="font-size:12px">Non-visible: ${data.nonVisibleSlots.join(", ")}</p>
      </div>
      <div class="modal-footer"><button type="button" class="btn" id="modalClose">Close</button></div>
    </div>`);
  $("modalClose").addEventListener("click", closeModal);
}

function basename(p) {
  const parts = p.replace(/\\/g, "/").split("/");
  return parts[parts.length - 1] || p;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(s) {
  return escapeHtml(s).replace(/'/g, "&#39;");
}

window.addEventListener("pywebviewready", initApp);
if (window.pywebview) initApp();
