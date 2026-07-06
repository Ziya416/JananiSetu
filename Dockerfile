FROM python:3.9-slim
# Set the working directory 
WORKDIR /app
# Copying requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copying application code
COPY . .
ENV PORT 8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
