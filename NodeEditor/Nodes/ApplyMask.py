import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class ApplyMask(Node):
        
    def __init__(self) -> None:
        super().__init__("Apply Mask", "BothDualIn", "Filter/Mask", 60, input_lable="Image", input_lable_2="Mask", output_lable="Image")
        
    def execute(self, data: NodePackage, data2: NodePackage) -> NodePackage:
        image = data.image
        mask = data2.image
        
        # Validate the image type and the mask type
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
        elif len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            
        if len(mask.shape) == 3:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        elif len(mask.shape) == 4:
            mask = cv2.cvtColor(mask, cv2.COLOR_BGRA2GRAY)
        
        image = cv2.bitwise_and(image, image, mask=mask)
        
        data.image = image
        
        return data