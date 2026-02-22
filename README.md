# Labs & Workshops — University Course Materials

> **Note:** All course materials, lab guides, and workshop documents in this repository are written in **Spanish**, as they are designed for Spanish-speaking university students.

This repository contains laboratory and workshop materials for university courses taught by Omar Francisco Velazquez Juarez. The content covers engineering topics including embedded systems, IoT communications, event-driven programming, computer vision, and natural language processing.

---

## Repository Structure

```
laboratorios-y-talleres/
├── embeded-systems/          # Embedded systems labs (ESP32, Arduino IDE, Wokwi)
├── iot-and-communications/   # IoT & communications labs (LoRaWAN, ChirpStack, MQTT)
├── POE/                      # Event-driven programming labs (React, Tkinter)
├── computer-vision/          # Computer vision notebooks (MRI tumor classification)
├── NLP/                      # Natural language processing (BERT, Orange)
├── sdd-for-claude-code/      # Software design documentation templates
├── Systems_architecture/     # Systems architecture (in progress)
├── LICENSE                   # CC BY 4.0 License
└── README.md                 # This file
```

---

## Courses & Topics

### Embedded Systems (`embeded-systems/`)
**Course:** Programación II — Ingeniería en TICs
Hands-on labs using ESP32-S3, Arduino IDE 2, and the Wokwi simulator. Topics include:
- Week 1 — Functions: non-blocking LED control with `millis()`
- Week 2 — Finite State Machines (FSM): debouncing and state-based logic
- Week 3 — Cooperative Schedulers: multi-task non-blocking architecture
- Week 4 — Libraries: Telemetry v1 library design for BMP280 and DHT sensors

### IoT & Communications (`iot-and-communications/`)
**Course:** Comunicaciones e IoT
Labs covering digital/analog signals, modulation, wireless protocols, and LoRaWAN deployment. Topics include:
- Weeks 1–3 — PWM, modulation fundamentals, wave analysis
- Week 4 — FSK modulation (Python)
- Week 5 — Binary encoding and network traffic observation (Wireshark)
- Week 6 — Error correction and detection; LoRaWAN device connection to ChirpStack
- Week 7 — TTGO LoRa32 registration with ChirpStack (OTAA)
- Week 8 — Ultrasonic sensor + LoRaWAN IoT system
- LoRaWAN Practice Weeks — ChirpStack API REST, codec decoders, Node-RED integration, webhooks

### Event-Driven Programming (`POE/`)
**Course:** Programación II — Ingeniería en TICs
Full-stack application development with UI event handling. Two supported routes:
- **Route A:** Node.js + React (TypeScript optional) with Vite
- **Route B:** Python + Tkinter

Topics include:
- Week 1 — Environment setup and first UI event
- Week 2 — Event programming with VS Code debugging
- Week 3 — Modular architecture: objects, controls, and components
- Week 4 — Application structure with logging, error handling, and assertions

### Computer Vision (`computer-vision/`)
Jupyter notebook for brain tumor MRI classification using machine learning (CNN/deep learning).

### Natural Language Processing (`NLP/`)
NLP experiments including BERT model implementation and Orange Data Mining workflows.

### Software Design Documentation (`sdd-for-claude-code/`)
FDR (Functional Design Record) templates and examples for structured software design documentation, intended for use with AI-assisted development tools.

---

## Teaching Methodology

All labs follow a consistent structure:
- **Incremental development:** step-by-step code progression with validation at each stage
- **Evidence-based learning:** students document execution screenshots, logs, and outputs
- **AI integration:** explicit documentation of AI tool usage (Claude, ChatGPT, Copilot)
- **Reproducibility:** exact commands, version numbers, and procedures provided

Each lab requires a student report including: header (name, ID, group, date), evidence of each stage, mandatory questions, AI usage declaration, and APA references.

---

## License

This work is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

You are free to share and adapt this material for any purpose, even commercially, as long as you give appropriate credit to the author. See the [LICENSE](LICENSE) file for full details.

---

## Author & Tutoring

**Omar Francisco Velazquez Juarez**
University instructor — Embedded Systems, IoT, and Software Engineering
[ovelazquezj@gmail.com](mailto:ovelazquezj@gmail.com)

For questions, tutoring, or academic support, contact the instructor directly by email.
