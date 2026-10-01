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

## Deploy to Render

1. Push this repository to GitHub.
2. In Render, choose **New + → Blueprint** and connect the `dagooc` repository. Render will read `render.yaml` and create the web service.
3. Wait for the build and deploy to finish, then open the generated `onrender.com` URL.

The Render configuration generates a Django secret key and serves collected static files through WhiteNoise. This prototype uses SQLite and mock operational data; its database file is ephemeral on Render and is recreated on redeploy. Do not use it for persistent production records without configuring a managed database.
