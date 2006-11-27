# This Python file uses the following encoding: utf-8
# filetype = ('r','d')

import datetime

class fileObj:
    """Main file object class"""
    def __init__(self, name=None, size=0, filetype="r", mtime=0, members=[], tmproot=''):
        date = datetime.datetime(datetime.MINYEAR,1,1)
        self.name = name
        self.size = size
        self.filetype = filetype
        self.members = members
        self.date = date.fromtimestamp(mtime)
        
    def add_member(self,member):
        if self.filetype == 'd':
            self.size = calculate_my_size(self)
        pass
        
    def calculate_my_size(self):
        size = 0
        for member in self.members:
            size += member.get_size()
        return size
        
    def get_size(self):
        return self.size

