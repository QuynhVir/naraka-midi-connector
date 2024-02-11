# This Python file uses the following encoding: utf-8
import os
import sys
import mido
import time
import keyboard
import threading

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon

import mido.backends.rtmidi

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

class MainWindow(QMainWindow):
    # Constants
    OCTAVE_INTERVAL = 12
    KEYTABLE = "z?x?cv?b?n?m" + "a?s?df?g?h?j" + "q?w?er?t?y?u"
    MASTER_MODE_KEYTABLE = ["z", "s", "x", "d", "c", "v", "g", "b", "h", "n", "j", "m"] + [",", "l", ".", ";", "/", "q", "2", "w", "3", "e", "4", "r"] + ["t", "6", "y", "7", "u", "i", "9", "o", "0", "p", "_", "["]
    C1_PITCH = 24

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.setWindowIcon(QIcon(self.resource_path('resources/midi.ico')))
        self.ui.setupUi(self)
        self.populate_midi_devices()
        self.populate_base_octave()

        # Initialize the stop event
        self.stop_event = threading.Event()

        # Connect the startButton's clicked signal to the toggle_midi_listen method
        self.ui.startButton.clicked.connect(self.toggle_midi_listen)

        # Initialize the port to None
        self.port = None

    def resource_path(self, relative_path):
        """Get absolute path to resource, works for development and PyInstaller."""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def closeEvent(self, event):
        # If the port is not None, stop listening
        if self.port is not None:
            self.port.close()
            self.port = None

            # Set the stop event
            self.stop_event.set()

            # Wait for the listen_thread to finish
            self.listen_thread.join()

        # Call the parent class's closeEvent method to do the default close action
        super().closeEvent(event)

    def populate_midi_devices(self):
        # Get the list of MIDI devices
        midi_devices = mido.get_input_names()

        # Clear the QComboBox
        self.ui.midi_device_list.clear()

        # Add the MIDI devices to the QComboBox
        for device in midi_devices:
            self.ui.midi_device_list.addItem(device)

        # Set the first device as the default if there are devices
        if midi_devices:
            self.ui.midi_device_list.setCurrentIndex(0)

    def populate_base_octave(self):
        # Define the range
        base_octave = ["1", "2", "3", "4", "5"]

        # Clear the QComboBox
        self.ui.base_octave.clear()

        # Add the range to the QComboBox
        for note in base_octave:
            self.ui.base_octave.addItem(note)

        # Set C3 as the default selection
        self.ui.base_octave.setCurrentText("3")

    def toggle_midi_listen(self):
        # If the port is None, start listening
        if self.port is None:
            # Get the selected MIDI device
            device = self.ui.midi_device_list.currentText()

            # Open the MIDI input port
            self.port = mido.open_input(device)

            # Change the button text to "Stop"
            self.ui.startButton.setText("Stop")

            # Clear the stop event
            self.stop_event.clear()

            # Start a separate thread to listen for MIDI messages
            self.listen_thread = threading.Thread(target=self.listen_midi)
            self.listen_thread.start()
        else:
            # If the port is not None, stop listening
            self.port.close()
            self.port = None

            # Set the stop event
            self.stop_event.set()

            # Wait for the listen_thread to finish
            self.listen_thread.join()

            # Change the button text back to "Start"
            self.ui.startButton.setText("Start")

    def listen_midi(self):
        while not self.stop_event.is_set():
            try:
                if self.port is None:
                    break
                # Listen for MIDI messages from the input port
                for msg in self.port.iter_pending():
                    self.play_midi(msg)
            except OSError:
                # The port was closed, so exit the loop
                break

            # Sleep for a small interval to reduce CPU usage, still looking for a better approach :(
            time.sleep(0.001)

    def calculate_keystroke(self, note):
        try:
            # Get the base octave
            base_octave = int(self.ui.base_octave.currentText())

            # Calculate the note number
            note_number = note.note - (self.C1_PITCH + (self.OCTAVE_INTERVAL * (base_octave - 1)))

            if note_number < 0 or note_number > self.OCTAVE_INTERVAL * 3 - 1:
                raise IndexError

            # Get the key from the KEYTABLE or MASTER_MODE_KEYTABLE if the master mode is enabled
            key = self.KEYTABLE[note_number] if not self.ui.guzheng_master_mode.isChecked() else self.MASTER_MODE_KEYTABLE[note_number]

            # Return the key
            return key
        except IndexError:
            print("Note out of range")
            return None
    
    def play_midi(self, msg):
        # If the msg is not note_on or note_off, return
        if msg.type not in ["note_on", "note_off"]:
            return
        
        # Calculate the keystroke
        key = self.calculate_keystroke(msg)

        # If key is None or '?' (invalid note), return
        if key is None or key == '?':
            return
        
        # If msg is note_on with velocity 0 or note_off, send the key release
        if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            keyboard.release(key)

        # If msg is note_on with velocity > 0, send the key press
        if msg.type == "note_on" and msg.velocity > 0:
            keyboard.press(key)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
