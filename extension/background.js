// ThreeTabs - limit the number of open tabs. FOSS, MIT licensed.
const api = globalThis.browser ?? globalThis.chrome;

const DEFAULTS = {
  limit: 3,
  scope: "all",      // "all" = across every window, "window" = per window
  mode: "block",     // "block" = discard the new tab, "redirect" = load its URL in the tab you came from
  enabled: true,
  checkUpdates: true,
  blocked: 0,
  blockedDay: "",
  blockedToday: 0,
};

const STARTUP_GRACE_MS = 5000; // session restore opens many tabs at once; don't touch those
let graceUntil = 0; // set on browser startup only, so service-worker wake-ups never open a loophole

async function getSettings() {
  const s = await api.storage.local.get(DEFAULTS);
  s.limit = Math.max(1, Math.min(50, parseInt(s.limit, 10) || DEFAULTS.limit));
  return s;
}

async function countTabs(scope, windowId) {
  const tabs = await api.tabs.query(scope === "window" ? { windowId } : {});
  return tabs.length;
}

async function recordBlock() {
  const s = await api.storage.local.get(DEFAULTS);
  const day = new Date().toISOString().slice(0, 10);
  const today = s.blockedDay === day ? s.blockedToday : 0;
  await api.storage.local.set({ blocked: s.blocked + 1, blockedDay: day, blockedToday: today + 1 });
}

async function flash(text) {
  try {
    await api.action.setBadgeText({ text });
    await api.action.setBadgeBackgroundColor({ color: "#FF4D8D" });
    setTimeout(updateBadge, 1500);
  } catch {}
}

async function updateBadge() {
  // Intentionally number-free: a counter in the toolbar is a distraction.
  const { enabled = true } = await api.storage.local.get("enabled");
  try {
    await api.action.setBadgeText({ text: enabled ? "" : "off" });
    await api.action.setBadgeBackgroundColor({ color: "#6B6785" });
  } catch {}
}

api.tabs.onCreated.addListener(async (tab) => {
  if (Date.now() < graceUntil) return updateBadge();
  const s = await getSettings();
  if (!s.enabled) return updateBadge();

  const target = tab.pendingUrl || tab.url || "";
  if (target.startsWith(api.runtime.getURL(""))) return updateBadge(); // our own settings page is always allowed
  const { allowUntil = 0 } = await api.storage.local.get("allowUntil");
  if (Date.now() < allowUntil) return updateBadge(); // popup is opening settings

  const n = await countTabs(s.scope, tab.windowId);
  if (n <= s.limit) return updateBadge();

  try {
    if (s.mode === "redirect" && tab.openerTabId != null && /^https?:/i.test(target)) {
      await api.tabs.update(tab.openerTabId, { url: target, active: true });
    }
    await api.tabs.remove(tab.id);
  } catch {
    return updateBadge();
  }
  await recordBlock();
  flash("✕");
});

api.tabs.onRemoved.addListener(updateBadge);
api.tabs.onAttached?.addListener(updateBadge);
api.tabs.onActivated.addListener(updateBadge);
api.windows?.onFocusChanged.addListener(updateBadge);
api.storage.onChanged.addListener(updateBadge);
api.runtime.onStartup.addListener(() => { graceUntil = Date.now() + STARTUP_GRACE_MS; updateBadge(); });
api.runtime.onInstalled.addListener(updateBadge);
updateBadge();

// --- Update check (optional): compares against the latest GitHub release, at most once a day.
const RELEASES_API = "https://api.github.com/repos/mkalmousli/ThreeTabs/releases/latest";
const newer = (a, b) => {
  const x = a.split(".").map(Number), y = b.split(".").map(Number);
  for (let i = 0; i < 3; i++) if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) > (y[i] || 0);
  return false;
};
async function checkForUpdate() {
  const { checkUpdates = true } = await api.storage.local.get("checkUpdates");
  if (!checkUpdates) return api.storage.local.set({ updateAvailable: "" });
  try {
    const res = await fetch(RELEASES_API, { headers: { Accept: "application/vnd.github+json" } });
    if (!res.ok) return;
    const latest = String((await res.json()).tag_name || "").replace(/^v/, "");
    const current = api.runtime.getManifest().version;
    await api.storage.local.set({ updateAvailable: newer(latest, current) ? latest : "" });
  } catch {} // offline: try again next time
}
api.alarms.create("update-check", { delayInMinutes: 1, periodInMinutes: 24 * 60 });
api.alarms.onAlarm.addListener((a) => a.name === "update-check" && checkForUpdate());
