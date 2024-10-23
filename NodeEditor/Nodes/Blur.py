import cv2
import dearpygui.dearpygui as dpg

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage

class Blur(Node):
    
    def __init__(self) -> None:
        super().__init__("Blur", catagory="Filter/Manipulation", max_width=120, input_lable="Image", output_lable="Image")
        self.method = dpg.generate_uuid()
        self.options = [
            "Mean",
            "Gaussian",
            "Median",
            "Bilateral"
        ]
        
        # Mean
        self.mean_ksize = dpg.generate_uuid()
        
        # Gaussian
        self.gaussian_ksize = dpg.generate_uuid()
        self.gaussian_sigma = dpg.generate_uuid()
        
        # Median
        self.median_ksize = dpg.generate_uuid()
        
        # Bilateral
        self.bilateral_d = dpg.generate_uuid()
        self.bilateral_sigma_color = dpg.generate_uuid()
        self.bilateral_sigma_space = dpg.generate_uuid()
        
    def on_save(self) -> dict:
        return {
            "method": dpg.get_value(self.method),
            "mean_ksize": dpg.get_value(self.mean_ksize),
            "gaussian_ksize": dpg.get_value(self.gaussian_ksize),
            "gaussian_sigma": dpg.get_value(self.gaussian_sigma),
            "median_ksize": dpg.get_value(self.median_ksize),
            "bilateral_d": dpg.get_value(self.bilateral_d),
            "bilateral_sigma_color": dpg.get_value(self.bilateral_sigma_color),
            "bilateral_sigma_space": dpg.get_value(self.bilateral_sigma_space)
        }
        
    def on_load(self, data: dict):
        dpg.set_value(self.method, data["method"])
        dpg.set_value(self.mean_ksize, data["mean_ksize"])
        dpg.set_value(self.gaussian_ksize, data["gaussian_ksize"])
        dpg.set_value(self.gaussian_sigma, data["gaussian_sigma"])
        dpg.set_value(self.median_ksize, data["median_ksize"])
        dpg.set_value(self.bilateral_d, data["bilateral_d"])
        dpg.set_value(self.bilateral_sigma_color, data["bilateral_sigma_color"])
        dpg.set_value(self.bilateral_sigma_space, data["bilateral_sigma_space"])
        self.selection_update()
        
    def selection_update(self):
        if dpg.get_value(self.method) == "Mean":
            dpg.configure_item(self.mean_ksize, show=True)
            dpg.configure_item(self.gaussian_ksize, show=False)
            dpg.configure_item(self.gaussian_sigma, show=False)
            dpg.configure_item(self.median_ksize, show=False)
            dpg.configure_item(self.bilateral_d, show=False)
            dpg.configure_item(self.bilateral_sigma_color, show=False)
            dpg.configure_item(self.bilateral_sigma_space, show=False)
        elif dpg.get_value(self.method) == "Gaussian":
            dpg.configure_item(self.mean_ksize, show=False)
            dpg.configure_item(self.gaussian_ksize, show=True)
            dpg.configure_item(self.gaussian_sigma, show=True)
            dpg.configure_item(self.median_ksize, show=False)
            dpg.configure_item(self.bilateral_d, show=False)
            dpg.configure_item(self.bilateral_sigma_color, show=False)
            dpg.configure_item(self.bilateral_sigma_space, show=False)
        elif dpg.get_value(self.method) == "Median":
            dpg.configure_item(self.mean_ksize, show=False)
            dpg.configure_item(self.gaussian_ksize, show=False)
            dpg.configure_item(self.gaussian_sigma, show=False)
            dpg.configure_item(self.median_ksize, show=True)
            dpg.configure_item(self.bilateral_d, show=False)
            dpg.configure_item(self.bilateral_sigma_color, show=False)
            dpg.configure_item(self.bilateral_sigma_space, show=False)
        elif dpg.get_value(self.method) == "Bilateral":
            dpg.configure_item(self.mean_ksize, show=False)
            dpg.configure_item(self.gaussian_ksize, show=False)
            dpg.configure_item(self.gaussian_sigma, show=False)
            dpg.configure_item(self.median_ksize, show=False)
            dpg.configure_item(self.bilateral_d, show=True)
            dpg.configure_item(self.bilateral_sigma_color, show=True)
            dpg.configure_item(self.bilateral_sigma_space, show=True)
        self.update()
        
    def compose(self):
        dpg.add_combo(label="Method", items=self.options, default_value="Mean", tag=self.method, callback=self.selection_update, width=100)
        
        # Mean
        dpg.add_input_int(label="Ksize", default_value=5, tag=self.mean_ksize, callback=self.update, show=True, width=100, step=0)
        
        # Gaussian
        dpg.add_input_int(label="Ksize", default_value=5, tag=self.gaussian_ksize, callback=self.update, show=False, width=100, step=0)
        dpg.add_input_int(label="Sigma", default_value=0, tag=self.gaussian_sigma, callback=self.update, show=False, width=100, step=0)
        
        # Median
        dpg.add_input_int(label="Ksize", default_value=5, tag=self.median_ksize, callback=self.update, show=False, width=100, step=0)
        
        # Bilateral
        dpg.add_input_int(label="D", default_value=9, tag=self.bilateral_d, callback=self.update, show=False, width=100, step=0)
        dpg.add_input_int(label="Sigma Color", default_value=75, tag=self.bilateral_sigma_color, callback=self.update, show=False, width=100, step=0)
        dpg.add_input_int(label="Sigma Space", default_value=75, tag=self.bilateral_sigma_space, callback=self.update, show=False, width=100, step=0)
        
    def execute(self, data: NodePackage) -> NodePackage:
        
        # Check if any of the kernel sizes are even and if so add 1 to them
        if dpg.get_value(self.mean_ksize) % 2 == 0:
            dpg.set_value(self.mean_ksize, dpg.get_value(self.mean_ksize) + 1)
        elif dpg.get_value(self.gaussian_ksize) % 2 == 0:
            dpg.set_value(self.gaussian_ksize, dpg.get_value(self.gaussian_ksize) + 1)
        elif dpg.get_value(self.median_ksize) % 2 == 0:
            dpg.set_value(self.median_ksize, dpg.get_value(self.median_ksize) + 1)
        elif dpg.get_value(self.bilateral_d) % 2 == 0:
            dpg.set_value(self.bilateral_d, dpg.get_value(self.bilateral_d) + 1)
        
        if dpg.get_value(self.method) == "Mean":
            data.image = cv2.blur(data.image, (dpg.get_value(self.mean_ksize), dpg.get_value(self.mean_ksize)))            
        elif dpg.get_value(self.method) == "Gaussian":
            data.image = cv2.GaussianBlur(data.image, (dpg.get_value(self.gaussian_ksize), dpg.get_value(self.gaussian_ksize)), dpg.get_value(self.gaussian_sigma))            
        elif dpg.get_value(self.method) == "Median":
            data.image = cv2.medianBlur(data.image, dpg.get_value(self.median_ksize))            
        elif dpg.get_value(self.method) == "Bilateral":
            data.image = cv2.bilateralFilter(data.image, dpg.get_value(self.bilateral_d), dpg.get_value(self.bilateral_sigma_color), dpg.get_value(self.bilateral_sigma_space))
            
        return data