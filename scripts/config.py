from pathlib import Path
from typing import List, Dict, Any

# Configuration des chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'

# Types d'actes valides
VALID_TYPES: List[str] = [
    'Certificat de mariage',
    'Contrat de mariage',
    'Divorce',
    'Mariage',
    'Promesse de mariage - fiançailles',
    'Publication de mariage',
    'Rectification de mariage'
]

# Départements valides
VALID_DEPTS: List[str] = ['44', '49', '79', '85']

# Valeurs invalides
INVALID_VALUES: List[str] = ['n/a', 'na', 'nan', 'none', '', '...']

# Configuration PostgreSQL Docker
DB_CONFIG: Dict[str, Any] = {
    'host': 'localhost',
    'port': '5432',
    'database': 'mariage',
    'user': 'postgres',
    'password': 'root'
}