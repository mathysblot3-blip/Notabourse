-- Bourse à lunettes : limites des deux tables Supabase (audit du 17/11/2026, constats S-C02 et S-C03).
-- À lancer UNE fois par Mathys : Supabase, SQL Editor, coller tout ce fichier, Run. Les lignes déjà présentes ne sont
-- ni modifiées ni revérifiées. Pour revenir en arrière : les quatre commandes « drop » en bas du fichier.
--
-- Pourquoi : la clé publique du site permet à n'importe qui d'ajouter des lignes directement, sans passer par le site.
-- Les limites de Python (3 messages, 20 recherches par visite) se contournent donc ; celles-ci sont dans la base.

-- 1. Format de l'adresse e-mail des messages, contrôlé par la base (le contrôle du site peut être contourné)
alter table public.messages
  add constraint messages_email_format
  check (email is null or email ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$') not valid;

-- 2. Au plus 60 messages par heure pour tout le site (le bouton « Questions ? » en reçoit quelques-uns par semaine)
create or replace function public.limiter_messages() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.messages where cree_le > now() - interval '1 hour') >= 60 then
    raise exception 'trop de messages en une heure : réessayer plus tard';
  end if;
  return new;
end $$;
drop trigger if exists limiter_messages on public.messages;
create trigger limiter_messages before insert on public.messages
  for each row execute function public.limiter_messages();

-- 3. Au plus 2 000 recherches comptées par heure pour tout le site (le site en fait au plus 300 calculs par heure)
create or replace function public.limiter_recherches() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.recherches where cree_le > now() - interval '1 hour') >= 2000 then
    raise exception 'trop de recherches en une heure';
  end if;
  return new;
end $$;
drop trigger if exists limiter_recherches on public.recherches;
create trigger limiter_recherches before insert on public.recherches
  for each row execute function public.limiter_recherches();

-- Pour revenir en arrière (ne pas lancer avec le reste) :
-- alter table public.messages drop constraint messages_email_format;
-- drop trigger limiter_messages on public.messages;      drop function public.limiter_messages();
-- drop trigger limiter_recherches on public.recherches;  drop function public.limiter_recherches();
