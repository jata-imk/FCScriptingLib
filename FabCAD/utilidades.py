#Modulo que contiene funciones para facilitar el desarrollo de el paquete FabCAD
def extraerString(dato):
    if type(dato) is str:
        return dato
    try:
        return dato.nombre
    except AttributeError:
        return dato.Name

def extraerStringPadre(dato):
    try:
        return dato.padre
    except AttributeError:
        return str(dato.Parents[0])[1:-1].split(",")[1].strip().strip("'").split(".")[0]
    
def vincular(objeto, objetoBase):
    if objetoBase.objetoActivo:
        objetoBase.base.getObject(objeto).adjustRelativeLinks(objetoBase.base.getObject(objetoBase.objetoActivo))
        objetoBase.base.getObject(objetoBase.objetoActivo).addObject(objetoBase.base.getObject(objeto))

#Modulos a importan cuando se haga un from xxx import __all__ (Convención)
__all__ = ["extraerString", "extraerStringPadre", "vincular"]