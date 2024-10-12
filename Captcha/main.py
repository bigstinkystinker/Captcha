import cv2
import threading
import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Signal
from PySide6 import QtCore, QtGui

# Load Haarcascade models
face_cascade = cv2.CascadeClassifier('haar/haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier('haar/haarcascade_smile.xml')


def detectsmile(callback):
    """ Detect smile and use the callback to emit signals """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera could not be opened.")
        return

    global smiledetect 
    smiledetect = False
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Frame capture failed.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)

            if len(smiles) > 0:
                smiledetect = True
                print('Smile detected!')
                # Use the callback to emit the signal
                callback(True)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Smile detected:", smiledetect)


class MemeWindow(QWidget):
    # Define a signal that takes a boolean (True when smile is detected)
    smile_detected_signal = Signal(bool)
    smile_lock = False
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaurieWired Captcha Challenge")
        self.resize(600, 400)

        # Create a vertical layout for the main window layout
        main_layout = QVBoxLayout()

        # Top header label (h_label)
        h_label = QLabel("Welcome! Please face your camera as you scroll through the memes :)")
        h_label.setAlignment(QtCore.Qt.AlignCenter)
        h_label.setFixedHeight(50)
        h_label.setStyleSheet("background-color: #C8A2C8; padding: 5px; font-family: Arial; font-size: 14pt; color: black;")
        main_layout.addWidget(h_label)

        # Create a horizontal layout for the meme widget and sidebar
        meme_layout = QHBoxLayout()

        # Create a vertical layout for the meme widget and button underneath it
        meme_vertical_layout = QVBoxLayout()

        # Meme widget (initially empty)
        self.meme_widget = QLabel("Meme widget")
        self.meme_widget.setStyleSheet("background-color: lightblue;")
        self.meme_widget.setAlignment(QtCore.Qt.AlignCenter)  # Center the image

        # Add the meme widget to the layout
        meme_vertical_layout.addWidget(self.meme_widget)

        # Initialize an array of images (local paths)
        self.memes = [
            "memes/1.jpg",
            "memes/2.png",
            "memes/3.jpeg",
            "memes/4.jpeg",
            "memes/5.jpeg",
            "memes/6.jpeg",
            "memes/7.png",
            "memes/8.png",
            "memes/9.png",
            "memes/10.png",
            "memes/11.png",
        ]
        self.current_index = 0

        # Load the first image
        self.update_meme()

        # Button widget under the meme widget
        button_widget = QLabel()
        button_widget.setStyleSheet("background-color: lightgreen; padding: 5px;")
        button_widget.setFixedHeight(35)  # Adjust height as necessary

        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)  # remove any margins
        button_layout.setSpacing(0)

        prev = QPushButton("<")
        next = QPushButton(">")

        button_layout.addWidget(prev)
        button_layout.addWidget(next)

        meme_vertical_layout.addWidget(button_widget)

        # Sidebar widget
        self.side_widget = QLabel("Results Here")
        self.side_widget.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.side_widget.setStyleSheet("background-color: lightgray; padding: 5px; font-family: Arial; font-size: 14pt; color: black;")
        self.side_widget.setFixedWidth(150)

        # Add the meme_vertical_layout and sidebar widget to the meme_layout
        meme_layout.addLayout(meme_vertical_layout)  # This will ensure meme_widget and button stack vertically
        meme_layout.addWidget(self.side_widget)

        # Add the horizontal layout (containing meme widget + button and sidebar) to the main vertical layout
        main_layout.addLayout(meme_layout)

        # Set the main layout as the layout for the window
        self.setLayout(main_layout)

        # Connect the buttons to the corresponding actions
        prev.clicked.connect(self.show_prev_meme)
        next.clicked.connect(self.show_next_meme)

        # Connect the smile_detected_signal to the slot that updates the sidebar
        self.smile_detected_signal.connect(self.update_sidebar_on_smile)

    def update_meme(self):
        """ Update the meme_widget with the current image from the array """
        image_path = self.memes[self.current_index]
        pixmap = QtGui.QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(self.meme_widget.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.meme_widget.setPixmap(scaled_pixmap)
        else:
            self.meme_widget.setText("Image not found")

    def show_next_meme(self, smile_detected):
        """ Show the next meme, loop around if at the end """
        self.current_index = (self.current_index + 1) % len(self.memes)
        if self.current_index == 10 and smile_detected == False and self.smile_lock == False:
            self.side_widget.setText("No Smile \nDetected, You\nAre:\n-Robot\n-Depressed\n-Have bad taste \nin memes")
            self.side_widget.setStyleSheet("background-color: Red; padding: 5px; font-family: Arial; font-size: 14pt; color: black;")
            self.smile_lock = True
        self.update_meme()

    def show_prev_meme(self):
        """ Show the previous meme, loop around if at the beginning """
        self.current_index = (self.current_index - 1) % len(self.memes)
        self.update_meme()

    def update_sidebar_on_smile(self, smile_detected):
        """ Update the sidebar when a smile is detected """
        if smile_detected and self.smile_lock == False:
            self.side_widget.setText("Smile detected! \nyou are (not) a\nrobot!")
            self.side_widget.setStyleSheet("background-color: green; padding: 5px; font-family: Arial; font-size: 14pt; color: black;")
            self.smile_lock = True

def startgui():
    """ Start the PySide GUI """
    app = QApplication(sys.argv)
    window = MemeWindow()

    # Start smile detection in a separate thread and pass the signal emitter as a callback
    smile_thread = threading.Thread(target=detectsmile, args=(window.smile_detected_signal.emit,))
    smile_thread.daemon = True  # Daemonize thread so it exits when the main program exits
    smile_thread.start()

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    startgui()
