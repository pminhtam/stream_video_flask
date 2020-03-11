# https://github.com/go2starr/py-flask-video-stream

from __future__ import print_function

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import logging
import os
import re
import sys
import time
import pprint
from datetime import datetime

import mimetypes
from flask import Response, render_template
from flask import Flask
from flask import send_file
from flask import request
import argparse
parser = argparse.ArgumentParser(description="Deepfake detection")
parser.add_argument('--path', default="data/train/", help='path to video ')
args = parser.parse_args()
# video_dir = 'D:\griffith\dfdc_train_part_0'
video_dir = args.path
LOG = logging.getLogger(__name__)
app = Flask(__name__)

VIDEO_PATH = '/video'
# VIDEO_PATH = 'D:\griffith\dfdc_train_part_0'

MB = 1 << 20
BUFF_SIZE = 10 * MB

@app.route('/show/<video_file>')
def home(video_file):
    print("33 home request : ",video_file)
    LOG.info('Rendering home page')
    response = render_template(
        'video.html',
        time=str(datetime.now()),
        video=VIDEO_PATH +"/"+ video_file,
        # path = 'D:/griffith/dfdc_train_part_0/'
    )
    return response


@app.route('/')
@app.route('/home')
def index():
    video_files = [f for f in os.listdir(video_dir) if f.endswith('mp4')]
    video_files_number = len(video_files)
    return render_template("index.html",
                        title = 'Home',
                        video_files_number = video_files_number,
                        video_files = video_files)
def partial_response(path, start, end=None):
    LOG.info('Requested: %s, %s', start, end)
    file_size = os.path.getsize(path)

    # Determine (end, length)
    if end is None:
        end = start + BUFF_SIZE - 1
    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)
    length = end - start + 1

    # Read file
    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    LOG.info('Response: %s', response)
    LOG.info('Response: %s', response.headers)
    return response

def get_range(request):
    range = request.headers.get('Range')
    LOG.info('Requested: %s', range)
    m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None
    
@app.route(VIDEO_PATH+"/<path>")
def video(path):
    # path = 'videos/movie.mp4'
    print("105 video path : ",path)
    # path = 'D:/griffith/dfdc_train_part_0/acdkfksyev.mp4'
    path = os.path.join(video_dir, path)
#    path = 'demo.mp4'

    start, end = get_range(request)
    return partial_response(path, start, end)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    HOST = '0.0.0.0'
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(4444)
    IOLoop.instance().start()

    # Standalone
    # app.run(host=HOST, port=8080, debug=True)




