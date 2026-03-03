# Image
# FROM registry.b2w.io/compliance/python:3.12-slim
FROM python:3.12-slim

# Installing necessary components
RUN apt update && apt -y upgrade

# Adjust Time Zone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Add files
COPY ./ /app

# Go to working directory
WORKDIR /app
RUN mkdir -p /app/_credentials

# Install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
# RUN python manage.py collectstatic --noinput

# Add new noroot user
# RUN adduser --system --no-create-home nonroot
# USER nonroot
