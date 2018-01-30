import os
import getpass
import maya.cmds as cmd

def makeAsset():
    nodes = []
    root = cmd.group(em = True, name = 'root')
    for one in ['anim', 'setup', 'render']:
        node = cmd.group(p = root, em = True, name = '%s_GP' % (one))
        nodes.append(node)
    ctlGP = cmd.group(em = True, p = nodes[0], name = 'CTL_GP')     
    CTL = cmd.circle(nr= (0, 1, 0), name = 'CTL')
    cmd.parent(CTL[0], ctlGP)
    lib = {'guts':1,'meshDisplay':2}
    for key, val in lib.iteritems() :
        cmd.addAttr(ctlGP, k = True, ln= key, at = 'long', min = 0, max = val, dv = 0)
    cmd.connectAttr('%s.guts' % ctlGP, '%s.%s' % (nodes[1], 'v'))
    for i in ['overrideEnabled', 'overrideDisplayType']:
        cmd.connectAttr('%s.meshDisplay' % ctlGP, '%s.%s' % (nodes[2], i))
makeAsset()
