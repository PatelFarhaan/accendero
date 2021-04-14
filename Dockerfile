FROM ubuntu:latest

ENV PROJECT_SQLALCHEMY_DATABASE $PROJECT_SQLALCHEMY_DATABASE

EXPOSE 5000

WORKDIR /farhaan

COPY app.py /farhaan

COPY requirements.txt /farhaan

COPY project /farhaan/project

RUN apt-get update && apt-get upgrade -y

RUN apt-get install sudo -y

RUN apt-get install python3-pip -y

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]