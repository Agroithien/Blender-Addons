bl_info = {
    "name": "Distribute X|Y|Z",
    "author": "Agroithien",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Item Tab > Distribute",
    "description": "An addon to distribute objects evenly on the X, Y, and Z axes",
    "category": "Object"
}

import bpy

class DistributeSelectedOperator(bpy.types.Operator):
    """Operator to distribute selected objects evenly"""
    bl_idname = "object.distribute_selected"
    bl_label = "Distribute Selected"
    
    axis: bpy.props.StringProperty()

    axis_map = {"X": 0, "Y": 1, "Z": 2}
    
    def execute(self, context):
        # Get the selected objects and sort them by their position on the specified axis
        selected_objects = context.selected_objects
        
        if len(selected_objects) < 2:
            self.report({'WARNING'}, "Select at least two objects")
            return {'CANCELLED'}
        
        axis_index = self.axis_map.get(self.axis.upper(), 0)
        selected_objects.sort(key=lambda obj: obj.location[axis_index])
        
        # First and last objects
        first_object = selected_objects[0]
        last_object = selected_objects[-1]
        
        # Distance between first and last
        total_distance = last_object.location[axis_index] - first_object.location[axis_index]
        
        # Spacing
        spacing = total_distance / (len(selected_objects) - 1)
        
        # Apply new positions
        for i, obj in enumerate(selected_objects):
            pos = list(obj.location)
            pos[axis_index] = first_object.location[axis_index] + (i * spacing)
            obj.location = tuple(pos)
        
        return {'FINISHED'}
    
class VIEW3D_PT_distribute_panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_distribute_panel"
    bl_label = "Distribute"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"  # Sidebar tab

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)  # X|Y|Z in one row
        row.operator("object.distribute_selected", text="X").axis = 'X'
        row.operator("object.distribute_selected", text="Y").axis = 'Y'
        row.operator("object.distribute_selected", text="Z").axis = 'Z'


def register():
    bpy.utils.register_class(DistributeSelectedOperator)
    bpy.utils.register_class(VIEW3D_PT_distribute_panel)

def unregister():
    bpy.utils.unregister_class(DistributeSelectedOperator)
    bpy.utils.unregister_class(VIEW3D_PT_distribute_panel)

if __name__ == "__main__":
    register()
