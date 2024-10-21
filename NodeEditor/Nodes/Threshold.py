import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Threshold(Node):
    
    def __init__(self) -> None:
        super().__init__("Threshold", "Both", "Filter/Mask", 150, input_lable="Image", output_lable="Mask", )
        self.threshold_min_id = dpg.generate_uuid()
        self.threshold_max_id = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {"threshold_min": dpg.get_value(self.threshold_min_id), "threshold_max": dpg.get_value(self.threshold_max_id)}
    
    def on_load(self, data: dict):
        dpg.set_value(self.threshold_min_id, data["threshold_min"])
        dpg.set_value(self.threshold_max_id, data["threshold_max"])
        
    def compose(self):
        dpg.add_slider_int(label="Min", default_value=0, min_value=0, max_value=256, width=100, tag=self.threshold_min_id, callback=self.update)
        dpg.add_slider_int(label="Max", default_value=256, min_value=0, max_value=256, width=100, tag=self.threshold_max_id, callback=self.update)
        
    def execute(self, data: NodePackage, data2: NodePackage | None = None) -> NodePackage | tuple[NodePackage, NodePackage]:
        
        if dpg.get_value(self.threshold_min_id) > dpg.get_value(self.threshold_max_id):
            dpg.set_value(self.threshold_min_id, dpg.get_value(self.threshold_max_id))
        elif dpg.get_value(self.threshold_max_id) < dpg.get_value(self.threshold_min_id):
            dpg.set_value(self.threshold_max_id, dpg.get_value(self.threshold_min_id))

        # Make the binary threshold image mask
        oneChannelMin = cv2.cvtColor(data.image, cv2.COLOR_BGR2GRAY) if len(data.image.shape) == 3 else data.image
        oneChannelMax = cv2.cvtColor(data.image, cv2.COLOR_BGR2GRAY) if len(data.image.shape) == 3 else data.image
        
        _, oneChannelMin = cv2.threshold(oneChannelMin, dpg.get_value(self.threshold_min_id), 255, cv2.THRESH_BINARY)
        _, oneChannelMax = cv2.threshold(oneChannelMax, dpg.get_value(self.threshold_max_id), 255, cv2.THRESH_BINARY_INV)
        
        data.image = cv2.bitwise_and(oneChannelMin, oneChannelMax)
        
        return data