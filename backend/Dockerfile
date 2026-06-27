FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install core deps first for better layer caching. Build arg lets you opt into
# the full LIVE stack (LangGraph + ChromaDB + LLM SDKs).
ARG INSTALL_FULL=false
COPY requirements.txt requirements-full.txt ./
RUN pip install --upgrade pip && \
    if [ "$INSTALL_FULL" = "true" ]; then \
        pip install -r requirements-full.txt ; \
    else \
        pip install -r requirements.txt ; \
    fi

COPY . .

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request,sys; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/api/health').status==200 else sys.exit(1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
