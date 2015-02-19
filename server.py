#!/usr/bin/env python3

from parser import Parser
from scope import Scope
from returns import Returns
import link_parser

import multiprocessing

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
                to_user.put(tosay)
                self._extend_expected(questions)
            # process input
            if not to_ds.empty():
                input_phrase = to_ds.get()
                # input_phrase = listener_queue.get() # IN CASE OF SPEECH RECOGNITION
                input_phrase = link_parser.parse(input_phrase)
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
                    to_user.put("no answer")
                else:
                    tosay, questions = state.accept(input_phrase)
                    for answer in tosay:
                        if answer != "":
                            # speaker_queue.put(answer)
                            # print("Bot> "+answer)
                            to_user.put("answer: "+answer)
                    self._extend_expected(questions)

from main_slave import export

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        # probably start handlers
        pass

        # print("starting dialog system")
        # self.write_message("Starting dialog system")
        dialog = Instance(export)
        # self.write_message("Using dialog description from %s" \
        #     % (dialog_description))
        dialog.load("examples/tickets.dlg")
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
        self.to_ds.put(message)

    def on_close(self):
        self.producer_process.terminate()
        self.dialog_system.terminate()

    def producer(self):
        while True:
            self.write_message(self.to_user.get())

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