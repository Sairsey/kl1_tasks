FROM ubuntu:18.04
RUN apt-get update && apt-get install -y python3.7 python3.7-dev python3-pip cmake clang make gcc g++ libgl1-mesa-glx
COPY ./requiments.txt /project/requirements.txt 
RUN pip3 install --upgrade pip && pip3 install opencv-python && pip3 install pika && pip3 install pyaml
COPY ./service2.py /project/service2.py
WORKDIR /project
CMD ["python3", "service2.py"]

