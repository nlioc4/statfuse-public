FROM python:3.12-alpine as statfuse

COPY requirements.txt /statfuse/requirements.txt

RUN pip install -r /statfuse/requirements.txt

COPY . /statfuse

WORKDIR /statfuse

CMD ["flask", "run", "--host=0.0.0.0"]





