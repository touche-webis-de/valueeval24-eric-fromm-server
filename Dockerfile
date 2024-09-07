FROM python:3.12.5

WORKDIR /
# Install requirements
COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY requester.py /

ENTRYPOINT ["python3", "/requester.py"]
