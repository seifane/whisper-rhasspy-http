FROM pytorch/pytorch:latest

ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get -y install git
RUN pip install git+https://github.com/openai/whisper.git

RUN mkdir /app
WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]