FROM alpine:3.18.0

RUN apk add --no-cache --update \
	python3 \
	py3-pip
RUN pip3 install --no-cache-dir \
	"falcon<3" \
	falcon-auth \
	falcon-cors \
	gunicorn!=20.0.0\
    requests
WORKDIR /simplerest
COPY simplerest.py .

CMD ["gunicorn", "-b", "0.0.0.0:8090", "simplerest:api"]
