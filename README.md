# Arvklart Kontrollsenter

Gruppe 6 sitt felles dashbord i STR466 Venture Creation (høst 2026): oppgaver, milepæler, områder, kontakter, kunnskap og økonomi.

## Slik henger det sammen

- **Nettsiden** er én fil, `index.html` (HTML, CSS og JavaScript, uten rammeverk).
- **Vercel** publiserer siden automatisk når noe pushes til `main`.
- **Supabase** (prosjektet «Arvklart Kontrollsenter») lagrer data og filer:
  - Tabellen `docs` har alle data, én rad per oppføring (`coll` = samling, `id`, `data` = innholdet).
  - Bøtta `files` har opplastede vedlegg. Den er privat, og filer åpnes med lenker som varer i fem minutter.
  - Tabellen `allowed_users` er listen over hvem som kan logge inn. Bare e-postadresser på listen kan lage konto, lese og skrive.
- **Innlogging** skjer med en lenke på e-post (ingen passord).

Den offentlige Supabase-nøkkelen i `index.html` er laget for å ligge i nettleseren. Tilgangen styres av innloggingen og RLS-reglene i databasen. Hemmelige nøkler (for eksempel `ANTHROPIC_API_KEY`) skal bare ligge som miljøvariabler i Vercel, aldri i koden.

## Gi en ny person tilgang

Supabase → Table Editor → `allowed_users` → legg til e-postadressen med små bokstaver.

## Databaseoppsett

SQL-en som er kjørt ligger i `supabase/migrations/`.
