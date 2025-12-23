FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . .

# Install dependencies
RUN uv sync --frozen --no-cache

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p /app/.cache/uv

# Change ownership to UID 1000 (the user we'll run as)
RUN chown -R 1000:1000 /app

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the application
CMD ["uv", "run", "start"]