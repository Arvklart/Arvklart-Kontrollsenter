-- Kjørt 8. oktober 2026. Lar serverfunksjonene (AI) sjekke at den innloggede brukeren er på teamets liste.
-- SECURITY INVOKER: kjører med brukerens egne rettigheter og avslører ingenting om listen.
create or replace function public.am_i_member()
returns boolean
language sql stable security invoker
set search_path = ''
as $$
  select private.is_member();
$$;
revoke all on function public.am_i_member() from public, anon;
grant execute on function public.am_i_member() to authenticated;
