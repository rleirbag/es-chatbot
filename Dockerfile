    FROM python:3.13-slim as builder

    WORKDIR /app
    
    RUN pip install uv
    
    COPY pyproject.toml README.md ./
    
    RUN uv pip install --system --no-cache .
    
    COPY . .
    
    FROM python:3.13-slim
    
    WORKDIR /app
    
    RUN useradd --create-home appuser
    USER appuser
    
    COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
    COPY --from=builder /usr/local/bin /usr/local/bin
    
    COPY --from=builder /app/app ./app
    COPY --from=builder /app/alembic.ini .
    COPY --from=builder /app/migrations ./migrations
    
    COPY --from=builder /app/entrypoint.sh .
    RUN chmod +x ./entrypoint.sh
    
    ENTRYPOINT ["./entrypoint.sh"]
    
    EXPOSE 8000
    
    # O CMD agora é passado como argumento para o ENTRYPOINT
    CMD ["fastapi", "run", "app/app.py", "--host", "0.0.0.0", "--port", "8000"]