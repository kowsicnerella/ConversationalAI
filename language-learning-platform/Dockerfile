FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Install dependencies and ensure websocket-client is properly installed
RUN pip install --upgrade pip && \
    pip uninstall -y websocket 2>/dev/null || true && \
    pip install -r requirements.txt && \
    pip install websocket-client>=1.6.0

COPY . .

RUN mkdir -p logs

EXPOSE 5000

CMD ["python", "app.py"]
