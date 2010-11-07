"""
Project: pyGTKtalog
Description: pyGTK common utility functions
Type: tility
Author: Roman 'gryf' Dobosz, gryf73@gmail.com
Created: 2010-11-07 13:30:37
"""

def get_tv_item_under_cursor(treeview):
    """
    Get item (most probably id of the row) form tree view under cursor.
    Arguments:
        @treeview - gtk.TreeView
    Returns:
        Item in first column of TreeModel, which TreeView is connected with,
        None in other cases
    """
    path, column = treeview.get_cursor()
    if path and column:
        model = treeview.get_model()
        tm_iter = model.get_iter(path)
        item_id = model.get_value(tm_iter, 0)
        return item_id
    return None

