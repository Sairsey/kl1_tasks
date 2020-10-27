FROM python:3.7
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavformat-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY ./requiments.txt /project/requirements.txt 
RUN pip3 install --upgrade pip && pip3 install -r /project/requirements.txt 
COPY ./service1.py /project/service1.py
WORKDIR /project
CMD ["python3", "service1.py"]

