import sys
import os
import wave
import mpg123
import pyaudio
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QTimeEdit
from PyQt5.QtCore import QTimer, Qt, QTime
from PyQt5.QtGui import QFont

class AlarmClock(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('闹钟')
        self.setGeometry(300, 300, 400, 200)

        self.time_label = QLabel('倒计时时间（时/分）：', self)
        self.time_label.move(20, 20)

        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat('hh:mm')
        self.time_edit.move(150, 20)

        self.file_label = QLabel('音频文件路径：', self)
        self.file_label.move(20, 60)

        self.file_edit = QLineEdit(self)
        self.file_edit.move(150, 60)

        self.browse_button = QPushButton('浏览', self)
        self.browse_button.move(300, 60)
        self.browse_button.clicked.connect(self.browse_file)

        self.start_button = QPushButton('开始', self)
        self.start_button.move(150, 100)
        self.start_button.clicked.connect(self.start_countdown)

        self.countdown_label = QLabel('倒计时：', self)
        self.countdown_label.move(20, 140)
        self.countdown_display = QLabel('00:00:00', self)
        self.countdown_display.move(150, 140)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)

    def browse_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择音频文件", "", "音频文件 (*.mp3 *.wav)", options=options)
        if file_name:
            self.file_edit.setText(file_name)

    def start_countdown(self):
        self.time = self.time_edit.time().hour() * 3600 + self.time_edit.time().minute() * 60 + self.time_edit.time().second()
        self.timer.start(1000)

    def update_countdown(self):
        self.time -= 1

        # Format the time in hours, minutes, and seconds
        time_str = QTime(0, 0).addSecs(self.time).toString('hh:mm:ss')

        self.countdown_display.setText(time_str)

        if self.time == 0:
            self.timer.stop()
            self.play_audio()

    def play_audio(self):
        file_path = self.file_edit.text()

        if not file_path:
            file_path = 'your_default_music_path'

        if file_path.endswith('.mp3'):
            player = mpg123.Mpg123(file_path)
            rate, channels, encoding = player.get_format()
            p = pyaudio.PyAudio()
            stream = p.open(rate=rate, channels=channels, format=p.get_format_from_width(encoding // 8), output=True)

            for frame in player.iter_frames():
                stream.write(frame)

            stream.close()
            p.terminate()
            player.close()

        elif file_path.endswith('.wav'):
            wf = wave.open(file_path, 'rb')
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)

            stream.stop_stream()
            stream.close()
            p.terminate()

        sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    alarm_clock = AlarmClock()
    alarm_clock.show()
    sys.exit(app.exec_())
