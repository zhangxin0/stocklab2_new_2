FROM alpine:latest

RUN apk add --update --no-cache mariadb-connector-c-dev \
	&& apk add --no-cache --virtual .build-deps \
		mariadb-dev \
		gcc \
		musl-dev \
	&& apk del .build-deps

FROM python:latest

WORKDIR /app

COPY . /app

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 8999

CMD ["python3","./manager.py","runserver"]