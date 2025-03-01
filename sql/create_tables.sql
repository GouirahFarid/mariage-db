CREATE TABLE IF NOT EXISTS type_acte (
    id INTEGER PRIMARY KEY,
    libelle VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS departement (
    code VARCHAR(2) PRIMARY KEY,
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
--     UNIQUE(commune_id, date_acte, num_vue)
);

-- Création des index si ils n'existent pas
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