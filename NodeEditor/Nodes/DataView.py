import dearpygui.dearpygui as dpg
import torch

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class DataView(Node):
    
    def __init__(self) -> None:
        super().__init__("Data View", "Input", "Output", input_lable="Data")
        self.shape = dpg.generate_uuid()
        self.input = dpg.generate_uuid()
        self.output = dpg.generate_uuid()
        
    def compose(self):
        dpg.add_text("Shape: ", tag=self.shape)
        dpg.add_text("Input: ", tag=self.input)
        dpg.add_text("Output: ", tag=self.output)
        
    def execute(self, data: NodePackage) -> NodePackage:
        dpg.set_value(self.shape, str(data.input_shape))
        dpg.set_value(self.input, str(data.input))
        dpg.set_value(self.output, str(data.output))
        
        return data
        