FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
COPY foodgram/ .
RUN pip3 install -r requirements.txt --no-cache-dir
RUN pip3 install django-extensions==3.1.0
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ] 