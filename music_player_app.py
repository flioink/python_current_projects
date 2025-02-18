import copy
import os
import random
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel,\
                             QListWidget, QFileDialog, QSlider, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import  QMediaPlayer, QAudioOutput

import json


# app class
class AudioApp(QWidget):
    def __init__(self):
        super().__init__()
        self.volume = 100
        self.folder_path = None
        self.playlist = None
        self.paused = False
        self.shuffle = False
        self.current_song_index = None
        self.loop_modes_list = ["NO LOOP", "LOOP ONE", "LOOP ALL"]
        self.loop_mode = self.loop_modes_list[0]
        self.loop_index = 0

        # The file list
        self.file_list = QListWidget()

        # Enable drag & drop
        self.file_list.setAcceptDrops(True)
        self.file_list.setDragEnabled(False)

        # Enable main window drag and drop
        self.setAcceptDrops(True)

        self.settings()
        self.init_UI()
        self.event_handler()
        self.load_last_playlist()

    # settings
    def settings(self):
        self.setWindowTitle("Flioink Audio Player")
        self.setGeometry(700, 300, 800, 600)
    # UI
    def init_UI(self):
        self.title = QLabel("Flioink Audio Player")
        self.title.setObjectName("title")

        self.btn_opener = QPushButton("Choose a folder")

        # Play Buttons
        self.btn_play = QPushButton("Play▶️")
        self.btn_pause = QPushButton("Pa⏸")
        self.btn_reset = QPushButton("Rst🔂")
        self.btn_shuffle = QPushButton("🔀: OFF")
        self.btn_previous = QPushButton("Prev⏮")
        self.btn_next = QPushButton("Next⏭")
        self.btn_loop = QPushButton("🔄:OFF")
        self.btn_del = QPushButton("Rem🗑️")
        # Buttons layout
        self.playback_buttons_layout_top = QHBoxLayout()
        # make buttons same size
        self.btn_play.setFixedSize(100, 80)
        self.btn_pause.setFixedSize(100, 80)
        self.btn_reset.setFixedSize(100, 80)
        self.btn_shuffle.setFixedSize(100, 80)
        self.btn_del.setFixedSize(100, 80)

        self.playback_buttons_layout_bottom = QHBoxLayout()
        self.btn_previous.setFixedSize(100, 80)
        self.btn_next.setFixedSize(100, 80)
        self.btn_loop.setFixedSize(100, 80)
        # disable buttons on start
        self.btn_pause.setDisabled(True)
        self.btn_reset.setDisabled(True)

        # add to layout top
        self.playback_buttons_layout_top.addWidget(self.btn_play)
        self.playback_buttons_layout_top.addWidget(self.btn_pause)
        self.playback_buttons_layout_top.addWidget(self.btn_reset)
        self.playback_buttons_layout_top.addWidget(self.btn_shuffle)
        self.playback_buttons_layout_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playback_buttons_layout_top.setSpacing(5)  # Reduce space between buttons
        self.playback_buttons_layout_top.setContentsMargins(0, 0, 0, 0)  # Remove extra margins

        # add to layout bottom
        self.playback_buttons_layout_bottom.addWidget(self.btn_previous)
        self.playback_buttons_layout_bottom.addWidget(self.btn_next)
        self.playback_buttons_layout_bottom.addWidget(self.btn_loop)
        self.playback_buttons_layout_bottom.addWidget(self.btn_del)
        self.playback_buttons_layout_bottom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.playback_buttons_layout_bottom.setSpacing(5)  # Reduce space between buttons
        self.playback_buttons_layout_bottom.setContentsMargins(0, 0, 0, 0)  # Remove extra margins

        # playlist buttons
        self.btn_save = QPushButton("Save Playlist")
        self.btn_load = QPushButton("Load Playlist")
        self.btn_clear = QPushButton("Clear Playlist")

        # speed label
        self.slider_text = QLabel("Speed: 100%")
        self.slider_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # speed slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(150)
        self.speed_slider.setValue(100)
        self.speed_slider.setSingleStep(1)
        self.speed_slider.setPageStep(10)
        self.speed_slider.setTracking(True)
        self.speed_slider.setSliderDown(False)


        # song duration
        self.time_display = QLabel("00:00 / 00:00")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # progress slider
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        self.progress_bar.setRange(0, 100)

        # enable interactive progress bar
        self.progress_bar.setEnabled(True)
        self.progress_bar.setTracking(True)

        self.progress_bar.setSingleStep(1)  # Ensures small increments
        self.progress_bar.setPageStep(10)  # Adjusts the jump size when clicking
        self.progress_bar.setTracking(True)  # Updates value immediately

        # volume slider
        self.volume_text = QLabel(f"Volume: {self.volume}%")
        self.volume_bar = QSlider(Qt.Orientation.Horizontal)
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(self.volume)
        # volume clicking enabled
        self.volume_bar.setSingleStep(1)
        self.volume_bar.setPageStep(10)
        self.volume_bar.setTracking(True)
        self.volume_bar.setSliderDown(False)

        # progress slider layout
        progress_bar_layout = QVBoxLayout()
        adjust_settings_layout = QHBoxLayout()

        adjust_settings_layout.addWidget(self.slider_text)
        adjust_settings_layout.addWidget(self.speed_slider)
        adjust_settings_layout.addWidget(self.volume_text)
        adjust_settings_layout.addWidget(self.volume_bar)

        progress_bar_layout.addWidget(self.progress_bar)
        progress_bar_layout.addWidget(self.time_display)

        # layout
        self.master = QVBoxLayout()
        row = QHBoxLayout()
        col1 = QVBoxLayout()
        col2 = QVBoxLayout()
        # Align buttons to top
        col2.setAlignment(Qt.AlignmentFlag.AlignTop)

        # load the layout
        self.master.addWidget(self.title)
        self.master.addLayout(progress_bar_layout)
        self.master.addLayout(adjust_settings_layout)

        # playlist
        col1.addWidget(self.file_list)
        # adding the buttons

        col2.addLayout(self.playback_buttons_layout_top)
        col2.addLayout(self.playback_buttons_layout_bottom)
        col2.addWidget(self.btn_opener)
        col2.addWidget(self.btn_save)
        col2.addWidget(self.btn_load)
        col2.addWidget(self.btn_clear)

        row.addLayout(col1, 4)
        row.addLayout(col2, 2)

        self.master.addLayout(row)
        self.setLayout(self.master)

        # special audio classes
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)

        self.media_player.mediaStatusChanged.connect(self.play_next_song)

        self.style()

    # Connect events
    def event_handler(self):
        # buttons
        self.speed_slider.valueChanged.connect(self.update_slider)
        self.btn_opener.clicked.connect(self.open_file)
        self.btn_play.clicked.connect(self.play_audio)
        self.btn_pause.clicked.connect(self.pause_audio)
        self.btn_reset.clicked.connect(self.reset_audio)
        self.btn_shuffle.clicked.connect(self.toggle_shuffle)
        self.btn_save.clicked.connect(self.save_playlist)
        self.btn_next.clicked.connect(self.skip_to_next)
        self.btn_previous.clicked.connect(self.skip_to_previous)
        self.btn_loop.clicked.connect(self.loop_mode_select)
        self.btn_del.clicked.connect(self.remove_song)
        # progress bar
        self.media_player.positionChanged.connect(self.update_progress_bar)
        self.media_player.durationChanged.connect(self.set_slider_range)
        # progress bar clicks
        self.progress_bar.sliderReleased.connect(self.seek_audio)
        self.progress_bar.sliderPressed.connect(self.seek_audio)
        self.progress_bar.sliderReleased.connect(self.seek_audio)

        # speed slider
        self.speed_slider.sliderMoved.connect(self.update_speed)
        self.file_list.itemDoubleClicked.connect(self.play_new_song)
        self.speed_slider.valueChanged.connect(self.update_speed)

        # volume slider
        self.volume_bar.sliderMoved.connect(self.volume_control)
        self.volume_bar.valueChanged.connect(self.volume_control)
        # clear playlist
        self.btn_clear.clicked.connect(self.clear_playlist)
        # load custom playlist
        self.btn_load.clicked.connect(self.load_custom_playlist)




    def update_slider(self):
        speed = self.speed_slider.value()
        self.slider_text.setText(f"Speed: {speed}%")

    def open_file(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")

        if path:
            self.file_list.clear()
            self.folder_path = path
            self.playlist = []

            for filename in os.listdir(path):
                if filename.endswith(".mp3"):
                    full_path = os.path.join(path, filename)
                    self.playlist.append(full_path)
                    self.file_list.addItem(filename)

        else:
            file, _ = QFileDialog.getOpenFileName(self, "Select File", filter="Audio Files (*.mp3)")
            if file:
                self.file_list.clear()
                self.playlist = [file]
                self.file_list.addItem(os.path.basename(file))

    def play_audio(self):
        self.progress_bar.setEnabled(True)

        if self.paused and self.file_list.currentRow() == self.current_song_index:
            self.media_player.play()
            self.paused = False

            self.btn_pause.setEnabled(True)
            self.btn_reset.setEnabled(True)
            self.btn_next.setEnabled(True)
            self.btn_play.setDisabled(True)

        else:
            self.play_new_song()


    def play_new_song(self):

        self.current_song_index = self.file_list.currentRow()

        if self.current_song_index >= 0:
            file_path = self.playlist[self.current_song_index]
            file_url = QUrl.fromLocalFile(file_path)
            self.media_player.setSource(file_url)
            self.media_player.setPlaybackRate(self.speed_slider.value() / 100.0)
            self.media_player.play()
            self.paused = False

            self.btn_pause.setEnabled(True)
            self.btn_play.setDisabled(True)
            self.progress_bar.setEnabled(True)

    def play_next_song(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.loop_mode == "LOOP ONE":
                self.file_list.setCurrentRow(self.current_song_index)
                self.play_audio()

            elif self.loop_mode == "LOOP ALL" and self.current_song_index >= len(self.playlist) - 1:
                print(self.loop_mode)
                self.current_song_index = 0
                self.file_list.setCurrentRow(self.current_song_index)
                self.play_audio()
                return

            else:
                if self.shuffle:
                    self.current_song_index = random.randint(0, len(self.playlist) - 1)
                else:
                    self.current_song_index = self.file_list.currentRow() + 1


            if self.current_song_index < len(self.playlist):
                self.file_list.setCurrentRow(self.current_song_index)  # Keep UI in sync
                self.play_audio()
            else:
                self.media_player.stop()

    def skip_to_next(self):
        if self.shuffle:
            self.current_song_index = random.randint(0, len(self.playlist) - 1)


        else:
            self.current_song_index = self.file_list.currentRow() + 1


        if self.current_song_index < len(self.playlist):
            self.file_list.setCurrentRow(self.current_song_index)  # Keep UI in sync
            self.play_audio()
        else:
            self.media_player.stop()

    def skip_to_previous(self):
        if self.shuffle:
            self.current_song_index = random.randint(0, len(self.playlist) - 1)
        else:
            if self.file_list.currentRow() > 0:
                self.current_song_index = self.file_list.currentRow() - 1


        if self.current_song_index < len(self.playlist):
            self.file_list.setCurrentRow(self.current_song_index)  # Keep UI in sync
            self.play_audio()
        else:
            self.media_player.stop()


    def pause_audio(self):
        if not self.paused:
            self.media_player.pause()
            self.btn_pause.setDisabled(True)
            self.btn_play.setEnabled(True)
            self.btn_next.setDisabled(True)
            self.paused = True


    def reset_audio(self):
        if self.media_player.isPlaying():
            self.media_player.stop()

        self.media_player.setPosition(0)
        self.media_player.setPlaybackRate(self.speed_slider.value() / 100.0)
        self.media_player.play()

        self.btn_pause.setEnabled(True)
        self.btn_reset.setDisabled(True)
        self.btn_play.setDisabled(True)
        self.paused = False

        QTimer.singleShot(100, lambda: self.btn_reset.setEnabled(True))

    def style(self):
        self.setStyleSheet(
            """
            QWidget{
                background-color: #F9DBBA;
                
            }
            
            QPushButton {
                background-color: #5BB9C2;
                padding: 15px;  /* Increase padding for bigger buttons */
                border-radius: 12px; /* More rounded corners */
                color: white;
                font-weight: bold;
                font-size: 16px; /* Bigger text */
                margin: 5px; /* Add spacing between buttons */
                border: 2px solid #1A4870;
                transition: 0.2s;
            }

            QPushButton:hover {
                background-color: #1A4870;
                color: #F9DBBA;
                border: 2px solid #5BB9C2;
            }
            
            QLabel{
                color: #333;
            
            }
            
            #title{
                font-family: Papyrus;
                font-size: 40px;
            }
            
            QSlider{
                margin-right: 15px;
            }
            
            QListWidget{
                color: #333;
            }
            
            QListWidget::item {
                padding: 4px;
            }         
            
            QListWidget {
                background-color: #E5E5E5; /* Light gray for contrast */
                border: 2px solid #5BB9C2; /* Adds a subtle border */
                color: #333; 
            }

            QListWidget::item:selected {
                background: #1A4870;
                color: #5BB9C2;
                font-weight: bold;
            }
            
            QSlider::groove:horizontal {
                height: 10px;
                background: #ddd;
                border-radius: 5px;
            }
            
            QSlider::handle:horizontal {
            background: #5BB9C2;
            width: 14px;
            height: 14px;
            border-radius: 7px;  /* This makes it circular */
            }

            
            QSlider::handle:horizontal:hover {
            background: #FF5733;
            width: 16px;
            height: 16px;
            border-radius: 8px;  /* Stays circular even when hovered */
            }
            
            QSlider::tick-mark {
                background: black;
                width: 2px;
                height: 10px;
            }   
                                 
            """
        )


    def update_progress_bar(self, position):
        if not self.progress_bar.isSliderDown():
            self.progress_bar.setValue(position)

        # Update the time display
        current_time = self.format_time(position)
        total_time = self.format_time(self.media_player.duration())
        self.time_display.setText(f"{current_time} / {total_time}")

    def set_slider_range(self, duration):
        self.progress_bar.setRange(0, duration)

    def load_last_playlist(self):
        if os.path.exists("last_playlist.json"):
            with open("last_playlist.json", "r") as file:
                try:
                    last_playlist_data = json.load(file)

                    last_playlist_name = last_playlist_data


                except json.JSONDecodeError:
                    print("Error reading last_playlist.json")
                    return

            if os.path.exists(last_playlist_name):
                self.load_playlist(last_playlist_name)
            else:
                print(f"Playlist file '{last_playlist_name}' not found.")

    def load_playlist(self, path):
        if os.path.exists(path):
            with open(path, "r") as file:
                self.playlist = json.load(file)
            self.file_list.clear()

            for idx, file in enumerate(self.playlist, start=1):
                song_name = os.path.basename(file)
                self.file_list.addItem(f"{idx}. {song_name}")
                idx += 1

    def save_playlist(self):
        if self.playlist:
            playlist_name, _ = QFileDialog.getSaveFileName(self, "Save Playlist", "", "JSON Files (*.json)")

            if playlist_name:
                json_object = json.dumps(self.playlist, indent=4)

                # Writing to sample.json
                with open(playlist_name, "w") as outfile:
                    outfile.write(json_object)
                    QMessageBox.information(self, "Saving", f"Saved {playlist_name} playlist.")

                # Set any saved playlist as default
                with open("last_playlist.json", "w") as last_file:
                    # use only json.dump method for passing info to json files, duh
                    json.dump(os.path.basename(playlist_name), last_file)

    def seek_audio(self):
        position = self.progress_bar.value()
        self.media_player.setPosition(position)

    def update_speed(self, value):
        self.media_player.setPlaybackRate(value / 100.0)
        self.slider_text.setText(f"Speed: {value}%")

    def volume_control(self, value):
        self.volume = value
        self.volume_text.setText(f"Volume: {self.volume}%")
        self.audio_output.setVolume(value / 100.0)

    def toggle_shuffle (self):
        if self.shuffle:
            self.shuffle = False
        else:
            self.shuffle = True
        self.btn_shuffle.setText("🔀: ON" if self.shuffle else "🔀: OFF")

    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    # Update song numbers if new stuff is added
    def renumber_playlist(self):
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            file_path = self.playlist[i]
            song_name = os.path.basename(file_path)
            # renames the item
            item.setText(f"{i + 1}. {song_name}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            print("drag event")

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                print("External Drop:", file_path)
                if file_path.endswith(".mp3") and file_path not in self.playlist:
                    self.playlist.append(file_path)
                    self.file_list.addItem(os.path.basename(file_path))
            self.renumber_playlist()
            event.acceptProposedAction()
        else:
            self.update_playlist_order(event)


    def update_playlist_order(self, event):
        new_order = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        print("New Order:", new_order)
        # Find new indices
        old_playlist = copy.deepcopy(self.playlist)
        new_playlist = []
        for song_name in new_order:
            for file_path in old_playlist:
                if os.path.basename(file_path) == song_name:
                    new_playlist.append(file_path)
                    old_playlist.remove(file_path)  # Remove to prevent duplicates
                    break

        self.playlist = new_playlist
        print("Updated Playlist:", self.playlist)  # Debugging
        event.acceptProposedAction()

    def loop_mode_select(self):

        self.loop_index += 1
        if self.loop_index > 2:
            self.loop_index = 0

        self.loop_mode = self.loop_modes_list[self.loop_index]
        if self.loop_mode == "NO LOOP":
            self.btn_loop.setText("🔄:OFF")

        elif self.loop_mode == "LOOP ONE":
            self.btn_loop.setText("🔂:ONE")

        elif self.loop_mode == "LOOP ALL":
            self.btn_loop.setText("🔁:ALL")

    def remove_song(self):
        selected_item = self.file_list.selectedItems()

        if selected_item:
            song_to_remove = selected_item[0].text()
            if song_to_remove in self.playlist:
                self.playlist.remove(song_to_remove)

        # remove from QlistWidget
        self.file_list.takeItem(self.file_list.row(selected_item[0]))

    def clear_playlist(self):

        msg = QMessageBox() # message box to warn you
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("Are you sure you want to clear the playlist?")
        msg.setWindowTitle("Confirm Action")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        response = msg.exec()  # This will return the button clicked
        if response == QMessageBox.StandardButton.Yes:
            self.playlist.clear()
            self.file_list.clear()


    def load_custom_playlist(self):

        custom_playlist_file, _ = QFileDialog.getOpenFileName(filter="JSON Files (*.json)")
        if os.path.exists(custom_playlist_file):

            with open(custom_playlist_file, "r") as file:
                self.playlist = json.load(file)
            self.file_list.clear()

            for idx, file in enumerate(self.playlist, start=1):
                song_name = os.path.basename(file)
                self.file_list.addItem(f"{idx}. {song_name}")




if __name__ == "__main__":
    app = QApplication([])
    main = AudioApp()
    main.show()
    app.exec()