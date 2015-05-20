#!/usr/bin/env python3

"""
Evaluation tests.

"""

from dialog import Dialog, handle

object_name = None
target = None
first = None

if __name__ == "__main__":
    DLG = Dialog(globals())
    DLG.load("examples/evaluation/evaluation.dlg")
    DLG.start()
