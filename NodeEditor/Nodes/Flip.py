import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Flip(Node):
    
    def __init__(self) -> None:
        super().__init__("Flip", catagory="Filter/Manipulation", input_lable="Image", output_lable="Image")
        self.horizontal = dpg.generate_uuid()
        self.vertical = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {"horizontal": dpg.get_value(self.horizontal), "vertical": dpg.get_value(self.vertical)}
    
    def on_load(self, data: dict):
        dpg.set_value(self.horizontal, data["horizontal"])
        dpg.set_value(self.vertical, data["vertical"])
        
    def compose(self):
        dpg.add_checkbox(label="Horizontal", default_value=False, tag=self.horizontal, callback=self.update)
        dpg.add_checkbox(label="Vertical", default_value=False, tag=self.vertical, callback=self.update)
        
    def execute(self, data: NodePackage) -> NodePackage:
        data.image = cv2.flip(data.image, 1) if dpg.get_value(self.horizontal) else data.image
        data.image = cv2.flip(data.image, 0) if dpg.get_value(self.vertical) else data.image        
        return data