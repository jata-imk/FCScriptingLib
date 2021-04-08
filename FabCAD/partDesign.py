import FreeCAD

import FabCAD.base
from FabCAD.utilidades import *

#FIXME Agregar metodo para seleccionar objetos
class Extrusion:
    #HACK Ver si se le puede omitir el parametro padreBase ya que a primera vista se puede obtener siempre de la base
    def extrusionAditiva(self, doc, padreBase = None, base = None, nombreExtrusion = "Pad", longitud = 10, invertido = 0, planoMedio = 0):
        self.nombre = nombreExtrusion
        self.doc = doc

        #Se extrae el string del padreBase ya que puede ser de diferentes tipos el parametro
        if padreBase is None:
            stringPadreBase = extraerString(self.doc.objetoActivo)
        else:
            stringPadreBase = extraerString(padreBase)

        #Se extrae el string de la base ya que puede ser de diferentes tipos el parametro
        stringBase = extraerString(base)

        self.doc.base.getObject(stringPadreBase).newObject('PartDesign::Pad',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringBase)
        self.base.Length = longitud
        self.base.Length2 = 100.000000
        self.base.UseCustomVector = 0
        self.base.Direction = (1, 1, 1)
        self.base.Type = 0
        self.base.UpToFace = None
        self.base.Reversed = invertido
        self.base.Midplane = planoMedio
        self.base.Offset = 0

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        return self

    #HACK Ver si se le puede omitir el parametro padreBase ya que a primera vista se puede obtener siempre de la base
    def extrusionDeVaciado(self, doc, padreBase = None, base = None, nombreExtrusion = "Pocket", longitud = 10, invertido = 0, planoMedio = 0):
        self.nombre = nombreExtrusion
        self.doc = doc

        #Se extrae el string del padreBase ya que puede ser de diferentes tipos el parametro
        if padreBase is None:
            stringPadreBase = extraerString(self.doc.objetoActivo)
        else:
            stringPadreBase = extraerString(padreBase)

        #Se extrae el string de la base ya que puede ser de diferentes tipos el parametro
        stringBase = extraerString(base)

        self.doc.base.getObject(stringPadreBase).newObject('PartDesign::Pocket',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringBase)
        self.base.Length = longitud
        self.base.Length2 = 100.000000
        self.base.Type = 0
        self.base.UpToFace = None
        self.base.Reversed = invertido
        self.base.Midplane = planoMedio
        self.base.Offset = 0

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        return self

    #HACK Ver si se le puede omitir el parametro padreBase ya que a primera vista se puede obtener siempre de la base
    def revolucionAditiva(self, doc, padreBase = None, base = None, nombreExtrusion = "Revolucion", angulo = 360, invertido = 0, planoMedio = 0 ):
        self.nombre = nombreExtrusion
        self.doc = doc

        #Se extrae el string del padreBase ya que puede ser de diferentes tipos el parametro
        if padreBase is None:
            stringPadreBase = extraerString(self.doc.objetoActivo)
        else:
            stringPadreBase = extraerString(padreBase)

        #Se extrae el string de la base ya que puede ser de diferentes tipos el parametro
        stringBase = extraerString(base)

        self.doc.contLineasReferencia += 1
        stringEjeRevolucion = f"EjeRevolucion{str(self.doc.contLineasReferencia).zfill(2)}"

        #EJE DE REVOLUCION
        self.doc.base.getObject(stringPadreBase).newObject('PartDesign::Line',stringEjeRevolucion)

        self.doc.base.getObject(stringEjeRevolucion).AttachmentOffset = FreeCAD.Placement(
            FreeCAD.Vector(0.0000000000, 0.0000000000, 0.0000000000),
            FreeCAD.Rotation(0.0000000000, 0.0000000000, 0.0000000000)
        )

        self.doc.base.getObject(stringEjeRevolucion).MapReversed = False
        self.doc.base.getObject(stringEjeRevolucion).Support = [(self.doc.base.getObject(stringBase),'Edge1')]
        self.doc.base.getObject(stringEjeRevolucion).MapPathParameter = 0.000000
        self.doc.base.getObject(stringEjeRevolucion).MapMode = 'TwoPointLine'

        #REVOLUCION
        self.doc.base.getObject(stringPadreBase).newObject('PartDesign::Revolution',nombreExtrusion)
        self.base = self.doc.base.getObject(nombreExtrusion)

        self.base.Profile = self.doc.base.getObject(stringBase)
        self.base.ReferenceAxis = (self.doc.base.getObject(stringBase), ['V_Axis'])
        self.base.Angle = angulo
        self.base.Reversed = invertido
        self.base.ReferenceAxis = (self.doc.base.getObject(stringEjeRevolucion), [''])
        self.base.Midplane = planoMedio

        self.doc.extrusiones[nombreExtrusion] = self
        self.doc.addExtern("Extrusion", nombreExtrusion)

        return self

class Cuerpo(Extrusion):
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

    #Handler
    def nuevoSketch(self, nombreDibujo, cuerpo = False, soporte = "XY_Plane", modoDeAdjuncion = "FlatFace"):
        FabCAD.nuevoSketch(doc = self.doc, nombreDibujo = nombreDibujo, cuerpo = cuerpo, soporte = soporte, modoDeAdjuncion = modoDeAdjuncion)
        
        return self

    #Handler
    def extrusionAditiva(self, padreBase = None, base = None, nombreExtrusion = 'Pad', longitud = 10, invertido = 0, planoMedio = 0):
        Extrusion().extrusionAditiva(self.doc, padreBase = None, base=base, nombreExtrusion=nombreExtrusion, longitud=longitud, invertido=invertido, planoMedio=planoMedio)
        
        return self 

    #Handler
    def extrusionDeVaciado(self, padreBase = None, base = None, nombreExtrusion = 'Pocket', longitud = 10, invertido = 0, planoMedio = 0):
        Extrusion().extrusionDeVaciado(self.doc, padreBase = None, base=base, nombreExtrusion=nombreExtrusion, longitud=longitud, invertido=invertido, planoMedio=planoMedio)
        
        return self 
    
    #Handler
    def revolucionAditiva(self, padreBase = None, base = None, nombreExtrusion = "Revolucion", angulo = 360, invertido = 0, planoMedio = 0 ):
        Extrusion().revolucionAditiva(self.doc, padreBase = None, base=base, nombreExtrusion=nombreExtrusion, angulo=angulo, invertido=invertido, planoMedio=planoMedio)
        
        return self 
