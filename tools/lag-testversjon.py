"""Lager «Arvklart Test» fra index.html.

Testversjonen er den samme appen, men dataene ligger i testartifactens egen
database i stedet for i Supabase. Ingenting i testversjonen påvirker den ekte
siden. Kjør:  python3 tools/lag-testversjon.py
Resultatet havner i test/arvklart-test.html (ikke i repoet).
"""
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
KILDE = ROT / "index.html"
MAL = ROT / "test" / "arvklart-test.html"

LAGRING = r'''/* ---------- TESTVERSJON (laget av tools/lag-testversjon.py) ----------
   Samme app, men dataene ligger i testartifactens egen database.
   Ingenting her påvirker den ekte siden eller Supabase. */
const BUCKET = "files";
const sb = { auth: { getSession: async () => ({ data: { session: null } }), signOut: async () => {} } };
let DB = null;
const queues = {};
function dbErr(e) {
  const code = e && e.code;
  if (code === "not_granted" || code === "permission_denied" || code === "invalid_argument") toast("Endringen ble ikke lagret. Du har bare lesetilgang til testversjonen.", true);
  else toast("Kunne ikke lagre i testversjonen. Prøv igjen om litt.", true);
  setSync("Lagringsfeil", "warn");
}
function enqueue(key, fn) {
  const prev = queues[key] || Promise.resolve();
  const next = prev.then(fn).catch(dbErr);
  queues[key] = next; return next;
}
async function must(p) { await p; }
function put(c, obj) {
  const o = clone(obj); S[c][o.id] = o;
  if (DB) { setSync("Lagrer …", ""); enqueue(c + "/" + o.id, () => DB.collection(c).doc(o.id).set(o).then(() => setSync("Testversjon · lagret", "ok"))); }
  render();
}
function del(c, id) {
  delete S[c][id];
  if (DB) enqueue(c + "/" + id, () => DB.collection(c).doc(id).delete());
  render();
}
function setSync(text, cls) { UI.sync = text; UI.syncCls = cls; const el = document.getElementById("syncline"); if (el) { el.className = "sync " + (cls || ""); el.lastChild.textContent = " " + text; } }
const docOf = (c, id, data) => { const d = Object.assign(clone(data || {}), { id }); if (c === "tasks") normTask(d); return d; };
let renderQueued = false;
function scheduleRender() { if (renderQueued) return; renderQueued = true; requestAnimationFrame(() => { renderQueued = false; render(); }); }
function subscribe() {
  for (const c of COLLS) DB.collection(c).onSnapshot(snap => {
    const m = {}; snap.docs.forEach(d => { if (!(c === "meta" && d.id === "seed")) m[d.id] = docOf(c, d.id, d.data()); });
    S[c] = m; setSync("Testversjon · lagret", "ok"); scheduleRender();
  }, () => setSync("Mistet forbindelsen – last siden på nytt", "warn"));
}
let started = false;
async function startApp() {
  if (started) return; started = true;
  document.getElementById("login").hidden = true;
  document.getElementById("app").hidden = false;
  document.getElementById("fab").hidden = false;
  setSync("Henter testdata …", "");
  route();
  let db = null;
  try { db = window.claude && window.claude.use ? await window.claude.use("db") : null; } catch (e) { db = null; }
  if (!db) { setSync("Testdatabasen er ikke tilgjengelig. Endringer lagres ikke.", "warn"); return; }
  DB = db; subscribe();
}
function showLogin() {}
function boot() { startApp(); }

/* ---------- Filer: slått av i testversjonen ---------- */
const UPLOAD_TYPES = { pdf: "application/pdf", png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp", txt: "text/plain", md: "text/markdown", csv: "text/csv", docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" };
const UPLOAD_ACCEPT = Object.keys(UPLOAD_TYPES).map(e => "." + e).join(",");
const UPLOAD_HINT = "Vedlegg virker bare på den ekte siden.";
async function uploadFile() { throw new Error("Vedlegg kan ikke lastes opp i testversjonen."); }
const fileLink = (id, name) => `<a class="linkout filelink" href="#" data-act="openFile" data-path="${esc(id)}">${esc(name || "Vedlagt fil")} ↗</a>`;

'''

AVSLUTT = r'''/* Testversjon: funksjoner som krever den ekte siden, er slått av */
A.importData = () => toast("Import er slått av i testversjonen.", true);
A.openFile = () => toast("Vedlegg kan ikke åpnes i testversjonen.", true);
A.logout = () => toast("Testversjonen har ingen innlogging.");
kbAutofill = async file => { const box = document.getElementById("ai-status"); if (!box) return; box.hidden = !file; box.className = "ai-status full"; box.textContent = "AI-utfylling virker bare på den ekte siden."; };
boot();'''

BANNER = '<div class="test-banner" role="note"><b>Testversjon</b> · endringer her påvirker ikke den ekte siden.</div>\n'
BANNER_CSS = '''.test-banner{position:sticky;top:env(safe-area-inset-top,0px);z-index:45;background:var(--ph-soft);color:#6A5016;border-bottom:1px dashed var(--ph);text-align:center;font-size:13px;padding:8px 16px}
</style>'''


def bytt(tekst, gammel, ny, antall=1):
    assert tekst.count(gammel) == antall, f"Fant ikke nøyaktig {antall} av: {gammel[:60]!r}"
    return tekst.replace(gammel, ny)


def main():
    s = KILDE.read_text(encoding="utf-8")
    # Artifacten lager selve dokumentrammen, så den fjernes her
    for linje in ['<!doctype html>\n', '<html lang="nb">\n', '<head>\n', '<meta charset="utf-8">\n',
                  '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n',
                  '<meta name="robots" content="noindex,nofollow">\n', '</head>\n', '<body>\n', '</body>\n', '</html>\n']:
        s = bytt(s, linje, "")
    s = bytt(s, "<title>Arvklart Kontrollsenter</title>", "<title>Arvklart Test</title>")
    s = bytt(s, '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.3/dist/umd/supabase.min.js"></script>\n', "")
    a = s.index("/* ---------- Supabase ----------")
    b = s.index("/* ---------- AI-utfylling ved opplasting")
    s = s[:a] + LAGRING + s[b:]
    s = bytt(s, "\nboot();\n</script>", "\n" + AVSLUTT + "\n</script>")
    s = bytt(s, "</style>", BANNER_CSS)
    s = bytt(s, '<div class="login" id="login" hidden>', BANNER + '<div class="login" id="login" hidden>')
    MAL.parent.mkdir(exist_ok=True)
    MAL.write_text(s, encoding="utf-8")
    print("Laget", MAL.relative_to(ROT))


if __name__ == "__main__":
    main()
