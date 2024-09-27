# Specify the base image
FROM ghcr.io/puppeteer/puppeteer:latest

# Set environment variables
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER root

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip pipx && \
    apt-get clean && \
    pipx ensurepath


WORKDIR /tmp

COPY . /tmp
#COPY ../requirements.txt /tmp

RUN python3 -m venv $VIRTUAL_ENV
RUN pip3 install --no-cache-dir -r requirements.txt

# Create app directory in the container
WORKDIR /usr/src/app

# USER pptruser
# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY crawler/package*.json ./

# Install dependencies
RUN npm install

# Bundle app source
COPY crawler .

COPY . /tmp

# Your app binds to port 3000 so you'll use the EXPOSE instruction to have it mapped by the docker daemon
EXPOSE 3000

# Define the command to run your app using CMD which defines your runtime
CMD [ "node", "app.js" ]
