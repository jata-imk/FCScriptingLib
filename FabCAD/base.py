""" Modulo que contiene las funciones base del paquete FabCAD"""

from FabCAD import documento, partDesign, dibujo

#Handler for the FabCAD.documento.Documento class
class Documento(documento.Documento):
     pass

#Handler for the FabCAD.partDesign.Parte3D class
class Parte3D(partDesign.Parte3D):
     pass

#Handler for the FabCAD.dibujo.Dibujo class
class Dibujo(dibujo.Dibujo):
     pass
     
def nuevoDocumento(nombre = "SinTitulo", etiqueta = None, oculto = False, temporal = False):
     """Crea un nuevo documento con el nombre dado\n\n
     
     Parametros:\n
     nombre: Nombre unico para el documento el cual es verificado automaticante por el programa\n
     etiqueta: Etiqueta opcional para identificar el documento que puede ser modificado por el usuario\n
     oculto: Parametro para elegir si se quiere ocultar la vista 3d del nuevo documento\n
     temporal: Marca el documento como temporal, asi que este no será guardado"""

     return Documento(nombre, etiqueta, oculto, temporal)

def nuevaPieza(doc, nombrePieza):
     return Parte3D(doc).nuevaPieza(nombrePieza)

def nuevoCuerpo(doc, nombreCuerpo):
     return Parte3D(doc).nuevoCuerpo(nombreCuerpo)

def crearPlano(doc, nombrePlano, soporte = "XY_Plane", cuerpo = False, modoDeAdjuncion = "FlatFace", offsets = [0, 0, 0], rotaciones = [0, 0, 0], invertido = False):
     return Parte3D(doc).crearPlano(nombrePlano, soporte, cuerpo, modoDeAdjuncion, offsets, rotaciones, invertido)

def extrusionAditiva(doc, croquis = None, nombreExtrusion = "Pad", longitud = 10, invertido = 0, planoMedio = 0):
     return Parte3D(doc).extrusionAditiva(croquis, nombreExtrusion, longitud, invertido, planoMedio)

def extrusionDeVaciado(doc, croquis = None, nombreExtrusion = "Pocket", longitud = 10, invertido = 0, planoMedio = 0):
     return Parte3D(doc).extrusionDeVaciado(croquis, nombreExtrusion, longitud, invertido, planoMedio)

def revolucionAditiva(doc, croquis = None, nombreExtrusion = "Revolucion", angulo = 360, invertido = 0, planoMedio = 0):
     return Parte3D(doc).revolucionAditiva(croquis, nombreExtrusion, angulo, invertido, planoMedio)

def revolucionDeVaciado(doc, croquis = None, nombreExtrusion = "RevDeVaciado", angulo = 360, invertido = 0, planoMedio = 0):
     return Parte3D(doc).revolucionDeVaciado(croquis, nombreExtrusion, angulo, invertido, planoMedio)

def recubrir(doc, croquisInicial, croquisParaRecubrir, nombreExtrusion = "extrusionRecubierta"):
     return Parte3D(doc).recubrir(croquisInicial=croquisInicial, croquisParaRecubrir=croquisParaRecubrir, nombreExtrusion=nombreExtrusion)

def recubrirCorte(doc, croquisInicial, croquisParaRecubrir, nombreExtrusion = "corteRecubierto"):
     return Parte3D(doc).recubrirCorte(croquisInicial=croquisInicial, croquisParaRecubrir=croquisParaRecubrir, nombreExtrusion=nombreExtrusion)

def salienteConducida(doc, croquisPerfil, croquisGuia, nombreExtrusion='salienteConducida'):
     return Parte3D(doc).salienteConducida(croquisPerfil=croquisPerfil, croquisGuia=croquisGuia, nombreExtrusion=nombreExtrusion)


def corteConducido(doc, croquisPerfil, croquisGuia, nombreExtrusion='corteConducido'):
     return Parte3D(doc).corteConducido(croquisPerfil=croquisPerfil, croquisGuia=croquisGuia, nombreExtrusion=nombreExtrusion)

#FIXME No permitir hacer croquis si no pertenecen a un cuerpo o pieza
def nuevoSketch(nombreDibujo, doc, cuerpo = False, soporte = "XY_Plane", modoDeAdjuncion = "FlatFace"):
     return Dibujo(nombreDibujo, doc, cuerpo, soporte, modoDeAdjuncion)


#TODO implementar lista de ultimos objetos creados para poder encadenar los metodos de clase
#TODO Añadir ejemplos de uso en la libreta de Jupyter de los metodos del Sketcher

#Modulos a importan cuando se haga un from xxx import __all__ (Convención)
__all__ = ["nuevoDocumento", "nuevaPieza", "nuevoCuerpo", "crearPlano", "extrusionAditiva", "extrusionDeVaciado", "revolucionAditiva", "revolucionDeVaciado", "recubrir", "recubrirCorte", "salienteConducida", "corteConducido", "nuevoSketch"]