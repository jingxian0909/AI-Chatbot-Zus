import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client
import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Keyword, DML
from typing import Tuple, List
from fastapi import APIRouter, Query, HTTPException

router = APIRouter(tags=["Outlets"])

Table_Schema = """
Table: outlets
    - id (SERIAL PRIMARY KEY)
    - name (VARCHAR NOT NULL)
    - address (TEXT)
    - google_map (VARCHAR)
"""
load_dotenv()  

class Outlets:
    @staticmethod
    def supabaseConnect() :
        supabase_url = os.environ["SUPABASE_URL"]  
        supabase_api_key = os.environ["SUPABASE_API_KEY"] 

        client = create_client(supabase_url, supabase_api_key) 
        return client

    def __init__(self):
        self.openai = OpenAI()
        self.supabase = Outlets.supabaseConnect()


    def generate_sql_query(self, user_question: str, schema_description: str) -> str:
        messages = [
                {
                    "role": "system",
                    "content": f"""
                        You are an expert Text-to-SQL translator for PostgreSQL (Supabase).
                        Your job is to convert a natural language question into a valid SQL query.

                        RULES:
                        1. Output ONLY SQL query (no explanations).
                        2. Never use DELETE, UPDATE, INSERT, DROP, or any other modification statements.
                        3. Do NOT interpolate raw user input into queries. 
                        4. Use safe WHERE clauses.Use ONLY tables/columns in the provided schema.
                        5. Do NOT invent tables or columns.
                        6. Use simple ANSI SQL.
                        7. Do not wrap SQL in markdown.
                        8. Never use wildcard * when generating SQL
                        9. When generating SQL, do NOT use parameters such as $1 or ?
                        10. When generating SQL for outlet lookup, always search using ONLY the "name" column. Do NOT filter by "address" because address strings vary and are not reliable for matching.
                            Never include conditions like address LIKE ... even if the user mentions the location. Use: WHERE name ILIKE '%<keywords>%' only.
                        11. Always end with a semicolon.
                        12. If user intent is impossible with the schema, output: -- Unable to generate SQL
                        

                        Database Schema:
                        {schema_description}
                        """
                },
                {
                    "role": "user",
                    "content": user_question
                }
        ]

        response = self.openai.chat.completions.create(
            model= "gpt-5-mini-2025-08-07",
            messages= messages
        )
        return response.choices[0].message.content

    def execute_sql_query(self, sql_query):
        try:
            result = self.supabase.rpc("custom_query", {"query_text": sql_query}).execute()
            return result.data
        except Exception as e:
            return {"error": str(e)}

    @staticmethod    
    def validate_generated_sql(sql: str) -> Tuple[bool, str]:
        # Parse SQL
        parsed = sqlparse.parse(sql)
        if not parsed:
            return False
        stmt = parsed[0]

        if stmt.get_type() != "SELECT":
            return False, "Only SELECT queries allowed."
        
        if "*" in sql:
            return False, "Wildcard '*' is not allowed."
        
        # Check for forbidden keywords
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "--", ";--"]
        for kw in forbidden:
            if kw.lower() in sql.lower():
                return False, f"Forbidden keyword detected: {kw}"
        
        tables = []
        from_seen = False
        
        # Check if only allowed tables are used
        for token in stmt.tokens:
            if token.ttype is Keyword and token.value.upper() == "FROM":
                from_seen = True
                continue

            if from_seen:
                if isinstance(token, Identifier):
                    tables.append(token.get_real_name())
                    from_seen = False
                elif isinstance(token, IdentifierList):
                    for ident in token.get_identifiers():
                        tables.append(ident.get_real_name())
                    from_seen = False

        if len(tables) == 0:
            return False, "No table found in FROM clause."

        if len(tables) > 1:
            return False, "Multiple tables detected. Only the 'outlets' table is allowed."

        if tables[0].lower() != "outlets":
            return False, f"Invalid table: {tables[0]}. Only 'outlets' table is allowed."     
               
        return True, ""

    def summarize_outlets(self, query: str, outlets):
        prompt = f"""
            You are a helpful assistant that answers user questions about outlets. 
            You have access to the following outlet data:
            {outlets}
            Each outlet has:
            - name
            - address
            - google_map

            Instructions:
            1. If the user asks about information that exists in the data (like address or Google Maps link), provide it clearly.
            2. If the user asks about information that does NOT exist in the data (like opening hours, closing time, menu items), politely tell the user you do not have that information, and provide the Google Maps link for reference.
            3. Respond in a friendly, natural, user-facing way.
            4. Only answer based on the data provided. Do NOT make up information.
            5. Provide concise answers, suitable for chat or voice assistant.

            Examples:
            User: "Where is ZUS Coffee – Uptown Damansara?"  
            Assistant: "ZUS Coffee – Uptown Damansara is located at 44-G (Ground Floor), JALAN SS21/39, DAMANSARA UTAMA, 47400 PETALING JAYA, SELANGOR. You can find it here: https://maps.app.goo.gl/SGuUWhHHEBNd8mFWA"

            User: "When does ZUS Coffee – Uptown Damansara open?"  
            Assistant: "Sorry, I don't have the opening or closing times for ZUS Coffee – Uptown Damansara. Please check here for more info: https://maps.app.goo.gl/SGuUWhHHEBNd8mFWA"

            User Question: {query}

            """
        response = self.openai.chat.completions.create(
        model="gpt-5-mini-2025-08-07",
        messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

@router.get("/outlets")
async def main(query: str, schema: str = Table_Schema):
    
    client = Outlets()
    print(f"User Question: {query}")

    sql_query = client.generate_sql_query(query, schema)
    print(f"Generated SQL Query:\n{sql_query}")

    is_valid, reason = client.validate_generated_sql(sql_query)

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Unsafe or invalid SQL generated: {reason}"
        )
    
    try:
        query_results = client.execute_sql_query(sql_query)
        data = client.summarize_outlets(query=query, outlets=query_results)
        print(f"Query Results:\n{data}")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main("How many outlets in Petaling Jaya?"))
