import time
import zmq
import SDC_DataPlatform as SDC

context = zmq.Context()

work_receiver = context.socket(zmq.PULL)
work_receiver.connect("tcp://127.0.0.1:5557")

poller = zmq.Poller()
poller.register(work_receiver, zmq.POLLIN)

# Loop and accept messages from both channels, acting accordingly
while True:
    socks = dict(poller.poll(1000))

    if socks:
        if socks.get(work_receiver) == zmq.POLLIN:
            recv = work_receiver.recv(zmq.NOBLOCK).decode("utf-8")
            print("got message: " + recv)
            c = SDC.ParamCommand.FromJson(recv)