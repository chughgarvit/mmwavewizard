# mmwavewizard
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   

.\venv\Scripts\activate   

pyinstaller --noconfirm --onefile --windowed --name mmWaveWizard --add-data ".\resources;resources" setup_wizard.py
