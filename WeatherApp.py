import json
import os
import sys


import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, \
    QCompleter, QHBoxLayout, QMessageBox, QComboBox
from PyQt5.QtCore import Qt, QStringListModel, QtWarningMsg

try:
    with open("api_key.txt", "r") as key_file:
        key = key_file.readline().strip()
        if not key:
            raise ValueError("Key not found!")
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}")
    sys.exit(1)




class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.kelvin_scale = 273.15
        self.load_icons()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button =  QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.icon_label = QLabel(self)
        self.description_label = QLabel(self)
        self.feels_like = QLabel(self)
        self.wind_speed = QLabel(self)

        # Load city list from JSON
        self.load_cities_from_json("cities.json")

        self.initUI()

    def initUI(self):
        self.setWindowTitle("WeatherApp")
        master_layout = QVBoxLayout()

        # city input layout
        self.city_input_layout = QVBoxLayout()
        self.city_input_layout.addWidget(self.city_label, alignment=Qt.AlignCenter)
        self.city_input_layout.addWidget(self.city_input)

        # button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.get_weather_button)
        self.clear_button = QPushButton("Clear")
        self.button_layout.addWidget(self.clear_button)

        # add to combo-box layout
        self.favorites_layout = QHBoxLayout()
        self.favorites_combo_box = QComboBox()
        self.add_button = QPushButton("Add")
        self.favorites_layout.addWidget(self.add_button)
        self.favorites_layout.addWidget(self.favorites_combo_box)

        # set default location button layout
        self.set_default_button_layout = QVBoxLayout()
        self.button_set_default = QPushButton("Set Default")
        self.set_default_button_layout.addWidget(self.button_set_default)

        # description and wind speed layout
        self.desc_temp_layout = QHBoxLayout()
        self.desc_temp_layout.addWidget(self.feels_like, alignment=Qt.AlignLeft)
        self.desc_temp_layout.addWidget(self.wind_speed, alignment=Qt.AlignRight)

        # temperature, emoji and description layout
        self.temperature_layout = QVBoxLayout()
        self.temperature_layout.addWidget(self.temperature_label, alignment=Qt.AlignCenter)
        self.temperature_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        self.temperature_layout.addWidget(self.description_label, alignment=Qt.AlignCenter)
        self.temperature_layout.addLayout(self.desc_temp_layout)


        # Wrap temperature layout in HBox to center it
        self.centered_temp_layout = QHBoxLayout()
        self.centered_temp_layout.addStretch()  # Pushes content to the center
        self.centered_temp_layout.addLayout(self.temperature_layout)
        self.centered_temp_layout.addStretch()  # Pushes content to the center

        master_layout.addLayout(self.city_input_layout)
        master_layout.addLayout(self.button_layout)
        master_layout.addLayout(self.favorites_layout)
        master_layout.addLayout(self.set_default_button_layout)
        master_layout.addLayout(self.centered_temp_layout)

        # set master layout
        self.setLayout(master_layout)

        # give widget objects names
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.clear_button.setObjectName("clear_button")
        self.button_set_default.setObjectName("set_default")
        self.temperature_label.setObjectName("temperature_label")
        self.icon_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")
        self.feels_like.setObjectName("feels_like")
        self.wind_speed.setObjectName("wind_speed")
        self.favorites_combo_box.setObjectName("favorites_combo_box")
        self.add_button.setObjectName("add_button")


        self.event_handler()
        self.style()
        self.load_default_location()
        self.load_favorites()

    def event_handler(self):
        # connect buttons
        self.get_weather_button.clicked.connect(self.get_weather)
        self.clear_button.clicked.connect(self.clear)
        self.button_set_default.clicked.connect(self.set_default_location)
        self.add_button.clicked.connect(self.add_to_favorites)
        self.favorites_combo_box.currentIndexChanged.connect(self.load_selected_favorite)

    def style(self):
        self.setStyleSheet("""
                                    QLabel, QPushButton{
                                        font-family: calibri;
                                    }

                                    QLabel#city_label{
                                        font-size: 40px;
                                        font-style: italic;
                                    }

                                    QLineEdit#city_input{
                                        font-size: 40px;
                                    }

                                    QPushButton#get_weather_button{
                                        font-size: 30px;
                                        font-weight: bold;
                                    }

                                    QPushButton#clear_button{
                                        font-size: 30px;
                                        font-weight: bold;
                                    }
                                    
                                    QPushButton#set_default{
                                        font-size: 30px;
                                        font-weight: bold;
                                    }
                                    
                                    QPushButton#add_button{
                                        font-size: 30px;
                                        font-weight: bold;
                                    }
                                    
                                    QComboBox#favorites_combo_box{
                                        font-size: 30px;
                                        font-weight: bold;
                                    }

                                    QLabel#temperature_label{
                                        font-size: 75px;
                                    }

                                    QLabel#emoji_label{
                                        font-size: 100px;
                                        font-family: Segoe UI emoji;
                                    }

                                    QLabel#description_label{
                                        font-size: 50px;
                                    }
                                    QLabel#feels_like{
                                        font-size: 25px;
                                    }
                                    QLabel#wind_speed{
                                        font-size: 25px;
                                    }


                                """)

    def get_input_text(self):
        city = self.city_input.text().split(",")[0]

        if not city:  # If both are empty, show an error
            self.display_error("Please enter or select a city.")
            return

        return city

    def get_weather(self):
        # Get manually entered text
        city = self.get_input_text()

        self.api_call(city)


    def clear(self):
        self.city_input.clear()
        self.temperature_label.clear()
        self.icon_label.clear()
        self.description_label.clear()
        self.feels_like.clear()
        self.wind_speed.clear()

    def set_default_location(self):
        print("set default location")
        current_city = self.city_input.text()
        if "," in current_city:
            current_city = current_city.split(",")[0]

        if current_city:

            msg = QMessageBox()  # message box to warn you
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(f"Do you want to set {current_city} as the default location on startup?")
            msg.setWindowTitle("Confirm Action")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            response = msg.exec()  # This will return the button clicked
            if response == QMessageBox.StandardButton.Yes:

                with open("settings.json", "w")as out_file:
                    json.dump({"default_city": current_city}, out_file, indent=4)

        else:
            QMessageBox.information(self, "Warning", f"No city entered to save.")

    def load_default_location(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                default_location = json.load(file)
                city = default_location.get("default_city", "").strip()

                if city:  # Only call API if there's a saved city
                    self.city_input.setText(city)
                    self.api_call(city)

    # send request to the api
    def api_call(self, city_name):
        api_key = key

        # call the api
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("cod") == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad Request. Check Input.")
                case 401:
                    self.display_error("Unauthorized. Invalid API.")
                case 403:
                    self.display_error("Access Denied.")
                case 404:
                    self.display_error("City Not Found.")
                case 500:
                    self.display_error("Internal Server Error.")
                case 502:
                    self.display_error("Bad Gateway.")
                case 503:
                    self.display_error("Service unavailable.")
                case 504:
                    self.display_error("Gateway Timeout.")
                case _:
                    self.display_error(f"HTTP error: {http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error: Check Your Internet")

        except requests.exceptions.Timeout:
            self.display_error("Request Timed Out")

        except requests.exceptions.TooManyRedirects:
            self.display_error("Too Many Redirects")

        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error: {req_error}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)
        self.icon_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        print(data)
        # get temp and weather description
        current_temp = self.calculate_temperature(data)
        weather_id, weather_desc = self.get_weather_descriptions(data)
        # get feels like temp
        feels_like = self.get_feels_like(data)
        # get wind speed
        wind_speed = self.get_wind_speed(data)

        # set labels
        self.temperature_label.setText(f"{current_temp:.0f}°C")
        self.wind_speed.setText(f"Wind speed: {wind_speed:.0f} m/s")
        self.feels_like.setText(f"Feels like: {feels_like:.0f}°C")
        self.description_label.setText(weather_desc)
        self.icon_label.setText(self.set_weather_image(weather_id))

    def load_icons(self):
        self.icons = {
            "clear": QPixmap("icons/clear_day.256.png"),
            "clear_n": QPixmap("icons/clear_night.256.png"),
            "cloudy": QPixmap("icons/clouds.256.png"),
            "few_clouds": QPixmap("icons/few-clouds.256.png"),
            "few_clouds_n": QPixmap("icons/few-clouds-night.256.png"),
            "overcast": QPixmap("icons/overcast.256.png"),
            "rain": QPixmap("icons/rain.256.png"),
            "snow": QPixmap("icons/snow.256.png"),
            "wind": QPixmap("icons/windy.256.png"),
            "storm": QPixmap("icons/storm.256.png"),
            "foggy": QPixmap("icons/foggy.256.png"),
            "gusty": QPixmap("icons/gusty.256.png"),
            "volcano": QPixmap("icons/volcano.128.png")
        }

        self.weather_icons_keys = {
            range(200, 233): "rain",
            range(300, 322): "few_clouds",
            range(500, 532): "rain",
            range(600, 623): "snow",
            range(701, 742): "foggy",
            (762,): "volcano",
            (771,): "gusty",
            (781,): "storm",
            (800,): "clear",
            (801,): "few_clouds",
            range(802, 805): "overcast"
        }


    def set_weather_image(self, weather_id):
        """Shows emoji based on the current weather"""
        for key, icon_name in self.weather_icons_keys.items():
            if weather_id in key:
                self.icon_label.setPixmap(self.icons.get(icon_name))
                return


    def load_cities_from_json(self, filename):
        """Load cities from a JSON file and enable autocomplete in QLineEdit."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                cities = json.load(file)

                # Store city names in a list
                self.city_names = [f"{city['name']}, {city['country']}" for city in cities]

                # Debug: Check if the list has data
                # print("Loaded cities:", len(city_names))

                if not self.city_names:
                    print("Warning: No cities loaded for autocomplete.")
                    return  # Avoid setting an empty model

                self.completer_setup(self.city_names)

        except Exception as e:
            print(f"Error loading cities: {e}")

    def completer_setup(self, city_names):
        # Create a QStringListModel and assign it to QCompleter
        model = QStringListModel(city_names)
        # Create QCompleter and attach it to self.city_input
        completer = QCompleter(self)
        completer.setModel(model)
        completer.setFilterMode(Qt.MatchContains)  # Allows matching anywhere in the text
        completer.setCompletionMode(QCompleter.PopupCompletion)  # Shows dropdown suggestions
        # Assign completer to the input field
        self.city_input.setCompleter(completer)

    def calculate_temperature(self, data):
        temp_k = data["main"]["temp"]
        temp_c = temp_k - self.kelvin_scale
        # temp_f = (temp_k * 9/5) - 459.67
        return temp_c

    def get_feels_like(self, data):
        temp_k = data["main"]["temp"]
        # feels like temp
        like = data["main"].get("feels_like", temp_k) - self.kelvin_scale
        print(like)
        return like

    def add_to_favorites(self):
        city_to_add = self.get_input_text()

        try:
            with open("favorites.json", "r") as in_file:
                current_favorites = json.load(in_file)
        except FileNotFoundError:
            print("File not found error!")
            current_favorites = {"favorites": []}  # Initialize if file doesn't exist
            with open("favorites.json", "w") as out_file:
                json.dump(current_favorites, out_file, indent=4)
            return

        # check for duplications
        if city_to_add not in current_favorites["favorites"]:
            current_favorites["favorites"].append(city_to_add)

        with open("favorites.json", "w") as out_file:
            json.dump(current_favorites, out_file, indent=4)

        self.load_favorites()
        self.city_input.setText(city_to_add)

    def load_favorites(self):
        try:
            with open("favorites.json", "r") as in_file:
                data = json.load(in_file)
                favorites_list = data.get("favorites", [])
                print(favorites_list)
        except FileNotFoundError:
            favorites_list = []

        self.favorites_combo_box.clear()  # Clear existing items
        for item in favorites_list:
            self.favorites_combo_box.addItem(item)

    def load_selected_favorite(self):
        selected_city = self.favorites_combo_box.currentText()
        self.city_input.setText(selected_city)

    @staticmethod
    def get_weather_descriptions(data):
        weather_id = data["weather"][0]["id"]
        weather_desc = data["weather"][0]["description"]
        print(weather_desc)
        return weather_id, weather_desc

    @staticmethod
    def get_wind_speed(data):
        wind_speed = data["wind"].get("speed", 0)
        return wind_speed



if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
