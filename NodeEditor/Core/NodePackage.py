import time
import cv2
import copy

class NodePackage:
    number: int
    image: cv2.typing.MatLike
    mask: cv2.typing.MatLike
    _start_time = time.time()
    
    def copy(self) -> 'NodePackage':
        new_package = NodePackage()
        for key, value in self.__dict__.items():
            setattr(new_package, key, copy.deepcopy(value))
        return new_package