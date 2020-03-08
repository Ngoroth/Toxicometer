FROM python:3.8

ENV HOME /root
ENV PYTHONPATH "/usr/lib/python3/dist-packages:/usr/local/lib/python3.8/site-packages"

WORKDIR /app
ADD . /app

# Install dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get install -y \
        gcc \
        build-essential \
        zlib1g-dev \
        wget \
        unzip \
        cmake \
        python3-dev \
        gfortran \
        libblas-dev \
        liblapack-dev \
        libatlas-base-dev \
    && apt-get clean

# Install Python packages
RUN pip install --upgrade pip \
    && pip install \
        ipython[all] \
        numpy \
        nose \
        matplotlib \
        pandas \
        scipy \
        sympy \
        cython \
        dostoevsky \
        python-telegram-bot \
    && rm -fr /root/.cache

RUN python -m dostoevsky download fasttext-social-network-model

COPY . .

CMD [ "python", "./TelegramBot.py" ]
