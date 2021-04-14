import FreeCAD

import FabCAD.base
from FabCAD.utilidades import extraerString

#COMPLETADO Agregar metodo para seleccionar objetos
class Documento:
    def __init__(self, nombre, etiqueta, oculto, temporal):
        """Constructor de la clase Documento"""
        #TODO Crear el nuevo documento con todos los parametros que se reciben
        FreeCAD.newDocument(nombre)

        self.nombre = nombre
        self.objetoActivo = ""
        self.contLineasReferencia = 0
        self.contPlanosReferencia = 0

        #HACK Ademas de agregar estos diccionarios preguntar si tambien se quiere que se creen 
        #atributos para poder acceder a estos objetos
        #Ejemplo doc.__dict__[nombreDelNuevoObjeto] = nuevoObjeto
        self.piezas = {}
        self.cuerpos = {}
        self.planos = {}
        self.dibujos = {}
        self.extrusiones = {}
        self.__piezas = {}
        self.__cuerpos = {}
        self.__planos = {}
        self.__dibujos = {}
        self.__extrusiones = {}

        self.base = FreeCAD.getDocument(nombre)

    #TODO Eliminar metodo
    def addExtern(self, tipo, nombre):
        if tipo == "Pieza":
            self.__piezas[nombre] = self.base.getObject(nombre)

        elif tipo == "Cuerpo":
            self.__cuerpos[nombre] = self.base.getObject(nombre)

        elif tipo == "Plano":
            self.__planos[nombre] = self.base.getObject(nombre)

        elif tipo == "Dibujo":
            self.__dibujos[nombre] = self.base.getObject(nombre)

        elif tipo == "Extrusion":
            self.__dibujos[nombre] = self.base.getObject(nombre)

    def nuevaPieza(self, nombrePieza = "SinTitulo"):
        """
        A part is a general purpose container that keeps together a group of objects so that they 
        can be moved together as a unit in the 3D view.

        The Std Part is intended to be the basic building block to create assemblies. Unlike a PartDesign Body, 
        an assembly is meant to be a collection of separate, distinguishable elements which are connected 
        in some way in the physical world.

        An open document can contain multiple Parts.
          
        Once a Part exists, other objects can be added to it with the addObject() or addObjects() 
        methods of this Part.
        """
        FabCAD.nuevaPieza(self, nombrePieza)
        return self

    def nuevoCuerpo(self, nombreCuerpo = "SinTitulo"):
        """
        A PartDesign Body is the base element to create solids shapes with the PartDesign Workbench. 
        It can contain sketches, datum objects, and PartDesign Features that help in building a single
        contiguous solid.
        
        The Body provides an Origin object which includes local X, Y, and Z axes, and standard planes. 
        These elements can be used as references to attach sketches and primitive objects.

        Do not confuse the PartDesign Body.svg PartDesign Body with the Std Part.svg Std Part. 
        The first one is a specific object used in the Workbench PartDesign.svg PartDesign Workbench, 
        intended to model a single contiguous solid by means of PartDesign Features. 
        The Std Part is a grouping object intended to create assemblies; it is not used for modelling,
        just to arrange different objects in space. Multiple bodies, and other Std Parts, 
        can be placed inside a single Std Part to create a complex assembly.
        """
        FabCAD.nuevoCuerpo(self, nombreCuerpo)
        return self

    def crearPlano(self, nombrePlano, soporte = "XY_Plane", cuerpo = False, modoDeAdjuncion = "FlatFace", offsets = [0, 0, 0], rotaciones = [0, 0, 0], invertido = False):
        FabCAD.crearPlano(self, nombrePlano, soporte, cuerpo, modoDeAdjuncion, offsets, rotaciones, invertido)
        return self

    def nuevoSketch(self, nombreDibujo, cuerpo = False, soporte = "XY_Plane", modoDeAdjuncion = "FlatFace"):
        FabCAD.nuevoSketch(doc = self, nombreDibujo = nombreDibujo, cuerpo = cuerpo, soporte = soporte, modoDeAdjuncion = modoDeAdjuncion)
        return self

    def seleccionarObjeto(self, nombreObjeto):
        """Envoltura para Documento.nombreDiccionario[nombreObjeto]"""
        dirObjetos = [self.piezas, self.cuerpos, self.planos, self.dibujos, self.extrusiones]

        for objeto in dirObjetos:
            try:        
                return objeto[nombreObjeto]
            except KeyError:
                continue

        print("No se pudo encontrar el objeto solicitado, la llave no existe...")

    def hacerActivo(self, objeto):
        """Cambia la propiedad objetoActivo de un objeto de la clase Documento"""
        self.objetoActivo = extraerString(objeto)
        return self

    def vincularObjetos(self, objetoBase, objeto):
        self.base.getObject(objeto).adjustRelativeLinks(self.base.getObject(objetoBase))
        self.base.getObject(objetoBase).addObject(self.base.getObject(objeto))
        
        #HACK Preguntar si es mejor invocar un error o dejar que solo imprima un mensaje de alerta
        print("No se encontró el objeto indicado")
        return self

    #TODO Modificar la propiedad __print__ para mostrar un mensaje personalizado al imprimir la clase
    def __setattr__(self, name, value):
        self.__dict__[name] = value