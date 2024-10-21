import threading
import time
from typing import Any, Callable, Literal, overload
import dearpygui.dearpygui as dpg
import copy
import traceback
import concurrent.futures as future

from NodeEditor.Core.NodePackage import NodePackage

dpg.create_context()

with dpg.theme() as error_theme:
    with dpg.theme_component():
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar, (96, 0, 0, 255), category=dpg.mvThemeCat_Nodes
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            (96, 0, 0, 150),
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            (96, 0, 0, 150),
            category=dpg.mvThemeCat_Nodes,
        )

with dpg.theme() as warning_theme:
    with dpg.theme_component():
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar, (96, 96, 0, 255), category=dpg.mvThemeCat_Nodes
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            (96, 96, 0, 150),
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            (96, 96, 0, 150),
            category=dpg.mvThemeCat_Nodes,
        )

with dpg.theme() as success_theme:
    with dpg.theme_component():
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar, (0, 96, 32, 255), category=dpg.mvThemeCat_Nodes
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            (0, 96, 32, 150),
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            (0, 96, 32, 150),
            category=dpg.mvThemeCat_Nodes,
        )

with dpg.theme() as delinked_theme:
    with dpg.theme_component():
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar, (96, 0, 96, 255), category=dpg.mvThemeCat_Nodes
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            (96, 0, 96, 150),
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            (96, 0, 96, 150),
            category=dpg.mvThemeCat_Nodes,
        )

with dpg.theme() as linked_theme:
    with dpg.theme_component():
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar, (0, 96, 96, 255), category=dpg.mvThemeCat_Nodes
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            (0, 96, 96, 150),
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            (0, 96, 96, 150),
            category=dpg.mvThemeCat_Nodes,
        )
        
with dpg.theme() as executing_theme:
    with dpg.theme_component():
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBar, (0, 0, 96, 255), category=dpg.mvThemeCat_Nodes
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarHovered,
            (0, 0, 96, 150),
            category=dpg.mvThemeCat_Nodes,
        )
        dpg.add_theme_color(
            dpg.mvNodeCol_TitleBarSelected,
            (0, 0, 96, 150),
            category=dpg.mvThemeCat_Nodes,
        )

