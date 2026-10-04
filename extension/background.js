// ThreeTabs - limit the number of open tabs. FOSS, MIT licensed.
const api = globalThis.browser ?? globalThis.chrome;

const DEFAULTS = {
  limit: 3,
  scope: "all",      // "all" = across every window, "window" = per window
  mode: "block",     // "block" = discard the new tab, "redirect" = load its URL in the tab you came from
  enabled: true,
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
  const s = await getSettings();
  if (!s.enabled) {
    await api.action.setBadgeText({ text: "off" });
    await api.action.setBadgeBackgroundColor({ color: "#6B6785" });
    return;
  }
  let win;
  try { win = await api.windows.getLastFocused(); } catch {}
  const n = await countTabs(s.scope, win?.id);
  await api.action.setBadgeText({ text: `${n}/${s.limit}` });
  await api.action.setBadgeBackgroundColor({ color: n >= s.limit ? "#FF4D8D" : "#8B5CF6" });
  try { await api.action.setBadgeTextColor?.({ color: "#FFFFFF" }); } catch {}
}

api.tabs.onCreated.addListener(async (tab) => {
  if (Date.now() < graceUntil) return updateBadge();
  const s = await getSettings();
  if (!s.enabled) return updateBadge();

  const n = await countTabs(s.scope, tab.windowId);
  if (n <= s.limit) return updateBadge();

  const target = tab.pendingUrl || tab.url || "";
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
