import os
import maya.cmds as cmd
import maya.mel as mel
import subprocess

try:
    import winreg
except ImportError:
    import _winreg as winreg

def alert(color = 'green', guiElement = 'VLC_record|top', message =''):
    colors = {
    'red':[1.0,0.0,0.0],
    'orange':[0.8,0.4,0.0],
    'green':[0.0,1.0,0.0],
    'blue':[0.0,0.0,1.0],
    'grey': [0.2,0.2,0.2]}
    #getColor = cmd.columnLayout(guiElement, q=True, bgc=True)
    newColor = colors.setdefault(color, [0.2,0.2,0.2])
    cmd.columnLayout(guiElement, e=True, bgc= (newColor[0],newColor[1],newColor[2]))
    cmd.refresh()
    
def _getVals():
    base = 'VLC_record|top|mainColumn|'
    w = cmd.intField('%swidth' %base, q=True, v=True)
    h = cmd.intField('%sheight'%base, q=True, v=True)
    fps = cmd.intField('%sfps'%base, q=True, v=True)
    out = cmd.textField('VLC_record|top|buttons|output', q=True, tx=True)
    return w, h, fps, out

def _get_vlc_path():
    views = [(winreg.HKEY_CURRENT_USER, 0),
             (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
             (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)]
    subkey = r'Software\VideoLAN\VLC'
    access = winreg.KEY_QUERY_VALUE
    for hroot, flag in views:
        try:
            with winreg.OpenKey(hroot, subkey, 0, access | flag) as hkey:
                value, type_id = winreg.QueryValueEx(hkey, None)
                if type_id == winreg.REG_SZ:
                    return value
        except WindowsError:
            pass
    raise SystemExit("Error: VLC not found.")
    
def _record_view():
    alert(color= 'orange', message = '')
    w, h, fps, out = _getVals()
    gMainWindow = mel.eval('$tmpVar=$gMainWindow') 
    saveWH = cmd.window(gMainWindow, q=True, wh= True)
    cmd.window(gMainWindow, edit=True, w= int(w), h=int(h), le=0, te=0)
    path = os.path.splitext(_get_vlc_path())[0]
    from os.path import expanduser
    home = expanduser("~")
    command =('screen:// :screen-fps=%s :screen-caching=50 :screen-top=0 '
    ':screen-left=0 :screen-width=%s :screen-height=%s '
    ':sout-udp-caching=0 :udp-caching=0 :rtsp-caching=0 :tcp-caching=0 '
    '--sout=#transcode{vcodec=H264,vb=1800,scale=1,fps=%s,width=%s,height=%s}'
    ':std{access=file,dst=%s}' % (fps,w,h,fps,w,h,out))
    call = '\"%s\" %s'%(path.replace('\\','/'), command)
    record = subprocess.Popen(call, shell=True)
    
class BaseWindow(object):
    def __init__(self):
        from os.path import expanduser
        self.name = 'VLC_record'
        self.windowSize = [207, 148]
        if cmd.window(self.name, exists = True):
            cmd.deleteUI(self.name)
        window = cmds.window(self.name, title = self.name, widthHeight=(self.windowSize[0], self.windowSize[1]))
        options = [("width", 1920), ("height", 1080),("fps",20)]
        cmd.columnLayout('top', adj=True)
        cmd.rowColumnLayout("mainColumn", nc=2, bgc= [0.2, 0.2, 0.2] )
        for one, val in options: 
            cmd.text(l=one, w =75)
            field = cmd.intField(one, ann = one, parent = "mainColumn", v = val)
            print field
        cmd.columnLayout('buttons', adj=True, parent = 'top', rs =5)
        print cmd.text('vlcPath', l=_get_vlc_path(), parent = 'buttons', al='left')
        print cmd.textField('output', tx=expanduser("~")+'/output.mp4', parent = 'buttons', ed = True)
        cmd.button( label='RECORD', parent = "buttons", command = '_record_view()')
        cmd.button( label='Close', parent = "buttons", command=('cmds.deleteUI(\"' + window + '\", window=True)'))
        cmd.showWindow( self.name )
        gMainWindow = maya.mel.eval('$tmpVar=$gMainWindow')
        cmd.window( self.name, edit=True, widthHeight=(self.windowSize[0], self.windowSize[1]), s=True )
     
BaseWindow()    

