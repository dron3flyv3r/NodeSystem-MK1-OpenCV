import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class MinimumDensity(Node):
    
    def __init__(self) -> None:
        super().__init__("Minimum Density", "Both", "Filter/Operation", 100, input_lable="Mask", output_lable="Mask")
        self.threshold_id = dpg.generate_uuid()
        
    def compose(self):
        dpg.add_input_int(label="Threshold", default_value=0, tag=self.threshold_id, width=100)
        
    def execute(self, data: NodePackage) -> NodePackage:
        # Make the threshold based on the pixel density for each component of the mask
        if len(data.image.shape) == 3:
            self.on_error("The mask must be a single channel image/gray scale")
            return data
        
        # Get the threshold value
        threshold = dpg.get_value(self.threshold_id)
        
        # Get the mask
        mask = data.image
        
        # Get clusters of pixels
        num_labels, labels = cv2.connectedComponents(mask)
        
        # Create a new mask
        new_mask = mask.copy()
        
        # Loop through the clusters
        for label in range(1, num_labels):
            # Get the cluster
            cluster = (labels == label).astype('uint8')
            
            # Get the density of the cluster
            density = cv2.countNonZero(cluster) / cluster.size
            
            # If the density is less than the threshold, remove the cluster
            if density < threshold:
                new_mask[cluster] = 0
                
        # Update the mask
        data.image = new_mask
        
        return data