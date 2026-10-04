const api = globalThis.browser ?? globalThis.chrome;
(async () => {
  const s = await api.storage.local.get({ limit: 3, scope: "all", enabled: true, blocked: 0, blockedToday: 0, blockedDay: "" });
  const win = await api.windows.getCurrent();
  const tabs = await api.tabs.query(s.scope === "window" ? { windowId: win.id } : {});
  const limit = Math.max(1, parseInt(s.limit, 10) || 3);
  document.getElementById("n").textContent = tabs.length;
  document.getElementById("lim").textContent = limit;
  const slots = document.getElementById("slots");
  for (let i = 0; i < Math.min(limit, 10); i++) {
    const d = document.createElement("div");
    d.className = "slot" + (i < tabs.length ? " on" : "");
    slots.appendChild(d);
  }
  const today = s.blockedDay === new Date().toISOString().slice(0, 10) ? s.blockedToday : 0;
  document.getElementById("today").textContent = today;
  document.getElementById("total").textContent = s.blocked;
  const cb = document.getElementById("enabled");
  cb.checked = s.enabled;
  cb.onchange = () => api.storage.local.set({ enabled: cb.checked });
  document.getElementById("opts").onclick = async (e) => { e.preventDefault(); await api.storage.local.set({ allowUntil: Date.now() + 3000 }); api.runtime.openOptionsPage(); window.close(); };
})();
