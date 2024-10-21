import time
import torch
import copy

class NodePackage:
    
    bases_model = torch.nn.Sequential()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def add_module(self, name: str, module: torch.nn.Module, node_id: str | int = 0):
        if node_id == 0:
            raise ValueError("Node ID not set")
        
        module_name = f"{name}_{node_id}"
        
        if module_name in [name for name, _ in self.bases_model.named_children()]:
            self.bases_model._modules[module_name] = module
        else:
            self.bases_model.add_module(module_name, module)
        
    def remove_module(self, name: str, node_id: str | int = 0):
        if node_id == 0:
            raise ValueError("Node ID not set")
        
        module_name = f"{name}_{node_id}"
        
        if module_name in [name for name, _ in self.bases_model.named_children()]:
            self.bases_model._modules.pop(module_name)
        
    output: torch.Tensor = torch.tensor([])
    output_shape: torch.Size = torch.Size([])
    input: torch.Tensor = torch.tensor([])
    input_shape: torch.Size = torch.Size([])
    
    pre_n_output: int = 0
    
    def copy(self) -> 'NodePackage':
        new_package = NodePackage()
        for key, value in self.__dict__.items():
            setattr(new_package, key, copy.deepcopy(value))
        return new_package