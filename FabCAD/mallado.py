import FreeCAD, Part, Mesh, MeshPart

from FabCAD.utilidades import extraerStringPadre, extraerString

class Mallas:
    def exportarEnSTL(self, cuerpo, rutaFichero = "C:/FabCAD/obj.stl"):
        doc         =   FreeCAD.getDocument(cuerpo.doc.nombre)

        doc.recompute()

        mesh        =   doc.addObject("Mesh::Feature","Mesh")
        part        =   doc.getObject(extraerStringPadre(cuerpo))
        shape       =   Part.getShape(part,extraerString(cuerpo))
        mesh.Mesh   =   MeshPart.meshFromShape(Shape=shape,Fineness=4,SecondOrder=0,Optimize=1,AllowQuad=0)

        mesh.Mesh.write(rutaFichero)