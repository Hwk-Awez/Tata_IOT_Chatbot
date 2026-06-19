# Tata_IOT_Chatbot

This repository contains "SteelBot," a conversational AI chatbot designed to query and analyze industrial IoT data from Tata Steel's machinery. Users can ask questions in plain English about machine performance, deviations, material consumption, and shift analytics, and the chatbot will generate and execute SQL queries to provide a natural language response.

The application is built with a Django backend, a vanilla JavaScript frontend, and a sophisticated AI pipeline that leverages Large Language Models (LLMs) and a vector database for a Text-to-SQL solution.

## How It Works

The chatbot operates on a Retrieval-Augmented Generation (RAG) pipeline to convert natural language questions into executable SQL queries and back into readable answers.

1.  **Schema Retrieval (Pinecone)**: When a user asks a question (e.g., "Which machine used the most LPG?"), the query is converted into a vector embedding. This vector is used to search a Pinecone vector database, which stores embeddings of the database table schemas. The most relevant schemas are retrieved.

2.  **SQL Generation (Groq)**: The user's original question and the retrieved schema context are passed to a powerful LLM (Llama-3.3-70B via Groq). The LLM is prompted to act as a PostgreSQL expert and generate a SQL `SELECT` query based on the provided information.

3.  **SQL Execution (Supabase)**: The generated SQL query is executed against a Supabase (PostgreSQL) database that contains the IoT machine data.

4.  **Natural Language Formatting (Groq)**: The raw data results from the database, along with the original question, are sent back to the LLM. The model is prompted to summarize this data into a clear, concise, and human-readable answer.

This entire process is orchestrated by a Django backend and presented to the user through a clean chat interface.

## Tech Stack

*   **Backend**: Django, Django REST Framework
*   **Frontend**: HTML, CSS, Vanilla JavaScript
*   **Database**: Supabase (PostgreSQL)
*   **Vector Database**: Pinecone
*   **LLM Provider**: Groq (using `llama-3.3-70b-versatile`)
*   **Embedding Model**: `all-MiniLM-L6-v2` (from Sentence Transformers)
*   **Core Libraries**: `sqlalchemy`, `pandas`, `python-dotenv`

## Project Structure

```
├── chatbot/            # Main Django app
│   ├── pipeline/       # Core AI logic (Retriever, SQL Gen, Executor, Formatter)
│   ├── static/         # Frontend CSS and JS
│   └── templates/      # Chat UI HTML
├── core/               # Django project settings and root URL configuration
├── embed_schema.py     # Script to embed and upload DB schemas to Pinecone
├── load_supabase.py    # Script to load data from CSVs into Supabase
├── chatbot_test.py     # Standalone script for testing the full pipeline
├── requirements.txt    # Python dependencies
└── manage.py           # Django command-line utility
```

## Setup and Installation

1.  **Clone the Repository**
    ```sh
    git clone https://github.com/hwk-awez/tata_iot_chatbot.git
    cd tata_iot_chatbot
    ```

2.  **Create a Virtual Environment**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    Create a `.env` file in the project root and add your API keys and database URL:
    ```env
    GROQ_API_KEY="your_groq_api_key"
    PINECONE_API_KEY="your_pinecone_api_key"
    PINECONE_INDEX="your_pinecone_index_name"
    SUPABASE_DB_URL="postgresql://user:password@host:port/dbname"
    ```

5.  **Load Data**
    a. **Database**: Place your data CSV files in a single directory. Update the `CSV_PATH` variable in `load_supabase.py` to point to this directory. Then, run the script to populate your Supabase database.
    ```sh
    python load_supabase.py
    ```
    b. **Vector Store**: Run `embed_schema.py` to embed the table schemas (defined within the script) and upload them to your Pinecone index.
    ```sh
    python embed_schema.py
    ```

6.  **Run the Application**
    Start the Django development server:
    ```sh
    python manage.py runserver
    ```
    Open your browser and navigate to `http://127.0.0.1:8000/`. You will be automatically redirected to the chat interface.

## Usage

Once the application is running, you can interact with the chatbot through the web interface. Type your question into the input box at the bottom and press Enter.

### Example Questions

*   "Which machine has the most deviations?"
*   "Total LPG consumption by shift"
*   "What is the average welding current for Rectifier1?"
*   "Show me machine performance for yesterday."
*   "Which machines were active today?"
*   "What is the average RPM for D&H-1?"
