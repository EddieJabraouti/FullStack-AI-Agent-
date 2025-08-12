import sqlite3 
from typing import Optional 
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass # Define a data class for Car
class Car: # Represents a car record in the database
    vin:str
    make:str
    model:str
    year:int

class DatabaseDriver: # Class to handle database operations like creating and retrieving car records
    def __init__(self, db_path = "auto_db.sqlite"): # Initialize the database driver with a path to the database file
        self.dbpath = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self): 
     conn = sqlite3.connect(self.dbpath) # Create a connection to the SQLite database
     try: 
        yield conn 
     finally: 
        conn.close()

    def _init_db(self): 
       with self.get_connection() as conn: 
          cursor = conn.cursor()

          cursor.execute(""" # Create the CARS table if it does not exist
                         CREATE TABLE IF NOT EXISTS CARS (
                             vin TEXT PRIMARY KEY,
                             make TEXT NOT NULL,
                             model TEXT NOT NULL,
                             year INTEGER NOT NULL
                         )
                         """)
          conn.commit()

    def create_car(self, vin:str, make:str, model:str, year:int) -> Car: # Create a new car record in the database
       with self.get_connection() as conn: 
          cursor = conn.cursor()
          cursor.exectute("INSERT INTO CARS (vin, make, model, year) VALUES (?, ?, ?, ?)",
                          (vin, make, model, year))
          conn.commit()
          return Car(vin, make, model, year)
       
    def get_car_by_vin(self, vin:str) -> Optional[Car]: # Retrieve a car record by its VIN
        with self.get_connection() as conn: 
           cursor = conn.cursor()
           cursor.execute("SELECT * FROM CARS WHERE vin = ?", (vin,)) 
           row = cursor.fetchone() # Fetch the first row that matches the VIN
           if not row: 
              return None 
           
           return Car(
            vin= row[0],
            make= row[1],
            model= row[2],
            year = row[3]
           )
            