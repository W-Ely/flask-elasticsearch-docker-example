FROM python:3.8.3-slim-buster as build-system-deps
LABEL service=geo-search
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -qq -y gcc g++ curl git libxml2-dev libxmlsec1-dev libxmlsec1-openssl \
    libxslt1-dev libpq-dev libffi-dev pkg-config gnupg2 --no-install-recommends && \
    curl http://nginx.org/keys/nginx_signing.key | apt-key add - && \
    touch /etc/apt/sources.list.d/nginx.list && \
    echo deb http://nginx.org/packages/mainline/debian/ stretch nginx >> /etc/apt/sources.list.d/nginx.list && \
    echo deb-src http://nginx.org/packages/mainline/debian/ stretch nginx >> /etc/apt/sources.list.d/nginx.list && \
    apt-get update && \
    apt-get install -qq -y nginx=1.17.7-1~stretch --no-install-recommends && \
    apt-get remove -y curl && \
    rm -rf /var/lib/apt/lists/*

#####

FROM geo-search:build-system-deps as build-python-deps
LABEL service=geo-search
ENV DEBIAN_FRONTEND noninteractive

RUN mkdir -p /python-build
WORKDIR /

COPY ./requirements.txt /app/requirements.txt

RUN PYTHONPATH=/python-build/lib/python3.8/site-packages \
    pip install --upgrade pip wheel setuptools\
        --prefix=/python-build \
        --no-warn-script-location \
        --no-cache-dir \
        -r /app/requirements.txt


#####

FROM geo-search:build-system-deps AS release
LABEL service=geo-search
ENV DEBIAN_FRONTEND noninteractive

COPY --from=geo-search:build-python-deps /python-build/ /usr/local/
WORKDIR /geo-search

COPY ./supervisord.conf /etc/supervisord.conf
COPY ./nginx.conf /etc/nginx/nginx.conf

COPY . .

CMD ["supervisord", "-c", "/etc/supervisord.conf", "-n"]
