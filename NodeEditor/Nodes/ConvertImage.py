import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class ConvertImage(Node):
        
    def __init__(self) -> None:
        super().__init__("Convert Image", "Both", "Filter/Operation", 60, output_lable="Image")
        self.color_space_to = dpg.generate_uuid()
        self.color_space_from = dpg.generate_uuid()
        self.color_space_ids = [
            "RGB",
            "BGR",
            "GRAY",
            "RGBA",
            "BGRA",
        ]
        
    def on_save(self) -> dict:
        return {
            "color_space_to": dpg.get_value(self.color_space_to),
            "color_space_from": dpg.get_value(self.color_space_from),
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.color_space_to, data["color_space_to"])
        dpg.set_value(self.color_space_from, data["color_space_from"])
        
    def compose(self):
        dpg.add_combo(label="From", items=self.color_space_ids + ["AUTO"], default_value="AUTO", tag=self.color_space_from, callback=self.update, width=60)
        dpg.add_combo(label="To", items=self.color_space_ids, default_value="BGRA", tag=self.color_space_to, callback=self.update, width=60)
        
    def execute(self, data: NodePackage) -> NodePackage:
        color_space_from = dpg.get_value(self.color_space_from)
        color_space_to = dpg.get_value(self.color_space_to)
        
        if color_space_from == "AUTO":
            if len(data.image.shape) == 3:
                if data.image.shape[2] == 3:
                    color_space_from = "BGR"
                elif data.image.shape[2] == 4:
                    color_space_from = "BGRA"
            elif len(data.image.shape) == 2:
                color_space_from = "GRAY"
            else:
                self.on_error("The image is not in a supported color space")
                return data
        
        if color_space_from == color_space_to:
            self.on_error("The color spaces are the same")
            return data
        
        if color_space_from == "RGB":
            if color_space_to == "BGR":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_RGB2BGR)
            elif color_space_to == "GRAY":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_RGB2GRAY)
            elif color_space_to == "RGBA":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_RGB2RGBA)
            elif color_space_to == "BGRA":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_RGB2BGRA)

        elif color_space_from == "BGR":
            if color_space_to == "RGB":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_BGR2RGB)
            elif color_space_to == "GRAY":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_BGR2GRAY)
            elif color_space_to == "RGBA":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_BGR2RGBA)
            elif color_space_to == "BGRA":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_BGR2BGRA)
    
        elif color_space_from == "GRAY":
            if color_space_to == "RGB":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_GRAY2RGB)
            elif color_space_to == "BGR":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_GRAY2BGR)
            elif color_space_to == "RGBA":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_GRAY2RGBA)
            elif color_space_to == "BGRA":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_GRAY2BGRA)
                
        elif color_space_from == "RGBA":
            if color_space_to == "RGB":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_RGBA2RGB)
            elif color_space_to == "BGR":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_RGBA2BGR)
            elif color_space_to == "GRAY":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_RGBA2GRAY)
            elif color_space_to == "BGRA":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_RGBA2BGRA)

        elif color_space_from == "BGRA":
            if color_space_to == "RGB":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_BGRA2RGB)
            elif color_space_to == "BGR":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_BGRA2BGR)
            elif color_space_to == "GRAY":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_BGRA2GRAY)
            elif color_space_to == "RGBA":
                data.image = cv2.cvtColor(data.image, cv2.COLOR_BGRA2RGBA)
        
        return data