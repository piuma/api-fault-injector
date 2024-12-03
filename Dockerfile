FROM python:3.13-alpine
LABEL maintainer="Danilo <danilo@piumalab.org>"

WORKDIR /app

COPY api-fault-injector.py /app/
COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

#Make port 8899 available to the container
EXPOSE 8899/tcp

# Execute command
ENTRYPOINT ["python3", "api-fault-injector.py", "--hostname=0.0.0.0"]
