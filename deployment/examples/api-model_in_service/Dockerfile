# Builder stage
FROM python:3.12-slim


# Set working directory
WORKDIR /app


RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev


ENV PORT=8000

COPY ./app ./app
COPY ./models ./models
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt


# Expose port
EXPOSE $PORT

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]