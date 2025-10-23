FROM ubuntu:latest
RUN apt-get update && apt-get install -y \
       python3 \
       python3-pip

COPY main.py .
RUN pip3 install -r requierements.txt

CMD ["python3", "main.py"]