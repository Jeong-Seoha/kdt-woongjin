# Subway Real-time Monitoring System

This project fetches real-time Seoul Subway train position data and stores it in a Supabase (PostgreSQL) database for analysis.

## Directory Structure
- `client/`: Contains the Python script (`collector.py`) to fetch data from the API.
- `database/`: Contains the SQL schema (`schema.sql`) to set up the database table.
- `.env`: Configuration file for API keys and database credentials.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables:**
    Copy the template and fill in your keys:
    ```bash
    cp .env.example .env 
    # Edit .env with your SEOUL_API_KEY, SUPABASE_URL, SUPABASE_KEY
    ```

3.  **Database Setup:**
    - Go to your Supabase SQL Editor.
    - Run the contents of `database/schema.sql`.

4.  **Run the Collector:**
    ```bash
    python client/collector.py
    ```

## Data Analysis
See `analysis_guide.md` for details on how to use the collected data.
