import random
import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class ConnectedComponents(Node):
        
    def __init__(self) -> None:
        super().__init__("Connected Components", "Both", "Filter/Operation", 120, input_lable="Mask", output_lable="Mask/Color")
        self.color_components = dpg.generate_uuid()
        self.num_components = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {
            "color_components": dpg.get_value(self.color_components)
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.color_components, data["color_components"])
        
    def compose(self):
        dpg.add_text("Count: 0", tag=self.num_components)
        dpg.add_checkbox(label="Colored", callback=self.update, tag=self.color_components)
        
    def execute(self, data: NodePackage) -> NodePackage:
        
        # Check if the image is binary or not
        if len(data.image.shape) < 2:
            self.on_error("The image is not binary")
            return data
        
        num_labels, labels = cv2.connectedComponents(data.image)
        
        dpg.set_value(self.num_components, f"Count: {num_labels}")
        
        output_image = np.zeros((data.image.shape[0], data.image.shape[1], 3), dtype=np.uint8)

        if dpg.get_value(self.color_components):
            for label in range(1, num_labels):  # Start from 1 to skip the background
                # Generate a random color (R, G, B)
                random_color = [random.randint(0, 255) for _ in range(3)]
                
                # Apply the random color to all pixels belonging to the current label
                output_image[labels == label] = random_color

            data.image = output_image
        return data