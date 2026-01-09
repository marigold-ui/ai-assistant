FROM ollama/ollama:latest

# Create entrypoint script to pull model on startup
RUN mkdir -p /app
COPY ollama-entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 11434

ENTRYPOINT ["/app/entrypoint.sh"]
