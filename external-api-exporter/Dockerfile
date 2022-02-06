FROM python:3.9

COPY requirements.txt /opt/app/
WORKDIR /opt/app

# https://forums.raspberrypi.com/viewtopic.php?t=289084
ENV CFLAGS=-fcommon

RUN pip install --upgrade pip \
  && pip install --upgrade setuptools \
  && pip install -r requirements.txt

COPY . /opt/app/

CMD ["python3", "/opt/app/main.py"]
