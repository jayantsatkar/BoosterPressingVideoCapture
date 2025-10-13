from PyQt6.QtCore import QThread, pyqtSignal
import cv2, mss, numpy as np, os, time
import datetime

class ScreenRecorder(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, dmc_clean):
        super().__init__()
        self.dmc_clean = dmc_clean
        self.is_running = True

    def run(self):
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        output_dir = os.path.join("videos", year, month, day)

        os.makedirs(output_dir, exist_ok=True)
        #output_path = f"videos/{self.dmc_clean}.avi"
        output_path = os.path.join(output_dir, f"{self.dmc_clean}.avi")
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        sct = mss.mss()
        monitor = sct.monitors[1]
        frame_width, frame_height = monitor["width"], monitor["height"]
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (frame_width, frame_height))

        try:
            while self.is_running:
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                out.write(frame)
                #time.sleep(1/40)  # ~20 FPS

        except Exception as e:
            self.error.emit(str(e))

        finally:
            out.release()
            self.finished.emit()

    def stop(self):
        self.is_running = False
