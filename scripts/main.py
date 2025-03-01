import sys
from typing import Optional

from config import *
from scripts.data_cleaner import DataCleaner
from scripts.database_manager import DatabaseManager


def process_database() -> None:
    """
    Fonction principale de traitement de la base de données.
    Gère le nettoyage des données et leur import dans PostgreSQL.
    """
    db: Optional[DatabaseManager] = None

    try:
        # Étape 1: Nettoyage des données
        print("1. Nettoyage des données...")
        cleaner = DataCleaner(RAW_DIR, PROCESSED_DIR)
        cleaner.process_all()

        # Étape 2: Configuration de la base de données
        print("\n2. Configuration de la base de données...")
        db = DatabaseManager(**DB_CONFIG)

        # Création et connexion à la base
        db.create_database()
        db.connect()

        # Étape 3: Création des tables
        print("\n3. Création des tables...")
        schema_path: Path = BASE_DIR / 'sql' / 'create_tables.sql'
        if not schema_path.exists():
            raise FileNotFoundError(f"Fichier SQL non trouvé: {schema_path}")
        db.execute_sql_file(schema_path)

        # Étape 4: Import des données
        print("\n4. Import des données...")
        tables: List[str] = [
            'type_acte', 'departement', 'commune',
            'personne', 'acte_mariage'
        ]

        for table in tables:
            csv_path: Path = PROCESSED_DIR / f'{table}.csv'
            if not csv_path.exists():
                raise FileNotFoundError(f"Fichier CSV non trouvé: {csv_path}")
            print(f"Import de {table}...")
            db.import_csv_data(table, csv_path)

        print("\nInstallation terminée avec succès!")

    except FileNotFoundError as e:
        print(f"Erreur fichier: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)
    finally:
        if db is not None:
            db.disconnect()


if __name__ == "__main__":
    process_database()
