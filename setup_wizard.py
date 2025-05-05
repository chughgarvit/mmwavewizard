import sys
import os
import shutil
import subprocess
import webbrowser
import winreg
import socket
import psutil
import requests
from serial.tools import list_ports
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QLabel,
    QPushButton, QVBoxLayout, QFileDialog, QMessageBox
)
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import Qt

# === Resource Paths ===
# Place these in ./resources/ alongside this script:
#   logo.png, watermark.png, banner.png,
#   power.png, ports.png, ip.png
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(SCRIPT_DIR, 'resources')

# === Helper Functions ===
def find_ti_subfolder(prefix):
    base = r"C:\ti"
    try:
        for name in os.listdir(base):
            if name.lower().startswith(prefix.lower()):
                return os.path.join(base, name)
    except FileNotFoundError:
        pass
    return None

# === Check and Run Implementations ===
def check_mmwave_sdk():
    return find_ti_subfolder("mmwave_sdk_") is not None

def run_mmwave_sdk_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select mmWave SDK installer", "", "*.exe")
    if path: subprocess.Popen([path])

def check_vc_redist_2013_x86():
    key = r"SOFTWARE\Wow6432Node\Microsoft\VisualStudio\12.0\VC\Runtimes\x86"
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key)
        inst, _ = winreg.QueryValueEx(k, "Installed")
        return inst == 1
    except FileNotFoundError:
        return False

def run_vc_redist_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select VC++ 2013 x86 installer", "", "*.exe")
    if path: subprocess.Popen([path])

def check_matlab_runtime():
    base = r"C:\Program Files\MATLAB\MATLAB Runtime"
    return any(d.lower().startswith("r2015a") for d in (os.listdir(base) if os.path.isdir(base) else []))

def run_matlab_runtime_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select MATLAB Runtime installer", "", "*.exe")
    if path: subprocess.Popen([path])

def check_ccstudio():
    return find_ti_subfolder("ccs") is not None

def run_ccstudio_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select Code Composer Studio installer", "", "*.exe")
    if path: subprocess.Popen([path])

def check_mmwave_studio():
    return find_ti_subfolder("mmwave_studio_") is not None

def run_mmwave_studio_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select mmWave Studio installer", "", "*.exe")
    if path: subprocess.Popen([path])

def check_ticloud_agent():
    return os.path.isdir(os.path.expanduser("~/TICloudAgent"))

def check_demo_visualizer():
    return os.path.isdir(os.path.expanduser("~/guicomposer/runtime/gcruntime.v11"))

def run_demo_visualizer_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select Demo Visualizer installer", "", "*.exe")
    if path: subprocess.Popen([path])

def check_emupack():
    base = r"C:\ti\ccs_base"
    return any(d.lower().startswith("emulation") for d in (os.listdir(base) if os.path.isdir(base) else []))

def run_emupack_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select EMUPACK installer", "", "*.exe")
    if path: subprocess.Popen([path])

def check_com_ports():
    ports = list_ports.comports()
    cnt = sum("AR-DevPack-EVM-012" in p.description for p in ports)
    cnt += sum("XDS110 Class" in p.description for p in ports)
    return cnt >= 6

def check_network_adapter():
    for addrs in psutil.net_if_addrs().values():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == "192.168.33.30" and addr.netmask == "255.255.255.0":
                return True
    return False

def get_mmwave_studio_scripts_dir():
    f = find_ti_subfolder("mmwave_studio_")
    return os.path.join(f, "mmWaveStudio", "Scripts") if f else None

def check_lua_script():
    d = get_mmwave_studio_scripts_dir()
    return os.path.isfile(os.path.join(d, "dataCaptureScriptStick.lua")) if d else False

def download_and_install_lua():
    url = "https://raw.githubusercontent.com/arghasen10/OpenRadar/master/dataCaptureScriptStick.lua"
    scripts_dir = get_mmwave_studio_scripts_dir()
    if not scripts_dir:
        QMessageBox.warning(None, "Warning", "Install mmWave Studio first.")
        return
    os.makedirs(scripts_dir, exist_ok=True)
    try:
        r = requests.get(url)
        r.raise_for_status()
        dest = os.path.join(scripts_dir, "dataCaptureScriptStick.lua")
        with open(dest, "wb") as f:
            f.write(r.content)
        QMessageBox.information(None, "Success", "Lua script installed.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Download failed:\n{e}")

