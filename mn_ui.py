import bpy
from . mn_execution import getCodeStrings, resetCompileBlocker, updateAnimationTrees, generateExecutionUnits
from . mn_keyframes import *
from . mn_utils import *
from . utils.mn_selection_utils import *

class AnimationNodesPerformance(bpy.types.Panel):
    bl_idname = "mn.performance_panel"
    bl_label = "Performance"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Settings"
    
    @classmethod
    def poll(self, context):
        return context.space_data.tree_type == "mn_AnimationNodeTree"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()
        col.scale_y = 1.3
        col.operator("mn.force_full_update", text = "Force Update", icon = "PLAY")
        
        col = layout.column(align = True)
        col.prop(scene.mn_settings.update, "frameChange", text = "Frame Changed")
        col.prop(scene.mn_settings.update, "sceneUpdate", text = "Scene Changed")
        col.prop(scene.mn_settings.update, "propertyChange", text = "Property Changed")
        col.prop(scene.mn_settings.update, "resetCompileBlockerWhileRendering", text = "Is Rendering")
        layout.prop(scene.mn_settings.update, "skipFramesAmount")
        layout.prop(scene.mn_settings.update, "redrawViewport")
    
class AnimationNodesDeveloperPanel(bpy.types.Panel):
    bl_idname = "mn.developer_panel"
    bl_label = "Developer"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Settings"
    
    @classmethod
    def poll(self, context):
        return context.space_data.tree_type == "mn_AnimationNodeTree"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        col = layout.column(align = True)
        col.operator("mn.unit_execution_code_in_text_block")
        col.operator("mn.print_node_tree_execution_string")
        
        col = layout.column(align = True)
        col.prop(scene.mn_settings.developer, "printUpdateTime", text = "Print Update Time")
        col.prop(scene.mn_settings.developer, "printGenerationTime", text = "Print Generation Time")
        col.prop(scene.mn_settings.developer, "executionProfiling", text = "Node Execution Profiling")
        
class SocketVisibilityPanel(bpy.types.Panel):
    bl_idname = "mn.socket_visibility_panel"
    bl_label = "Socket Visibility"
    bl_space_type = "NODE_EDITOR"   
    bl_region_type = "UI"
    
    @classmethod
    def poll(self, context):
        return context.active_node
        
    def draw(self, context):
        layout = self.layout
        node = context.active_node
        
        row = layout.row(align = False)
        
        col = row.column(align = True)
        col.label("Inputs:")
        for socket in node.inputs:
            col.prop(socket, "show", text = socket.name)
            
        col = row.column(align = True)
        col.label("Outputs:")
        for socket in node.outputs:
            col.prop(socket, "show", text = socket.name)
        
class KeyframeManagerPanel(bpy.types.Panel):
    bl_idname = "mn.keyframes_manager"
    bl_label = "Keyframes Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        keyframes = getKeyframes()
        box = layout.box()
        col = box.column(align = True)
        for i, keyframe in enumerate(keyframes):
            row = col.row(align = True)
            row.label(keyframe[0])
            row.label(keyframe[1])
            if i > 0:
                remove = row.operator("mn.remove_keyframe", text = "Remove", icon = "X")
                remove.keyframeName = keyframe[0]
                
        row = layout.row(align = True)
        row.prop(scene.mn_settings.keyframes, "selectedType", text = "")
        row.prop(scene.mn_settings.keyframes, "newName", text = "")
        new = row.operator("mn.new_keyframe", text = "Create", icon = "PLUS")
        new.keyframeName = scene.mn_settings.keyframes.newName
        new.keyframeType = scene.mn_settings.keyframes.selectedType
        
class KeyframePanel(bpy.types.Panel):
    bl_idname = "mn.keyframes"
    bl_label = "Keyframes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        objects = getSortedSelectedObjects()
        
        layout.prop(scene.mn_settings.keyframes, "selectedName", text = "Keyframe")
        
        name = scene.mn_settings.keyframes.selectedName
        type = getKeyframeType(name)
        
        row = layout.row()
        
        if type == "Float":
            layout.prop(context.scene.mn_settings.keyframes, "selectedPath", text = "Path")
            setKeyframe = layout.operator("mn.set_float_keyframe", text = "Set Value From Path")
            setKeyframe.keyframeName = name
            setKeyframe.dataPath = context.scene.mn_settings.keyframes.selectedPath
        elif type == "Transforms":
            setTransformsKeyframe = layout.operator("mn.set_transforms_keyframe", text = "Set From Current", icon = "PASTEDOWN")
            setTransformsKeyframe.keyframeName = name
            layout.operator("mn.reset_object_transformations", text = "Set Initial Transforms on Object", icon = "PASTEFLIPUP")
        elif type == "Vector":
            layout.label("Set Vector From:")
            row = layout.row(align = True)
            for path in [("Location", "location"), ("Rotation", "rotation_euler"), ("Scale", "scale")]:
                setKeyframe = row.operator("mn.set_vector_keyframe_from_path", text = path[0])
                setKeyframe.keyframeName = name
                setKeyframe.vectorPath = path[1]
        
        for object in objects:
            box = layout.box()
            row = box.row()
            row.prop(object, "name", text = "")
            
            remove = row.operator("mn.remove_keyframe_from_object", text = "Remove Keyframe")
            remove.objectName = object.name
            remove.keyframeName = name
            
            drawKeyframeInput(box, object, name)
        
        
class ForceNodeTreeUpdate(bpy.types.Operator):
    bl_idname = "mn.force_full_update"
    bl_label = "Force Node Tree Update"
    bl_description = "Recalculate the nodes / Start the execution again after an error happened"

    def execute(self, context):
        resetCompileBlocker()
        generateExecutionUnits()
        updateAnimationTrees()
        return {'FINISHED'}
        
class PrintNodeTreeExecutionStrings(bpy.types.Operator):
    bl_idname = "mn.print_node_tree_execution_string"
    bl_label = "Print Node Tree Code"
    bl_description = "Print the auto generated python code into the console"

    def execute(self, context):
        print()
        for codeString in getCodeStrings():
            print(codeString)
            print()
            print("-"*80)
            print()
        return {'FINISHED'}
        
class UnitExecutionCodeInTextBlock(bpy.types.Operator):
    bl_idname = "mn.unit_execution_code_in_text_block"
    bl_label = "Code in Text Block"
    bl_description = "Create a text block and insert the auto generated python code"
    
    def execute(self, context):
        codeString = ("\n\n#"+ "-"*50 + "\n\n").join(getCodeStrings())
        textBlock = bpy.data.texts.get("Unit Execution Code")
        if textBlock is None:
            textBlock = bpy.data.texts.new("Unit Execution Code")
        textBlock.from_string(codeString)
        return {'FINISHED'}