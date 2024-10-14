import cv2
import threading
import sys
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Signal
from PySide6 import QtCore, QtGui
"""
Hello Laurie! The premise of this CAPTCHA idea is that while the AI of 2038 are more capable than
humans at most tasks, they cannot enjoy memes. This CAPTCHA takes advantage of this fact by showing the
viewer various memes that are meant to make them smile, and if a smile is detected they pass the test.

Along with keeping out robots, this CAPTCHA idea has the added benefit of keeping out psychopaths, 
depressed people and people who don't share your taste in memes. The depressed people can then be
redirected to therapy instead of whatever is behind the CAPTCHA because mental health is more important.
the others can have a trap door open underneath them Bugs Bunny style or something idk I haven't gotten 
that far. Enjoy!

NOTE: Your camera may take 5-10 seconds to start so take your time scrolling through the memes
"""
###
# Compile instructions:
#   1. run: pip install pyinstaller PySide6 opencv-python
#   2. cd into Captcha file and run: pyinstaller --onefile --windowed --add-data "haar;haar" --add-data "memes;memes" main.py
#      (make sure python scripts added to PATH it gave me lotta trouble ):<)
#   3. manually add memes and haar files into dist file
#   4. Done!
#   (sry I couldn't add the exe into the github repo it's huge D: hope this is ok)
###

#Haar cascade models
face_cascade = cv2.CascadeClassifier('haar/haarcascade_frontalface_default.xml')
smile_cascade = cv2.CascadeClassifier('haar/haarcascade_smile.xml')


#OpenCV smile detection
def detectsmile(callback):
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
    #print("Smile detected:", smiledetect)


class MemeWindow(QWidget):
    smile_detected_signal = Signal(bool)
    smile_lock = False
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaurieWired Captcha Challenge")
        self.resize(600, 400)

        # Create a vertical layout for the main window layout
        main_layout = QVBoxLayout()

        # Top header label
        h_label = QLabel("Welcome! Please face your camera as you scroll through the memes :)")
        h_label.setAlignment(QtCore.Qt.AlignCenter)
        h_label.setFixedHeight(50)
        h_label.setStyleSheet("background-color: #C8A2C8; padding: 5px; font-family: Arial; font-size: 14pt; color: black;")
        main_layout.addWidget(h_label)

        meme_layout = QHBoxLayout()
        meme_vertical_layout = QVBoxLayout()

        # Meme
        self.meme_widget = QLabel("Meme widget")
        self.meme_widget.setStyleSheet("background-color: lightblue;")
        self.meme_widget.setAlignment(QtCore.Qt.AlignCenter)  # Center the image
        meme_vertical_layout.addWidget(self.meme_widget)

        # Images
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

        # Button widget
        button_widget = QLabel()
        button_widget.setStyleSheet("background-color: lightgreen; padding: 5px;")
        button_widget.setFixedHeight(35)

        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0) 
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

        # Combining Layouts
        meme_layout.addLayout(meme_vertical_layout)
        meme_layout.addWidget(self.side_widget)

        main_layout.addLayout(meme_layout)

        #Final layout
        self.setLayout(main_layout)

        #Connecting buttons
        prev.clicked.connect(self.show_prev_meme)
        next.clicked.connect(self.show_next_meme)

        #Connect smile_detected_signal to gui
        self.smile_detected_signal.connect(self.update_sidebar_on_smile)

    def update_meme(self):
        image_path = self.memes[self.current_index]
        pixmap = QtGui.QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(self.meme_widget.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.meme_widget.setPixmap(scaled_pixmap)
        else:
            self.meme_widget.setText("Image not found")

    def show_next_meme(self, smile_detected):
        self.current_index = (self.current_index + 1) % len(self.memes)
        if self.current_index == 10 and smile_detected == False and self.smile_lock == False:
            self.side_widget.setText("No Smile \nDetected, You\nAre:\n-Robot\n-Depressed\n-Have bad taste \nin memes")
            self.side_widget.setStyleSheet("background-color: Red; padding: 5px; font-family: Arial; font-size: 14pt; color: black;")
            self.smile_lock = True
        self.update_meme()

    def show_prev_meme(self):
        self.current_index = (self.current_index - 1) % len(self.memes)
        self.update_meme()

    def update_sidebar_on_smile(self, smile_detected):
        if smile_detected and self.smile_lock == False:
            self.side_widget.setText("Smile detected! \nyou are (not) a\nrobot!")
            self.side_widget.setStyleSheet("background-color: green; padding: 5px; font-family: Arial; font-size: 14pt; color: black;")
            self.smile_lock = True

#Start da gui
def startgui():
    app = QApplication(sys.argv)
    window = MemeWindow()

    smile_thread = threading.Thread(target=detectsmile, args=(window.smile_detected_signal.emit,))
    smile_thread.daemon = True  # Daemon thread for exit
    smile_thread.start()

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    startgui()
