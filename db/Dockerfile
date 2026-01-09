FROM pgvector/pgvector:pg16

LABEL maintainer="Marigold AI"
LABEL description="PostgreSQL with pgvector for RAG embeddings"

# Install additional PostgreSQL extensions
RUN apt-get update && apt-get install -y \
    postgresql-contrib-16 \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 5432

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD pg_isready -U postgres

# Use the default entrypoint from pgvector image
