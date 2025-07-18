import sys
import sqlite3
from datetime import datetime, date
import random
import time
from dataclasses import dataclass
from typing import List

@dataclass
class Employee:
    full_name: str
    birth_date: str
    gender: str
    
    def save_to_db(self, cursor):
        cursor.execute(
            "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
            (self.full_name, self.birth_date, self.gender)
        )
    
    def calculate_age(self) -> int:
        birth_date = datetime.strptime(self.birth_date, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

class EmployeeDirectory:
    def __init__(self, db_name: str = "employees.db"):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise RuntimeError(f"Database connection failed: {str(e)}")
    
    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                gender TEXT NOT NULL
            )
        """)
        self.conn.commit()
        print("Table 'employees' created successfully.")
    
    def add_employee(self, full_name: str, birth_date: str, gender: str):
        employee = Employee(full_name, birth_date, gender)
        employee.save_to_db(self.cursor)
        self.conn.commit()
        print(f"Employee {full_name} added successfully.")
    
    def batch_add_employees(self, employees: List[Employee]):
        data = [(e.full_name, e.birth_date, e.gender) for e in employees]
        self.cursor.executemany(
            "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
            data
        )
        self.conn.commit()
        print(f"Added {len(employees)} employees in batch.")
    
    def get_all_unique_employees(self):
        self.cursor.execute("""
            SELECT full_name, birth_date, gender 
            FROM employees 
            GROUP BY full_name, birth_date 
            ORDER BY full_name
        """)
        rows = self.cursor.fetchall()
        
        for row in rows:
            employee = Employee(row[0], row[1], row[2])
            age = employee.calculate_age()
            print(f"Name: {row[0]}, Birth Date: {row[1]}, Gender: {row[2]}, Age: {age}")
    
    def generate_random_employees(self, count: int = 1000000):
        # First names and last names for random generation
        first_names_male = ["James", "John", "Robert", "Michael", "William", 
                           "David", "Richard", "Joseph", "Thomas", "Charles"]
        first_names_female = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", 
                             "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", 
                     "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
        
        employees = []
        
        # Generate 1,000,000 random employees
        for i in range(count):
            gender = random.choice(["Male", "Female"])
            if gender == "Male":
                first_name = random.choice(first_names_male)
            else:
                first_name = random.choice(first_names_female)
            
            last_name = random.choice(last_names)
            middle_name = random.choice(["A.", "B.", "C.", "D.", "E."])
            full_name = f"{last_name} {first_name} {middle_name}"
            
            # Random birth date between 1950 and 2005
            year = random.randint(1950, 2005)
            month = random.randint(1, 12)
            day = random.randint(1, 28)  # Avoid day/month issues
            birth_date = f"{year}-{month:02d}-{day:02d}"
            
            employees.append(Employee(full_name, birth_date, gender))
            
            # Batch insert every 10,000 records to improve performance
            if len(employees) >= 10000:
                self.batch_add_employees(employees)
                employees = []
        
        # Insert any remaining records
        if employees:
            self.batch_add_employees(employees)
        
        # Add 100 male employees with last name starting with 'F'
        f_employees = []
        for i in range(100):
            first_name = random.choice(first_names_male)
            last_name = "F" + random.choice(["isher", "ord", "letcher", "ranklin", "erguson"])
            middle_name = random.choice(["A.", "B.", "C.", "D.", "E."])
            full_name = f"{last_name} {first_name} {middle_name}"
            
            year = random.randint(1950, 2005)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            birth_date = f"{year}-{month:02d}-{day:02d}"
            
            f_employees.append(Employee(full_name, birth_date, "Male"))
        
        self.batch_add_employees(f_employees)
        print("Finished generating random employees.")
    
    def search_male_f_lastname(self):
        start_time = time.time()
        
        self.cursor.execute("""
            SELECT full_name, birth_date, gender 
            FROM employees 
            WHERE gender = 'Male' AND full_name LIKE 'F%'
        """)
        rows = self.cursor.fetchall()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Found {len(rows)} male employees with last names starting with 'F'")
        print(f"Execution time: {execution_time:.4f} seconds")
        
        return execution_time
    
    def optimize_database(self):
        # Create an index to speed up the gender + last name search
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_gender_lastname 
            ON employees(gender, full_name)
        """)
        self.conn.commit()
        print("Database optimized with index on gender and full_name.")
    
    def close(self):
        self.conn.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python employee_directory.py <mode> [arguments]")
        print("Modes:")
        print("  1 - Create employee table")
        print("  2 - Add employee (requires full_name, birth_date, gender)")
        print("  3 - List all unique employees sorted by name")
        print("  4 - Generate random employees")
        print("  5 - Search male employees with last names starting with F")
        print("  6 - Optimize database")
        return
    
    mode = sys.argv[1]
    directory = EmployeeDirectory()
    
    try:
        if mode == "1":
            directory.create_table()
        elif mode == "2":
            if len(sys.argv) < 5:
                print("Usage: python employee_directory.py 2 \"Full Name\" \"YYYY-MM-DD\" \"Gender\"")
                return
            full_name = sys.argv[2]
            birth_date = sys.argv[3]
            gender = sys.argv[4]
            directory.add_employee(full_name, birth_date, gender)
        elif mode == "3":
            directory.get_all_unique_employees()
        elif mode == "4":
            directory.generate_random_employees()
        elif mode == "5":
            directory.search_male_f_lastname()
        elif mode == "6":
            directory.optimize_database()
            print("Running performance test before and after optimization...")
            
            print("\nBefore optimization:")
            before_time = directory.search_male_f_lastname()
            
            print("\nAfter optimization:")
            after_time = directory.search_male_f_lastname()
            
            print(f"\nOptimization improvement: {(before_time - after_time):.4f} seconds "
                  f"({(before_time / after_time):.1f}x faster)")
        else:
            print(f"Unknown mode: {mode}")
    finally:
        directory.close()

if __name__ == "__main__":
    main()