FROM python:3.13

WORKDIR /app

# Ensure pip is up to date
RUN python -m pip install --upgrade pip

# Copy requirements first for better cache utilization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the bot
CMD ["python", "main.py"]
