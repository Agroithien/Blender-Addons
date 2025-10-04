bl_info = {
    "name": "Move Objects to Named Subcollections",
    "author": "Agroithien",
    "version": (1, 2),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Item Tab",
    "description": "Moves selected objects (and their children) into subcollections named after themselves, keeping them under the same parent collection.",
    "category": "Object",
}

import bpy


def get_all_children(obj):
    """Recursively get all children of an object."""
    children = []
    for child in obj.children:
        children.append(child)
        children.extend(get_all_children(child))
    return children


class OBJECT_OT_move_to_named_subcollections(bpy.types.Operator):
    bl_idname = "object.move_to_named_subcollections"
    bl_label = "Move to Named Subcollections"
    bl_description = "Move selected objects (and their children) into subcollections named after themselves within the same parent collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        moved_count = 0

        for obj in selected_objects:
            # include the object + its hierarchy
            # include the object + its hierarchy
            objects_to_move = [obj] + get_all_children(obj)
            collection_name = obj.name

            # Get the object's current parent collection (first one, if multiple)
            if not obj.users_collection:
                self.report({'WARNING'}, f"Object '{obj.name}' is not in any collection.")
                continue

            parent_collection = obj.users_collection[0]

            # Check if subcollection exists
            subcollection = parent_collection.children.get(collection_name)
            if not subcollection:
                subcollection = bpy.data.collections.new(collection_name)
                parent_collection.children.link(subcollection)

            # Move all objects in the hierarchy
            for o in objects_to_move:
                # Unlink only from this parent collection (not all)
                if parent_collection in o.users_collection:
                    parent_collection.objects.unlink(o)

                # Link to subcollection (avoid double-linking)
                if o.name not in subcollection.objects:
                    subcollection.objects.link(o)

                moved_count += 1

        self.report({'INFO'}, f"Moved {moved_count} object(s) (including children) to name-based subcollections.")
        return {'FINISHED'}


class OBJECT_PT_named_subcollections_panel(bpy.types.Panel):
    bl_label = "Named Subcollections"
    bl_idname = "OBJECT_PT_named_subcollections_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.move_to_named_subcollections", icon='OUTLINER_COLLECTION')


classes = (
    OBJECT_OT_move_to_named_subcollections,
    OBJECT_PT_named_subcollections_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
