# executor.py
# This file runs the SQL query against Supabase
# and returns the results as a list of dictionaries.

from sqlalchemy import create_engine, text
from django.conf import settings

# Connect to Supabase PostgreSQL once when server starts
engine = create_engine(settings.SUPABASE_DB_URL)


def execute_sql(sql):
    try:
        with engine.connect() as conn:
            # Run the query
            result = conn.execute(text(sql))

            # Get column names
            columns = list(result.keys())

            # Convert each row into a dictionary {column: value}
            rows = [dict(zip(columns, row)) for row in result.fetchall()]

            return rows

    except Exception as e:
        # If something goes wrong, return the error message
        return [{"error": str(e)}]