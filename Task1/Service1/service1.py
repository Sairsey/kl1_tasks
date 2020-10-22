import cv2
from multiprocessing import Process, Manager, Value
import queue
import yaml
import pika
import pickle

def grabber(path, q, n):
    with n.get_lock():
        n.value += 1
    cap = cv2.VideoCapture(path)
    while (cap.isOpened()):
        ret, frame = cap.read()
        if (ret != True):
            break
        q.put(frame)
    with n.get_lock():
        n.value -= 1
    print("grabber quitted")

def resizer(q_in, q_out, size, n_grabbers):
    while n_grabbers.value > 0:
        try:
            frame = q_in.get_nowait() 
        except queue.Empty:
            continue            
        newframe = cv2.resize(frame, size)
        q_out.put(newframe)
    print("resizer quitted")

def rabitter(q_in, n_grabbers):    
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
            channel = connection.channel()
            channel.queue_declare(queue='frames')
            break
        except:
            continue
    while n_grabbers.value > 0:
        try:
            frame = q_in.get_nowait()
        except queue.Empty:
            continue                        
        print("Connected to RabbitMQ")        
        flag = True # Trying to send untill we sucessful.
        while flag:
            try:
                channel.basic_publish(exchange='', routing_key='frames', body=pickle.dumps(frame))
            except (pika.exceptions.ConnectionClosedByBroker, pika.exceptions.AMQPChannelError, pika.exceptions.AMQPConnectionError):
                while True:
                    try:
                        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
                        channel = connection.channel()
                        channel.queue_declare(queue='frames')
                        break
                    except:
                        continue
                continue
            flag = False
            
    print("rabbiter quitted")
    connection.close()

if __name__ == '__main__':
    config = []
    with open("outdir/config.yaml") as f:
        config = yaml.load(f)

    with Manager() as manager:
        Queue1 = manager.Queue()
        Queue2 = manager.Queue()
        GrabbersNum = Value("i", 0)
        Grabbers = []
        Resizers = []
        Rabbiter = Process(target=rabitter, args=(Queue2, GrabbersNum))
        for i in config["paths"]:
            proc = Process(target=grabber, args=("outdir/" + i, Queue1, GrabbersNum))
            Grabbers.append(proc)


        for i in range(int(config["resizers_num"])):
            proc = Process(target=resizer, args=(Queue1, Queue2, (int(config["width"]), int(config["height"])), GrabbersNum))
            Resizers.append(proc)

        for i in Grabbers:
            i.start()

        for i in Resizers:
            i.start()

        Rabbiter.start()

        for i in Grabbers:
            i.join()

        for i in Resizers:
            i.join()

        Rabbiter.join()
