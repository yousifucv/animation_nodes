import bpy
from bpy.types import Node
from mathutils import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

trackItems = [("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", ""),("-X", "-X", ""), ("-Y", "-Y", ""), ("-Z", "-Z", "")]
upItems = [("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")]

class mn_DirectionToRotation(Node, AnimationNode):
    bl_idname = "mn_DirectionToRotation"
    bl_label = "Direction to Rotation"
    
    trackAxis = bpy.props.EnumProperty(items = trackItems, update = nodeTreeChanged, default = "Z")
    upAxis = bpy.props.EnumProperty(items = upItems, update = nodeTreeChanged, default = "X")
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "Direction")
        self.outputs.new("mn_VectorSocket", "Rotation")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        col = layout.column(align = True)

        row = col.row(align = True)
        row.label("To:")
        row.prop(self, "trackAxis", expand = True)
        
        col.separator()

        row = col.row(align = True)
        row.label("Up:")
        row.prop(self, "upAxis", expand = True)
        
        if self.trackAxis == self.upAxis:
            layout.label("Must be different", icon = "ERROR")
        
    def getInputSocketNames(self):
        return {"Direction" : "direction"}
    def getOutputSocketNames(self):
        return {"Rotation" : "rotation"}

    def execute(self, direction):
        if self.trackAxis == self.upAxis:
            if self.trackAxis == "Z": self.upAxis = "X"
            else: self.trackAxis = "Z"
        out = direction.to_track_quat(self.trackAxis, self.upAxis).to_euler()
        return out
        

