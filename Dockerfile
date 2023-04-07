
# use ubuntu
FROM ubuntu:latest

# install python3
RUN apt-get update && apt-get install -y python3 python3-pip

# copy requirements.txt
COPY requirements.txt /app/requirements.txt

# install python packages
RUN pip3 install -r /app/requirements.txt

# copy the app
COPY . /app

# set the working directory
WORKDIR /app

# run the app
CMD python3 app.py

