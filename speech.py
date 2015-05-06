#!/usr/bin/env python3

"""
Dialog interperter.
"""
__author__ = "Mark Birger"
__date__ = "1 Jan 2015"

import subprocess, os, json, urllib.request
from urllib.parse import quote

import pyaudio, wave, math, audioop, time
from collections import deque

ATT_API_TOKEN = "BF-ACSI~2~20150313232123~gFirQv6InqBTx9bkWEc3fMpBApKDZKk0"
# TODO: solve this bug/issue
# def get_att_token():
#     url = 'https://api.att.com/oauth/v4/token'
#     data = "client_id=vif9lbw1cqcklfpjaewt8nhsm3rxyneu&client_secret=aif0secggtrnkuouprogzheqziucepxc&grant_type=client_credentials&scope=SPEECH,STTC,TTS"
#     req = urllib.request.Request(
#         url, 
#         headers={
#             "Accept": "application/json",
#             "Content-Type": "application/x-www-form-urlencoded"
#         },
#         data=str.encode(data)
#     )
#     response = urllib.request.urlopen(req).read().decode("utf-8")
#     return json.loads(response)["access_token"]

def speaker(occupation, tosay):
    """
    TTS engine process by AT&T.
    """
    while True:
        text = tosay.get()
        url = 'https://api.att.com/speech/v3/textToSpeech'
        req = urllib.request.Request(
            url, 
            data=str.encode(text), 
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/35.0.1916.47 Safari/537.36',           
                "Authorization": "Bearer "+ATT_API_TOKEN,
                "Accept": "audio/x-wav",
                "Content-Type": "text/plain"
            }
        )
        # try:
        response = urllib.request.urlopen(req)
        # except urllib.error.HTTPError as err:
        #     if err.code == 400 or err.code == 401:
        #         get_att_token()
        #         response = urllib.request.urlopen(req)
        filename = 'temporary/answer_' + str(int(time.time()))
        output = open(filename, 'wb')
        output.write(response.read())
        output.close()

        occupation.wait()
        occupation.clear()

        chunk = 1024
        wf = wave.open(filename, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(
            format = p.get_format_from_width(wf.getsampwidth()),
            channels = wf.getnchannels(),
            rate = wf.getframerate(),
            output = True)
        data = wf.readframes(chunk)

        while data != '':
            stream.write(data)
            data = wf.readframes(chunk)

        stream.close()
        p.terminate()

        occupation.set()
        # TODO: clear answers database automatically
        # os.remove(filename)

def speaker_google(occupation, tosay):
    """
    TTS engine process.
    """
    # TODO: rewrite it using pyaudio ioutput engine
    while True:
        # TODO: save phrases for later usage
        text = tosay.get()
        url = 'http://translate.google.com/translate_tts?tl=en&q='
        url += quote(text)
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        response = urllib.request.urlopen(req)
        filename = 'temporary/answer_' + str(int(time.time()))
        output = open(filename, 'wb')
        output.write(response.read())
        output.close()
        command = ['mpg123', filename]
        devnull = open('/dev/null', 'w')
        occupation.wait()
        occupation.clear()
        player = subprocess.Popen(command, stdout=devnull, stderr=devnull)
        player.wait()
        occupation.set()
        # TODO: clear answers database automatically
        # os.remove(filename)


def listener(occupation, recognizer_queue, threshold=2500, silence_limit=1):
    prepend = 0.5                   # prepend audio lenth in seconds

    chunk = 1024                    # number of frames in buffer
    audio_format = pyaudio.paInt16  # sampling size and format
    channels = 1                    # number of channels
    rate = 16000#44100                    # sampling rate (samples per second)

    relative = rate / chunk         # chunks per second

    proc = pyaudio.PyAudio()        # create PyAudio object

    # devinfo = proc.get_device_info_by_index(1)
    # if proc.is_format_supported(
    #     rate,  # Sample rate
    #     input_device=devinfo['index'],
    #     input_channels=devinfo['maxInputChannels'],
    #     input_format=audio_format):
    #     print("device supported")

    stream = proc.open(             # open audio stream
        format=audio_format,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk)

    current_data = b''              # current chunk of audio data

    started = False                 # starting flag
    # queue of counted thresholds
    levels = deque(maxlen=int(silence_limit * relative))
    # queue of recorded audio
    previuos = deque(maxlen=int(prepend * relative))
    frames = []                     # recorded frames

    while True:
        # if speaker started to speak
        if not occupation.is_set() and not started:
            # wait till speaker ends
            occupation.wait()
            # clear data for next iteration
            started = False
            levels = deque(maxlen=int(silence_limit * relative))
            previuos = deque(maxlen=int(prepend * relative)) 
            frames = []

        # read chunk of audio stream
        try:
            current_data = stream.read(chunk)
        except OSError: # portaudio OSX troubles
            # dirty fix is reopen the stream
            # TODO: find another way to fix it
            stream = proc.open(
                format=audio_format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk)
            continue

        # add recorded level to level queue
        levels.append(math.sqrt(abs(audioop.avg(current_data, 4))))
        # if more than threshols occurred in level queue
        if sum([x > threshold for x in levels]) > 0:
            # we are occupying sound
            occupation.clear()
            # set up start flag if not setted up
            started = True if not started else started 
            # append recorded frame
            frames.append(current_data)
        # if have silence and record was started
        elif started is True:
            # send raw data to recognizer
            recognizer_queue.put((
                b''.join(list(previuos) + frames),
                proc.get_sample_size(pyaudio.paInt16),
                rate))
            # free sound engine
            occupation.set()
            # clear data for next iteration
            started = False
            levels = deque(maxlen=int(silence_limit * relative))
            previuos = deque(maxlen=int(prepend * relative)) 
            frames = []
        # if silence and recorded not started
        else:
            # record data for future prepend
            previuos.append(current_data)

def recognizer(recognizer_queue, listener_queue):
    while True:
        data, sample_size, rate = recognizer_queue.get()

        url = 'https://api.att.com/speech/v3/speechToText'
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/35.0.1916.47 Safari/537.36',           
                "Authorization": "Bearer "+ATT_API_TOKEN,
                "Accept": "application/json",
                "Content-Type": "audio/raw;coding=linear;rate=16000;byteorder=LE"
            }
        )
        # try:
        response = urllib.request.urlopen(req)
        # except urllib.error.HTTPError as err:
        #     print("warn")
        #     if err.code == 400 or err.code == 401:
        #         get_att_token()
        #         response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))["Recognition"]
        if result["Status"] == "OK":
            listener_queue.put(result["NBest"][0]["ResultText"])
        else:
            print("You> ???")

