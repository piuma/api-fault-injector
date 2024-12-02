# Dockerfile to build an image/container to host api-fault-injector

FROM abhinavsingh/proxy.py
LABEL maintainer = "Piuma <piuma@piumalab.org>"

#Set working directory
WORKDIR api-fault-injector

# Install packages listed in requirements.txt file
RUN pip install -r requirements.txt

#Make port 8899 available to the container
EXPOSE 8899/tcp

# Execute command
ENTRYPOINT [ "python", "api-fault-injector.py" ]

CMD [ \
  "--hostname=0.0.0.0" \
  ]
