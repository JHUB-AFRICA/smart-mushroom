# 🍄 Smart Mushroom Farming System

An IoT-based smart mushroom cultivation system that automatically monitors and controls environmental conditions to optimize mushroom growth. The project uses ESP32, Raspberry Pi, sensors, actuators, and a web dashboard to provide real-time monitoring, automation, and remote management.

---

## 📖 Project Overview

Mushroom cultivation requires precise environmental conditions such as temperature, humidity, carbon dioxide concentration, and lighting. Manual monitoring is time-consuming and can lead to inconsistent yields.

The Smart Mushroom Farming System automates these processes by continuously monitoring the growing environment and controlling the necessary equipment to maintain ideal conditions for healthy mushroom production.

---

## 🎯 Objectives

- Monitor environmental conditions in real time
- Automatically regulate mushroom growing conditions
- Reduce manual labour
- Improve mushroom yield and quality
- Enable remote monitoring through an IoT dashboard
- Store environmental data for analysis and future prediction

---

# 🏗️ System Architecture

```
                +----------------+
                | Web Dashboard  |
                +-------+--------+
                        |
                    Wi-Fi/Internet
                        |
                +-------+--------+
                | Raspberry Pi   |
                | Data Server    |
                +-------+--------+
                        |
                   MQTT / HTTP
                        |
                +-------+--------+
                |     ESP32      |
                +-------+--------+
                        |
      ---------------------------------------
      |        |        |        |           |
   DHT22     LDR     CO₂      Soil       Water
Temperature  Light  Sensor   Moisture   Level
Humidity

                        |
                Relay Module
                        |
    --------------------------------------------
    |          |          |          |          |
   Fan      Heater   Humidifier    Lights    Water Pump

```

---

# 🧰 Hardware Components

## Microcontroller

- ESP32 Development Board

## Edge Computing

- Raspberry Pi 4

## Sensors

- DHT22 Temperature & Humidity Sensor
- LDR Light Sensor
- CO₂ Sensor
- Water Level Sensor
- Soil Moisture Sensor (optional)

## Actuators

- Exhaust Fan
- Humidifier
- Heater
- LED Grow Lights
- Water Pump

## Other Components

- Relay Module
- LCD Display
- Power Supply
- Jumper Wires

---

# 💻 Software Stack

## Programming Languages

- Python
- C++
- HTML
- CSS
- JavaScript

## Frameworks & Libraries

- Arduino IDE
- ESP32 WiFi Library
- MQTT
- Flask
- SQLite
- Chart.js

## Simulation

- Wokwi

## Dashboard

- Flask Web Server
- HTML/CSS
- JavaScript

---

# 🌐 Features

- Real-time monitoring
- Automatic environmental control
- Remote web dashboard
- Historical data logging
- Graphical visualization
- Alert notifications
- Scalable architecture
- Low power operation

---

# 📂 Project Structure

```
Smart-Mushroom-System/

│
├── ESP32/
│   ├── main.ino
│   └── sensors.cpp
│
├── RaspberryPi/
│   ├── app.py
│   ├── mqtt_client.py
│   ├── database.py
│   └── requirements.txt
│
├── Dashboard/
│   ├── templates/
│   ├── static/
│   └── app.py
│
├── Simulation/
│   ├── wokwi-project.json
│   └── diagram.json
│
├── Images/
│
├── Documentation/
│
└── README.md
```

---

# ⚙️ Working Principle

1. Sensors continuously measure environmental conditions.
2. ESP32 reads all sensor values.
3. Sensor data is transmitted to the Raspberry Pi.
4. Raspberry Pi stores the data in a database.
5. Dashboard displays live environmental conditions.
6. If any parameter exceeds predefined thresholds:
   - Fan turns ON
   - Humidifier activates
   - Heater activates
   - Lights switch ON/OFF
   - Water pump irrigates when required
7. Users can remotely monitor the system through the dashboard.

---

# 📊 Parameters Monitored

| Parameter | Sensor |
|-----------|--------|
| Temperature | DHT22 |
| Humidity | DHT22 |
| Light Intensity | LDR |
| CO₂ | CO₂ Sensor |
| Water Level | Water Level Sensor |

---

# 🚀 Future Improvements

- AI-based environmental prediction
- Machine learning for yield optimisation
- Mobile application
- Camera monitoring
- Automatic disease detection
- Cloud integration
- SMS and Email alerts
- Solar-powered operation

---

# 📸 Project Images

Add screenshots here:

- Mushroom house design
- Wokwi simulation
- Dashboard
- Hardware prototype
- Wiring diagrams

---

# 📈 Project Status

🚧 Currently Under Development

### Completed

- System design
- Hardware selection
- Wokwi simulation
- Mushroom room design
- Raspberry Pi integration planning

### In Progress

- Dashboard development
- Hardware prototype
- ESP32 programming
- Raspberry Pi communication

### Upcoming

- Testing
- Data analysis
- AI integration
- Final deployment

---

# 🤝 Contributors

- **Emmanuel Mudasia** (IoT lead)
- IoT Team lead
1.talesofmaurixio
2.TonyK0
3.Caroline-Irura
4.mwcee2222-commits
5.christophermabinda-beep
6.vincentnganga-eng
7.karume-tech
8.Eliud305
9.mrcloeteex-ai
10.akomo
11.nyangicharles960-sys

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub!
