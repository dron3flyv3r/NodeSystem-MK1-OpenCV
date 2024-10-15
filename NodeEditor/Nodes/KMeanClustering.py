import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from NodeEditor.Core.Node import Node
from NodeEditor.Core.NodePackage import NodePackage


class KMeanClustering(Node):
    def __init__(self):
        super().__init__(
            "KMean Clustering",
            "Both",
            "Filter",
            100,
            output_lable="Image",
            input_lable="Image",
        )
        self.k = dpg.generate_uuid()
        self.iterations = dpg.generate_uuid()
        self.attempts = dpg.generate_uuid()
        self.color_space = dpg.generate_uuid()

    def compose(self):
        dpg.add_text("K")
        dpg.add_slider_int(
            min_value=1, max_value=10, default_value=1, tag=self.k, width=100, callback=self.update
        )

        dpg.add_text("Attempts")
        dpg.add_slider_int(
            min_value=1,
            max_value=10,
            tag=self.attempts,
            width=100,
            callback=self.update,
        )
        dpg.add_text("Color Space")
        dpg.add_radio_button(
            ["RGB", "HSV", "LAB"], tag=self.color_space, callback=self.update
        )

    def on_save(self) -> dict:
        return {
            "k": dpg.get_value(self.k),
            "iterations": dpg.get_value(self.iterations),
            "attempts": dpg.get_value(self.attempts),
            "color_space": dpg.get_value(self.color_space),
        }

    def on_load(self, data: dict):
        dpg.set_value(self.k, data["k"])
        dpg.set_value(self.iterations, data["iterations"])
        dpg.set_value(self.attempts, data["attempts"])
        dpg.set_value(self.color_space, data["color_space"])

    def execute(self, data: NodePackage) -> NodePackage:

        image = data.image

        k = dpg.get_value(self.k)
        attempts = dpg.get_value(self.attempts)
        color_space = dpg.get_value(self.color_space)

        if color_space == "RGB":
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if color_space == "HSV":
            image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        if color_space == "LAB":
            image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        image = image.reshape((-1, 3))
        image = image.astype(np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        best_labels = np.zeros((image.shape[0], 1), dtype=np.int32)
        _, labels, centers = cv2.kmeans(
            image,
            k,
            best_labels, 
            criteria,
            attempts,
            cv2.KMEANS_RANDOM_CENTERS,
        )

        centers = np.uint8(centers)
        image = centers[labels.flatten().astype(int)] # type: ignore
        image = image.reshape((data.image.shape))
        
        if color_space == "RGB":
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if color_space == "HSV":
            image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        if color_space == "LAB":
            image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
            
        data.image = image

        return data
