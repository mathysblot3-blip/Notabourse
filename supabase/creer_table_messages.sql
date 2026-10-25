-- Bourse à lunettes : table des messages du bouton « Questions ? » (25/10/2026).
-- À coller UNE fois dans Supabase : menu « SQL Editor » > « New query », puis bouton « Run ».
-- Résultat attendu : « Success. No rows returned ».

-- 1. La table : une ligne par message envoyé depuis le site.
create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),                       -- identifiant unique, créé par Supabase
  cree_le timestamptz not null default now(),                          -- date et heure d'envoi (heure UTC)
  type text not null check (type in ('question', 'demande', 'erreur')),  -- question, demande ou erreur signalée
  message text not null check (char_length(message) between 5 and 2000),  -- le texte du visiteur
  email text check (email is null or char_length(email) <= 200),      -- adresse facultative, pour lui répondre
  langue text check (langue in ('fr', 'en')),                          -- langue du site au moment de l'envoi
  envoye boolean not null default false                                -- déjà envoyé dans le mail du samedi ?
);

-- 2. Sécurité : avec la clé publique du site, on peut seulement AJOUTER des messages, jamais les lire.
--    Seul le robot du samedi, avec la clé secrète rangée dans GitHub, peut les lire, les marquer et les effacer.
alter table public.messages enable row level security;               -- règles d'accès ligne par ligne activées
revoke all on table public.messages from anon, authenticated;        -- retire tous les droits donnés par défaut
grant insert on table public.messages to anon;                       -- redonne seulement le droit d'ajouter
create policy "insertion seule" on public.messages
  for insert to anon with check (envoye = false);                    -- ajout permis, jamais déjà « envoyé »
