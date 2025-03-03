


# Rapport de Projet - Base de Données Généalogique Mariage
Ce projet a été développé dans le cadre du cours "Modélisation de bases de données" pour créer une solution complète de gestion d'actes de mariage historiques. Le code source complet est disponible sur GitHub pour permettre aux utilisateurs d'explorer l'implémentation en détail.

## Auteurs

### - GOUIRAH Farid
### - REKAI Nesrine


## Prérequis

```
- Python 3.8+
- PostgreSQL 12+
- Pandas
- Psycopg2
```

## Installation
```
git clone https://github.com/GouirahFarid/mariage-db.git
cd mariage-db
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez les paramètres dans `config.py` :
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'mariage',
    'user': 'postgres',
    'password': 'votre_mot_de_passe'
}
```

## Utilisation

1. Assurez-vous que le fichier complet `mariages_L3.csv` est présent dans le dossier `data/raw/`.

2. Exécutez le script principal :
```bash
python main.py
```

Ce script va :
- Nettoyer et transformer les données du fichier complet
- Créer la base de données
- Créer les tables
- Importer les données

3. Exécutez les requêtes SQL dans `scripts/sql/queries.sql` pour analyser les données.

## Jeux de Données

Le projet prend en charge deux fichiers :
- **mariages_L3_5k.csv** : Version réduite de 5000 enregistrements (pour tests)
- **mariages_L3.csv** : Fichier complet avec environ 564 000 enregistrements

Le système est optimisé pour traiter le fichier complet avec une gestion efficace de la mémoire et des performances.

## Modèle de Données

Le modèle relationnel comprend les tables suivantes :

- **type_acte** : Types d'actes valides
- **departement** : Départements (44, 49, 79, 85)
- **commune** : Communes avec références aux départements
- **personne** : Personnes uniques
- **acte_mariage** : Actes avec références

## Schéma de la Base de Données

```sql
CREATE TABLE IF NOT EXISTS type_acte (
    id INTEGER PRIMARY KEY,
    libelle VARCHAR(50) UNIQUE CHECK (libelle IN (
        'Certificat de mariage',
        'Contrat de mariage',
        'Divorce',
        'Mariage',
        'Promesse de mariage - fiançailles',
        'Publication de mariage',
        'Rectification de mariage'
    ))
);

CREATE TABLE IF NOT EXISTS departement (
    code VARCHAR(2) PRIMARY KEY CHECK (code IN ('44', '49', '79', '85')),
    nom VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS commune (
    id INTEGER PRIMARY KEY,
    nom VARCHAR(100),
    dept_code VARCHAR(2) REFERENCES departement(code),
    UNIQUE(nom, dept_code)
);

CREATE TABLE IF NOT EXISTS personne (
    id INTEGER PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    prenom_pere VARCHAR(100),
    nom_mere VARCHAR(100),
    prenom_mere VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS acte_mariage (
    id INTEGER PRIMARY KEY,
    type_id INTEGER REFERENCES type_acte(id),
    personne_a_id INTEGER REFERENCES personne(id),
    personne_b_id INTEGER REFERENCES personne(id),
    commune_id INTEGER REFERENCES commune(id),
    date_acte VARCHAR(20),
    num_vue VARCHAR(20)
);
```

## Requêtes Disponibles

```sql
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
```

## Optimisations

Le projet inclut des optimisations pour gérer le volume important de données :
- Index sur les colonnes fréquemment utilisées
- Dédoublonnage des personnes
- Traitement par lots pour économiser la mémoire
- Validation des contraintes métier

```sql
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_acte_date') THEN
        CREATE INDEX idx_acte_date ON acte_mariage(date_acte);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_acte_type') THEN
        CREATE INDEX idx_acte_type ON acte_mariage(type_id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_commune_nom') THEN
        CREATE INDEX idx_commune_nom ON commune(nom);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_personne_nom') THEN
        CREATE INDEX idx_personne_nom ON personne(nom, prenom);
    END IF;
END $$;
```

## Gestion des Erreurs

Le système gère les problèmes courants dans les données :
- Valeurs manquantes
- Points flottants dans les codes département
- Caractères spéciaux et retours à la ligne
- Doublons d'identifiants

## Processus de Normalisation

1. **Première Forme Normale (1NF)**
   - Élimination des groupes répétitifs (personnes A et B)
   - Atomicité des données (séparation nom/prénom)
   - Identifiants uniques pour chaque entité

2. **Deuxième Forme Normale (2NF)**
   - Séparation des types d'actes
   - Création de la table des personnes
   - Isolation des données géographiques

3. **Troisième Forme Normale (3NF)**
   - Séparation des départements et communes
   - Élimination des dépendances transitives
   - Optimisation des relations


