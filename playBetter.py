import maya.cmds as cmd
import os
import re
import subprocess
from shutil import copy2

def defineProjDirs(proj='\\192.168.11.200\kmr'):
    dailies = '\\'+ os.path.join(proj,'check')
    if not os.path.exists(dailies):
        os.mkdir(dailies)
    return dailies

def getParentDir(path, level=1):
    for i in range(level):
        path = os.path.dirname(path)
    return path
    
def alert(color = 'green', guiElement = 'playBetter|mainColumn', message =''):
    colors = {
    'red':[1.0,0.0,0.0],
    'orange':[0.8,0.4,0.0],
    'green':[0.0,1.0,0.0],
    'blue':[0.0,0.0,1.0],
    'grey': [0.2,0.2,0.2]}
    #getColor = cmd.columnLayout(guiElement, q=True, bgc=True)
    newColor = colors.setdefault(color, [0.2,0.2,0.2])
    cmd.columnLayout(guiElement, e=True, bgc= (newColor[0],newColor[1],newColor[2]))
    cmd.text(guiElement+'|message', e=True, l= (message))
    cmd.refresh()
 

def playBetter(go = 0, scale=100.0, imgCommand = 'nul', movCommand = 'nul', imgFilePath = 'nul', firstImg = 'nul', lastImg = 'nul'): 
    fpsDict = {'ntsc': 30, 'film': 24, 'pal': 25}
    fps = fpsDict[cmd.currentUnit(q = True, t = True)]
    from subprocess import call
    width = cmds.getAttr('defaultResolution.width')
    height = cmds.getAttr('defaultResolution.height')
    imageType = '.png' 
    curPath = cmd.file(q=True, sn=True)
    fileName = cmd.file(q=True, sn=True, shn=True)
    fileBase = os.path.splitext(fileName)[0]
    curFile = os.path.splitext(curPath)[0]
    version = curFile.split('_')[-1]
    movPath = os.path.realpath(os.path.join (getParentDir(curPath, 1), 'movies', str(version)))
    imgPath = os.path.realpath(os.path.join (getParentDir(curPath, 1), 'images', str(version)))
    mayaPath = os.path.realpath(os.path.join (getParentDir(curPath, 1), 'maya'))
    for path in (movPath, imgPath, mayaPath):
        if not os.path.isdir(path): 
            os.makedirs(path)
    movFile = os.path.join (movPath, fileName.replace('.ma', '.mov'))  
    playMov = 'djv_view '+movFile+' -playback_speed '+str(fps) 
    if go==1:
        #turn off nurbs curves - replace with store and restore
        panels= []
        getPanels = cmd.getPanel(all=True)
        for panel in getPanels:
            if panel.startswith('model'):
                cmd.modelEditor(panel, e=True, nc=False)
        cmd.select(clear = True)
        cmd.evaluationManager(mode= 'parallel')
        pb = cmd.playblast(v=0,format='image', filename=os.path.join(imgPath, fileBase), sqt=0, os=True, fp=4, p=scale, c='png', wh=[width, height])
        cmd.evaluationManager(mode= 'off')
    imageFiles = []
    for file in os.listdir(imgPath):
    	if file.endswith(imageType):
    		imageFiles.append(file)
    imageFiles.sort()
    if len(imageFiles):
        firstImg = imageFiles[0].split('.')[1]	
        lastImg = imageFiles[-1].split('.')[1]		
        imgFilePath = os.path.join (imgPath,fileBase+'.'+firstImg+'-'+lastImg+'.png')
        movCommand = 'djv_convert '+imgFilePath+' '+movFile+' -resize '+str(width)+' '+str(height)+' -default_speed '+str(fps)
        imgCommand = 'djv_view '+os.path.join(imgPath, imageFiles[0])+' -playback_speed '+ str(fps)
        if go==2:
            subprocess.Popen(imgCommand, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True )
        if go==3:
            subprocess.call(movCommand, shell=True )
        elif go==4:
            subprocess.Popen(playMov, stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True )
        elif go==5:
            dailies = os.path.normpath(defineProjDirs('X:/'))
            if os.path.isfile(movFile): 
                copy2(movFile, dailies)      
    if not go:
        for all in curPath, curFile, movPath, movFile, imgPath, imageFiles, movCommand, imgCommand, playMov:
            print all
    
def playBetterGUI():
    vals = [0,0,0,0,0]
    options = ["playblast", "playImages","convertToMovie","playMovie", "copyToDailies"]
    window = 'playBetter'
    for one in range (0,5):
        go = one+1
        checkbox = '%s|%s|%s' %(window, 'mainColumn', options[one])
        if (cmd.checkBox(checkbox, q = True, v = True)):
            alert(color= 'orange', message = ('Please Wait, doing '+options[one]))  
            playBetter(go)
    alert(color= 'grey', message = '')  


class BaseWindow(object):
    def __init__(self):
        self.name = 'playBetter'
        self.windowSize = [207, 148]
        if cmd.window(self.name, exists = True):
            cmd.deleteUI(self.name)
        window = cmds.window(self.name, title = self.name, widthHeight=(self.windowSize[0], self.windowSize[1]))
        #Type your UI code here
        options = ["playblast", "playImages","convertToMovie","playMovie", "copyToDailies"]
        cmd.columnLayout("mainColumn", adjustableColumn=True, bgc= [0.2, 0.2, 0.2] )
        for one in options:
            check = 1
            if one == "playImages": 
                check = 0             
            cmd.checkBox(one, l = one, parent = "mainColumn", v = check)
        cmd.text('message', l='')
        cmd.button( label='PlayBetter', parent = "mainColumn", command = 'playBetterGUI()')
        cmd.button( label='Close', parent = "mainColumn", command=('cmds.deleteUI(\"' + window + '\", window=True)') )
        cmd.showWindow( self.name )
        gMainWindow = maya.mel.eval('$tmpVar=$gMainWindow')
        cmd.window( self.name, edit=True, widthHeight=(self.windowSize[0], self.windowSize[1]) )
    
BaseWindow()
   
