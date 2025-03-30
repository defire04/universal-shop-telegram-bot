FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /data
RUN chmod 777 /data

COPY . .

CMD ["python", "bot.py"]