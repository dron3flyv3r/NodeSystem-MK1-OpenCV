import dearpygui.dearpygui as dpg
import torch

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class ViewModel(Node):
    
    def __init__(self):
        super().__init__("View Model", "Input", "Output", input_lable="Model")
        self.output = dpg.generate_uuid()
        self.n_params = dpg.generate_uuid()
        
    def compose(self):
        dpg.add_text("Params: ", tag=self.n_params)
        dpg.add_spacer()
        dpg.add_text("", tag=self.output)
        
    def execute(self, data: NodePackage) -> NodePackage:
            
        model = ""
                
        # Run the input data through the model
        data.bases_model(data.input)
        
        for name, module in data.bases_model.named_children():
            name = name.split("_")[0]
            model += f"{name}: {module}\n"
        
        dpg.set_value(self.n_params, f"Params: {len(list(data.bases_model.parameters()))}")
        dpg.set_value(self.output, model)
        
        return data