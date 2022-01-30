FROM python:3.8-slim

EXPOSE 6006
EXPOSE 3306

# Create app directory
#WORKDIR /app

COPY . /app

#RUN pip install fastapi uvicorn pytz requests sqlalchemy mysql-connector-python celery redis schedule aiofiles gevent
RUN pip install fastapi uvicorn requests sqlalchemy mysql-connector-python pymysql pytz

#CMD ["uvicorn", "app.main:controller", "--host", "0.0.0.0","--port","6006"]
#CMD ["uvicorn", "main:controller", "--host", "0.0.0.0","--port","15400"]
CMD ["uvicorn", "app.main:controller", "--host", "0.0.0.0","--port","6006", "--reload"]

