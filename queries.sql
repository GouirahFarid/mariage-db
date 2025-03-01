SELECT
    d.code as code_departement,
    d.nom as nom_departement,
    COUNT(DISTINCT c.id) as nombre_communes
FROM departement d
LEFT JOIN commune c ON d.code = c.dept_code
GROUP BY d.code, d.nom
ORDER BY d.code;

SELECT
    c.nom as commune,
    COUNT(*) as nombre_actes
FROM acte_mariage am
JOIN commune c ON am.commune_id = c.id
WHERE c.nom = 'LUÇON'
GROUP BY c.nom;

SELECT
    COUNT(*) as nombre_contrats
FROM acte_mariage am
JOIN type_acte ta ON am.type_id = ta.id
WHERE
    ta.libelle = 'Contrat de mariage'
    AND COALESCE(NULLIF(SUBSTRING(am.date_acte FROM 7 FOR 4), ''), '0') ~ '^\d+$'
    AND CAST(COALESCE(NULLIF(SUBSTRING(am.date_acte FROM 7 FOR 4), ''), '0') AS INTEGER) < 1855;

SELECT
    MIN(date_acte) as premier_acte,
    MAX(date_acte) as dernier_acte
FROM acte_mariage;