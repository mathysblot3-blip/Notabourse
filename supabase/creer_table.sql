-- NotaBourse : table du compteur des recherches (étape e, 19/10/2026).
-- À coller UNE fois dans Supabase : menu « SQL Editor » > « New query », puis bouton « Run ».
-- Résultat attendu : « Success. No rows returned ».

-- 1. La table : une ligne par fiche affichée sur le site. Rien sur le visiteur, seulement la société cherchée.
create table if not exists public.recherches (
  id uuid primary key default gen_random_uuid(),                       -- identifiant unique, créé par Supabase
  cree_le timestamptz not null default now(),                          -- date et heure de la recherche (heure UTC)
  symbole text not null check (char_length(symbole) between 1 and 20), -- symbole boursier, par exemple AAPL
  nom text check (char_length(nom) <= 200)                             -- nom de la société, par exemple Apple Inc.
);

-- 2. Sécurité : avec la clé publique du site, on peut seulement AJOUTER des lignes (proposition P7 du plan).
alter table public.recherches enable row level security;              -- règles d'accès ligne par ligne activées
revoke all on table public.recherches from anon, authenticated;       -- retire tous les droits donnés par défaut
grant insert on table public.recherches to anon;                      -- redonne seulement le droit d'ajouter
create policy "insertion seule" on public.recherches
  for insert to anon with check (true);                               -- ajout permis ; aucune règle de lecture,
                                                                      -- de modification ni d'effacement
