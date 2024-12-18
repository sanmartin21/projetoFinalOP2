FROM python:3.9-slim

RUN pip install requests prometheus_client

COPY check_site.py /app/check_site.py
COPY urls.json /app/urls.json

WORKDIR /app

CMD ["python", "check_site.py"]
