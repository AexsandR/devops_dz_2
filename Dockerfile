FROM python:alpine
COPY . /app
RUN apk update && apk add  g++
RUN pip install -r /app/requirements.txt
EXPOSE 5000
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0"]


