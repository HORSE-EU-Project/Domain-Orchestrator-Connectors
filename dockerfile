# base image
FROM python:3.12-slim AS base

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
       build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# python deps
WORKDIR /app
COPY /src/requirements.txt  .
RUN pip install --no-cache-dir -r requirements.txt

# copy code
COPY . .

# runtime env vars (docs only)
# real ones will be set via docker-compose
ENV MONGO_URI=mongodb://mongo:27017 \
    MONGO_DB=doc_database \
    MONGO_COLL=mitigation_actions

# expose + entrypoint
EXPOSE 8
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]