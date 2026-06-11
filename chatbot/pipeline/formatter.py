# formatter.py
# This file takes the raw SQL results and converts them
# into a human-readable answer using the LLM.

from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def format_answer(user_query, sql, results):
    # Handle empty results
    if not results:
        return "No data found for your query."

    # Handle SQL errors
    if "error" in results[0]:
        return f"Something went wrong: {results[0]['error']}"

    # Build the prompt with the query and results
    prompt = f"""You are a helpful assistant explaining industrial machine data from Tata Steel.

The user asked: {user_query}

The data returned was: {str(results[:20])}

Write a clear, short answer (under 150 words):
- Use specific numbers and machine names from the data
- Use correct units: amps for current, volts for voltage, litres for LPG
- Do not mention SQL or databases
- Summarize if there are many results"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()