import os, json
import psycopg2
from dotenv import load_dotenv
load_dotenv()

class DatabaseConnector:
    def __init__(self, table_name: str = "chunks"):
        self.table_name = table_name
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "marigold_rag"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
        self.cur = self.conn.cursor()

    def search_similar(self, embedding: list, limit: int = 5, component_filter: str | None = None) -> list[dict]:
        """
        Search for similar chunks using vector similarity.
        Returns chunks with parent context and demo code for RAG.
        
        Args:
            embedding: Vector embedding to search for
            limit: Number of results to return
            component_filter: Optional component name to filter results (e.g., "button", "datepicker")
        """
        # 1. Vector search to find most similar chunks
        if component_filter:
            query = f"""
                SELECT 
                    id, component, section_path, content, parent_id, demo_code,
                    1 - (embedding <=> %s::vector) as similarity
                FROM {self.table_name}
                WHERE component = %s
                ORDER BY similarity DESC
                LIMIT %s
            """
            self.cur.execute(query, (json.dumps(embedding), component_filter, limit))
        else:
            query = f"""
                SELECT 
                    id, component, section_path, content, parent_id, demo_code,
                    1 - (embedding <=> %s::vector) as similarity
                FROM {self.table_name}
                ORDER BY similarity DESC
                LIMIT %s
            """
            self.cur.execute(query, (json.dumps(embedding), limit))
        
        results = []
        for row in self.cur.fetchall():
            chunk_id, component, section_path, content, parent_id, demo_code, similarity = row
            
            # 2. If chunk has a parent, fetch parent context
            parent_context = None
            if parent_id is not None:
                self.cur.execute(f"""
                    SELECT section_path, content 
                    FROM {self.table_name} WHERE id = %s
                """, (parent_id,))
                parent_row = self.cur.fetchone()
                if parent_row:
                    parent_section_path, parent_content = parent_row
                    parent_context = {
                        "section_path": parent_section_path,
                        "content": parent_content
                    }
            
            # 3. Parse demo_code if it's a JSON string
            demo_code_dict = {}
            if demo_code:
                try:
                    if isinstance(demo_code, str):
                        demo_code_dict = json.loads(demo_code)
                    else:
                        demo_code_dict = demo_code
                except (json.JSONDecodeError, TypeError):
                    demo_code_dict = {}
            
            results.append({
                "id": chunk_id,
                "component": component,
                "section_path": section_path,
                "content": content,
                "parent_context": parent_context,
                "demo_code": demo_code_dict,
                "similarity": similarity
            })
        
        return results

    def get_components(self) -> list[str]:
        """Get all unique component names from the database"""
        self.cur.execute(f"SELECT DISTINCT component FROM {self.table_name} ORDER BY component")
        return [row[0] for row in self.cur.fetchall()]

    def close(self):
        self.cur.close()
        self.conn.close()