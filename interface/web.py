import flask
import os
import subprocess
import signal

app = flask.Flask(__name__)
serialPort = '/dev/ttyVUSB0'
python2env = '../../env2/bin/python'

@app.route('/')
def index():
    return flask.render_template('cncinator.html',status=flask.request.args.keys())

@app.route('/upload', methods=['GET','POST'])
def upload():
    if flask.request.method == 'POST':
        if 'file' not in flask.request.files:
            flask.flash('No file part')
            return flask.redirect('/?noFile')
        file = flask.request.files['file']
        if file.filename == '':
            flask.flash('No selected file')
            return flask.redirect('/?noFile')
        if file:
            file.save(os.path.join('upload', 'upload.gcode.tmp'))
            subprocess.run('echo -1 > check.txt', shell=True)
            subprocess.run('./stream.py -c ./upload/upload.gcode.tmp '+serialPort, shell=True)

            with open('check.txt', 'r') as checkFile:
                error_count = checkFile.readline()

            if int(error_count)==0:
                os.rename(os.path.join('upload', 'upload.gcode.tmp'),os.path.join('upload', 'upload.gcode'))
                return flask.redirect('/?okFile')
            os.remove(os.path.join('upload', 'upload.gcode.tmp'))
            return flask.redirect('/?fileError')
    return flask.redirect('/')

@app.route('/start')
def start():
    if not os.path.isfile(os.path.join('upload', 'upload.gcode')):
        return flask.redirect('/?noFile')
    if os.path.isfile('status.txt'):
        with open('status.txt', 'r') as statusFile:
            status = statusFile.read().splitlines()[0]

        if not (status == 'End' or status == 'Aborted'):
            return flask.redirect('/?runningErr')

    pid = os.fork()
    if pid > 0:
        with open('pid.txt','w') as pidFile:
            pidFile.write(str(pid))
        return flask.redirect('/?running')

    os.execl(python2env,python2env,'stream.py',os.path.join('upload', 'upload.gcode'),serialPort)

@app.route('/probe')
def probe():
    if os.path.isfile('status.txt'):
        with open('status.txt', 'r') as statusFile:
            status = statusFile.read().splitlines()[0]

        if not (status == 'End' or status == 'Aborted'):
            return flask.redirect('/?runningErr')

    pid = os.fork()
    if pid > 0:
        with open('pid.txt','w') as pidFile:
            pidFile.write(str(pid))
        return flask.redirect('/?running')

    os.execl(python2env,python2env,'stream.py','-p','probe.gcode',serialPort)

@app.route('/pause-resume')
def pauseResume():
    if not os.path.isfile('pid.txt'):
        return flask.redirect('/?noRunningErr')
    with open('pid.txt','r') as pidFile:
        pid = pidFile.read().splitlines()[0]
    os.kill(int(pid),signal.SIGUSR1)
    return flask.redirect('/?running')

@app.route('/abort')
def abort():
    if not os.path.isfile('pid.txt'):
        return flask.redirect('/?noRunningErr')
    with open('pid.txt','r') as pidFile:
        pid = pidFile.read().splitlines()[0]
    os.kill(int(pid),signal.SIGTERM)
    return flask.redirect('/')

@app.route('/status')
def getStatus():
    if not os.path.isfile('status.txt'):
        return flask.jsonify({'status':'Stop'})
    with open('status.txt','r') as file:
        status = file.read().splitlines()[0]
    return flask.jsonify({'status':status})
