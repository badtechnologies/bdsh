# Bad Dynamic Shell Interpreter Dummy Code (for BadBand SSH Server)

newline = '\r\n'

def run_line(line):
	args = line.decode().split(' ')
	return f"Invalid command: {args[0]}{newline}".encode()

def get_header():
	return f"BadOS Dynamic Shell (v0.1) (BadBandSSH){newline}(c) Bad Technologies. All rights reserved.{newline}".encode()

def get_prompt():
	return f"{newline}$ ".encode()
