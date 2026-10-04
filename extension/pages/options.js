const api = globalThis.browser ?? globalThis.chrome;
const $ = (id) => document.getElementById(id);
const DEF = { limit: 3, scope: "all", mode: "block", enabled: true };
let t;
function saved() { $("saved").textContent = "Saved ✓"; clearTimeout(t); t = setTimeout(() => ($("saved").textContent = ""), 1200); }
function setLimit(v) {
  v = Math.max(1, Math.min(50, parseInt(v, 10) || 3));
  $("limit").value = v;
  api.storage.local.set({ limit: v }).then(saved);
}
(async () => {
  const s = await api.storage.local.get(DEF);
  $("limit").value = s.limit; $("scope").value = s.scope; $("mode").value = s.mode; $("enabled").checked = s.enabled;
  $("limit").onchange = () => setLimit($("limit").value);
  $("minus").onclick = () => setLimit(+$("limit").value - 1);
  $("plus").onclick = () => setLimit(+$("limit").value + 1);
  $("scope").onchange = () => api.storage.local.set({ scope: $("scope").value }).then(saved);
  $("mode").onchange = () => api.storage.local.set({ mode: $("mode").value }).then(saved);
  $("enabled").onchange = () => api.storage.local.set({ enabled: $("enabled").checked }).then(saved);
})();
