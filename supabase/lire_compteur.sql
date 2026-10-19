-- NotaBourse : lire le compteur des recherches. À lancer dans Supabase, « SQL Editor » (toi seul y as accès).

-- Nombre total de recherches, de sociétés différentes, première et dernière recherche
select count(*) as recherches, count(distinct symbole) as societes, min(cree_le) as premiere, max(cree_le) as derniere
from public.recherches;

-- Les 20 sociétés les plus cherchées
select symbole, nom, count(*) as recherches
from public.recherches
group by symbole, nom
order by recherches desc
limit 20;

-- Recherches par jour (30 derniers jours)
select date_trunc('day', cree_le)::date as jour, count(*) as recherches
from public.recherches
where cree_le > now() - interval '30 days'
group by jour
order by jour;
