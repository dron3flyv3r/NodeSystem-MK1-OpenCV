import dearpygui.dearpygui as dpg
import torch

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class InputsBase(Node):
    
    def __init__(self) -> None:
        super().__init__("Inputs Base", "Output", "Inputs", max_width=150)
        self.n_inputs = dpg.generate_uuid()
        self.n_dims = dpg.generate_uuid()
        self.type = dpg.generate_uuid()
        self.shape = dpg.generate_uuid()
        self.data_types = {
            "float32": "torch.float32",
            "int32": "torch.int32",
            "int8": "torch.int8",
            "uint8": "torch.uint8",
            "bool": "torch.bool"
        }
        
        self.input = dpg.generate_uuid()
        self.input_types = {
            "Zero": "zeros",
            "One": "ones",
            "Random": "randn"
        }
        
    def compose(self):
        dpg.add_text("Shape: ", tag=self.shape)
        dpg.add_input_int(label="Number of Inputs", default_value=1, tag=self.n_inputs, width=100, callback=self.update)
        dpg.add_input_int(label="Number of Dimensions", default_value=1, tag=self.n_dims, width=100, callback=self.update)
        dpg.add_combo(label="Data Type", items=list(self.data_types.keys()), default_value="float32", tag=self.type, width=100, callback=self.update)
        dpg.add_combo(label="Input Type", items=list(self.input_types.keys()), default_value="Zero", tag=self.input, width=100, callback=self.update)
        
    def on_save(self) -> dict:
        return {
            "n_inputs": dpg.get_value(self.n_inputs),
            "n_dims": dpg.get_value(self.n_dims),
            "type": dpg.get_value(self.type)
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.n_inputs, data["n_inputs"])
        dpg.set_value(self.n_dims, data["n_dims"])
        dpg.set_value(self.type, data["type"])
        
    def execute(self, data: NodePackage) -> NodePackage:
        data.input = eval(f"torch.{self.input_types[dpg.get_value(self.input)]}({dpg.get_value(self.n_dims)}, {dpg.get_value(self.n_inputs)}, dtype={self.data_types[dpg.get_value(self.type)]})")
        data.input = data.input.to(data.device)
        data.input_shape = data.input.shape
        
        data.bases_model = torch.nn.Sequential()
        
        
        dpg.set_value(self.shape, str(data.input_shape))
        
        return data