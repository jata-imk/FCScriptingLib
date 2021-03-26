import FreeCAD

from FabCAD.utilidades import *

#FIXME Agregar metodo para seleccionar objetos
class Cuerpo:
    def nuevoCuerpo(self, doc, nombreCuerpo):
        """Constructor de la clase Parte 3D"""
        self.doc = doc
        self.nombre = nombreCuerpo

        self.doc.base.addObject('PartDesign::Body',self.nombre)
        self.doc.cuerpos[self.nombre] = self
        self.doc.addExtern("Cuerpo", self.nombre)
        self.base = self.doc.base.getObject(nombreCuerpo)

        vincular(self.nombre, doc)

        self.doc.objetoActivo = nombreCuerpo

        return self

    def crearPlano(self, nombrePlano, soporte = "XY_Plane", cuerpo = False, modoDeAdjuncion = "FlatFace", offsets = [0, 0, 0], rotaciones = [0, 0, 0], invertido = False):
        #Lo que se necesita para seleccionar el cuerpo es un string, sin embargo este metodo admite que se 
        #pase como parametro un objeto tipo 'Body', para lo cual se extrae el string de su nombre
        
        if cuerpo is False:
            stringCuerpo = self.doc.objetoActivo
        else:
            stringCuerpo = extraerString(cuerpo)

        #Se crea y agrega el plano como una propiedad del objeto
        #HACK Probar de en lugar de agregar directamente al cuerpo activo primero crear y luego vincular
        self.doc.base.getObject(stringCuerpo).newObject('PartDesign::Plane', nombrePlano)
        self.doc.planos[nombrePlano] = self
        self.doc.addExtern("Plano", nombrePlano)
        self.base = self.doc.base.getObject(nombrePlano)
        
        #Cuerpo del metodo
        self.base.AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(offsets[0], offsets[1], offsets[2]),
            FreeCAD.Rotation(rotaciones[0], rotaciones[1], rotaciones[2])
        )
        self.base.MapReversed = invertido
        self.base.Support = [(self.doc.base.getObject(soporte),'')]
        self.base.MapPathParameter = 0.000000
        self.base.MapMode = modoDeAdjuncion

        return self

class Pieza(Cuerpo):
    def nuevaPieza(self, doc, nombrePieza):
        """Constructor de la clase Parte 3D"""
        self.doc = doc
        self.nombre = nombrePieza

        self.doc.base.addObject('App::Part',self.nombre)
        self.doc.piezas[self.nombre] = self
        self.doc.addExtern("Pieza", self.nombre)
        self.base = self.doc.base.getObject(nombrePieza)

        self.doc.objetoActivo = nombrePieza

        return self

class Parte3D(Pieza):
    def __init__(self, doc):
        """Constructor de la clase Parte 3D"""
        self.doc = doc
        self.nombre = ""

    #Handler
    def nuevaPieza(self, nombrePieza):
        Pieza().nuevaPieza(self.doc, nombrePieza)

        return self
    
    #Handler
    def nuevoCuerpo(self, nombreCuerpo):
        Cuerpo().nuevoCuerpo(self.doc, nombreCuerpo)

        return self