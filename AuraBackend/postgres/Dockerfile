FROM postgres:16

# Instalar herramientas necesarias y añadir el repositorio de apt de PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    && curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-key.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/postgresql-key.gpg] http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y \
        postgresql-16-pgaudit \
        postgresql-16-pgvector \
    # Limpiar
    && apt-get remove -y curl ca-certificates gnupg \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*