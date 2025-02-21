import json
import os
import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, \
    QCompleter, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QStringListModel


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

        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button =  QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.feels_like = QLabel(self)

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

        # set default location button layout
        self.set_default_button_layout = QVBoxLayout()
        self.button_set_default = QPushButton("Set Default")
        self.set_default_button_layout.addWidget(self.button_set_default)

        # temperature, emoji and description layout
        self.temperature_layout = QVBoxLayout()
        self.temperature_layout.addWidget(self.temperature_label, alignment=Qt.AlignCenter)
        self.temperature_layout.addWidget(self.emoji_label, alignment=Qt.AlignCenter)
        self.temperature_layout.addWidget(self.description_label, alignment=Qt.AlignCenter)
        self.temperature_layout.addWidget(self.feels_like, alignment=Qt.AlignCenter)

        # Wrap temperature layout in HBox to center it
        self.centered_temp_layout = QHBoxLayout()
        self.centered_temp_layout.addStretch()  # Pushes content to the center
        self.centered_temp_layout.addLayout(self.temperature_layout)
        self.centered_temp_layout.addStretch()  # Pushes content to the center

        master_layout.addLayout(self.city_input_layout)
        master_layout.addLayout(self.button_layout)
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
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")
        self.feels_like.setObjectName("feels_like")


        self.event_handler()
        self.style()
        self.load_default_location()

    def event_handler(self):
        # connect buttons
        self.get_weather_button.clicked.connect(self.get_weather)
        self.clear_button.clicked.connect(self.clear)
        self.button_set_default.clicked.connect(self.set_default_location)

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


                                """)

    def get_weather(self):
        # Get manually entered text
        city = self.city_input.text().split(",")[0]

        if not city:  # If both are empty, show an error
            self.display_error("Please enter or select a city.")
            return

        self.api_call(city)

    def clear(self):
        self.city_input.clear()
        self.temperature_label.clear()
        self.emoji_label.clear()
        self.description_label.clear()

    def set_default_location(self):
        print("set default location")
        current_city = self.city_input.text()
        if "," in current_city:
            current_city = current_city.split(",")[0]

        if current_city:
            json_object = json.dumps(current_city, indent=4)

            with open("settings.json", "w")as out_file:
                json.dump({"default_city": current_city}, out_file, indent=4)
                QMessageBox.information(self, "Saving", f"Saved {current_city} as a default.")
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



    def api_call(self, city_name):
        api_key = key

        # call the api
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data["cod"] == 200:
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
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        print(data)
        kelvin_scale = 273.15
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temp_k = data["main"]["temp"]
        temp_c = temp_k - kelvin_scale
        #temp_f = (temp_k * 9/5) - 459.67
        self.temperature_label.setText(f"{temp_c:.0f}°C")

        weather_id = data["weather"][0]["id"]
        weather_desc = data["weather"][0]["description"]
        like = data["main"]["feels_like"]
        like -= kelvin_scale
        self.feels_like.setText(f"Feels like: {like:.0f}")
        self.description_label.setText(weather_desc)

        self.emoji_label.setText(self.get_weather_emoji(weather_id))

    @staticmethod
    def get_weather_emoji(weather_id):
        """Shows emoji based on the current weather"""
        if 200 <= weather_id <= 232:
            return "🌧"

        elif 300 <= weather_id <= 321:
            return "⛅"

        elif 500 <= weather_id <= 531:
            return "🌧"

        elif 600 <= weather_id <= 622:
            return "❄"

        elif 701 <= weather_id <= 741:
            return "🌫"

        elif weather_id == 762:
            return "🌋"

        elif weather_id == 771:
            return "💨"

        elif weather_id == 781:
            return "🌪"

        elif weather_id == 800:
            return "🌞"

        elif 801 <= weather_id <= 804:
            return "☁"
        else:
            return ""

    def load_cities_from_json(self, filename):
        """Load cities from a JSON file and enable autocomplete in QLineEdit."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                cities = json.load(file)

                # Store city names in a list
                city_names = [f"{city['name']}, {city['country']}" for city in cities]

                # Debug: Check if the list has data
                # print("Loaded cities:", len(city_names))

                if not city_names:
                    print("Warning: No cities loaded for autocomplete.")
                    return  # Avoid setting an empty model

                # Create a QStringListModel and assign it to QCompleter
                model = QStringListModel(city_names)

                # Create QCompleter and attach it to self.city_input
                completer = QCompleter(self)
                completer.setModel(model)
                completer.setFilterMode(Qt.MatchContains)  # Allows matching anywhere in the text
                completer.setCompletionMode(QCompleter.PopupCompletion)  # Shows dropdown suggestions

                # Assign completer to the input field
                self.city_input.setCompleter(completer)

        except Exception as e:
            print(f"Error loading cities: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
