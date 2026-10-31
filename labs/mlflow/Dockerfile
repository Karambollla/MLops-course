FROM python:3.12.12-slim
COPY server.txt /tmp/server.txt
RUN pip install --no-cache-dir -r /tmp/server.txt
WORKDIR /data
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "sqlite:////data/mlflow.db", "--serve-artifacts", "--artifacts-destination", "/data/artifacts"]
