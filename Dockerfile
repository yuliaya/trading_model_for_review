FROM ubuntu:latest
MAINTAINER Julia
RUN apt-get update -y
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-dev
RUN apt-get install -y build-essential
RUN apt-get install -y python3-setuptools
COPY . /app
WORKDIR /app
RUN pip install Cython==0.28.5
RUN pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]