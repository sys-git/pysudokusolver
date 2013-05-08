'''
Created on 15 Mar 2013

@author: francis.horsman:gmail.com
'''

class iModelNotifications(object):
    @staticmethod
    def ALL():
        return 1
    @staticmethod
    def CELL():
        return 2
    @staticmethod
    def ROW():
        return 3
    @staticmethod
    def COL():
        return 4
    @staticmethod
    def ELEMENT():
        return 5
    @staticmethod
    def UNSOLVABLE():
        return 6
    @staticmethod
    def SOLVED():
        return 7
    @staticmethod
    def UPDATE():
        return 8
    @staticmethod
    def CUSTOM():
        return 9
    @staticmethod
    def LOGIC_ERROR():
        return 10

