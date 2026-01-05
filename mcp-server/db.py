import os
import json
import logging
import sys
from typing import Optional
from dataclasses import dataclass, asdict

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    id: str
    component: str
    section_title: str
    section_path: str
    content: str
    demo_files: list
    images: list
    token_count: int
    embedding: list


@dataclass
class SearchResult:
    id: str
    component: str
    section_title: str
    section_path: str
    content: str
    similarity: float
    token_count: int


class DatabaseConnector:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "marigold_rag"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "postgres"),
            )
            logger.info(f"Connected to {os.getenv('DB_NAME', 'marigold_rag')}")
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def search_similar(
        self, embedding: list, limit: int = 5, threshold: float = 0.5
    ) -> list[SearchResult]:
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)

            query = """
            SELECT
                id,
                component,
                section_title,
                section_path,
                content,
                token_count,
                1 - (embedding <=> %s::vector) as similarity
            FROM chunks
            WHERE 1 - (embedding <=> %s::vector) > %s
            ORDER BY similarity DESC
            LIMIT %s
            """

            cursor.execute(
                query,
                (json.dumps(embedding), json.dumps(embedding), threshold, limit),
            )
            rows = cursor.fetchall()
            cursor.close()

            return [SearchResult(**row) for row in rows]
        except psycopg2.Error as e:
            logger.error(f"Database query error: {e}")
            return []

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Chunk]:
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM chunks WHERE id = %s", (chunk_id,))
            row = cursor.fetchone()
            cursor.close()

            if row:
                return Chunk(**row)
            return None
        except psycopg2.Error as e:
            logger.error(f"Database query error: {e}")
            return None

    def get_chunks_by_component(self, component: str) -> list[Chunk]:
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM chunks WHERE component = %s ORDER BY id",
                (component,),
            )
            rows = cursor.fetchall()
            cursor.close()

            return [Chunk(**row) for row in rows]
        except psycopg2.Error as e:
            logger.error(f"Database query error: {e}")
            return []

    def get_all_components(self) -> list[str]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT component FROM chunks ORDER BY component")
            rows = cursor.fetchall()
            cursor.close()

            return [row[0] for row in rows]
        except psycopg2.Error as e:
            logger.error(f"Database query error: {e}")
            return []

    def get_stats(self) -> dict:
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_chunks,
                    COUNT(DISTINCT component) as unique_components,
                    AVG(token_count) as avg_token_count
                FROM chunks
                """
            )
            row = cursor.fetchone()
            cursor.close()

            return {
                "total_chunks": int(row["total_chunks"]),
                "unique_components": int(row["unique_components"]),
                "avg_token_count": round(float(row["avg_token_count"]), 1),
            }
        except psycopg2.Error as e:
            logger.error(f"Database query error: {e}")
            return {}
