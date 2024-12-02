# Dockerfile to build an image/container to host api-fault-injector

FROM abhinavsingh/proxy.py
LABEL maintainer = "Piuma <piuma@piumalab.org>"

# Clone repository for Docker Image creation
RUN apk add git && \
    git clone https://github.com/piuma/api-fault-injector.git && \
    apk del git && \
    cd api-fault-injector && \
    pip install -r requirements.txt

#Set working directory
WORKDIR api-fault-injector

#Make port 8899 available to the container
EXPOSE 8899/tcp

# Execute command
ENTRYPOINT [ "python", "api-fault-injector.py" ]

CMD [ \
  "--hostname=0.0.0.0" \
  ]
