import time
import cv2
import dearpygui.dearpygui as dpg
import threading

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class ImreadVideo(Node):
    
    frame: cv2.typing.MatLike
    
    def __init__(self):
        super().__init__("Imread Video", "Output", "Inputs", 400, output_lable="Video (Images)")
        self.file_path = dpg.generate_uuid()
        self.image_view = dpg.generate_uuid()
        self.video_selected = ""
        self.vidoe_running = False
        
        threading.Thread(target=self._run_video, daemon=True).start()
        
        
    def start_video(self):
        self.vidoe_running = True
        
    def stop_video(self):
        self.vidoe_running = False
        
    def set_file_path(self, sender, app_data):
        self.vidoe_running = False
        video_selected: dict = app_data["selections"]

        for i in video_selected.values():
            self.video_selected = i
            break
        
        self._set_first_frame()
        self._call_output_nodes()
        
    def _set_frame_to_texture(self, frame):
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
        
    def _set_first_frame(self):
        if self.video_selected:
            cap = cv2.VideoCapture(self.video_selected)
            ret, frame = cap.read()
            self.frame = frame
            
            self._set_frame_to_texture(frame)
            
            cap.release()
        
    def _run_video(self):
        delta = 0
        while True:
            if not self.vidoe_running:
                time.sleep(0.1)
                continue
            if self.video_selected == "":
                self.vidoe_running = False
                self.on_error("No video selected")
                continue
            cap = cv2.VideoCapture(self.video_selected if self.video_selected else 0)
            start = time.time()
            while self.vidoe_running:
                ret, frame = cap.read()
                if ret:
                    self.frame = frame
                    self._set_frame_to_texture(frame)
                    self.force_update()
                    delta = time.time() - start
                    time.sleep(max(0, 1/cap.get(cv2.CAP_PROP_FPS) - delta))
                    start = time.time()
                else:
                    # Restart the video
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            cap.release()
            time.sleep(0.1)
            
    def execute(self, data: NodePackage) -> NodePackage:
            
        data.image = self.frame
        
        return data
            
    def compose(self):
        
        with dpg.file_dialog(directory_selector=False, show=False, tag=self.file_path, file_count=1, width=700, height=400, callback=self.set_file_path):
            dpg.add_file_extension(".mp4")
            
        dpg.add_button(label="Select Video", callback=lambda: dpg.show_item(self.file_path))
        
        with dpg.group(horizontal=True):
            dpg.add_button(label="Start Video", callback=self.start_video)
            dpg.add_button(label="Stop Video", callback=self.stop_video)
        
        with dpg.texture_registry():
            dpg.add_dynamic_texture(400, 400, [0.0, 0.0, 0.0, 255.0] * 400 * 400, tag=self.image_view)
        
        dpg.add_image(self.image_view, width=400, height=400)