"""Example only: replace the marking action with the requested tool behavior."""
import c4d


def execute(doc):
    obj=doc.GetActiveObject()
    if obj is None:
        raise ValueError('请先选择一个对象')
    doc.StartUndo()
    try:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE,obj)
        obj.SetName(obj.GetName()+' · 山泽')
    finally:
        doc.EndUndo()
    c4d.EventAdd()
    return True