def launch_mmwave_studio():
    folder = find_ti_subfolder("mmwave_studio_") or ""
    exe = os.path.join(folder, "mmWaveStudio", "mmWaveStudio.exe")
    if os.path.isfile(exe):
        subprocess.Popen([exe])
    else:
        QMessageBox.critical(None, "Error", f"Executable not found at {exe}")

def check_data_capture():
    folder = find_ti_subfolder("mmwave_studio_") or ""
    post = os.path.join(folder, "mmWaveStudio", "PostProc")
    return os.path.isdir(post) and bool(os.listdir(post))

# === Corrective Actions ===
def open_device_manager():
    subprocess.Popen(["mmc", "devmgmt.msc"] )

def open_network_settings():
    subprocess.Popen(["control.exe", "ncpa.cpl"] )

# === Wizard Page Classes ===
class InstructionPage(QWizardPage):
    def __init__(self, title, html, image_name=None, check_fn=None, correct_fn=None):
        super().__init__()
        self.setTitle(title)
        self.check_fn = check_fn
        self.correct_fn = correct_fn
        layout = QVBoxLayout(self)

        lbl = QLabel(html)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        if image_name:
            img = os.path.join(RESOURCES_DIR, f"{image_name}.png")
            if os.path.isfile(img):
                pix = QPixmap(img)
                dpi = QApplication.primaryScreen().logicalDotsPerInch()
                size = int(dpi * 6.0 / 2.54)
                pix = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                il = QLabel()
                il.setAlignment(Qt.AlignCenter)
                il.setPixmap(pix)
                layout.addWidget(il)

        if check_fn:
            btn = QPushButton("Check")
            btn.clicked.connect(self.do_check)
            layout.addWidget(btn)

        btn_prev = QPushButton("Previous")
        btn_prev.clicked.connect(lambda: self.wizard().back())
        layout.addWidget(btn_prev)

    def do_check(self):
        try:
            ok = self.check_fn()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        if ok:
            QMessageBox.information(self, "Check Passed", f"{self.title()} OK.")
            self.wizard().next()
        else:
            if self.correct_fn:
                resp = QMessageBox.question(
                    self, "Check Failed",
                    f"{self.title()} not OK. Open settings?",
                    QMessageBox.Ok | QMessageBox.Cancel
                )
                if resp == QMessageBox.Ok:
                    self.correct_fn()
            else:
                QMessageBox.warning(self, "Check Failed", f"{self.title()} not OK.")

