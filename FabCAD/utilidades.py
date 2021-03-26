#Modulo que contiene funciones para facilitar el desarrollo de el paquete FabCAD
def extraerString(dato):    
    if type(dato) is str:
        return dato
    try:
        return dato.nombre
    except:
        return dato.Name
    
def vincular(objeto, objetoBase):
    if objetoBase.objetoActivo:
        objetoBase.base.getObject(objeto).adjustRelativeLinks(objetoBase.base.getObject(objetoBase.objetoActivo))
        objetoBase.base.getObject(objetoBase.objetoActivo).addObject(objetoBase.base.getObject(objeto))