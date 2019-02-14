import threading
import time

class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.count = 10

    def run(self):
        while self.count > 0 and not self.event.is_set():
            print (self.count)
            self.count -= 1
            self.event.wait(1)
        print('finish')

    def stop(self):
        self.event.set()

tmr = TimerClass()
tmr.start()
print('start')
time.sleep(3)

tmr.stop()
time.sleep(3)
stat = tmr.is_alive()
print(stat)
tmr = TimerClass()
tmr.start()
print('again')
stat = tmr.is_alive()
while(stat):
    stat = tmr.is_alive()
    time.sleep(3)
    print(stat)
