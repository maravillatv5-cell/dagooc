# Dagooc Farm Internal Management System

This project is an owner- and staff-facing farm management portal with four core modules:

- Dashboard analytics
- Inventory management
- POS sales
- HR management

## Run locally

1. Open a terminal in this folder.
2. Create a virtual environment and install dependencies:

   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt

3. Apply the database schema:

   .\.venv\Scripts\python.exe manage.py migrate

4. Start the app:

   .\.venv\Scripts\python.exe manage.py runserver

Open http://127.0.0.1:8000/ to access the dashboard.
