-- Insertion des données depuis les fichiers CSV
\copy type_acte FROM 'processed/type_acte.csv' WITH (FORMAT csv, HEADER true);
\copy departement FROM 'processed/departement.csv' WITH (FORMAT csv, HEADER true);
\copy commune FROM 'processed/commune.csv' WITH (FORMAT csv, HEADER true);
\copy personne FROM 'processed/personne.csv' WITH (FORMAT csv, HEADER true);
\copy acte_mariage FROM 'processed/acte_mariage.csv' WITH (FORMAT csv, HEADER true);