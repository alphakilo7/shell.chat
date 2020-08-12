import socket
from INIParser import *

def run():
	inir = INIParser("shellchat.ini")

	print(inir.get_all())

if __name__ == "__main__":
	run()

