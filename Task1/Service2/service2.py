import cv2
import pickle
import pika
import sys
import os

IsFirst = True
out = None
frames = 0
MaxFrames = 200

def callback(ch, method, properties, body):
    global IsFirst
    global out
    global frames
    global MaxFrames
    frame = pickle.loads(body)
    if (IsFirst):
        IsFirst = False
        fshape = frame.shape
        fheight = fshape[0]
        fwidth = fshape[1]
        print (fwidth , fheight)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('outdir/output.avi',fourcc, 20.0, (fwidth,fheight))
    else:
        out.write(frame)
        frames += 1
        print(frames)
        if (frames > MaxFrames):
            out.release()
            raise KeyboardInterrupt

def main():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
            channel = connection.channel()
            break
        except:
            continue
    print("Connected to RabbitMQ")                
    channel.basic_consume(queue='frames', auto_ack=True, on_message_callback=callback)
    channel.start_consuming()
   


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

