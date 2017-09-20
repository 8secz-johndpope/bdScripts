import maya.cmds as mc
import traceback


#	code by Kris Andrews
def repeatable(function):
    '''A decorator that will make commands repeatable in maya'''

    def decoratorCode(*args, **kwargs):
        functionReturn = None
        argString = ''
        if args:
            for each in args:
                argString += str(each) + ', '

        if kwargs:
            for key, item in kwargs.iteritems():
                argString += str(key) + '=' + str(item) + ', '

        commandToRepeat = 'python("' + __name__ + '.' + function.__name__ + '(' + argString + ')")'

        functionReturn = function(*args, **kwargs)
        try:
            mc.repeatLast(ac=commandToRepeat, acl=function.__name__)
        except:
            pass

        return functionReturn

    return decoratorCode


#	based on code by Kris Andrews 
def undoable(function):
    '''A decorator that will make commands undoable in maya'''

    def decoratorCode(*args, **kwargs):
        mc.undoInfo(openChunk=True)
        functionReturn = None
        try:
            functionReturn = function(*args, **kwargs)
            mc.undoInfo(closeChunk=True)

        except:
            mc.undoInfo(closeChunk=True)
            print(traceback.format_exc())

            #	throw the actual error
            mc.error()

    return decoratorCode


class undo_chunk(object):
    def __enter__(self):
        mc.undoInfo(openChunk=True)

    def __exit__(self, *_):
        mc.undoInfo(closeChunk=True)
