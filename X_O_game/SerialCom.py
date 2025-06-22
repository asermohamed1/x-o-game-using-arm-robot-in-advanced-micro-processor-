import serial.tools.list_ports
import serial
import time

class SerialCom:
    def __init__(self):
        ports = serial.tools.list_ports.comports()

        portsList = []
        for port in ports:
            portsList.append(str(port))
            print(str(port))

        value = input("Select port: COM")

        port = ""

        for i in range(len(portsList)):
            if "COM"+value in portsList[i]:
                port = portsList[i].split(" ")[0]
                break

        if(port == ""):
            print("Invalid port")
            self.ser = None
            exit()

        self.ser = serial.Serial(port, 9600, timeout=1)


    def write(self, command):
        self.ser.write(command.encode())
    
    def recieve(self):
        if(self.ser.in_waiting > 0):
            return self.ser.readline().decode()
        else:
            return "No data"
    def close(self):
        self.ser.close()

    def open(self):
        self.ser.open()