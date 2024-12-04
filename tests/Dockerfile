FROM python:3
RUN apt-get update -y
RUN apt-get install -yy --no-install-recommends --no-install-suggests bash fish tcsh zsh
RUN pip install --upgrade pip
COPY . /src
RUN pip install /src
