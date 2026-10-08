/* Felles hjelpere for AI-funksjonene i api/. Filer som starter med _ blir ikke egne adresser på Vercel. */
import Anthropic from "@anthropic-ai/sdk";

// Offentlige verdier (de samme som i index.html). Tilgang styres av innlogging og RLS.
export const SUPABASE_URL = "https://zgflofmkcuvgaehsfixe.supabase.co";
export const SUPABASE_KEY = "sb_publishable_jYWPoa076ydyD_OxsGerWA_AIQ5zXUk";
export const MODEL = "claude-haiku-4-5";

export const json = (status, body) => new Response(JSON.stringify(body), {
  status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }
});
export const str = (v, max) => (typeof v === "string" ? v.trim().slice(0, max) : "");
export const uniq = a => [...new Set(a)];
export const bearer = request => (request.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");

// Er brukeren logget inn og på teamets liste? Spør databasen med brukerens egen innlogging.
export async function isMember(token) {
  if (!token) return false;
  try {
    const r = await fetch(`${SUPABASE_URL}/rest/v1/rpc/am_i_member`, {
      method: "POST",
      headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: "{}"
    });
    return r.ok && (await r.json()) === true;
  } catch {
    return false;
  }
}

// Leser alle oppføringer med brukerens egen innlogging (RLS gjelder som i appen)
export async function loadDocs(token) {
  const r = await fetch(`${SUPABASE_URL}/rest/v1/docs?select=coll,id,data&order=coll,id&limit=10000`, {
    headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("docs " + r.status);
  return r.json();
}

export function newClient() {
  try { return new Anthropic(); } catch { return null; }
}

// Gjør feil fra Claude om til korte meldinger på norsk. Logger bare feiltypen, aldri innhold.
export function aiError(e, where) {
  console.error(where + ":", e && e.constructor && e.constructor.name, e && e.status);
  if (e instanceof Anthropic.RateLimitError) return json(429, { error: "AI-en har for mye å gjøre akkurat nå. Vent litt og prøv igjen." });
  if (e instanceof Anthropic.AuthenticationError) return json(500, { error: "AI-nøkkelen i Vercel er ugyldig." });
  if (e instanceof Anthropic.APIConnectionError) return json(502, { error: "Fikk ikke kontakt med AI-tjenesten. Prøv igjen." });
  return json(502, { error: "Noe gikk galt med AI-en. Prøv igjen." });
}
export const NO_KEY = () => json(500, { error: "AI er ikke satt opp: mangler API-nøkkel (ANTHROPIC_API_KEY) i Vercel." });
