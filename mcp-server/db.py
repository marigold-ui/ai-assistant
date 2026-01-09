import os, json
import psycopg2
from dotenv import load_dotenv
load_dotenv()

class DatabaseConnector:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "marigold_rag"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        self.cur = self.conn.cursor()

    def search_similar(self, embedding: list, limit: int = 5) -> list[dict]:
        self.cur.execute("""
            SELECT 
                id, component, section_title, section_path, content,
                1 - (embedding <=> %s::vector) as similarity
            FROM chunks
            ORDER BY similarity DESC
            LIMIT %s
        """, (json.dumps(embedding), limit))
        
        rows = self.cur.fetchall()
        return [
            {
                "id": row[0],
                "component": row[1],
                "section_title": row[2],
                "section_path": row[3],
                "content": row[4],
                "similarity": row[5]
            }
            for row in rows
        ]

    def close(self):
        self.cur.close()
        self.conn.close()