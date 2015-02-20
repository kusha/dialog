#!/usr/bin/env python3

from parser import Parser
from scope import Scope
from returns import Returns
import link_parser

import multiprocessing
import json

from dialog import Dialog

class Instance(Dialog):
    """
    Dialog interperter connected with websockets.
    """
    def start_server(self, to_user, to_ds):
        """
        Interprets dialog
        """
        # occupation = multiprocessing.Event()
        # listener_queue = multiprocessing.Queue(maxsize=0)
        # recognizer_queue = multiprocessing.Queue(maxsize=0)
        # speaker_queue = multiprocessing.Queue(maxsize=0)
        # speaker = multiprocessing.Process(
        #     target=speech.speaker,
        #     args=(occupation, speaker_queue, ))
        # recognizer = multiprocessing.Process(
        #     target=speech.recognizer,
        #     args=(recognizer_queue, listener_queue, ))
        # listener = multiprocessing.Process(
        #     target=speech.listener,
        #     args=(occupation, recognizer_queue, ))
        # speaker.start()
        # recognizer.start() # IN CASE OF SPEECH RECOGNITION
        # listener.start()   # IN CASE OF SPEECH RECOGNITION
        # occupation.set()
        # print("======")
        # for state in self.expected:
        #     print("\t%s" % (state))
        # print("======")
        while True:
            # process routines answers
            answers = self.returns.get_returns()
            for answer in answers:
                tosay, questions = answer.accept()
                to_user.put(json.dumps({'type': 'phrase', 'text': tosay}))
                self._extend_expected(questions)
            # process input
            if not to_ds.empty():
                input_origin = to_ds.get()
                # input_phrase = listener_queue.get() # IN CASE OF SPEECH RECOGNITION
                input_phrase = link_parser.parse(input_origin)
                states_probability = []
                for state in self.expected:
                    # print(state, state.compare(input_phrase))
                    states_probability.append((state, state.compare(input_phrase)))
                states_probability = sorted(states_probability, key=lambda x: x[1], reverse=True)
                # print("======")
                # for state in states_probability:
                #     print("%.2f\t%s" % (state[1], state[0]))
                # print("======")
                state = states_probability[0][0]
                if states_probability[0][1] < 0.2:
                    # print("Bot> ???")
                    to_user.put(json.dumps({
                        'type': 'origin',
                        'text': input_origin
                    }))
                    to_user.put(json.dumps({'type': 'unknown'}))
                    #TODO: save unknown request, with state!!!
                else:
                    to_user.put(json.dumps({
                        'type': 'interpretation',
                        'origin': input_origin,
                        'phrase': str(state),
                        'similarity': states_probability[0][1]
                    }))
                    tosay, questions = state.accept(input_phrase)
                    for answer in tosay:
                        if answer != "":
                            # speaker_queue.put(answer)
                            # print("Bot> "+answer)
                            to_user.put(json.dumps({'type': 'phrase', 'text': answer}))
                    self._extend_expected(questions)

from main_slave import export

py_filename = "main_slave.py"
ddl_filename = "examples/demo.dlg"

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

import time, os.path

class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return False

    def open(self):
        # probably start handlers
        pass

        # print("starting dialog system")
        # self.write_message("Starting dialog system")
        dialog = Instance(export)
        # self.write_message("Using dialog description from %s" \
        #     % (dialog_description))
        dialog.load(ddl_filename)
        self.to_user = multiprocessing.Queue(maxsize=0)
        self.to_ds = multiprocessing.Queue(maxsize=0)
        self.dialog_system = multiprocessing.Process(
            target=dialog.start_server,
            args=(self.to_user, self.to_ds, ))
        self.dialog_system.start()
        self.producer_process = multiprocessing.Process(
            target=self.producer,
            args=())
        self.producer_process.start()
      
    def on_message(self, message):
        message = json.loads(message)
        if message['type'] == 'phrase':
            print(">", message)
            self.to_ds.put(message['text'])
        elif message['type'] == 'sources':
            global py_file
            global ddl_file
            ddl_modified = int(os.path.getmtime(ddl_filename))
            py_modified = int(os.path.getmtime(py_filename))
            ddl_content = open(ddl_filename, "rb").read().decode("utf-8")
            py_content = open(py_filename, "rb").read().decode("utf-8")
            response = {
                "type": "sources",
                "modified": max(py_modified, ddl_modified) * 1000,
                "description": {
                    "filename": ddl_filename,
                    "content":  ddl_content,
                    "modified": ddl_modified * 1000
                },
                "code": {
                    "filename": py_filename,
                    "content":  py_content,
                    "modified": py_modified * 1000
                }
            }
            self.to_user.put(json.dumps(response))
        elif message['type'] == 'interpretation':
            print(">", message)
            # print(message['origin'])
            #TODO: save reports

    def on_close(self):
        self.producer_process.terminate()
        self.dialog_system.terminate()

    def producer(self):
        while True:
            message = self.to_user.get()
            time.sleep(0.5)
            print("<", message)
            self.write_message(message)

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.render('index.html')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = (
            # (r'/', MainHandler),
            (r'/api/?', WSHandler),
        )
        tornado.web.Application.__init__(self, handlers)

application = Application()
http_server = tornado.httpserver.HTTPServer(application)
http_server.listen(8888)
tornado.ioloop.IOLoop.instance().start()
