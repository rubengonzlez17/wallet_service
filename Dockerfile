FROM python:3.10-slim

WORKDIR /wallet_service
COPY . /wallet_service

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]