-- Kjørt i Supabase-prosjektet «Arvklart Kontrollsenter» (zgflofmkcuvgaehsfixe) 8. oktober 2026.
-- Ligger her som dokumentasjon. Ikke kjør på nytt.

-- Private hjelpefunksjoner (ikke eksponert i API-et)
create schema if not exists private;
revoke all on schema private from public;
grant usage on schema private to authenticated;

-- Godkjente e-postadresser. RLS på uten policyer: ingen klient kan lese eller endre listen.
-- Legg til eller fjern personer i Supabase: Table Editor → allowed_users.
create table public.allowed_users (
  email text primary key check (email = lower(email))
);
alter table public.allowed_users enable row level security;

create or replace function private.is_member()
returns boolean
language sql stable security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.allowed_users a
    where a.email = lower(coalesce(auth.jwt() ->> 'email', ''))
  );
$$;
revoke all on function private.is_member() from public;
grant execute on function private.is_member() to authenticated;

-- Stopp kontoer for e-postadresser som ikke er på listen
create or replace function private.block_unknown_signup()
returns trigger
language plpgsql security definer
set search_path = ''
as $$
begin
  if not exists (select 1 from public.allowed_users a where a.email = lower(new.email)) then
    raise exception 'Denne e-postadressen har ikke tilgang til Arvklart Kontrollsenter.';
  end if;
  return new;
end;
$$;
revoke all on function private.block_unknown_signup() from public;
create trigger block_unknown_signup
  before insert on auth.users
  for each row execute function private.block_unknown_signup();

-- Alle data i appen: én rad per dokument (samling + id), innholdet som JSON
create table public.docs (
  coll text not null,
  id text not null,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  updated_by text,
  primary key (coll, id)
);
alter table public.docs enable row level security;

create policy "Medlemmer kan lese" on public.docs
  for select to authenticated using ((select private.is_member()));
create policy "Medlemmer kan legge til" on public.docs
  for insert to authenticated with check ((select private.is_member()));
create policy "Medlemmer kan endre" on public.docs
  for update to authenticated using ((select private.is_member())) with check ((select private.is_member()));
create policy "Medlemmer kan slette" on public.docs
  for delete to authenticated using ((select private.is_member()));

create or replace function private.touch_doc()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := now();
  new.updated_by := auth.jwt() ->> 'email';
  return new;
end;
$$;
create trigger touch_doc
  before insert or update on public.docs
  for each row execute function private.touch_doc();

revoke all on public.docs from anon;
revoke all on public.allowed_users from anon, authenticated;

-- Sanntid: alle ser endringer med en gang
alter publication supabase_realtime add table public.docs;

-- Fillagring: privat bøtte, bare medlemmer
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('files', 'files', false, 20971520, array[
  'application/pdf','image/png','image/jpeg','image/webp','text/plain','text/markdown','text/csv',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]);

create policy "Medlemmer kan lese filer" on storage.objects
  for select to authenticated using (bucket_id = 'files' and (select private.is_member()));
create policy "Medlemmer kan laste opp filer" on storage.objects
  for insert to authenticated with check (bucket_id = 'files' and (select private.is_member()));
create policy "Medlemmer kan endre filer" on storage.objects
  for update to authenticated using (bucket_id = 'files' and (select private.is_member()));
create policy "Medlemmer kan slette filer" on storage.objects
  for delete to authenticated using (bucket_id = 'files' and (select private.is_member()));

-- Supabase sin hjelpefunksjon for automatisk RLS skal ikke kunne kalles via API-et
revoke execute on function public.rls_auto_enable() from public, anon, authenticated;
