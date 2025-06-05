from enum import Enum
class IOStatus(Enum):
    INSIDE = "inside"
    OUTSIDE = "outside"
    SURFACE = "surface"
    REFLECT = "reflect"
    STICK = "stick"
    BORDER = "border"
    ON_POLYGON = "on_polygon"
    END_POLYGON = "end_polygon"
    BOTTOM_OUT = "bottom_out"
    SPOT_EDGE_OUT = "spot_edge_out"
    SPHERE_OUT = "sphere_out"  # ← SpotIO側にしかなかった項目もここに統合
