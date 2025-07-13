#!/usr/bin/env python
"""
Supervisor event listener for handling process failures
"""
import sys
import os

def write_stdout(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def write_stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()

def main():
    while True:
        # Transition from ACKNOWLEDGED to READY
        write_stdout('READY\n')
        
        # Read header line
        line = sys.stdin.readline()
        headers = dict([x.split(':') for x in line.split()])
        
        # Read the event data
        data = sys.stdin.read(int(headers['len']))
        
        # Process the event
        write_stderr(f"Process failure detected: {data}\n")
        
        # Transition from READY to ACKNOWLEDGED
        write_stdout('RESULT 2\nOK')

if __name__ == '__main__':
    main()