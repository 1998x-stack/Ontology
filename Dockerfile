FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir ".[postgres]"
ENV DATABASE_URL=sqlite:////app/data/ontology.db
EXPOSE 8000
# Provide ONTOLOGY_API_KEY and a persistent DATABASE_URL on deployment.
CMD ["uvicorn", "auto_ontology.api:app", "--host", "0.0.0.0", "--port", "8000"]
