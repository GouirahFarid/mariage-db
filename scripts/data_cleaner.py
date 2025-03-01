from typing import List, Tuple, Dict, Set, Optional, Any
import pandas as pd
from pathlib import Path
import csv
from config import VALID_TYPES, VALID_DEPTS, INVALID_VALUES


class DataCleaner:
    """Nettoyeur de données pour les actes de mariage"""

    def __init__(self, input_dir: Path, output_dir: Path):
        """Initialise le nettoyeur"""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.df: Optional[pd.DataFrame] = None

    def read_source_file(self) -> pd.DataFrame:
        """Lit le fichier source CSV"""
        column_names: List[str] = [
            'id', 'type_acte',
            'nom_a', 'prenom_a', 'prenom_pere_a', 'nom_mere_a', 'prenom_mere_a',
            'nom_b', 'prenom_b', 'prenom_pere_b', 'nom_mere_b', 'prenom_mere_b',
            'commune', 'departement', 'date_acte', 'num_vue'
        ]

        self.df = pd.read_csv(
            self.input_dir / 'mariages_L3.csv',
            names=column_names,
            lineterminator='\n',
            quoting=csv.QUOTE_MINIMAL,
            escapechar='\\'
        )
        return self.df

    def clean_value(self, value: Any) -> str:
        """Nettoie une valeur"""
        if pd.isna(value):
            return "non specifies"

        value = str(value).strip()
        if not value or value.lower() in INVALID_VALUES:
            return "non specifies"

        value = value.replace('\n', ' ').replace('\r', ' ')
        value = ' '.join(value.split())
        value = value.replace('"', "'").replace(';', ',')

        return value.strip()

    def create_person_key(self, row: pd.Series, prefix: str) -> Tuple[str, ...]:
        """
        Crée une clé unique pour une personne.

        Args:
            row: Ligne de données
            prefix: Préfixe ('a' ou 'b')

        Returns:
            Tuple de valeurs identifiant la personne
        """
        fields = ['nom', 'prenom', 'prenom_pere', 'nom_mere', 'prenom_mere']
        return tuple(
            self.clean_value(row[f'{field}_{prefix}'])
            for field in fields
        )

    def clean_dept_code(self, value: Any) -> Optional[str]:
        """Nettoie un code département"""
        return str(int(float(value))) if pd.notna(value) else None

    def write_csv_safely(self, filepath: Path, headers: List[str], data: List[Any]) -> None:
        """Écrit un fichier CSV"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(
                f,
                delimiter=';',
                quoting=csv.QUOTE_MINIMAL,
                quotechar='"',
                escapechar='\\',
                lineterminator='\n'
            )
            writer.writerow(headers)
            writer.writerows([
                [self.clean_value(val) for val in row]
                for row in data
            ])

    def create_mappings(self, types_df: pd.DataFrame, communes_df: pd.DataFrame,
                        personnes_df: pd.DataFrame) -> Tuple[Dict, Dict, Dict]:
        """Crée les dictionnaires de mapping"""
        type_mapping = dict(zip(types_df['libelle'], types_df['id']))

        commune_mapping = dict(
            zip(
                zip(communes_df['nom'], communes_df['dept_code']),
                communes_df['id']
            )
        )

        def create_person_key(row: pd.Series) -> Tuple[str, ...]:
            return tuple(
                self.clean_value(row[field])
                for field in ['nom', 'prenom', 'prenom_pere', 'nom_mere', 'prenom_mere']
            )

        personne_mapping = dict(
            zip(
                personnes_df.apply(create_person_key, axis=1),
                personnes_df['id']
            )
        )

        return type_mapping, commune_mapping, personne_mapping

    def process_single_acte(self, row: pd.Series,
                            mappings: Tuple[Dict, Dict, Dict]) -> Optional[List]:
        """Traite un acte individuel"""
        type_mapping, commune_mapping, personne_mapping = mappings

        personne_a_key = self.create_person_key(row, 'a')
        personne_b_key = self.create_person_key(row, 'b')

        personne_a_id = personne_mapping.get(personne_a_key)
        personne_b_id = personne_mapping.get(personne_b_key)
        commune_id = commune_mapping.get(
            (row['commune'], int(self.clean_dept_code(row['departement'])))
        )
        type_id = type_mapping.get(row['type_acte'])
        if all([personne_a_id, personne_b_id, commune_id, type_id]):
            return [
                row['id'],
                type_id,
                personne_a_id,
                personne_b_id,
                commune_id,
                row['date_acte'] if pd.notna(row['date_acte']) else 'non specifies',
                row['num_vue'] if pd.notna(row['num_vue']) else 'non specifies'
            ]
        return None

    def process_types_acte(self) -> pd.DataFrame:
        """Traite les types d'actes"""
        types = [t for t in self.df['type_acte'].unique()
                 if t in VALID_TYPES]
        types_data = [(i + 1, type_) for i, type_ in enumerate(sorted(types))]

        self.write_csv_safely(
            self.output_dir / 'type_acte.csv',
            ['id', 'libelle'],
            types_data
        )
        return pd.DataFrame(types_data, columns=['id', 'libelle'])

    def process_departements(self) -> pd.DataFrame:
        """Traite les départements"""
        depts_data = [(code, f'Département {code}')
                      for code in sorted(VALID_DEPTS)]

        self.write_csv_safely(
            self.output_dir / 'departement.csv',
            ['code', 'nom'],
            depts_data
        )
        return pd.DataFrame(depts_data, columns=['code', 'nom'])

    def process_communes(self) -> pd.DataFrame:
        """Traite les communes"""
        communes = self.df[
            self.df['departement'].apply(self.clean_dept_code).isin(VALID_DEPTS)
        ]
        communes = communes[['commune', 'departement']].drop_duplicates()

        communes_data = [
            (i + 1, self.clean_value(row['commune']),
             str(int(float(row['departement']))))
            for i, (_, row) in enumerate(communes.iterrows())
        ]

        self.write_csv_safely(
            self.output_dir / 'commune.csv',
            ['id', 'nom', 'dept_code'],
            communes_data
        )
        return pd.DataFrame(communes_data, columns=['id', 'nom', 'dept_code'])

    def process_personnes(self) -> pd.DataFrame:
        """Traite les personnes"""
        unique_persons: Set[Tuple] = set()
        personnes_data: List[List] = []
        current_id: int = 1

        for _, row in self.df.iterrows():
            for prefix in ['a', 'b']:
                nom = self.clean_value(row[f'nom_{prefix}'])
                prenom = self.clean_value(row[f'prenom_{prefix}'])

                if nom != "non specifies" and prenom != "non specifies":
                    person_key = self.create_person_key(row, prefix)
                    if person_key not in unique_persons:
                        unique_persons.add(person_key)
                        personnes_data.append([current_id] + list(person_key))
                        current_id += 1

        self.write_csv_safely(
            self.output_dir / 'personne.csv',
            ['id', 'nom', 'prenom', 'prenom_pere', 'nom_mere', 'prenom_mere'],
            personnes_data
        )
        return pd.DataFrame(
            personnes_data,
            columns=['id', 'nom', 'prenom', 'prenom_pere', 'nom_mere', 'prenom_mere']
        )

    def process_actes(self) -> pd.DataFrame:
        """Traite les actes"""
        # Charger les références
        types_df = pd.read_csv(self.output_dir / 'type_acte.csv', sep=';')
        communes_df = pd.read_csv(self.output_dir / 'commune.csv', sep=';')
        personnes_df = pd.read_csv(self.output_dir / 'personne.csv', sep=';')

        # Filtrer les actes valides
        valid_actes = self.df[
            (self.df['type_acte'].isin(VALID_TYPES)) &
            (self.df['departement'].apply(self.clean_dept_code).isin(VALID_DEPTS))
            ]

        # Traiter les actes
        mappings = self.create_mappings(types_df, communes_df, personnes_df)
        actes_data = []

        for _, row in valid_actes.iterrows():
            acte = self.process_single_acte(row, mappings)
            if acte:
                actes_data.append(acte)

        self.write_csv_safely(
            self.output_dir / 'acte_mariage.csv',
            ['id', 'type_id', 'personne_a_id', 'personne_b_id',
             'commune_id', 'date_acte', 'num_vue'],
            actes_data
        )

        return pd.DataFrame(
            actes_data,
            columns=['id', 'type_id', 'personne_a_id', 'personne_b_id',
                     'commune_id', 'date_acte', 'num_vue']
        )

    def process_all(self) -> None:
        """Traite l'ensemble des fichiers"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.read_source_file()

        print("Traitement des données...")
        for process in [
            self.process_types_acte,
            self.process_departements,
            self.process_communes,
            self.process_personnes,
            self.process_actes
        ]:
            print(f"Exécution de {process.__name__}...")
            process()
        print("Traitement terminé!")