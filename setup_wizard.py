import sys
import os
import shutil
import subprocess
import webbrowser
import winreg
import socket
import psutil
from serial.tools import list_ports
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QLabel,
    QPushButton, QVBoxLayout, QFileDialog, QMessageBox
)

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

# === Check & Run Implementations ===

def check_mmwave_sdk():
    return find_ti_subfolder("mmwave_sdk_") is not None

def run_mmwave_sdk_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select mmWave SDK installer", "", "Executable Files (*.exe)")
    if path:
        try:
            subprocess.Popen([path])
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to launch SDK installer:\n{e}")

def check_vc_redist_2013_x86():
    key_path = r"SOFTWARE\Wow6432Node\Microsoft\VisualStudio\12.0\VC\Runtimes\x86"
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        installed, _ = winreg.QueryValueEx(key, "Installed")
        return installed == 1
    except FileNotFoundError:
        return False

def run_vc_redist_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select VC++ 2013 x86 installer", "", "Executable Files (*.exe)")
    if path:
        subprocess.Popen([path])

def check_matlab_runtime():
    base = r"C:\Program Files\MATLAB\MATLAB Runtime"
    try:
        for d in os.listdir(base):
            if d.startswith("R2015a"):
                return True
    except FileNotFoundError:
        pass
    return False

def run_matlab_runtime_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select MATLAB Runtime installer", "", "Executable Files (*.exe)")
    if path:
        subprocess.Popen([path])

def check_ccstudio():
    return find_ti_subfolder("ccs") is not None

def run_ccstudio_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select Code Composer Studio installer", "", "Executable Files (*.exe)")
    if path:
        subprocess.Popen([path])

def check_mmwave_studio():
    return find_ti_subfolder("mmwave_studio_") is not None

def run_mmwave_studio_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select mmWave Studio installer", "", "Executable Files (*.exe)")
    if path:
        subprocess.Popen([path])

def check_ticloud_agent():
    return shutil.which("ticloud_agent") is not None

def check_demo_visualizer():
    return find_ti_subfolder("mmwave_demo_visualizer") is not None

def run_demo_visualizer_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select Demo Visualizer installer", "", "Executable Files (*.exe)")
    if path:
        subprocess.Popen([path])

def check_emupack():
    return find_ti_subfolder("xds_emulation_software_package") is not None

def run_emupack_installer():
    path, _ = QFileDialog.getOpenFileName(None, "Select EMUPACK installer", "", "Executable Files (*.exe)")
    if path:
        subprocess.Popen([path])

def check_com_ports():
    ports = list_ports.comports()
    count = sum(1 for p in ports if "AR-DevPack-EVM-012" in p.description)
    return count >= 4

def check_network_adapter():
    for nic, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                if addr.address == "192.168.33.30" and addr.netmask == "255.255.255.0":
                    return True
    return False

def get_mmwave_studio_scripts_dir():
    folder = find_ti_subfolder("mmwave_studio_")
    if folder:
        return os.path.join(folder, "mmWaveStudio", "Scripts")
    return None

def check_lua_script():
    scripts_dir = get_mmwave_studio_scripts_dir()
    if scripts_dir:
        return os.path.isfile(os.path.join(scripts_dir, "dataCaptureScriptStick.lua"))
    return False

def run_copy_lua_script():
    src, _ = QFileDialog.getOpenFileName(None, "Select dataCaptureScriptStick.lua", "", "Lua Files (*.lua)")
    scripts_dir = get_mmwave_studio_scripts_dir()
    if not scripts_dir:
        QMessageBox.warning(None, "Warning", "Install mmWave Studio first to copy Lua script.")
        return
    if src:
        os.makedirs(scripts_dir, exist_ok=True)
        try:
            shutil.copy(src, os.path.join(scripts_dir, os.path.basename(src)))
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to copy Lua script:\n{e}")

def launch_mmwave_studio():
    folder = find_ti_subfolder("mmwave_studio_")
    if not folder:
        QMessageBox.warning(None, "Warning", "Install mmWave Studio first.")
        return
    exe = os.path.join(folder, "mmWaveStudio", "mmWaveStudio.exe")
    if os.path.isfile(exe):
        subprocess.Popen([exe])
    else:
        QMessageBox.critical(None, "Error", "mmWaveStudio.exe not found.")

def check_data_capture():
    folder = find_ti_subfolder("mmwave_studio_")
    if not folder:
        return False
    post = os.path.join(folder, "mmWaveStudio", "PostProc")
    if not os.path.isdir(post):
        return False
    return len(os.listdir(post)) > 0

# === Instruction Page ===
class InstructionPage(QWizardPage):
    def __init__(self, title, html_content):
        super().__init__()
        self.setTitle(title)
        label = QLabel()
        label.setWordWrap(True)
        label.setText(html_content)
        layout = QVBoxLayout(self)
        layout.addWidget(label)

