FROM python:3.14-slim
WORKDIR /app
COPY . .
RUN pip install -r agentlens/requirements.txt
CMD ["python", "-m", "agentlens.main", "--host", "0.0.0.0", "--port", "8000"]
