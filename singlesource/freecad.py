# Copyright 2016, Jon Nordby <jononor@gmail.com>. Licensed LGPLv2+ & MIT

"""
exportProject:

Exports all files in document which has names like "mypart [dxf]" or "otherpart[stl,step]"
to individual files in a export directory. Default prefix: 'export/$project-'
Can be ran both as a macro from the FreeCAD UI and as a script on commandline.
"""

# TODO: support some kind of preview. Maybe using the recent camera macros?

import sys, os
import re
partTypeRegex = re.compile(r'^(.*)\[([,\w]+)\].*$')

import FreeCAD

def exportMesh(objs, p):
    import Mesh
    Mesh.export(objs, p)
def exportDxf(objs, p):
    import importDXF
    importDXF.export(objs, p)
def exportStep(objs, p):
    # XXX: will overwrite file if called with multiple args.. Last write wins
    for o in objs:
        shape = o.Shape
        shape.exportStep(p)

# TODO: support CAM and post-processors like: rml, spb
supportedTypes = {
    'stl': exportMesh,
    'obj': exportMesh,
    'step': exportStep,
    'dxf': exportDxf,
}

def extractTypes(label):
    match = re.search(partTypeRegex, label)
    if match:
        types = match.group(2).split(',')
        part = match.group(1)
    else:
        part = label
        types = []
    return [part, types]


def exportDocument(doc, exportdir):
    exported = []
    if not os.path.exists(exportdir):
        os.makedirs(exportdir)

    docname = os.path.splitext(os.path.basename(doc.FileName))[0]
    for obj in doc.Objects:
        partname, types = extractTypes(obj.Label)
        #print "obj %s %s" % (obj.Label, types)
        for t in types:
            exporter = supportedTypes[t]
            filename = "%s-%s.%s" % (docname, partname, t)
            filepath = os.path.join(exportdir, filename)
            exporter([obj], filepath)
            exported.append(filename)

    return exported


def fileListing(files):
    return '\n'.join("\t"+f for f in files)

def main():
    projectfile = sys.argv[1]
    doc = FreeCAD.openDocument(projectfile)

    if len(sys.argv) >= 3:
        exportdir = sys.argv[2]
    else:
        docdir = os.path.dirname(doc.FileName)
        exportdir = os.path.join(docdir, 'export/')

    print 'Opening project', projectfile
    files = exportDocument(doc, exportdir)
    print "Exported %d files to '%s'\n%s" % (len(files), exportdir, fileListing(files))

