import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class CustomCode(Node):
    
    def __init__(self) -> None:
        super().__init__("Custom Code", catagory="Filter/Manipulation", max_width=220, input_lable="Image", output_lable="Image")
        self.code = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {"code": dpg.get_value(self.code)}
    
    def on_load(self, data: dict):
        dpg.set_value(self.code, data["code"])
        
    def compose(self):
        dpg.add_input_text(label="Code", default_value="img = cv2.flip(img, 1)", tag=self.code, width=200, height=200, multiline=True)
        
    def execute(self, data: NodePackage) -> NodePackage:
        
        code = dpg.get_value(self.code)
        
        img = data.image
        local_scope = {"img": img}
        exec(code, globals(), local_scope)
        data.image = local_scope["img"]
        
        return data