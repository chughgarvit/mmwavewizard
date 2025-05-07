from OpenRadar.mmwave.dataloader import DCA1000
import time
from datetime import datetime
import sys
import numpy as np

dca = DCA1000()

start_time = time.time()
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
adc_data = dca.read(num_frames=200,chirps=128, samples=140)
end_time = time.time()
total_time = end_time-start_time
print("total time ", total_time)
filename = f"adc_data_{current_time}.npy"
print("file saved as ", filename)
np.save(filename, adc_data)
# time.sleep(1)
