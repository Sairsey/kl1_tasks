import cv2
from multiprocessing import Process, Manager, Value
import json
import pika
import pickle

def grabber(path, q, n):
    with n.get_lock():
        n.value += 1
    cap = cv2.VideoCapture(path)
    i = 0
    while (cap.isOpened()):
        ret, frame = cap.read()
        if (ret != True):
            break
#        print("Grabbed frame")
        q.put(frame)
#        if i > 20:
#            break
#        else:
#            i += 1
    with n.get_lock():
        n.value -= 1
    print("grabber quitted")

def resizer(q_in, q_out, size, n_grabbers):
    while(n_grabbers.value > 0):
        if (not q_in.empty()):
            frame = q_in.get()
            newframe = cv2.resize(frame, size)
 #           print("Frame resized")
            q_out.put(newframe)
    print("resizer quitted")

def rabitter(q_in, n_grabbers):
    while(n_grabbers.value > 0):
        if (not q_in.empty()):
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()
            channel.queue_declare(queue='frames')
            frame = q_in.get()
#            print("Publish frame")
            channel.basic_publish(exchange='', routing_key='frames', body=pickle.dumps(frame))
            connection.close()
    print("rabbiter quitted")

if __name__ == '__main__':
    config = []
    with open("config.json") as f:
        config = json.load(f)

    with Manager() as manager:
        Queue1 = manager.Queue()
        Queue2 = manager.Queue()
        GrabbersNum = Value("i", 0)
        Grabbers = []
        Resizers = []
        Rabbiter = Process(target=rabitter, args=(Queue2, GrabbersNum))
        for i in config["paths"]:
            proc = Process(target=grabber, args=(i, Queue1, GrabbersNum))
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