def recognizer_google(recognizer_queue, listener_queue):
    while True:
        data, sample_size, rate = recognizer_queue.get()
        # save to wav file
        filename = 'temporary/question_'+str(int(time.time()))
        wav_file = wave.open(filename+'.wav', 'wb')
        wav_file.setnchannels(1)
        wav_file.setsampwidth(sample_size)
        wav_file.setframerate(rate)
        wav_file.writeframes(data)
        wav_file.close()
        # convert to flac file
        command = "flac -f" + ' ' + filename +'.wav'
        devnull = open('/dev/null', 'w')
        converter = subprocess.Popen(
            command,
            shell=True,
            stdout=devnull,
            stderr=devnull)
        converter.wait()
        # TODO: clear questions database
        # os.remove(filename)
        # recognize text
        flac_file = open(filename+'.flac', 'rb')
        flac_container = flac_file.read()
        api_key = "AIzaSyDoimriZhFy84NbqLEUU27c_nAEeHpdw18"
        url = "https://www.google.com/speech-api/v2/recognize?output=json&lang=en-us&key="+api_key
        req = urllib.request.Request(
            url, 
            data=flac_container, 
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux i686) Apple\
WebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
                'Content-type': 'audio/x-flac; rate=44100'
            }
        )
        response = urllib.request.urlopen(req)
        os.remove(filename+'.flac')
        response = response.read().decode('utf-8')
        response = response.split('\n', 1)[1]
        if not response:
            print("You> ???")
        else:
            result = json.loads(response)['result'][0]['alternative'][0]['transcript']
            print("You> "+result)
            listener_queue.put(result)
