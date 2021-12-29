FROM python:3.8.12

ADD . /python-flask
WORKDIR /python-flask
RUN pip3 install Cython==0.28.5
RUN pip install -r requirements.txt