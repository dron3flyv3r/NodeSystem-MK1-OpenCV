import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class CropFromRef(Node):
        
    def __init__(self) -> None:
        super().__init__("Crop Ref", "BothDualIn", "Filter/Manipulation", 60, input_lable="Image", input_lable_2="Ref", output_lable="Image")
        
    def execute(self, data: NodePackage, data2: NodePackage) -> NodePackage:
        data.image = cv2.resize(data.image, (data2.image.shape[1], data2.image.shape[0]))
        return data