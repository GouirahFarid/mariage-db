-- Nombre de communes par département

SELECT
    d.code as code_departement,
    d.nom as nom_departement,
    COUNT(DISTINCT c.id) as nombre_communes
FROM departement d
LEFT JOIN commune c ON d.code = c.dept_code
GROUP BY d.code, d.nom
ORDER BY d.code;

-- Quantité d'actes à LUÇON
SELECT
    c.nom as commune,
    COUNT(*) as nombre_actes
FROM acte_mariage am
JOIN commune c ON am.commune_id = c.id
WHERE c.nom = 'LUÇON'
GROUP BY c.nom;

-- Contrats de mariage avant 1855

SELECT
    COUNT(*) as nombre_contrats
FROM acte_mariage am
JOIN type_acte ta ON am.type_id = ta.id
WHERE
    ta.libelle = 'Contrat de mariage'
    AND COALESCE(NULLIF(SUBSTRING(am.date_acte FROM 7 FOR 4), ''), '0') ~ '^\d+$'
    AND CAST(COALESCE(NULLIF(SUBSTRING(am.date_acte FROM 7 FOR 4), ''), '0') AS INTEGER) < 1855;

-- Commune avec le plus de publications

SELECT
    c.nom, COUNT(*) as nb_publications
FROM acte_mariage am
JOIN type_acte ta ON am.type_id = ta.id
JOIN commune c ON am.commune_id = c.id
WHERE
    ta.libelle = 'Publication de mariage'
GROUP BY c.nom
ORDER BY nb_publications DESC
LIMIT 1;

-- Premier et dernier acte

SELECT
  MIN(TO_DATE(date_acte, 'DD/MM/YYYY')) AS premier_acte,
  MAX(TO_DATE(date_acte, 'DD/MM/YYYY')) AS dernier_acte
FROM acte_mariage
WHERE date_acte ~ '^(0[1-9]|[12][0-9]|3[01])/(0[13578]|1[02])/([0-9]{4})$'  -- 31 jours pour Jan, Mar, Mai, Jul, Aoû, Oct, Déc
   OR date_acte ~ '^(0[1-9]|[12][0-9]|30)/(0[469]|11)/([0-9]{4})$'          -- 30 jours pour Avr, Jun, Sep, Nov
   OR date_acte ~ '^(0[1-9]|1[0-9]|2[0-8])/02/([0-9]{4})$'                  -- 28 jours en Février (année non bissextile)
   OR date_acte ~ '^29/02/(([0-9]{2}(0[48]|[2468][048]|[13579][26]))|(([02468][048]|[13579][26])00))$'; -- 29 Février en années bissextiles