# Dialog system framework


## Overview

This project implements dialog system (DS) framework. This framework is designed for robotic pruposes, but it's possible to create spoken dialog interface for any Python software.

<!--Project structure:

	.
	├── LICENSE.txt
	├── README.md
	├── data
	│   ├── answers
	│   │   └── answer_XXXX.mp3
	│   ├── questions
	│   │   └── question_XXXX.wav
	│   └── sentences.db
	├── dialog
	│   ├── __init__.py
	│   ├── interpreter.py
	│   ├── link_parser.py
	│   ├── parser.py
	│   ├── phrase.py
	│   ├── returns.py
	│   ├── scope.py
	│   ├── server.py
	│   ├── speech.py
	│   └── states.py
	├── docs
	│   └── ...
	├── examples
	│   ├── assistant.dlg
	│   ├── demo.dlg
	│   ├── echo.dlg
	│   ├── features_demo
	│   ├── pizza_order
	│   ├── pr2_control
	│   │   ├── movement.py
	│   │   └── pr2_control.py
	│   ├── tickets.dlg
	│   └── web_interface
	│       └── main_slave.py
	├── remote
	│   ├── spoken_mode.py
	│   └── text_mode.py
	├── setup.py
	├── test.py
	└── tests-->


## Documentation

Implemented framework isn't complicated, so it uses light-weight document generator Pycco. To build a documentation, simply run this command at the repository root.

	pycco ./dialog/*.py -d ./docs
	
## Virtual environment installation

Make sure, that you have a Python3 and `pip3` and/or `easy_install-3.x` installed.

	sudo apt-get install python3-setuptools python3.4-dev python3-pip



You should see a path to executable. If it's available, you can run initialization script:

	. ./init.sh

`init.sh` file creates virtual environment, downloads and compiles Link Grammar Parser. 

Anyway, to run spoken dialog system you also need to install this packages:

	sudo apt-get install portaudio19-dev mpg123 flac
	
After, you can run examples 
	
	python3 examples/pr2_control/main.py
	
To leave a virtual environment:

	deactivate

To activate an environment again:

	source env/bin/activate
	
To leave and delete a virtual environment:

	. ./clean.sh
	
## Custom installation


Recommended way to install this package is using the pip3. Run this command inside of a project directory.

	pip3 install ./

If you don't have a root:

	pip3 install --user ./
	
After this command, you can import inside of your python3 programs. Also this installation adds a command-line `dialog_system` command. Use this command to run slave activity code.
	
To uninstall this package:

	pip3 uninstall dialog
	
## Dependencies
	
This DS framework use Link Grammar parser for natural language processing. You can install Link Grammar parser from the aptitude:

	sudo apt-get install link-grammar
	
Another option is to compile from sources: http://www.abisource.com/projects/link-grammar/#download. DS tested with 5.2.5 version.
	
If you would like to run spoken dialog system (not in text mode):

	sudo apt-get install portaudio19-dev mpg123 flac
	easy_install-3.x pyaudio
	
For WebSocket DS you also need a Tornado webserver:

	pip3 install tornado
	
## Getting started

Your code should have this structure:

	from dialog import Dialog
	
	# your variables definitions
	# your functions/callable objects definition

	if __name__ == "__main__":
    	DLG = Dialog(globals(), storage="./")
    	DLG.load("example.dlg")
    	DLG.start_spoken()
 
In storage directory DS will create `tmp` folder *(changed! for now, data is link-grammar data folder)* for recorded answers/questions and sentences database. Storage directory by default is `./`. `DLG.start_text()` оr `DLG.start_spoken()` define spoken mode or text mode.

## Dialog description files

`.dlg` file describe a dialog model.

## Examples

First of all, take a look at the unfinished documentation here: http://markbirger.info/dialog/. It also includes version 0.2 interactive demo. This version doesn't support duplex routines, but can explain some principles.

In `examples` directory you can find a few usage examples:

- **features_demo** uses all DS framework features
- **pr2_control** allows to control PR2 robot
- **slave_mode** implements the same as a features_demo, but for slave activity code execution

## PR2 implementation

### Microphone issue

The PR2 robot don't have an access to Kinect microphone. Spoken DS isn't be able to record an audio at the PR2. We've created a `DLG.start_socket(port=42424)` option to run DS. In this example dialog system listens 42424 port, receives text messages and responds with speech. You need to run special remote configuration at the basestation, which can send recognized messages to the socket.

Run remote client in text mode:

	python3 remote/text_mode.py -p 42424 127.0.0.1
	python3 remote/spoken_mode.py -p 42424 127.0.0.1
	
*Note, that spoken mode client stores question in `./tmp/` directory!*

### Python 2 issue

PR2 has a ROS hydro onboard. hydro distribution uses Python 2 as a default interpreter and it wasn't possible to run Python3 program, which uses rospy. Recommended way to solve this issue is `execnet` module:

	pip3 install execnet
	
This module allows to communicate between Python2 and Python3 interpreters. Take a look at `examples/pr2_control/` for an example.

### How to run dialog system with pr2 simulation

Run your ROS hydro or connect to robodev1.fit.vutbr.cz server with this instruction [Robodev1 How to get remote desktop](http://merlin.fit.vutbr.cz/wiki/index.php/Robodev1).

- Create an empty work catkin workspace
- Put this repo ([PR2/pr2_simulator](https://github.com/PR2/pr2_simulator)) inside of the `src/` directory
- Make catkin workspace
- `source devel/setup.bash`
- `vglrun roslaunch pr2_gazebo pr2_empty_world.launch`

You should see a PR2 robot inside of the simulation. Then you can run your Python code from anywhere.

## Other stuff

To run from the command line:

	dialog_system -s examples/web_interface/test_slave.py -d examples/web_interface/test_slave.dlg --spoken
	dialog_system -s code1.py code2.py -d dialog1.dlg dialog2.dlg --spoken

To generate a modules graph:

	pyreverse -f 'ALL' -m y -o png -p Dialog *
	
To run websocket server in background mode:

	screen -S dialog_screen -d -m python3 server.py

The MIT License (MIT)

Copyright (c) 2015 Mark Birger