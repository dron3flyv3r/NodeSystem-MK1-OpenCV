import dearpygui.dearpygui as dpg
import cv2
import numpy as np

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class SolidColor(Node):
    
    def __init__(self):
        super().__init__("Solid Color", "Output", "Inputs", 150, output_lable="Image")
        self.color = dpg.generate_uuid()
        self.width = dpg.generate_uuid()
        self.height = dpg.generate_uuid()
        self.alpha = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {
            "color": dpg.get_value(self.color),
            "width": dpg.get_value(self.width),
            "height": dpg.get_value(self.height),
            "alpha": dpg.get_value(self.alpha)
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.color, data["color"])
        dpg.set_value(self.width, data["width"])
        dpg.set_value(self.height, data["height"])
        dpg.set_value(self.alpha, data["alpha"])
        
    def compose(self):
        dpg.add_color_picker(label="Color", default_value=(255, 255, 255, 255), tag=self.color, callback=self.update, width=150, no_alpha=True)
        dpg.add_input_int(label="Width", default_value=100, tag=self.width, width=150, callback=self.update)
        dpg.add_input_int(label="Height", default_value=100, tag=self.height, width=150, callback=self.update)
        dpg.add_checkbox(label="Alpha", default_value=False, tag=self.alpha, callback=self.update)
        
    def execute(self, data: NodePackage) -> NodePackage:
            
        width = dpg.get_value(self.width)
        height = dpg.get_value(self.height)
        color = dpg.get_value(self.color)
        alpha = dpg.get_value(self.alpha)
        
        if width + height == 0:
            return data
        else:
            if width == 0:
                width = height
            elif height == 0:
                height = width
        
        # Make a solid color image
        data.image = np.zeros((height, width, 3), np.uint8)
        data.image[:] = color[:3]
        data.image = cv2.cvtColor(data.image, cv2.COLOR_RGB2BGR)
        data.image = cv2.resize(data.image, (width, height))
        
        if alpha:
            data.image = cv2.cvtColor(data.image, cv2.COLOR_BGR2BGRA)
        
        return data