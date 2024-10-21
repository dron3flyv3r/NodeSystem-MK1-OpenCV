import cv2
import dearpygui.dearpygui as dpg
import numpy as np
import torch
from transformers import pipeline
from PIL import Image

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class DepthAI(Node):
    
    def __init__(self) -> None:
        super().__init__("Depth AI", "BothDualOut", "AI", 150, input_lable="Image", output_lable="Image", output_lable_2="Mask")
        self.model_size = dpg.generate_uuid()
        self.size_selected = "Small"
        
    def on_size_selected(self, sender, app_data):
        if app_data == self.size_selected:
            return
        self.size_selected = app_data
        self.load_model()
        
    def on_init(self):
        self.load_model()
        
    def on_save(self) -> dict:
        return {"size": self.size_selected}
    
    def on_load(self, data: dict):
        self.size_selected = data["size"]
        self.load_model()
        
    def compose(self):
        dpg.add_combo(items=["Small", "Base", "Large"], label="Model Size", default_value=self.size_selected, width=100, callback=self.on_size_selected)
        
    def load_model(self):
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"

        self.pipe = pipeline(task="depth-estimation", model=f"depth-anything/Depth-Anything-V2-{self.size_selected}-hf", device=device)
    
        
    def execute(self, data: NodePackage) -> tuple[NodePackage, NodePackage]:
        data2 = data.copy()
        
        image = Image.fromarray(data.image)
        result = self.pipe(image)
        depth: Image.Image = result['depth'] # type: ignore
        cv = np.array(depth)
        cv = cv2.cvtColor(cv, cv2.COLOR_RGB2BGR)
        
        data2.image = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
        
        return data, data2