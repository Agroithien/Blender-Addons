bl_info = {
    "name": "Custom Align Tools",
    "blender": (4, 2, 0),
    "category": "Object",
    "author": "Agroithien",
    "version": (1, 0, 2),
    "location": "View3D > Sidebar > Item Tab > Custom Align tools",
    "description": "Align selected objects in a grid pattern with customizable spacing and other tools.",
}

import bpy
import math


class DistributeSelectedOperator(bpy.types.Operator):
    """Operator to distribute selected objects evenly"""
    bl_idname = "object.distribute_selected"
    bl_label = "Distribute Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[
            ('0', "X", "Distribute along the X-axis"),
            ('1', "Y", "Distribute along the Y-axis"),
            ('2', "Z", "Distribute along the Z-axis")
        ],
        default='0'
    )
    
    def execute(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) < 2:
            self.report({'WARNING'}, "Select at least two objects")
            return {'CANCELLED'}
        
        axis_index = int(self.axis)
        selected_objects.sort(key=lambda obj: obj.location[axis_index])
        
        first_object = selected_objects[0]
        last_object = selected_objects[-1]
        
        total_distance = last_object.location[axis_index] - first_object.location[axis_index]
        spacing = total_distance / (len(selected_objects) - 1) if len(selected_objects) > 1 else 0
        
        for i, obj in enumerate(selected_objects):
            obj.location[axis_index] = first_object.location[axis_index] + (i * spacing)
        
        self.report({'INFO'}, "Objects distributed successfully")
        return {'FINISHED'}


class VIEW3D_PT_distribute_panel(bpy.types.Panel):
    """Panel to house the distribute buttons"""
    bl_idname = "VIEW3D_PT_distribute_panel"
    bl_label = "Distribute"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_context = "Object"
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Distribute Objects:")
        
        row = layout.row(align=True)
        row.operator("object.distribute_selected", text="X").axis = '0'
        row.operator("object.distribute_selected", text="Y").axis = '1'
        row.operator("object.distribute_selected", text="Z").axis = '2'


class OBJECT_OT_RemoveUnusedMaterialSlots(bpy.types.Operator):
    """Remove all unused material slots in selected objects"""
    bl_idname = "object.remove_unused_material_slots"
    bl_label = "Remove Unused Material Slots"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        
        for obj in selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                mesh = obj.data
                used_materials = set(face.material_index for face in mesh.polygons)
                
                for index in reversed(range(len(obj.material_slots))):
                    if index not in used_materials:
                        obj.active_material_index = index
                        bpy.ops.object.material_slot_remove()

        self.report({'INFO'}, "Unused material slots removed.")
        return {'FINISHED'}


class MATERIAL_PT_RemoveUnusedSlotsPanel(bpy.types.Panel):
    """Creates a Panel in the sidebar"""
    bl_label = "Material Slot Cleanup"
    bl_idname = "MATERIAL_PT_remove_unused_slots_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Cleanup Tools:")
        col.operator(OBJECT_OT_RemoveUnusedMaterialSlots.bl_idname, text="Remove Unused Material Slots")


class AlignObjectsInGrid(bpy.types.Operator):
    """Align selected objects in a grid pattern"""
    bl_idname = "object.align_in_grid"
    bl_label = "Align Objects in Grid"
    bl_options = {'REGISTER', 'UNDO'}

    rows: bpy.props.IntProperty(name="Rows", default=3, min=1)
    columns: bpy.props.IntProperty(name="Columns", default=3, min=1)
    spacing: bpy.props.FloatProperty(name="Base Spacing", default=0.1, min=0.01)
    spacing_factor: bpy.props.FloatProperty(name="Spacing Factor", default=1, min=0.001)

    def execute(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) == 0:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        if self.rows == 3 and self.columns == 3:
            total_objects = len(selected_objects)
            self.rows = math.ceil(math.sqrt(total_objects))
            self.columns = math.ceil(total_objects / self.rows)

        max_size = 0
        for obj in selected_objects:
            dimensions = obj.dimensions
            max_size = max(max_size, max(dimensions))

        adjusted_spacing = max(self.spacing, max_size * self.spacing_factor)

        for i, obj in enumerate(selected_objects):
            row = i // self.columns
            col = i % self.columns
            x = col * adjusted_spacing
            y = row * adjusted_spacing
            obj.location = (x, y, 0)

        return {'FINISHED'}


class AlignGridPanel(bpy.types.Panel):
    """Panel for aligning objects in a grid"""
    bl_label = "Align Objects in Grid"
    bl_idname = "OBJECT_PT_align_grid"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator("object.align_in_grid")
        layout.prop(scene, "align_grid_spacing_factor", text="Spacing Factor")


def register():
    bpy.utils.register_class(DistributeSelectedOperator)
    bpy.utils.register_class(VIEW3D_PT_distribute_panel)
    bpy.utils.register_class(OBJECT_OT_RemoveUnusedMaterialSlots)
    bpy.utils.register_class(MATERIAL_PT_RemoveUnusedSlotsPanel)
    bpy.utils.register_class(AlignObjectsInGrid)
    bpy.utils.register_class(AlignGridPanel)

    bpy.types.Scene.align_grid_spacing_factor = bpy.props.FloatProperty(
        name="Spacing Factor",
        default=0.5,
        min=0.001,
        description="Multiplier for spacing between objects in the grid"
    )


def unregister():
    bpy.utils.unregister_class(DistributeSelectedOperator)
    bpy.utils.unregister_class(VIEW3D_PT_distribute_panel)
    bpy.utils.unregister_class(OBJECT_OT_RemoveUnusedMaterialSlots)
    bpy.utils.unregister_class(MATERIAL_PT_RemoveUnusedSlotsPanel)
    bpy.utils.unregister_class(AlignObjectsInGrid)
    bpy.utils.unregister_class(AlignGridPanel)

    del bpy.types.Scene.align_grid_spacing_factor


if __name__ == "__main__":
    register()
