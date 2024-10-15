import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class PlotMask(Node):
    def __init__(self):
        super().__init__("Plot Mask", "BothDualIn", "Filter/Mask", 100, output_lable="Image", input_lable="Image", input_lable_2="Mask")
        self.plotting_type = dpg.generate_uuid()
        self.thickness = dpg.generate_uuid()
        self.color = dpg.generate_uuid()
        
    def compose(self):
        dpg.add_text("Plotting Type")
        dpg.add_radio_button(["None", "Contour", "Rectangle", "Circle"], tag=self.plotting_type, callback=self.update)
        dpg.add_text("Thickness")
        dpg.add_slider_float(min_value=1, max_value=10, tag=self.thickness, width=100, callback=self.update)
        dpg.add_text("Color")
        dpg.add_color_picker(tag=self.color, no_alpha=True, no_label=True, no_side_preview=True, no_small_preview=True, width=100, callback=self.update)
        
    def on_save(self) -> dict:
        return {
            "plotting_type": dpg.get_value(self.plotting_type),
            "thickness": dpg.get_value(self.thickness),
            "color": dpg.get_value(self.color)
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.plotting_type, data["plotting_type"])
        dpg.set_value(self.thickness, data["thickness"])
        dpg.set_value(self.color, data["color"])
        
    def execute(self, data: NodePackage, data2: NodePackage) -> NodePackage:
        
        image = data.image
        mask = data2.image
        
        plotting_type = dpg.get_value(self.plotting_type)
        thickness = int(dpg.get_value(self.thickness))
        color = tuple(map(int, dpg.get_value(self.color)[:3]))  # Convert color to tuple of integers (B, G, R)
        # Convert the color from RGB to BGR
        color = (color[2], color[1], color[0])
        
        if plotting_type == "None":
            return data
        
        if plotting_type == "Contour":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(image, contours, -1, color, thickness)
            
        if plotting_type == "Rectangle":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)
                
        if plotting_type == "Circle":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(image, center, radius, color, thickness)
                
        data.image = image
        return data   