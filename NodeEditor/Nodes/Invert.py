import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Invert(Node):
    
    def __init__(self) -> None:
        super().__init__("Invert", "Both", "Filter/Operation", 60, input_lable="Image", output_lable="Image")
        
    def execute(self, data: NodePackage) -> NodePackage:
        data.image = cv2.bitwise_not(data.image)
        return data