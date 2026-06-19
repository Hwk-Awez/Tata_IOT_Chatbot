# sql_gen.py
# This file sends the user's question + relevant table schemas
# to the LLM and gets back a SQL query.

from groq import Groq
from django.conf import settings

# Connect to Groq LLM
client = Groq(api_key=settings.GROQ_API_KEY)


def generate_sql(user_query, schema_context):
    # Build the prompt — tell the LLM what it knows and what we want
    prompt = f"""You are an SQL expert for a PostgreSQL database of industrial machines at Tata Steel.

Here are the relevant table schemas:
{schema_context}

Important rules:
- Only write SELECT queries, never modify the database
- The table named 'user' must always be quoted: SELECT * FROM "user"
- Use exact table names as shown in the schemas
- period_start and period_end are stored as TEXT, cast them when using time functions: period_start::TIME or period_start::TIMESTAMP
- To join deviation with machine names: deviation.hardware_id = machines.hardware_id
- To join periodic_data_interval2 with machine names: periodic_data_interval2.hardware_id = machines.hardware_id
- business_date is stored as TEXT, always cast when filtering by date or year: business_date::DATE or EXTRACT(YEAR FROM business_date::DATE)
- Limit results to 50 rows
- The 'deleted' column is stored as TEXT not boolean, filter like this: WHERE deleted = 'f' or WHERE deleted = 'false'
- Only use columns that exist in the provided schema. Never add columns like 'deleted', 'active_status' unless they appear in the schema context.
- Return ONLY the SQL query, nothing else

User question: {user_query}

SQL:"""

    # Send to Groq and get the SQL back
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # 0 = deterministic, good for SQL generation
    )

    sql = response.choices[0].message.content.strip()

    # Remove markdown backticks if LLM adds them
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql

    