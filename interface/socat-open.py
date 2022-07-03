#/usr/bin/env python3
import os

pid = os.fork()

if pid == 0:
    os.execlp('socat','socat','tcp-listen:8888,reuseaddr','file:/dev/ttyUSB0,nonblock,cs8,b115200,cstopb=0,raw,echo=0')

with open('pid-socat-server.txt','w') as pidFile:
    pidFile.write(str(pid))

pid = os.fork()

if pid == 0:
    os.execlp('sudo','sudo','socat','PTY,raw,echo=0,b115200,link=/dev/ttyVUSB0','tcp:127.0.0.1:8888')

with open('pid-socat-client.txt','w') as pidFile:
    pidFile.write(str(pid))
