import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class HueSelection(Node):
    
    def __init__(self) -> None:
        super().__init__("Hue Selection", "Both", "Filter/Mask", 120, input_lable="Image", output_lable="Mask")
        self.hue_id = dpg.generate_uuid()
        self.window_id = dpg.generate_uuid()
        self.hue_preview_id = dpg.generate_uuid()
        self.hue = 0
        self.window = 0
        
    def on_save(self) -> dict:
        return {"hue": self.hue, "window": self.window}
    
    def on_load(self, data: dict):
        self.hue = data["hue"]
        self.window = data["window"]
        dpg.set_value(self.hue_id, self.hue)
        dpg.set_value(self.window_id, self.window)
        
        
    def execute(self, data: NodePackage) -> NodePackage:
        # Make a mask of the hue value within a certain range (window)
        self.hue = dpg.get_value(self.hue_id)
        self.window = dpg.get_value(self.window_id)   
        hsv = cv2.cvtColor(data.image, cv2.COLOR_BGR2HSV)
        lower = (self.hue - self.window, 0, 0)
        upper = (self.hue + self.window, 255, 255)
        mask = cv2.inRange(hsv, lower, upper) # type: ignore
        data.image = mask                
        return data
        
    def compose(self):
        # dpg.add_slider_float(label="Hue", default_value=90, min_value=0, max_value=180, width=100, tag=self.hue_id, callback=self.update, format="%.0f")
        dpg.add_input_float(label="Hue", default_value=90, width=100, tag=self.hue_id, callback=self.update)
        dpg.add_slider_int(label="Window", default_value=10, min_value=0, max_value=180, width=100, tag=self.window_id, callback=self.update)