import dearpygui.dearpygui as dpg
import torch

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Compile(Node):
    
    def __init__(self):
        super().__init__("Compile", "Input", "Output", input_lable="Model")
        self.output = dpg.generate_uuid()
        
    def compose(self):
        dpg.add_text("Output: ", tag=self.output)
        
    def execute(self, data: NodePackage) -> NodePackage:
        
        # Run the input data through the model
        output = data.bases_model(data.input)
        
        
        dpg.set_value(self.output, str(output))
        
        return data