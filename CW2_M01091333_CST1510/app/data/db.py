#Libraries needed for this python program
import sqlite3
from pathlib import Path

#Sets path where database is present in
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

#Function where it returns the database which will be interacted with
def connect_database(db_path=DB_PATH):
    return sqlite3.connect(str(db_path))