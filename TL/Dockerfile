FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /TL
COPY requirements.txt /TL/
RUN pip install -r requirements.txt
COPY . /TL/