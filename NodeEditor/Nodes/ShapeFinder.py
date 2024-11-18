import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class ShapeFinder(Node):
    
    def __init__(self):
        super().__init__("Shape Finder", "DualInDualOut", "Filter/Mask", 150, input_lable="Image", input_lable_2="Outlines", output_lable="Image", output_lable_2="Mask")
        
        self.shapes = ["Rectangle", "Circle", "Ellipse", "Line", "Polygon"]
        self.shape_id = dpg.generate_uuid()
        self.shape = self.shapes[0]
        
    def on_save(self) -> dict:
        return {"shape": self.shape}
    
    def on_load(self, data: dict):
        self.shape = data["shape"]
        dpg.set_value(self.shape_id, self.shapes.index(self.shape))
        
    def compose(self):
        dpg.add_combo(label="Shape", items=self.shapes, width=100, tag=self.shape_id, callback=self.update, default_value=self.shape)
        
    def execute(self, data: NodePackage, data2: NodePackage):
        mask = cv2.cvtColor(data2.image, cv2.COLOR_BGR2GRAY) if len(data2.image.shape) == 3 else data2.image
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
        
        self.shape = dpg.get_value(self.shape_id)
        
        if self.shape == "Rectangle":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(data.image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
        elif self.shape == "Circle":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(data.image, center, radius, (0, 255, 0), 2)
                
        elif self.shape == "Ellipse":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                ellipse = cv2.fitEllipse(contour)
                cv2.ellipse(data.image, ellipse, (0, 255, 0), 2)
                
        elif self.shape == "Line":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                rows, cols = data.image.shape[:2]
                [vx, vy, x, y] = cv2.fitLine(contour, cv2.DIST_L2, 0, 0.01, 0.01)
                lefty = int((-x*vy/vx) + y)
                righty = int(((cols-x)*vy/vx)+y)
                cv2.line(data.image, (cols-1, righty), (0, lefty), (0, 255, 0), 2)
                
        elif self.shape == "Polygon":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                cv2.drawContours(data.image, [approx], 0, (0, 255, 0), 2)
                
        return data, data2