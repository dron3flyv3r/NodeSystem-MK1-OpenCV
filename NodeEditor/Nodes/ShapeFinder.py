import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class ShapeFinder(Node):
    
    def __init__(self):
        super().__init__("Shape Finder", "DualInDualOut", "Filter/Mask", 150, input_lable="Image", input_lable_2="Outlines", output_lable="Image", output_lable_2="Mask")
        
        self.shapes = ["Rectangle", "Circle", "Ellipse", "Line", "Polygon"]
        self.shape_id = dpg.generate_uuid()
        self.shape = self.shapes[0]
        self.threshold = 0.1
        self.threshold_id = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {"shape": self.shape, "threshold": self.threshold}
    
    def on_load(self, data: dict):
        self.shape = data["shape"]
        self.threshold = data["threshold"]
        dpg.set_value(self.shape_id, self.shape)
        dpg.set_value(self.threshold_id, self.threshold)
        
    def compose(self):
        dpg.add_combo(label="Shape", items=self.shapes, width=100, tag=self.shape_id, callback=self.update, default_value=self.shape)
        dpg.add_slider_float(label="Threshold", default_value=0.1, min_value=0.0, max_value=1.0, width=100, tag=self.threshold_id, callback=self.update)
        
    def execute(self, data: NodePackage, data2: NodePackage):
        mask = cv2.cvtColor(data2.image, cv2.COLOR_BGR2GRAY) if len(data2.image.shape) == 3 else data2.image
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
        
        self.shape = dpg.get_value(self.shape_id)
        
        # Ensure self.shape is a string
        if isinstance(self.shape, int):
            self.shape = self.shapes[self.shape]
        
        # Prepare reference contour for matching
        ref_shape = None
        if self.shape == "Rectangle":
            ref_shape = np.array([[0,0], [1,0], [1,1], [0,1]]).reshape((-1,1,2))
        elif self.shape == "Circle":
            ref_shape = cv2.ellipse2Poly((0,0), (1,1), 0, 0, 360, 10)
        elif self.shape == "Ellipse":
            ref_shape = cv2.ellipse2Poly((0,0), (1,2), 0, 0, 360, 10)
        elif self.shape == "Line":
            ref_shape = np.array([[0,0], [1,0]]).reshape((-1,1,2))
        elif self.shape == "Polygon":
            angles = np.linspace(0, 2*np.pi, 6)[:-1]
            ref_shape = np.array([[np.cos(a), np.sin(a)] for a in angles]).reshape((-1,1,2))
            
        new_mask = np.zeros_like(mask, dtype=np.uint8)
        if len(new_mask.shape) == 2:
            new_mask = cv2.cvtColor(new_mask, cv2.COLOR_GRAY2BGR)
        
        if ref_shape is not None:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                match_score = cv2.matchShapes(np.array(ref_shape, dtype=np.float32), np.array(contour, dtype=np.float32), cv2.CONTOURS_MATCH_I1, 0.0)
                if match_score < dpg.get_value(self.threshold_id):
                    cv2.drawContours(new_mask, [contour], -1, (255, 255, 255), -1)
                    
        data2.image = new_mask
        
        return data, data2