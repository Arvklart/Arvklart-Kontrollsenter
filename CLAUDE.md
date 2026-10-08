# Arvklart Kontrollsenter – regler for Claude Code

Arvklart er Gruppe 6 sin venture i NHH-kurset STR466 Venture Creation (høst 2026): en norsk digital plattform for rettferdig og åpen fordeling av løsøre i arveoppgjør. Teamet er Andrea, Bård, Julie og Ørjan. Dette repoet er teamets felles dashbord («Arvklart Kontrollsenter»).

Brukerne er ikke tekniske. Forklar kort og med enkle ord på norsk hva du gjør etter hvert steg, og spør hvis noe er uklart.

## Oppsett

- `index.html` er hele appen (HTML, CSS og JavaScript, uten rammeverk og byggesteg).
- **Vercel** publiserer automatisk ved push til `main`: https://arvklart-kontrollsenter.vercel.app
- **GitHub:** https://github.com/Arvklart/Arvklart-Kontrollsenter
- **Supabase:** bruk KUN prosjektet «Arvklart Kontrollsenter» (`zgflofmkcuvgaehsfixe`). Ikke rør hovedprosjektet («admin@arvklart.no's Project», `tfnneryybolaolyaurdn`), og ikke slett eller endre noe der.
  - `public.docs`: alle data, én rad per oppføring (`coll`, `id`, `data` jsonb). Sanntid er på.
  - `public.allowed_users`: e-postadressene som kan logge inn. RLS uten policyer, med vilje.
  - Bøtta `files`: private vedlegg, åpnes med signerte lenker.
  - SQL som er kjørt ligger i `supabase/migrations/`. Legg nye migreringer der også.
- Innlogging skjer med e-postlenke (Supabase Auth). En trigger på `auth.users` stopper e-postadresser som ikke står i `allowed_users`.

## Slik jobber vi med endringer

1. Hent siste versjon (`git pull`) før du endrer noe.
2. **Små endringer** (tekst, farger, små justeringer): test lokalt og push rett til `main`.
3. **Større endringer** (nye funksjoner, nye sider, endret datastruktur, AI-funksjoner): lag en egen gren og push den. Gi brukeren testlenken Vercel lager, og vent på godkjenning før du slår den inn i `main`.
4. Test før du publiserer: syntakssjekk av scriptet, og se på siden i nettleseren (også i mobilbredde). Innlogging og delt database virker bare på Vercel.
5. Endrer du datastrukturen, migrer eksisterende rader i `public.docs` samtidig. Si fra til brukeren før du rører dataene.

## Kode

- Tilstand: `S[samling][id]`. Lagring via `put(samling, objekt)` og `del(samling, id)`, som skriver til Supabase og tegner siden på nytt. `COLLS` er listen over samlinger.
- `render()` tegner sidekolonnen og hovedflaten. Sidene ligger i `VIEWS`. Områdesidene tegnes med `areaView`/`areaOverview`.
- Alle klikk går via `data-act="navn"` og objektet `A`. Skjemaer lages med `openForm({ title, fields, value, onSave, onDelete })`.
- Navigasjon via hash: `#side` eller `#område.delside`. `ALIAS` mapper gamle lenker.
- Områder: `AREAS`. Delområder: `SUBS`.
- Oppgaver: status «Må gjøres» → «Pågår» → «Ferdig». Må ha minst én ansvarlig før «Pågår» eller «Ferdig». Alle oppgavelister bruker `taskRows()`.
- Vedlegg: `attachFields(rec)` + `applyAttach(o, v)` i skjemaene, og `filesHtml(rec)`/`fileLink()` for visning. Filer lagres som `{ id: sti i bøtta, name }`.
- Grafer er håndlaget SVG. Datoer regnes i Europe/Oslo og vises på norsk.

## Design (skal beholdes)

- Varm brun bakgrunn (`#6E5847`), kremhvite kort (`#F0E8DC`) med 22px avrundede hjørner og mørk brun tekst (`#3B2F27`). Alle farger er CSS-variabler i `:root`.
- Skrifter: Fraunces (overskrifter), Inter (brødtekst), JetBrains Mono (tall og datoer).
- Rosa nedtellingskort med vippefliser øverst i sidekolonnen.
- Logoen (huset) er en base64-maske i `.logo-mark` og får samme farge som teksten rundt.
- Fargekode: rød = kritisk eller forfalt, oransje = snart, grønn = i rute eller ferdig.
- Plassholdere skrives som `[FYLL INN …]` eller `[BEKREFT …]` og vises som gule felt.

## Regler

- All tekst i appen skal være på norsk bokmål.
- Nesten ingen emoji. Bruk bare små, diskrete SVG-ikoner.
- Ikke dikt opp tall, navn eller data. Bruk plassholdere når noe mangler.
- Hold det ryddig: bare det teamet trenger mest, ikke flere bokser og sider enn nødvendig.
- Siden må fungere på mobil (minst 16px sidemarg, ingen horisontal scroll).

## Sikkerhet

- Vi håndterer kundedata og personopplysninger. Sikkerhet går foran fart.
- RLS skal være på for alle tabeller. Kjør Supabase sine security advisors etter hver databaseendring.
- Ingen hemmelige nøkler i koden. `ANTHROPIC_API_KEY` ligger som miljøvariabel i Vercel. Alle kall til Claude går via serverless-funksjoner i `api/`, aldri fra nettleseren.
- Den offentlige Supabase-nøkkelen i `index.html` er ment å være der. Tilgang styres av innlogging og RLS.
- Repoet er offentlig. Ikke legg e-postadresser, dataeksporter eller personopplysninger i repoet.

## AI-funksjoner

- Modell: `claude-haiku-4-5`.
- AI-en lagrer aldri noe automatisk. Den foreslår, og brukeren bekrefter eller endrer før lagring.
