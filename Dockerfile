# --- Estágio 1: Builder ---
    FROM python:3.13-slim as builder

    WORKDIR /app
    
    RUN pip install uv
    
    COPY pyproject.toml .
    
    # Instala apenas as dependências de PRODUÇÃO
    RUN uv pip install --system --no-cache .
    
    COPY . .
    
    # --- Estágio 2: Final ---
    FROM python:3.13-slim
    
    WORKDIR /app
    
    RUN useradd --create-home appuser
    USER appuser
    
    # Copia as dependências instaladas do estágio 'builder'
    COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
    COPY --from=builder /usr/local/bin /usr/local/bin
    
    # Copia o código da aplicação do estágio 'builder'
    COPY --from=builder /app/app ./app
    COPY --from=builder /app/credentials.json .
    COPY --from=builder /app/alembic.ini .
    COPY --from=builder /app/migrations ./migrations
    
    # --- NOVIDADES AQUI ---
    # Copia o script de entrada e o torna executável
    COPY --from=builder /app/entrypoint.sh .
    RUN chmod +x ./entrypoint.sh
    
    # Define o script de entrada como o ponto de partida do container
    ENTRYPOINT ["./entrypoint.sh"]
    # --- FIM DAS NOVIDADES ---
    
    EXPOSE 8000
    
    # O CMD agora é passado como argumento para o ENTRYPOINT
    CMD ["fastapi", "run", "app/app.py", "--host", "0.0.0.0", "--port", "8000"]