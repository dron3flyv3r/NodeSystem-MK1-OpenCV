import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class MinimumDensity(Node):
    
    def __init__(self) -> None:
        super().__init__("Minimum Density", "Both", "Filter/Operation", 100, input_lable="Mask", output_lable="Mask")
        self.threshold_id = dpg.generate_uuid()
        self.avg_density = 0
        self.avg_density_id = dpg.generate_uuid()
        
    def compose(self):
        dpg.add_text(f"Average Density: {self.avg_density}", tag=self.avg_density_id)
        dpg.add_input_int(label="Threshold", default_value=0, tag=self.threshold_id, width=100, callback=self.update)
        
    def execute(self, data: NodePackage) -> NodePackage:
        # Make the threshold based on the pixel density for each component of the mask
        if len(data.image.shape) == 3:
            self.on_error("The mask must be a single channel image/gray scale")
            return data
        
        # Get the mask
        mask = data.image

        # Get clusters of pixels with stats
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

        # Get the area (size) of each cluster, excluding the background
        cluster_sizes = stats[1:, cv2.CC_STAT_AREA]

        # Get the average cluster size
        avg_cluster_size = np.mean(cluster_sizes)
        self.avg_density = avg_cluster_size
        dpg.set_value(self.avg_density_id, f"Average Cluster Size: {avg_cluster_size}")

        # Threshold value
        threshold = dpg.get_value(self.threshold_id)

        # Create a new mask
        new_mask = np.zeros_like(mask)

        # Loop through clusters and keep clusters above threshold
        for label in range(1, num_labels):
            cluster_size = stats[label, cv2.CC_STAT_AREA]
            if cluster_size >= threshold:
                new_mask[labels == label] = 255

        # Update the mask
        data.image = new_mask

        return data