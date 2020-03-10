FROM python:3.4-slim

RUN mkdir /run/uwsgi
ENV PYTHONPATH /opt/knasta/microservicio_chm
WORKDIR /opt/knasta/microservicio_chm
RUN apt-get update
RUN apt-get install -y libpq-dev python-dev gcc

COPY requirements.txt /
RUN pip install -r /requirements.txt

EXPOSE 8006
