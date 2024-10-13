import time
import cv2
import dearpygui.dearpygui as dpg
import threading

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class ImreadWebcam(Node):
    
    def __init__(self) -> None:
        super().__init__("Imread Webcam", "Output", "Inputs", 400, output_lable="Image")
        self.camera_id = dpg.generate_uuid()
        self.image_view = dpg.generate_uuid()
        self.vidoe_running = False
        self.cam_list = list()
        self.latest_frame = None
        
    def on_init(self):
        self._make_cam_list()
        threading.Thread(target=self._run_video, daemon=True).start()
        
    def start_video(self):
        self.vidoe_running = True
        
    def stop_video(self):
        self.vidoe_running = False
        
    def set_image(self, frame):
        texture_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        # Resize the image to 400x400 (But keep the aspect ratio and fill the rest with black)
        if texture_image.shape[0] > texture_image.shape[1]:
            new_width = int(texture_image.shape[1] * 400 / texture_image.shape[0])
            new_height = 400
        else:
            new_width = 400
            new_height = int(texture_image.shape[0] * 400 / texture_image.shape[1])
        texture_image = cv2.resize(texture_image, (new_width, new_height))
        texture_image = cv2.copyMakeBorder(texture_image, (400 - new_height) // 2, (400 - new_height) // 2, (400 - new_width) // 2, (400 - new_width) // 2, cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])
        texture_image = texture_image.astype(float)
        texture_image /= 255
        dpg.set_value(self.image_view, texture_image.flatten())
        
    def _run_video(self):
        while True:
            if self.vidoe_running:
                cap = cv2.VideoCapture(self.cam_list.index(dpg.get_value(self.camera_id)))
                while self.vidoe_running:
                    ret, frame = cap.read()
                    if ret:
                        self.set_image(frame)
                        self.latest_frame = frame
                    else:
                        break
                    
                cap.release()
            else:
                time.sleep(0.1)
                
    def _make_cam_list(self):
        for i in range(10):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.cam_list.append(f"Camera {i}")
                    cap.release()
            except Exception as e:
                pass
                
        dpg.configure_item(self.camera_id, items=self.cam_list)
        
    def compose(self):
        
        dpg.add_combo(label="Webcam", tag=self.camera_id, width=100)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Start Video", callback=self.start_video)
            dpg.add_button(label="Stop Video", callback=self.stop_video)
        
        with dpg.texture_registry():
            dpg.add_dynamic_texture(400, 400, [0.0, 0.0, 0.0, 255.0] * 400 * 400, tag=self.image_view)
        
        dpg.add_image(self.image_view, width=400, height=400)
        
    def execute(self, data: NodePackage) -> NodePackage:
        
        if self.vidoe_running:
            data.image = self.latest_frame or data.image
        
        return data