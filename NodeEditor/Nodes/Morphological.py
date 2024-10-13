import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Morphological(Node):
    
    def __init__(self) -> None:
        super().__init__("Morphological", "Both", "Filter/Mask", 150, input_lable="Image", output_lable="Mask", )
        self.kernel_size = dpg.generate_uuid()
        self.iterations = dpg.generate_uuid()
        self.operation = dpg.generate_uuid()
        self.kernel = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {
            "kernel_size": dpg.get_value(self.kernel_size),
            "iterations": dpg.get_value(self.iterations),
            "operation": dpg.get_value(self.operation),
            "kernel": dpg.get_value(self.kernel)
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.kernel_size, data["kernel_size"])
        dpg.set_value(self.iterations, data["iterations"])
        dpg.set_value(self.operation, data["operation"])
        dpg.set_value(self.kernel, data["kernel"])
        
    def compose(self):
        dpg.add_input_int(label="Kernel Size", default_value=3, min_value=1, tag=self.kernel_size, width=100, callback=self.update)
        dpg.add_input_int(label="Iterations", default_value=1, min_value=1, tag=self.iterations, width=100, callback=self.update)
        dpg.add_combo(label="Operation", items=["Erosion", "Dilation", "Opening", "Closing"], default_value="Erosion", tag=self.operation, width=100, callback=self.update)
        dpg.add_combo(label="Kernel", items=["Rect", "Cross", "Ellipse"], default_value="Rect", tag=self.kernel, width=100, callback=self.update)
        
    def execute(self, data: NodePackage):
        
        kernel_size = dpg.get_value(self.kernel_size)
        iterations = dpg.get_value(self.iterations)
        operation = dpg.get_value(self.operation)
        kernel = dpg.get_value(self.kernel)
        
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        if kernel == "Rect":
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        elif kernel == "Cross":
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (kernel_size, kernel_size))
        elif kernel == "Ellipse":
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        if operation == "Erosion":
            data.image = cv2.erode(data.image, kernel, iterations=iterations)
        elif operation == "Dilation":
            data.image = cv2.dilate(data.image, kernel, iterations=iterations)
        elif operation == "Opening":
            data.image = cv2.morphologyEx(data.image, cv2.MORPH_OPEN, kernel, iterations=iterations)
        elif operation == "Closing":
            data.image = cv2.morphologyEx(data.image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
            
        return data