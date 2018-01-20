import time
import os


class Outputer:

    def __init__(self, e):
        self.data = list()
        self.current_count = int()
        self.total_count = int()
        self.buffer_size = 3000
        self.buffer_trigger = e
        self.end_writing = False

    def collect_data(self, data):
        self.data.extend(data)
        self.current_count += len(data)

    def write_data(self):
        print("\n\n*********\twritten data: %d\t*********\n"%self.total_count)
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path += ("/data/" + str(int(time.time())) + ".txt")
        with open(path, 'w') as f:
            for item in self.data:
                f.write(item + "\n")
        print("%s data saved in file: %s"%(self.current_count, path))
        print("**********************************************")

    def export_data(self, a, b):
        while not self.end_writing:
            self.buffer_trigger.wait()
            self.write_data()
            self.data = list()
            self.total_count += self.current_count
            self.current_count = int()
            self.buffer_trigger.clear()
