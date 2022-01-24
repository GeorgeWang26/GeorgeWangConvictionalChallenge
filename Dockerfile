FROM python:3.9.9

WORKDIR /convictional
COPY api-server api-server
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python3", "api-server/server.py"]