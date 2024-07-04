FROM python:3.9-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip install gunicorn

COPY . .

CMD exec gunicorn server:app --bind 0.0.0.0:8000