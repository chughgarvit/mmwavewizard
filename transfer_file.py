import time
import os
import re
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import paramiko
from scp import SCPClient

class DelayedTransferHandler(FileSystemEventHandler):
    def __init__(self):
        self.bin_pattern = re.compile(r"adc_data_Raw_(\d+)\.bin")

    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            folder = os.path.dirname(file_path)

            match = self.bin_pattern.match(file_name)
            if match:
                current_index = int(match.group(1))
                prev_index = current_index - 1
                if prev_index >= 0:
                    prev_file = f"adc_data_Raw_{prev_index}.bin"
                    prev_file_path = os.path.join(folder, prev_file)
                    if os.path.exists(prev_file_path):
                        print(f"Detected {file_name}, transferring {prev_file}")
                        self.transfer_file(prev_file_path)
                    else:
                        print(f"Previous file {prev_file} not found for transfer.")

    def transfer_file(self, filepath):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect('10.5.20.128', username='argha', password='nitd@12345')

            with SCPClient(ssh.get_transport()) as scp:
                scp.put(filepath, remote_path='/home/argha')
                print(f"✅ Transfer successful: {filepath}")
        except Exception as e:
            print(f"❌ Transfer failed: {e}")
        finally:
            ssh.close()

def monitor_directory(path_to_watch):
    event_handler = DelayedTransferHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    observer.start()
    print(f"🔍 Monitoring directory and subdirectories: {path_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Main block
if __name__ == "__main__":
    directory_to_monitor = r"C:\ti\mmwave_studio_02_01_01_00\mmWaveStudio\PostProc"
    monitor_directory(directory_to_monitor)
