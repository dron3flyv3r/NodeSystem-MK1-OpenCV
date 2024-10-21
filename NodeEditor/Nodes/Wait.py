import time
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Wait(Node):
    
    def __init__(self) -> None:
        super().__init__("Wait", "Both", "System", input_lable="Any", output_lable="Any")
        self.time = dpg.generate_uuid()
        
    def compose(self):
        dpg.add_input_float(label="Time", default_value=1, tag=self.time, format="%.1f", step=0.1, width=100)
        
    def on_save(self) -> dict:
        return {"time": dpg.get_value(self.time)}
    
    def on_load(self, data: dict):
        dpg.set_value(self.time, data["time"])
        
    def execute(self, data: NodePackage) -> NodePackage:
        
        time_to_wait = dpg.get_value(self.time)
        
        time.sleep(time_to_wait)
        
        return data