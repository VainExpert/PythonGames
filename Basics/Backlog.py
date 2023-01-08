#Program Logger
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
from datetime import datetime

class Backlog():

    def __init__(self, prog):
        self.program = prog		
        self.dir = "./{}/".format(prog)
        
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)
        
        self.file = "{}-{}.txt".format(self.format_time().replace(" ", "_").replace(":", ""), prog)

        #Init File with Title
        self.f = open(self.dir + self.file, mode='a+', encoding='utf-8')
        self.f.write("{} - {}\n".format(self.format_time(), prog))
        self.f.close()

    def format_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log(self, flag, string):

        self.f = open(self.dir + self.file, mode='a+', encoding='utf-8')

        string = string.split("\n")
        for line in string:
            
            print(line)
            self.f.write("{} - {} - {}\n".format(self.format_time(), flag.upper(), line))
            
        self.f.close()

    def subtitle(self, string):

        self.f = open(self.dir + self.file, mode='a+', encoding='utf-8')
        print(string)
        self.f.write("{} - {}\n".format(self.format_time(), string))
        self.f.close()

    def save(self):

        self.f = open(self.dir + self.file, mode='a+', encoding='utf-8')
        print("{} has finished!".format(self.program))
        self.f.write("{} - {} has finished!".format(self.format_time(), self.program))
        self.f.close()
