from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from groq import Groq
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

# ── CLIENTS ───────────────────────────────────────────────────────────────────
pc       = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index    = pc.Index(os.getenv("PINECONE_INDEX"))
embedder = SentenceTransformer("all-MiniLM-L6-v2")
llm      = Groq(api_key=os.getenv("GROQ_API_KEY"))
engine   = create_engine(os.getenv("SUPABASE_DB_URL"))

# ── STEP 1: RETRIEVE RELEVANT SCHEMAS FROM PINECONE ──────────────────────────
def retrieve_schemas(query: str, top_k: int = 3) -> str:
    query_embedding = embedder.encode(query).tolist()
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    schemas = [match["metadata"]["text"] for match in results["matches"]]
    return "\n\n".join(schemas)

# ── STEP 2: GENERATE SQL FROM QUERY + SCHEMA ─────────────────────────────────
def generate_sql(query: str, schema_context: str) -> str:
    prompt = f"""You are an expert SQL generator for a PostgreSQL database monitoring industrial IoT machines at Tata Steel.

Here are the relevant table schemas:
{schema_context}

Important rules:
- Only generate SELECT statements, never INSERT, UPDATE, DELETE, or DROP
- Always use lowercase table names exactly as shown in the schema
- For machine names use the 'machines' table with the 'name' column
- For date filtering use business_date column
- Limit results to 50 rows unless the user asks for all
- Return ONLY the SQL query, no explanation, no markdown, no backticks

User question: {query}

SQL query:"""

    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# ── STEP 3: EXECUTE SQL ON SUPABASE ──────────────────────────────────────────
def execute_sql(sql: str) -> list:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return rows
    except Exception as e:
        return [{"error": str(e)}]

# ── STEP 4: FORMAT RESULT INTO NATURAL LANGUAGE ──────────────────────────────
def format_answer(query: str, sql: str, results: list) -> str:
    if not results:
        return "No data found for your query."

    if "error" in results[0]:
        return f"There was an error executing the query: {results[0]['error']}"

    results_text = str(results[:20])  # Limit to first 20 rows for formatting

    prompt = f"""You are a helpful assistant analyzing industrial IoT machine data for Tata Steel.

The user asked: {query}

The SQL query executed was: {sql}

The results returned were: {results_text}

Please provide a clear, concise natural language answer based on the data.
- Be specific with numbers and machine names
- If there are multiple results, summarize the key findings
- Use appropriate units (amps for current, volts for voltage, litres for LPG)
- Keep the answer under 150 words"""

    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ── MAIN PIPELINE ─────────────────────────────────────────────────────────────
def ask(query: str) -> dict:
    print(f"\nQuery: {query}")

    # Step 1 — Retrieve relevant schemas
    schema_context = retrieve_schemas(query)
    print(f"Relevant tables retrieved from Pinecone")

    # Step 2 — Generate SQL
    sql = generate_sql(query, schema_context)
    print(f"SQL generated: {sql}")

    # Step 3 — Execute SQL
    results = execute_sql(sql)
    print(f"Rows returned: {len(results)}")

    # Step 4 — Format answer
    answer = format_answer(query, sql, results)

    return {
        "query": query,
        "sql": sql,
        "results": results,
        "answer": answer
    }

# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "Which machine has the highest number of current deviations?",
        "What is the average welding current for Rectifier1?",
        "Show me total LPG consumption by shift",
    ]

    for query in test_queries:
        response = ask(query)
        print(f"\nAnswer: {response['answer']}")
        print("-" * 60)