import json
from typing import Any
import dearpygui.dearpygui as dpg
import os
import importlib
import pickle

from NodeEditor.Core.Node import Node

class NodeEditor:
    
    _menu_node_setup: dict[str, dict[str, list[dict]]] = {}
    _minimap: bool = False

    def __init__(self, nodes_dir: str = "NodeEditor/Nodes") -> None:
        
        self.nodes_dir = nodes_dir
        
        self.available_nodes: list = []
        self.nodes: list[Node] = []
        self.node_links: list[tuple[str | int, Node, Node]] = []
        self.node_editor = dpg.generate_uuid()
        self.right_click_menu = dpg.generate_uuid()
        self.save_dialog_id = dpg.generate_uuid()
        self.load_dialog_id = dpg.generate_uuid()
        
        self._auto_load_available_nodes()
        
    def save_workspace(self, sender, app_data):
        
        if "file_path_name" in app_data:
            filepath = app_data["file_path_name"]
        else:
            dpg.hide_item(self.save_dialog_id)
            return
        
        
        data = {}
        
        # add all nodes and there locations
        data["nodes"] = []
        for node in self.nodes:
            data["nodes"].append({
                "node": node.__class__.__name__,
                "pos": node._node_pos,
                "data": node.on_save()
            })
            
        # add all the links (Use the node class name and location to find the node)
        data["links"] = []
        for link_id, input_node, output_node in self.node_links:
            data["links"].append({
                "to": {
                    "node": output_node.__class__.__name__,
                    "pos": output_node._node_pos,
                    # Witch output (1 or 2) is it based on if the input node has it as a second output or not
                    "output_1": output_node._input_node == input_node,
                    "output_2": output_node._input_node_2 == input_node
                },
                "from": {
                    "node": input_node.__class__.__name__,
                    "pos": input_node._node_pos,
                    # Witch input (1 or 2) is it
                    "input": output_node in input_node._output_nodes,
                    "input_2": output_node in input_node._output_nodes_2
                }
            })
        
        
        with open(filepath, "w") as f:
            json.dump(data, f)
            
        dpg.hide_item(self.save_dialog_id)

    def load_workspace(self, sender, app_data):
        
        if "selections" in app_data:
            for i in app_data["selections"].values():
                filepath = i
                break
        else:
            dpg.hide_item(self.load_dialog_id)
            return
        
        if not os.path.exists(filepath):
            print("File not found")
            return
        
        with open(filepath, "r") as f:
            data = json.load(f)
            
        # Clear the current workspace
        for node in self.nodes:
            dpg.delete_item(node._node_id)
        self.nodes = []
        
        for link_id, input_node, output_node in self.node_links:
            dpg.delete_item(link_id)
        self.node_links = []
        
        # Add all the nodes
        for node_data in data["nodes"]:
            for available_node in self.available_nodes:
                if available_node.__name__ == node_data["node"]:
                    new_node = available_node()
                    self._add_node(new_node)
                    new_node._set_node_pos(node_data["pos"][0], node_data["pos"][1])
                    try:
                        new_node.on_load(node_data["data"])
                    except Exception:
                        pass
                    break
                
        # Add all the links
        for link_data in data["links"]:
            from_data = link_data["from"]
            to_data = link_data["to"]
            
            from_node = to_node = None
            for node in self.nodes:
                if node.__class__.__name__ == from_data["node"] and node._node_pos == from_data["pos"]:
                    from_node = node
                if node.__class__.__name__ == to_data["node"] and node._node_pos == to_data["pos"]:
                    to_node = node
                if from_node and to_node:
                    break
                
            if not from_node or not to_node:
                print("Node not found")
                continue
            
            attr_Output = None
            if from_data["input"]:
                from_node.add_output_node(to_node)
                attr_Output = from_node._output_id
            elif from_data["input_2"]:
                from_node.add_output_node_2(to_node)
                attr_Output = from_node._output_id_2
                
            attr_Input = None
            if to_data["output_1"]:
                to_node.set_input_node(from_node)
                attr_Input = to_node._input_id
            elif to_data["output_2"]:
                to_node.set_input_node_2(from_node)
                attr_Input = to_node._input_id_2
                
            if not attr_Input or not attr_Output:
                print("Attr not found")
                continue
                
            node_link_id = dpg.generate_uuid()
            dpg.add_node_link(attr_Input, attr_Output, parent=self.node_editor, tag=node_link_id)
            self.node_links.append((node_link_id, from_node, to_node))
            from_node._on_linked()
            to_node._on_linked()
            
        dpg.hide_item(self.load_dialog_id)
        
    def clear_workspace(self):
        # Delete all the links
        for link_id, _, _ in self.node_links:
            dpg.delete_item(link_id)
            
        # Delete all the nodes
        for node in self.nodes:
            dpg.delete_item(node._node_id)
            
        self.nodes = []
        self.node_links = []
        
    def _auto_load_available_nodes(self):
        
        file_path = self.nodes_dir
        import_path = file_path.replace("/", ".")
        files = os.listdir(file_path)
        
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                file = file.replace(".py", "")
                module = importlib.import_module(f"{import_path}.{file}")
                class_name = file
                class_ = getattr(module, class_name)
                self.available_nodes.append(class_)
        
    def _setup_menu(self):
        for node in self.available_nodes:
            temp_node: Node = node()
            catagory = temp_node.catagory
            main_catagory = catagory if "/" not in catagory else catagory.split("/")[0]
            sub_catagory = "" if "/" not in catagory else catagory.split("/")[1]
            
            if main_catagory not in self._menu_node_setup:
                self._menu_node_setup[main_catagory] = {}
                
            if sub_catagory not in self._menu_node_setup[main_catagory]:
                self._menu_node_setup[main_catagory][sub_catagory] = []
            
                
            d = {
                    "name": temp_node.label,
                    "user_data": node
                }
                        
            self._menu_node_setup[main_catagory][sub_catagory].append(d)
        
    def _link_nodes_callback(self, sender, user_data, app_data):
        input_node_id, output_node_id = user_data
        
        input_node = output_node = None
        
        for node in self.nodes:
            if node._input_id == output_node_id or node._input_id_2 == output_node_id:
                output_node = node
                
            if node._output_id == input_node_id:
                input_node = node
                
        if not input_node:
            # Check for dual output nodes
            for node in self.nodes:
                if node._output_id_2 == input_node_id:
                    input_node = node
                    break
            if not input_node:
                print("Input Node not found")
                return
            if not output_node:
                print("Output Node not found")
                return
            
            print(f"Linking {input_node.label} to {output_node.label} (Dual Output)")
            input_node.add_output_node_2(output_node)
            output_node.auto_set_input_node(input_node, output_node_id)
            
        elif input_node and output_node:
            print(f"Linking {input_node.label} to {output_node.label}")
            input_node.add_output_node(output_node)
            output_node.auto_set_input_node(input_node, output_node_id)
            
        else:
            print("input_id:", input_node_id, "output_id:", output_node_id)
            for node in self.nodes:
                print(node.label, node._input_id, node._output_id)
                print()
            return
        
        node_link_id = dpg.generate_uuid()
        dpg.add_node_link(input_node_id, output_node_id, parent=sender, tag=node_link_id)
        self.node_links.append((node_link_id, input_node, output_node))
        
        # Set the nodes to _on_linked()
        input_node._on_linked()
        output_node._on_linked()
                                
        # print(f"Linking {input_node.lable} to {output_node.lable}")
        
    def _delink_nodes_callback(self, sender, app_data, user_data):
        node_link_id = app_data
        
        for link_id, input_node, output_node in self.node_links:
            if link_id == node_link_id:
                node_set = (input_node, output_node)
                break
        else:
            print("Link not found")
            return
            
        input_node, output_node = node_set
        print(f"Delinking {input_node.label} from {output_node.label}")
        input_node.remove_output_node(output_node)
        output_node.remove_input_node(input_node)
        
        # Set the nodes to _on_delinked()
        input_node._on_delinked()
        output_node._on_delinked()
        
        dpg.delete_item(node_link_id)

        return
        
        input_node_id, output_node_id = user_data
        
        input_node = output_node = None
        
        for node in self.nodes:
            if node._input_id == output_node_id:
                output_node = node
                
            if node._output_id == input_node_id:
                input_node = node
                
        if input_node and output_node:
            print(f"Delinking {input_node.lable} from {output_node.lable}")
            input_node.remove_output_node(output_node)
            output_node.remove_input_node(input_node)
        else:
            print("input_id:", input_node_id, "output_id:", output_node_id)
            for node in self.nodes:
                print(node.lable, node._input_id, node._output_id)
                
        dpg.delete_item(user_data)
        
    def _left_click_callback(self, sender, app_data, user_data):
        print("Right Click")
        print(app_data, user_data)
        
    def compose(self, parent: str | int = ""):
        with dpg.node_editor(callback=self._link_nodes_callback, delink_callback=self._delink_nodes_callback, minimap=self._minimap, tag=self.node_editor, parent=parent):                            
            for node in self.nodes:
                node._compose()
                
    def _add_node(self, node: Node):
        self.nodes.append(node)
        node._node_delete_callback = self._node_delete_callback
        node._node_duplicate_callback = self._node_duplicate_callback
        node._compose(self.node_editor)
        node.on_init()
        
    def _node_delete_callback(self, sender, app_data, user_data):
        
        node_id = user_data
        
        # Find the node
        for node in self.nodes:
            if node._node_id == node_id:
                node_to_remove = node
                break
        else:
            print("Node not found")
            return
        
        # Find all the links connected to this nodes output
        output_links = []
        link_deleted = []
        for link_id, input_node, output_node in self.node_links:
            if output_node._node_id == node_id:
                output_links.append(link_id)
                
        # Delink all the nodes connected to this node
        node_links = []
        for link_id in output_links:
            for link_id_out, input_node, output_node in self.node_links:
                if link_id == link_id_out:               
                    input_node.remove_output_node(output_node)
                    output_node.remove_input_node(input_node)
                    
                    input_node._on_delinked()
                    output_node._on_delinked()
                    
                    node_links.append((link_id, input_node, output_node))
                    if link_id not in link_deleted:
                        try:
                            dpg.delete_item(link_id)
                        except Exception as e:
                            print(e)
                        link_deleted.append(link_id)
                    break
                
        # Find all the links connected to this nodes input
        input_links = []
        for link_id, input_node, output_node in self.node_links:
            if input_node._node_id == node_id:
                input_links.append(link_id)
                
        # Delink all the nodes connected to this node
        for link_id in input_links:
            for link_id_in, input_node, output_node in self.node_links:
                if link_id == link_id_in:
                    input_node.remove_output_node(output_node)
                    output_node.remove_input_node(input_node)
                    
                    input_node._on_delinked()
                    output_node._on_delinked()
                    
                    node_links.append((link_id, input_node, output_node))
                    if link_id not in link_deleted:
                        try:
                            dpg.delete_item(link_id)
                        except Exception as e:
                            print(e)
                        link_deleted.append(link_id)
                    else:
                        print("Link already deleted")
                    break
                
        # Remove the node
        for d in node_links:
            self.node_links.remove(d)
                
        self.nodes.remove(node_to_remove)
        dpg.delete_item(node_id)
        
    def _node_duplicate_callback(self, sender, app_data, user_data):
        node_id = user_data
        # Find the node type and create a new node of that type
        for node in self.nodes:
            if node._node_id == node_id:
                for available_node in self.available_nodes:
                    if isinstance(node, available_node):
                        new_node: Node = available_node()
                        self._add_node(new_node)
                        # Set the new nodes position to the old nodes position + 25 on each axis
                        new_node._set_node_pos(node._node_pos[0] + 25, node._node_pos[1] + 25)
                        break
                break
        
    def _menu_callback(self, sender, user_data, app_data):
        node = app_data
        node = node()
        self._add_node(node)
        
    def _menu_callback_right_click(self, sender, user_data, app_data):
        node: Node = app_data()
        self._add_node(node)
        dpg.configure_item(self.right_click_menu, show=False)
        mouse_position = dpg.get_mouse_pos(local=False)
        node._set_node_pos(mouse_position[0] - 25, mouse_position[1] - 50)
        
    def right_click_cb(self, sender, app_data):
        
        # Check if the right click is in a node
        for node in self.nodes:
            node_pos = node._node_pos
            node_size = node._node_size
            mouse_pos = dpg.get_mouse_pos(local=False)
            
            if node_pos[0] < mouse_pos[0] < node_pos[0] + node_size[0] and node_pos[1] < mouse_pos[1] < node_pos[1] + node_size[1]:
                return
        
        mice_pos = dpg.get_mouse_pos(local=False)
        dpg.configure_item(self.right_click_menu, show=True)
        dpg.set_item_pos(self.right_click_menu, [mice_pos[0], mice_pos[1]])
        
    def left_click_cb(self, sender, app_data):
        if dpg.get_item_state(self.right_click_menu).get("visible", False):
            window_pos = dpg.get_item_pos(self.right_click_menu)
            window_size = dpg.get_item_rect_size(self.right_click_menu)
            mouse_pos = dpg.get_mouse_pos(local=False)
            
            if window_pos[0] + window_size[0] < mouse_pos[0]:
                return
            
            # Check if the left click is in the window
            if window_pos[0] < mouse_pos[0] < window_pos[0] + window_size[0] and window_pos[1] < mouse_pos[1] < window_pos[1] + window_size[1]:
                return
            
            dpg.configure_item(self.right_click_menu, show=False)
    
    def right_click_key_cb(self, sender, app_data):
        dpg.configure_item(self.right_click_menu, show=False)
        
    def toggle_minimap(self):
        self._minimap = not self._minimap
        dpg.configure_item(self.node_editor, minimap=self._minimap)
        
    def start(self):
        dpg.create_context()
        self._setup_menu()
            
        with dpg.handler_registry():
            dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Right, callback=self.right_click_cb)
            dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=self.left_click_cb)
            dpg.add_key_down_handler(key=dpg.mvKey_Escape, callback=self.right_click_key_cb)

        with dpg.window(label="Right click window", modal=False, show=False, tag=self.right_click_menu, no_title_bar=True):
            # Add the nodes to the right click menu
            for catagory, nodes in self._menu_node_setup.items():
                    with dpg.menu(label=catagory):
                        
                        for sub_catagory, nodes in nodes.items():
                            if sub_catagory == "":
                                for node in nodes:
                                    dpg.add_menu_item(label=node["name"], callback=self._menu_callback_right_click, user_data=(node["user_data"]))
                            else:
                                with dpg.menu(label=sub_catagory):
                                    for node in nodes:
                                        dpg.add_menu_item(label=node["name"], callback=self._menu_callback_right_click, user_data=(node["user_data"]))
                
        with dpg.window(label="Node Editor") as main_window:
            # dpg.bind_theme(create_star_trek_theme())
            
            with dpg.file_dialog(directory_selector=False, show=False, tag=self.save_dialog_id, file_count=0, width=700, height=400, callback=self.save_workspace):
                dpg.add_file_extension(".json")
                
            with dpg.file_dialog(directory_selector=False, show=False, tag=self.load_dialog_id, file_count=0, width=700, height=400, callback=self.load_workspace):
                dpg.add_file_extension(".json")
            with dpg.menu_bar():
                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(label="Save Project", callback=lambda: dpg.show_item(self.save_dialog_id))
                    dpg.add_menu_item(label="Load Project", callback=lambda: dpg.show_item(self.load_dialog_id))
                    dpg.add_menu_item(label="Clear Nodes", callback=self.clear_workspace)
                    dpg.add_menu_item(label="Toggle Minimap", callback=self.toggle_minimap)
                    
                for catagory, nodes in self._menu_node_setup.items():
                    with dpg.menu(label=catagory):
                        
                        for sub_catagory, nodes in nodes.items():
                            if sub_catagory == "":
                                for node in nodes:
                                    dpg.add_menu_item(label=node["name"], callback=self._menu_callback, user_data=(node["user_data"]))
                            else:
                                with dpg.menu(label=sub_catagory):
                                    for node in nodes:
                                        dpg.add_menu_item(label=node["name"], callback=self._menu_callback, user_data=(node["user_data"]))  
                
            self.compose()
            
        dpg.create_viewport(title="Main Viewport")
        dpg.set_primary_window(main_window, True)
        dpg.setup_dearpygui()
        
        self.load_workspace(None, {"selections": {"file_path_name": "temp_node_editor.json"}})
        
        # dpg.show_style_editor()
        
        dpg.show_viewport()
        dpg.start_dearpygui()
        self.save_workspace(None, {"file_path_name": "temp_node_editor.json"})
        dpg.destroy_context()