class Node:
    _node_delete_callback: Callable[[Any, Any, Any], None]
    _node_duplicate_callback: Callable[[Any, Any, Any], None]
    _latest_data: NodePackage | None = None
    _latest_data_2: NodePackage | None = None
    _skip_execution: bool = False
    _first_time_run: bool = True
    _keep_error: bool = False

    def __init__(
        self,
        lable: str,
        type: Literal[
            "Input", "Both", "Output", "BothDualOut", "BothDualIn", "DualInDualOut"
        ] = "Both",
        catagory: Literal["Inputs", "Output", "Filter"] | str = "All",
        max_width: int = 100,
        *,
        input_lable: str = "",
        input_lable_2: str = "",
        output_lable: str = "",
        output_lable_2: str = "",
    ) -> None:
        self.label = lable
        self.type = type
        self.catagory = catagory
        self._max_width = max_width if max_width > 100 else 100

        self._input_lable = input_lable
        self._input_lable_2 = input_lable_2
        self._output_lable = output_lable
        self._output_lable_2 = output_lable_2

        self._output_nodes: list["Node"] = []
        self._output_nodes_2: list["Node"] = []
        self._input_node: Node | None = None
        self._input_node_2: Node | None = None
        self._node_id = dpg.generate_uuid()

        self._input_id = dpg.generate_uuid()
        self._input_id_2 = dpg.generate_uuid()
        self._output_id = dpg.generate_uuid()
        self._output_id_2 = dpg.generate_uuid()

        self._error_text_id = dpg.generate_uuid()

        self._latest_output = None

        self._custom_outputs: list[tuple[Callable[[Any], Any], str]] = []

        self._last_update_call = 0
        self._min_delay = 50 # ms
        self._update_call: bool = False

        threading.Thread(target=self._update_thread, daemon=True).start()

    def on_init(self):
        pass

    def on_load(self, data: dict):
        pass

    def on_save(self) -> dict:
        return {}

    def add_custom_output(self, call_back: Callable[[Any], Any], lable: str = ""):
        self._custom_outputs.append((call_back, lable))

    def update(self):
        self._update_call = True
        self._last_update_call = time.time()

    def _update_thread(self):
        while True:
            self._update()
            time.sleep(0.01) if self._update_call else time.sleep(0.2)

    def _update(self):
        if (
            time.time() - self._last_update_call > self._min_delay * 0.001
            and self._update_call
        ):
            self._update_call = False
            if self._latest_data is not None:
                self._call_output_nodes(self._latest_data)

    def force_update(self):
        if self._latest_data is not None:
            self._call_output_nodes(self._latest_data)
        else:
            print("No data")

    @overload
    def execute(
        self, data: NodePackage
    ) -> NodePackage | tuple[NodePackage, NodePackage]: ...

    @overload
    def execute(
        self, data: NodePackage, data2: NodePackage
    ) -> NodePackage | tuple[NodePackage, NodePackage]: ...

    def execute(
        self, data: NodePackage, data2: NodePackage | None = None
    ) -> NodePackage | tuple[NodePackage, NodePackage]:

        print(f"Executing: {self.label}")

        return data

    def compose(self):
        pass

    def reset(self):
        pass

    def _compose(self, parent: int | str = 0):

        with dpg.node(label=self.label, tag=self._node_id, parent=parent):

            if self.type == "Output":
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                    dpg.add_button(
                        label="Run", callback=lambda: self._call_output_nodes()
                    )

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_checkbox(
                    label="Skip Execution",
                    default_value=False,
                    callback=self._toggle_skip_execution,
                )
                dpg.add_text("", wrap=self._max_width, tag=self._error_text_id)

            if self.type != "Output":
                with dpg.node_attribute(
                    label="Input",
                    attribute_type=dpg.mvNode_Attr_Input,
                    tag=self._input_id,
                    shape=dpg.mvNode_PinShape_TriangleFilled,
                ):
                    dpg.add_text(self._input_lable or "Input")

            if self.type == "BothDualIn" or self.type == "DualInDualOut":
                with dpg.node_attribute(
                    label="Input 2",
                    attribute_type=dpg.mvNode_Attr_Input,
                    tag=self._input_id_2,
                    shape=dpg.mvNode_PinShape_TriangleFilled,
                ):
                    dpg.add_text(self._input_lable_2 or "Input 2")

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_spacer(height=10)
                self.compose()
                dpg.add_spacer(height=10)

            if self.type != "Input":
                with dpg.node_attribute(
                    label="Output",
                    attribute_type=dpg.mvNode_Attr_Output,
                    tag=self._output_id,
                    shape=dpg.mvNode_PinShape_TriangleFilled,
                ):
                    dpg.add_text(self._output_lable or "Output", indent=self._max_width)

            # with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            #     dpg.add_spacer(height=10)

            if self.type == "BothDualOut" or self.type == "DualInDualOut":
                with dpg.node_attribute(
                    label="Output 2",
                    attribute_type=dpg.mvNode_Attr_Output,
                    tag=self._output_id_2,
                    shape=dpg.mvNode_PinShape_TriangleFilled,
                ):
                    dpg.add_text(
                        self._output_lable_2 or "Output 2", indent=self._max_width
                    )

            with dpg.popup(self._node_id):
                dpg.add_menu_item(
                    label="Delete",
                    callback=self._node_delete_callback,
                    user_data=self._node_id,
                )
                dpg.add_menu_item(
                    label="Duplicate",
                    callback=self._node_duplicate_callback,
                    user_data=self._node_id,
                )
                dpg.add_menu_item(label="Force Update", callback=self.force_update)
                dpg.add_menu_item(label="Reset", callback=self.reset)

    def on_error(self, error: str = ""):
        self._keep_error = True
        # Make the node border red
        try:
            dpg.bind_item_theme(self._node_id, error_theme)
        except Exception as e:
            try:
                dpg.set_item_theme(self._node_id, error_theme)
            except Exception as e:
                print("Error setting theme")
        if error:
            dpg.set_value(self._error_text_id, error)

    def _on_warning(self):
        # Make the node border yellow
        try:
            dpg.bind_item_theme(self._node_id, warning_theme)
        except Exception as e:
            try:
                dpg.set_item_theme(self._node_id, warning_theme)
            except Exception as e:
                print("Error setting theme")

        dpg.set_value(self._error_text_id, "")

    def _on_delinked(self):
        # Make the node border purple
        try:
            dpg.bind_item_theme(self._node_id, delinked_theme)
        except Exception as e:
            try:
                dpg.set_item_theme(self._node_id, delinked_theme)
            except Exception as e:
                print("Error setting theme")

        dpg.set_value(self._error_text_id, "")
        self.reset()

    def _on_linked(self):
        # Make the node border teal
        try:
            dpg.bind_item_theme(self._node_id, linked_theme)
        except Exception as e:
            try:
                dpg.set_item_theme(self._node_id, linked_theme)
            except Exception as e:
                print("Error setting theme")

        dpg.set_value(self._error_text_id, "")

    def _on_success(self):
        # Make the node border green
        try:
            dpg.bind_item_theme(self._node_id, success_theme)
        except Exception as e:
            try:
                dpg.set_item_theme(self._node_id, success_theme)
            except Exception as e:
                print("Error setting theme")

        dpg.set_value(self._error_text_id, "")

    def add_output_node(self, node: "Node"):
        self._output_nodes.append(node)

    def add_output_node_2(self, node: "Node"):
        self._output_nodes_2.append(node)

    def set_input_node(self, node: "Node"):
        self._input_node = node
        print("Setting input node", node.label)
        print(
            "Setting input node 2",
            n.label if (n := self._input_node_2) is not None else None,
        )

    def set_input_node_2(self, node: "Node"):
        self._input_node_2 = node
        print(
            "Setting input node",
            n.label if (n := self._input_node) is not None else None,
        )
        print("Setting input node 2", node.label)

    def auto_set_input_node(self, node: "Node", link_id: str | int):
        if self._input_id == link_id:
            self.set_input_node(node)
        elif self._input_id_2 == link_id:
            self.set_input_node_2(node)
        else:
            raise ValueError("Link ID not found")

    def remove_output_node(self, node: "Node"):
        if node in self._output_nodes:
            self._output_nodes.remove(node)
        else:
            if node in self._output_nodes_2:
                self._output_nodes_2.remove(node)
            else:
                print("Node not found")

    def remove_input_node(self, node: "Node"):

        if self._input_node == node:
            self._input_node = None
            self._latest_data = None
        else:
            self._input_node_2 = None
            self._latest_data_2 = None

    def remove_output_node_2(self, node: "Node"):
        self._output_nodes_2.remove(node)

    def _auto_set_latest_data(self, data: NodePackage, node: "Node"):
        # Check to see if the data is from the first or second input
        if self.type == "BothDualIn" or self.type == "DualInDualOut":
            if self._input_node and self._input_node._node_id == node._node_id:
                self._latest_data = data
            else:
                self._latest_data_2 = data
        else:
            self._latest_data = data

    def _call_output_nodes(self, data: NodePackage | None = None):

        self._keep_error = False

        if data is None:
            data = NodePackage()

        if self.type == "Output":
            data._start_time = time.time()
            self._latest_data = copy.deepcopy(data)
        # self._latest_data = copy.deepcopy(data)

        if self.type == "BothDualIn" or self.type == "DualInDualOut":
            if self._latest_data_2 is None or self._latest_data is None:
                print("Not enough data")
                self._on_warning()
                return
            try:
                try:
                    dpg.bind_item_theme(self._node_id, executing_theme)
                except Exception as e:
                    try:
                        dpg.set_item_theme(self._node_id, executing_theme)
                    except Exception as e:
                        print("Error setting theme")
                output = (
                    self.execute(
                        copy.deepcopy(self._latest_data),
                        copy.deepcopy(self._latest_data_2),
                    )
                    if not self._skip_execution
                    else self._latest_data or data
                )

                self._on_success() if not self._keep_error else None

            except Exception as e:
                print("Error in execute method")
                traceback.print_exc()
                self.on_error()
                return
            # self._latest_output = output
        else:
            try:
                try:
                    dpg.bind_item_theme(self._node_id, executing_theme)
                except Exception as e:
                    try:
                        dpg.set_item_theme(self._node_id, executing_theme)
                    except Exception as e:
                        print("Error setting theme")
                output = (
                    self.execute(copy.deepcopy(data))
                    if not self._skip_execution
                    else self._latest_data or data
                )
                self._on_success() if not self._keep_error else None

            except Exception as e:
                print("Error in execute method")
                traceback.print_exc()
                self.on_error()
                return

        output1 = output2 = None

        if isinstance(output, tuple):
            output1, output2 = output
        else:
            output1 = output
            
        futures: list[future.Future] = []

        if self.type == "BothDualOut":
            with future.ThreadPoolExecutor() as executor:
                for node in self._output_nodes:
                    temp_data = copy.deepcopy(output1)
                    node._auto_set_latest_data(temp_data, self)
                    futures.append(executor.submit(node._call_output_nodes, temp_data))
                    # node._call_output_nodes(temp_data)
            with future.ThreadPoolExecutor() as executor:
                for node in self._output_nodes_2:
                    temp_data = copy.deepcopy(output2)
                    if temp_data is not None:
                        node._auto_set_latest_data(temp_data, self)
                    futures.append(executor.submit(node._call_output_nodes, temp_data))
                    # node._call_output_nodes(temp_data)

        elif self.type == "DualInDualOut":
            with future.ThreadPoolExecutor() as executor:
                for node in self._output_nodes:
                    temp_data = copy.deepcopy(output1)
                    node._latest_data = temp_data
                    futures.append(executor.submit(node._call_output_nodes, temp_data))
                    # node._call_output_nodes(temp_data)
            with future.ThreadPoolExecutor() as executor:
                for node in self._output_nodes_2:
                    temp_data = copy.deepcopy(output2)
                    if temp_data is not None:
                        node._latest_data_2 = temp_data
                    futures.append(executor.submit(node._call_output_nodes, temp_data))
                    # node._call_output_nodes(temp_data)
        else:
            with future.ThreadPoolExecutor() as executor:
                for node in self._output_nodes:
                    temp_data = copy.deepcopy(output1)
                    node._auto_set_latest_data(temp_data, self)
                    futures.append(executor.submit(node._call_output_nodes, temp_data))
                    # node._call_output_nodes(temp_data)
                    
        future.wait(futures, return_when=future.ALL_COMPLETED)

    def _toggle_skip_execution(self):
        self._skip_execution = not self._skip_execution
        self.update()

    @property
    def _node_pos(self):
        return dpg.get_item_pos(self._node_id)

    @property
    def _node_size(self):
        return dpg.get_item_rect_size(self._node_id)

    def _set_node_pos(self, x: float, y: float):
        dpg.set_item_pos(self._node_id, [x, y])

    def to_dict(self):
        return {
            "label": self.label,
            "type": self.type,
            "data": self._latest_data,
            "output_nodes": [node._node_id for node in self._output_nodes],
            "output_nodes_2": (
                [node._node_id for node in self._output_nodes_2]
                if hasattr(self, "_output_nodes_2")
                else []
            ),
        }

    @classmethod
    def from_dict(cls, data, node_map):
        node = cls(data["label"])
        node.type = data["type"]
        node._latest_data = data["data"]
        node._output_nodes = [node_map[node_id] for node_id in data["output_nodes"]]
        if "output_nodes_2" in data:
            node._output_nodes_2 = [
                node_map[node_id] for node_id in data["output_nodes_2"]
            ]
        return node

    def __str__(self) -> str:
        return str(
            {
                "label": self.label,
                "type": self.type,
                "node_id": self._node_id,
                "input1": (
                    {}
                    if (n1 := self._input_node) is None
                    else {"label": n1.label, "node_id": n1._node_id}
                ),
                "input2": (
                    {}
                    if (n2 := self._input_node_2) is None
                    else {"label": n2.label, "node_id": n2._node_id}
                ),
                "output1": self._output_nodes,
                "output2": self._output_nodes_2,
            }
        )

    def __repr__(self) -> str:
        return self.__str__()
