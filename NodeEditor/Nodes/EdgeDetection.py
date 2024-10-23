import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class EdgeDetection(Node):
        
    def __init__(self) -> None:
        super().__init__("Edge Detection", catagory="Filter/Manipulation", max_width=150, input_lable="Image", output_lable="Image")
        self.method = dpg.generate_uuid()
        
        # Method options
        # Canny
        self.low_threshold = dpg.generate_uuid()
        self.high_threshold = dpg.generate_uuid()
        
        # Sobel
        self.x_order = dpg.generate_uuid()
        self.y_order = dpg.generate_uuid()
        
        # Laplacian
        self.ddepth = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {
            "method": dpg.get_value(self.method),
            "low_threshold": dpg.get_value(self.low_threshold),
            "high_threshold": dpg.get_value(self.high_threshold),
            "x_order": dpg.get_value(self.x_order),
            "y_order": dpg.get_value(self.y_order),
            "ddepth": dpg.get_value(self.ddepth)
        }
    
    def on_load(self, data: dict):
        dpg.set_value(self.method, data["method"])
        dpg.set_value(self.low_threshold, data["low_threshold"])
        dpg.set_value(self.high_threshold, data["high_threshold"])
        dpg.set_value(self.x_order, data["x_order"])
        dpg.set_value(self.y_order, data["y_order"])
        dpg.set_value(self.ddepth, data["ddepth"])
        
        self.selection_update()
        
    def selection_update(self):
        if dpg.get_value(self.method) == "Canny":
            dpg.configure_item(self.low_threshold, show=True)
            dpg.configure_item(self.high_threshold, show=True)
            dpg.configure_item(self.x_order, show=False)
            dpg.configure_item(self.y_order, show=False)
            dpg.configure_item(self.ddepth, show=False)
        elif dpg.get_value(self.method) == "Sobel":
            dpg.configure_item(self.low_threshold, show=False)
            dpg.configure_item(self.high_threshold, show=False)
            dpg.configure_item(self.x_order, show=True)
            dpg.configure_item(self.y_order, show=True)
            dpg.configure_item(self.ddepth, show=False)
        elif dpg.get_value(self.method) == "Laplacian":
            dpg.configure_item(self.low_threshold, show=False)
            dpg.configure_item(self.high_threshold, show=False)
            dpg.configure_item(self.x_order, show=False)
            dpg.configure_item(self.y_order, show=False)
            dpg.configure_item(self.ddepth, show=True)
        self.update()
        
    def compose(self):
        dpg.add_combo(label="Method", items=["Canny", "Sobel", "Laplacian"], default_value="Canny", tag=self.method, callback=self.selection_update, width=100)
        
        # Canny
        dpg.add_input_int(label="Low Threshold", default_value=100, tag=self.low_threshold, callback=self.update, width=100, step=0)
        dpg.add_input_int(label="High Threshold", default_value=200, tag=self.high_threshold, callback=self.update, width=100, step=0)
        
        # Sobel
        dpg.add_input_int(label="X Order", default_value=1, tag=self.x_order, callback=self.update, show=False, width=100, step=0)
        dpg.add_input_int(label="Y Order", default_value=1, tag=self.y_order, callback=self.update, show=False, width=100, step=0)
        
        # Laplacian
        dpg.add_input_int(label="Ddepth", default_value=-1, tag=self.ddepth, callback=self.update, show=False, width=100, step=0)
        
    def execute(self, data: NodePackage) -> NodePackage:
        if dpg.get_value(self.method) == "Canny":
            data.image = cv2.Canny(data.image, dpg.get_value(self.low_threshold), dpg.get_value(self.high_threshold))
        elif dpg.get_value(self.method) == "Sobel":
            data.image = cv2.Sobel(data.image, -1, dpg.get_value(self.x_order), dpg.get_value(self.y_order))
        elif dpg.get_value(self.method) == "Laplacian":
            data.image = cv2.Laplacian(data.image, -1, dpg.get_value(self.ddepth))
        return data