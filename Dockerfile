FROM ubuntu:latest
RUN apt-get update && apt-get install -y \
       python3 \
       python3-pip

COPY src/main.py .
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]
