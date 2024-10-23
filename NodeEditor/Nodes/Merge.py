from typing import Literal
import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Merge(Node):
    
    def __init__(self) -> None:
        super().__init__("Merge","BothDualIn", "Filter/Operation", 60, input_lable="Image", input_lable_2="Image", output_lable="Image")
        
    def execute(self, data: NodePackage, data2: NodePackage) -> NodePackage:
        image_top = data2.image
        image_buttom = data.image
        
        # Check if both images have an alpha channel
        if image_top.shape[2] != 4 or image_buttom.shape[2] != 4:
            self.on_error("Both images must have an alpha channel")
            return data
        
        if image_top.shape != image_buttom.shape:
            self.on_error("The two images must have the same shape got {} and {}".format(image_top.shape, image_buttom.shape))
            return data
        
        for i in range(3):
            image_top[:,:,i] = np.where(image_buttom[:,:,3] == 0, image_top[:,:,i], image_buttom[:,:,i])
                                
        data.image = image_top        
        return data