# This Python file uses the following encoding: utf-8
# filetype = ('r','d')

import datetime

class fileObj:
    """Main file object class"""
    def __init__(self, name=None, size=0, filetype="r", mtime=0):
        date = datetime.datetime(datetime.MINYEAR,1,1)
        self.name = name
        self.size = size
        if filetype == 'r':
            self.filetype = 1
        elif filetype == 'd':
            self.filetype = 2
        self.members = []
        self.date = date.fromtimestamp(mtime)
        
    def add_member(self,member):
        """add another fileObj to array"""
        self.members.append(member)
        if self.filetype == 'd':
            self.size = self.calculate_my_size()
        
    def calculate_my_size(self):
        """TODO: fixme!"""
        size = 0
        for member in self.members:
            size += member.get_size()
        return size
        
    def get_size(self):
        return self.size

    def __str__(self):
        """show name of main object and his members """
        print "<%s>" % self.name
        def showtree(obj,spc):
            """how about members?"""
            for i in obj.members:
                if i.filetype == "d":
                    print "%s[%s]" % (spc, i.name)
                else:
                    print "%s%s" % (spc, i.name)
                showtree(i,spc+".")
        showtree(self,".")
        return ""
