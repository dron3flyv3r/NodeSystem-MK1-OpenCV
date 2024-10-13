import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Crop(Node):
    
    def __init__(self):
        super().__init__("Crop", "Both", "Filter/Manipulation", input_lable="Image", output_lable="Image")
        self.width = dpg.generate_uuid()
        self.height = dpg.generate_uuid()
        self.keep_aspect_ratio = dpg.generate_uuid()
        self.is_linked = dpg.generate_uuid()
    
    def compose(self):
        dpg.add_input_int(label="Width", default_value=0, tag=self.width, width=100, callback=self.input_change)
        dpg.add_input_int(label="Height", default_value=0, tag=self.height, width=100, callback=self.input_change)
        dpg.add_checkbox(label="Link Width width Geight", default_value=False, tag=self.is_linked)
        dpg.add_checkbox(label="Keep Aspect Ratio", default_value=True, tag=self.keep_aspect_ratio, callback=self.update)
        
    def on_save(self) -> dict:
        return {
            "width": dpg.get_value(self.width),
            "height": dpg.get_value(self.height),
            "keep_aspect_ratio": dpg.get_value(self.keep_aspect_ratio),
            "is_linked": dpg.get_value(self.is_linked)
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.width, data["width"])
        dpg.set_value(self.height, data["height"])
        dpg.set_value(self.keep_aspect_ratio, data["keep_aspect_ratio"])
        dpg.set_value(self.is_linked, data["is_linked"])
        self.update_link()
        
    def update_link(self):
        if dpg.get_value(self.is_linked):
            dpg.configure_item(self.height, enabled=False)
        else:
            dpg.configure_item(self.height, enabled=True)
        self.input_change()
        
    def input_change(self):
        if dpg.get_value(self.is_linked):
            dpg.set_value(self.height, dpg.get_value(self.width))
        self.update()
                    
    def execute(self, data: NodePackage) -> NodePackage:
        
        width = dpg.get_value(self.width)
        height = dpg.get_value(self.height)
        keep_aspect_ratio = dpg.get_value(self.keep_aspect_ratio)
        
        if width + height == 0:
            return data
        else:
            if width == 0:
                width = height
            elif height == 0:
                height = width
        
        if keep_aspect_ratio:
            if width > height:
                height = int(data.image.shape[0] * width / data.image.shape[1])
            else:
                width = int(data.image.shape[1] * height / data.image.shape[0])
        
        data.image = cv2.resize(data.image, (width, height))
        
        return data
       