# === Step Page ===
class StepPage(QWizardPage):
    def __init__(self, title, check_fn, run_fn=None, download_url=None):
        super().__init__()
        self.setTitle(title)
        self.check_fn = check_fn
        self.run_fn = run_fn
        self.download_url = download_url
        self.status_label = QLabel("Status: Not checked")
        btn_check = QPushButton("Check")
        btn_check.clicked.connect(self.do_check)
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(btn_check)
        if self.run_fn:
            btn_run = QPushButton("Run Installer / Action")
            btn_run.clicked.connect(self.run_fn)
            layout.addWidget(btn_run)
        if self.download_url:
            btn_download = QPushButton("Download Installer")
            btn_download.clicked.connect(lambda: webbrowser.open(self.download_url))
            layout.addWidget(btn_download)
        btn_skip = QPushButton("Skip")
        btn_skip.clicked.connect(self.skip_step)
        layout.addWidget(btn_skip)
        btn_prev = QPushButton("Previous")
        btn_prev.clicked.connect(lambda: self.wizard().back())
        layout.addWidget(btn_prev)
    def do_check(self):
        try:
            ok = self.check_fn()
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
            return
        if ok:
            self.status_label.setText("✔️ Done")
            self.completeChanged.emit()
        else:
            self.status_label.setText("❌ Not detected or incomplete")
    def skip_step(self):
        self.status_label.setText("⏭️ Skipped by user")
        self.completeChanged.emit()
        self.wizard().next()
    def isComplete(self):
        t = self.status_label.text()
        return t.startswith("✔️") or t.startswith("⏭️")

# === Main Application ===
def main():
    app = QApplication(sys.argv)
    wiz = QWizard()
    wiz.setWindowTitle("mmWave Setup Wizard")
    # Installation Steps
    wiz.addPage(StepPage("Install mmWave SDK", check_mmwave_sdk, run_mmwave_sdk_installer,
        "https://www.ti.com/tool/MMWAVE-SDK"))
    wiz.addPage(StepPage("Install Visual C++ 2013 x86", check_vc_redist_2013_x86, run_vc_redist_installer,
        "https://www.microsoft.com/en-in/download/details.aspx?id=40784"))
    wiz.addPage(StepPage("Install MATLAB Runtime R2015a SP1", check_matlab_runtime, run_matlab_runtime_installer,
        "https://ssd.mathworks.com/supportfiles/downloads/R2015a/deployment_files/R2015aSP1/installers/win32/MCR_R2015aSP1_win32_installer.exe"))
    wiz.addPage(StepPage("Install Code Composer Studio", check_ccstudio, run_ccstudio_installer,
        "https://www.ti.com/tool/CCSTUDIO"))
    wiz.addPage(StepPage("Install mmWave Studio", check_mmwave_studio, run_mmwave_studio_installer,
        "https://www.ti.com/tool/MMWAVE-STUDIO"))
    wiz.addPage(StepPage("Install ticloud_agent", check_ticloud_agent, None, None))
    wiz.addPage(StepPage("Install mmWave Demo Visualizer 3.6.0", check_demo_visualizer, run_demo_visualizer_installer,
        "https://dev.ti.com/gallery/view/mmwave/mmWave_Demo_Visualizer/ver/3.6.0/"))
    wiz.addPage(StepPage("Install EMUPACK", check_emupack, run_emupack_installer,
        "http://processors.wiki.ti.com/index.php/XDS_Emulation_Software_Package"))
    # Flashing Instructions
    wiz.addPage(InstructionPage(
        "Hardware Connection", 
        "Connect the IWR1843 radar to the DCA1000 EVM, attach Ethernet and USB cables, and power with a 5V/2A adapter.\n\n"
        "Set SOP pins to Debug mode as shown in the TI documentation."
    ))
    wiz.addPage(InstructionPage(
        "COM Port Detection",
        "Once connected, click 'Check' to verify at least four AR-DevPack-EVM-012 COM ports appear."
    ))
    wiz.addPage(StepPage("Detect COM Ports (IWR1843 + DCA1000)", check_com_ports))
    wiz.addPage(InstructionPage(
        "Network Configuration",
        "Open Network Settings → Adapter Settings → IPv4. Set IP to 192.168.33.30, Mask 255.255.255.0, then click 'Check'."
    ))
    wiz.addPage(StepPage("Configure Network Adapter", check_network_adapter))
    wiz.addPage(InstructionPage(
        "Lua Script Setup",
        "Download dataCaptureScriptStick.lua, then click 'Run Action' to copy it into the mmWave Studio Scripts folder."
    ))
    wiz.addPage(StepPage("Copy Lua Script into Scripts Folder", check_lua_script, run_copy_lua_script,
        "https://github.com/arghasen10/OpenRadar/blob/master/dataCaptureScriptStick.lua"))
    wiz.addPage(InstructionPage(
        "Launch mmWave Studio",
        "Click 'Run Action' to open mmWave Studio, go to Lua Shell → Load, and select the script."
    ))
    wiz.addPage(StepPage("Launch mmWave Studio", check_mmwave_studio, launch_mmwave_studio))
    wiz.addPage(InstructionPage(
        "Verify Data Capture",
        "After script runs, 'Check' will confirm files appear in the PostProc folder."
    ))
    wiz.addPage(StepPage("Verify Data Capture", check_data_capture))
    wiz.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()