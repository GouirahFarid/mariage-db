from typing import Dict, Any, Optional
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import connection, cursor
import sys
from pathlib import Path


class DatabaseManager:
    """
    Gestionnaire de base de données PostgreSQL.
    Gère les connexions, les opérations et les imports de données.
    """

    def __init__(self, **db_params: Dict[str, Any]):
        """
        Initialise le gestionnaire de base de données.

        Args:
            **db_params: Paramètres de connexion (host, port, database, user, password)
        """
        self.connection_params: Dict[str, Any] = db_params
        self.conn: Optional[connection] = None
        self.cur: Optional[cursor] = None

    def connect(self) -> None:
        """
        Établit la connexion à la base de données.

        Raises:
            Error: En cas d'échec de connexion
        """
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.cur = self.conn.cursor()
            print("Connexion établie avec succès!")
        except Error as e:
            print(f"Erreur de connexion: {e}")
            sys.exit(1)

    def disconnect(self) -> None:
        """Ferme proprement la connexion à la base de données"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            print("Connexion fermée.")

    def create_database(self) -> None:
        """
        Crée la base de données si elle n'existe pas.

        Raises:
            Error: En cas d'échec de création
        """
        temp_params = self.connection_params.copy()
        temp_params['database'] = 'postgres'

        try:
            with psycopg2.connect(**temp_params) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM pg_database WHERE datname = %s",
                        (self.connection_params['database'],)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            f"CREATE DATABASE {self.connection_params['database']}"
                        )
                        print(f"Base {self.connection_params['database']} créée!")
                    else:
                        print(f"Base {self.connection_params['database']} existe déjà.")
        except Error as e:
            print(f"Erreur création base: {e}")
            sys.exit(1)

    def execute_sql_file(self, file_path: Path) -> None:
        """
        Exécute un fichier SQL.

        Args:
            file_path: Chemin vers le fichier SQL

        Raises:
            Error: En cas d'erreur d'exécution SQL
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_commands = f.read()
                self.cur.execute(sql_commands)
                self.conn.commit()
                print(f"Exécution réussie de {file_path}")
        except Error as e:
            print(f"Erreur SQL: {e}")
            self.conn.rollback()
            raise

    def import_csv_data(self, table_name: str, csv_path: Path) -> None:
        """
        Importe des données depuis un fichier CSV.

        Args:
            table_name: Nom de la table cible
            csv_path: Chemin vers le fichier CSV

        Raises:
            Error: En cas d'erreur d'import
        """
        try:
            copy_sql = f"""
                COPY {table_name} FROM STDIN WITH 
                DELIMITER ';' 
                CSV HEADER 
                NULL 'non specifies'
            """
            with open(csv_path, 'r', encoding='utf-8') as f:
                self.cur.copy_expert(copy_sql, f)
            self.conn.commit()
            print(f"Données importées dans {table_name}")
        except Error as e:
            print(f"Erreur import {table_name}: {e}")
            self.conn.rollback()
            raise