class StepPage(QWizardPage):
    def __init__(self, title, check_fn, run_fn=None, download_url=None):
        super().__init__()
        self.setTitle(title)
        self.check_fn = check_fn
        self.run_fn = run_fn
        self.download_url = download_url
        layout = QVBoxLayout(self)

        self.status = QLabel("Status: Not checked")
        layout.addWidget(self.status)

        btn_check = QPushButton("Check")
        btn_check.clicked.connect(self.do_check)
        layout.addWidget(btn_check)

        if run_fn:
            btn_run = QPushButton("Run Installer")
            btn_run.clicked.connect(run_fn)
            layout.addWidget(btn_run)

        if download_url:
            btn_dl = QPushButton("Download Installer")
            btn_dl.clicked.connect(lambda: webbrowser.open(download_url))
            layout.addWidget(btn_dl)

        btn_skip = QPushButton("Skip")
        btn_skip.clicked.connect(lambda: self.wizard().next())
        layout.addWidget(btn_skip)

        btn_prev = QPushButton("Previous")
        btn_prev.clicked.connect(lambda: self.wizard().back())
        layout.addWidget(btn_prev)

    def do_check(self):
        try:
            ok = self.check_fn()
        except Exception as e:
            self.status.setText(f"Error: {e}")
            return
        if ok:
            self.status.setText("✔️ Done")
            resp = QMessageBox.question(
                self, "Check Passed",
                f"{self.title()} detected. Proceed?",
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if resp == QMessageBox.Ok:
                self.wizard().next()
        else:
            self.status.setText("❌ Not OK")

    def isComplete(self):
        return self.status.text().startswith("✔️")

# === Main Application ===
def main():
    app = QApplication(sys.argv)
    wiz = QWizard()
    wiz.setWindowTitle("mmWave Setup Wizard")
    wiz.setWindowIcon(QIcon(os.path.join(RESOURCES_DIR, 'logo.png')))
    wiz.setWizardStyle(QWizard.ModernStyle)

    # Watermark + Banner stacked
    dpi = app.primaryScreen().logicalDotsPerInch()
    cm3 = int(dpi * 3.0 / 2.54)
    wm = QPixmap(os.path.join(RESOURCES_DIR, 'watermark.png')).scaled(
        cm3, cm3, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    bn = QPixmap(os.path.join(RESOURCES_DIR, 'banner.png')).scaled(
        cm3, cm3, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    combo = QPixmap(cm3, wm.height() + bn.height())
    combo.fill(Qt.transparent)
    painter = QPainter(combo)
    painter.drawPixmap((cm3 - wm.width())//2, 0, wm)
    painter.drawPixmap((cm3 - bn.width())//2, wm.height(), bn)
    painter.end()
    wiz.setPixmap(QWizard.WatermarkPixmap, combo)

    # 1) Installation
    installs = [
        ("Install mmWave SDK", check_mmwave_sdk, run_mmwave_sdk_installer, "https://www.ti.com/tool/MMWAVE-SDK"),
        ("Install Visual C++ 2013 x86", check_vc_redist_2013_x86, run_vc_redist_installer, "https://www.microsoft.com/en-in/download/details.aspx?id=40784"),
        ("Install MATLAB Runtime R2015a SP1", check_matlab_runtime, run_matlab_runtime_installer, 
         "https://ssd.mathworks.com/supportfiles/downloads/R2015a/deployment_files/R2015aSP1/installers/win32/MCR_R2015aSP1_win32_installer.exe"),
        ("Install Code Composer Studio", check_ccstudio, run_ccstudio_installer, "https://www.ti.com/tool/CCSTUDIO"),
        ("Install mmWave Studio", check_mmwave_studio, run_mmwave_studio_installer, "https://www.ti.com/tool/MMWAVE-STUDIO"),
        ("Install ticloud_agent", check_ticloud_agent, None, None),
        ("Install Demo Visualizer 3.6.0", check_demo_visualizer, run_demo_visualizer_installer, "https://dev.ti.com/gallery/view/mmwave/mmWave_Demo_Visualizer/ver/3.6.0/"),
        ("Install EMUPACK", check_emupack, run_emupack_installer, "http://processors.wiki.ti.com/index.php/XDS_Emulation_Software_Package"),
    ]
    for t, ck, rn, url in installs:
        wiz.addPage(StepPage(t, ck, rn, url))

    # 2) Hardware Connection
    wiz.addPage(InstructionPage(
        "Hardware Connection",
        "Connect IWR1843 to DCA1000, attach Ethernet & USB, power with 5V/2A.\nSet SOP pins to Debug mode (see TI docs).",
        image_name="power"
    ))

    # 3) COM Port Detection
    wiz.addPage(InstructionPage(
        "COM Port Detection",
        "Ensure you see 4× AR-DevPack-EVM-012 and 2× XDS110 ports.",
        image_name="ports",
        check_fn=check_com_ports,
        correct_fn=open_device_manager
    ))

    # 4) Network Configuration
    wiz.addPage(InstructionPage(
        "Network Configuration",
        "Set IPv4 → IP: 192.168.33.30, Mask: 255.255.255.0.",
        image_name="ip",
        check_fn=check_network_adapter,
        correct_fn=open_network_settings
    ))

    # 5) Lua Script Setup
    wiz.addPage(InstructionPage(
        "Lua Script Setup",
        "Check or install the Lua script in mmWaveStudio/Scripts.",
        check_fn=check_lua_script,
        correct_fn=download_and_install_lua
    ))

    # 6) Launch mmWave Studio
    wiz.addPage(InstructionPage(
        "Launch mmWave Studio",
        "Open mmWave Studio and load your Lua script via Lua Shell.",
        check_fn=check_mmwave_studio
    ))
    wiz.addPage(StepPage("Launch mmWave Studio", check_mmwave_studio, launch_mmwave_studio))

    # 7) Verify Data Capture
    wiz.addPage(InstructionPage(
        "Verify Data Capture",
        "After running the script, confirm files appear in PostProc.",
        check_fn=check_data_capture
    ))
    wiz.addPage(StepPage("Verify Data Capture", check_data_capture))

    wiz.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()