import logging
from threading import Thread

import serial
import serial.tools.list_ports

import struct
from queue import Queue


class MotorController:
    def __init__(self):

        self.pico = None

        self.prevData = None
        self.structFormat = "bh"

        self.queue = Queue()
        self.running = True

    def getPorts(self):
        return serial.tools.list_ports.comports()

    def start(self, port=None):
        t = Thread(target=self.get, args=(port,))
        t.start()
        return self

    def get(self, port=None):

        try:
            self.pico = serial.Serial(
                port="/dev/tty.usbmodem1201" if port == None else port,
            )
        except Exception as e:
            logging.error(f"Motor controller failed to start: {repr(e)}")
            return

        speed = 0
        direction = 0

        while self.running:
            (direction, speed) = self.queue.get()
            self.pico.write(struct.pack(self.structFormat, direction, speed))

    def stop(self):
        self.running = False
        if not self.pico:
            return
        self.pico.write(struct.pack(self.structFormat, 0, 0))
        self.pico.close()
