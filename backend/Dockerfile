FROM python:3.13.4-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

# flask env
ENV FLASK_APP=app.main
ENV FLASK_ENV=development

# flask app port
EXPOSE 5000

# run main
CMD ["python", "-m", "app.main"]