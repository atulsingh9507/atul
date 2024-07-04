from fastapi import FastAPI, HTTPException, Body, Depends
from pydantic import BaseModel
from datetime import date, datetime
import asyncpg

# Database connection information
DATABASE_URL = "postgresql://postgres:atul9507@localhost:5432/slintek"

# FastAPI app instance
app = FastAPI()

# Pydantic models for request and response
class Employees(BaseModel):
    first_name: str
    middle_name: str = None
    last_name: str
    joining_date: str = None
    date_of_birth: str = None
    confirmation_date: str = None
    gender: str = None
    email: str = None
    mobile_number: str = None
    residence_phone: str = None
    emergency_contact: str = None
    employee_code: str = None
    biometric_code: str = None

class EmployeeInDB(Employees):
    id: int

# Database connection pool
async def get_database_pool():
    return await asyncpg.create_pool(DATABASE_URL)

# Route to handle POST requests to create an employees
@app.post("/employees/", response_model=EmployeeInDB)
async def create_employees(employees: Employees = Body(...), db_pool: asyncpg.Pool = Depends(get_database_pool)):
    query = """
        INSERT INTO employees
        (first_name, middle_name, last_name, joining_date, date_of_birth, confirmation_date,
         gender, email, mobile_number, residence_phone, emergency_contact, 
         employee_code, biometric_code) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) 
        RETURNING id
    """
    # Convert date strings to datetime.date objects if they are provided
    values = (
        employees.first_name, employees.middle_name, employees.last_name,
        parse_date(employees.joining_date), parse_date(employees.date_of_birth), parse_date(employees.confirmation_date),
        employees.gender, employees.email, employees.mobile_number,
        employees.residence_phone, employees.emergency_contact,
        employees.employee_code, employees.biometric_code
    )

    async with db_pool.acquire() as connection:
        employee_id = await connection.fetchval(query, *values)
        return {**employees.dict(), "id": employee_id}

# Function to parse date strings to datetime.date objects
def parse_date(date_str: str) -> date:
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None



