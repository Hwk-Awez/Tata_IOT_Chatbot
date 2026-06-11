# views.py
# This file defines the API endpoint that receives a user query
# and returns a natural language answer.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .pipeline.retriever import retrieve_schemas
from .pipeline.sql_gen import generate_sql
from .pipeline.executor import execute_sql
from .pipeline.formatter import format_answer


class ChatView(APIView):

    def post(self, request):
        # Step 1: Get the user's question from the request
        user_query = request.data.get("query", "").strip()

        if not user_query:
            return Response(
                {"error": "Please provide a query."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Retrieve relevant table schemas from Pinecone
        schema_context = retrieve_schemas(user_query)

        # Step 3: Generate SQL using the LLM
        sql = generate_sql(user_query, schema_context)

        # Step 4: Execute the SQL against Supabase
        results = execute_sql(sql)

        # Step 5: Format the results into a natural language answer
        answer = format_answer(user_query, sql, results)

        # Step 6: Return everything to the client
        return Response({
            "query": user_query,
            "sql": sql,
            "answer": answer,
            "raw_results": results
        })
    
from django.shortcuts import render

def chat_page(request):
    return render(request, "core/chat.html")