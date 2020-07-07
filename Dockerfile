# pull official base image
FROM python:3.8.1-slim-buster as builder

ENV HTTP_PROXY=http://10.35.255.65:8080
ENV HTTPS_PROXY=http://10.35.255.65:10443
# set work directory
WORKDIR /usr/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN env | sort
# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc net-tools curl netcat



COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# lint
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install flake8


# COPY requirements.txt .
COPY requirements.dev.txt /tmp/requirements.dev.txt

# install python dependencies
# RUN pip install -r requirements.txt
RUN pip install -r /tmp/requirements.dev.txt


COPY . /usr/src/

RUN flake8 /usr/src/
RUN pip install -e /usr/src
WORKDIR /work
ENTRYPOINT ["/entrypoint.sh"]

#########
# FINAL #
#########

# pull official base image
FROM python:3.8.1-slim-buster as flask_prod

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --group app


# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/flaskerize
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat
COPY --from=builder /usr/src/wheels /wheels
COPY --from=builder /usr/src/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypoint-prod.sh
COPY --from=builder /usr/src/entrypoint.sh .

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

RUN ["chmod", "+x", "/home/app/rest/entrypoint.sh"]

ENTRYPOINT ["/home/app/rest/entrypoint.sh", "fz"]
