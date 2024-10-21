import dearpygui.dearpygui as dpg
import torch

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Linear(Node):
    
    def __init__(self):
        super().__init__("Linear", "Both", "Linear", input_lable="Data", output_lable="Data")
        self.n_outputs = dpg.generate_uuid()
        self.n_inputs = dpg.generate_uuid()
        
        self.activation = dpg.generate_uuid()
        self.activation_types = {
            "None": "None",
            "ReLU": "torch.nn.ReLU()",
            "Sigmoid": "torch.nn.Sigmoid()",
            "Tanh": "torch.nn.Tanh()"
        }
        
        
    def compose(self):
        dpg.add_input_int(label="Number of Inputs", default_value=1, tag=self.n_inputs, width=100, callback=self.update)
        dpg.add_input_int(label="Number of Outputs", default_value=1, tag=self.n_outputs, width=100, callback=self.update)
        dpg.add_combo(label="Activation", items=list(self.activation_types.keys()), default_value="None", tag=self.activation, width=100, callback=self.update)
        
    def on_save(self) -> dict:
        return {
            "n_inputs": dpg.get_value(self.n_inputs),
            "n_outputs": dpg.get_value(self.n_outputs),
            "activation": dpg.get_value(self.activation)
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.n_inputs, data["n_inputs"])
        dpg.set_value(self.n_outputs, data["n_outputs"])
        dpg.set_value(self.activation, data["activation"])
        
    def execute(self, data: NodePackage) -> NodePackage:
        
        
        if data.pre_n_output > 0 and data.pre_n_output != dpg.get_value(self.n_inputs):
            self.on_error()
        
        linear = torch.nn.Linear(dpg.get_value(self.n_inputs), dpg.get_value(self.n_outputs), device=data.device)
            
        data.add_module("Linear", linear, self._node_id)
        if dpg.get_value(self.activation) != "None":
            data.add_module("Activation", eval(self.activation_types[dpg.get_value(self.activation)]), self._node_id)
        else:
            data.remove_module("Activation", self._node_id)
            
        data.pre_n_output = dpg.get_value(self.n_outputs)
        
        return data