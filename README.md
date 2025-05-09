# mmWave Setup Wizard

A PySide6-based GUI wizard to streamline the installation of TI mmWave SDK tools and automate data collection for your mmWave hardware.

## 📂 Project Structure

```

your\_project/
│
├── setup\_wizard.py        # Main Qt wizard application
├── transfer\_file.py       # Data-transfer script (loose file)
├── config.json            # Configuration for transfer\_file.py
└── resources/             # GUI assets
├── logo.png
├── banner.png
└── watermark.png

````

## Prerequisites

- **Windows 10+**
- **Python 3.6+** (must be on your `PATH`)
- Install dependencies via pip:
  ```bash
  pip install PySide6 psutil requests pyserial
