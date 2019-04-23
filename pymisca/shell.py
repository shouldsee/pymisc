import os,sys
import re
import subprocess
import shutil
import StringIO
import warnings


import pymisca.io
##### Shell util
import tempfile
import subprocess
import re
import collections
# import pymisca.header as pyheader

pysh=sys.modules[__name__]


def job__shellexec(d):
    try:
        d['result'] = shellexec(d['CMD'])
        d['suc'] = True
    except:
        d['result'] = None
        d['suc'] = False
    return d

def dir__curr(silent = 1):
    res = shellexec('pwd -L',silent=silent).strip()
    return res


def nTuple(lst,n,silent=1):
    """ntuple([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]
    
    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.
    
    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    """
    if not silent:
        L = len(lst)
        if L % n != 0:
            print '[WARN] nTuple(): list length %d not of multiples of %d, discarding extra elements'%(L,n)
    return zip(*[lst[i::n] for i in range(n)])

def quote(s):
    return u'"%s"'%s

def xargsShellCMD(CMD, lst):
# def getHeaders(lst):
    with tempfile.TemporaryFile() as f:
        f = pymisca.io.unicodeIO(handle=f)
        f.write(u' '.join(map(quote,lst)))
        f.seek(0)
        p = subprocess.Popen('xargs {CMD}'.format(**locals()),stdin=f,stdout=subprocess.PIPE,shell=True)
        res = p.communicate()[0]
    return res
def getHeaders(lst):
    res = xargsShellCMD('head -c2048',lst)
    lst = re.split('==> *(.+) *<==',res)[1:]
    lst = [x.strip() for x in lst] 
    res = collections.OrderedDict(nTuple(lst,2))
    return res
def getTails(lst):
    res = xargsShellCMD('tail -c2048',lst)
    lst = re.split('==> *(.+) *<==',res)[1:]
    lst = [x.strip() for x in lst] 
    res = collections.OrderedDict(nTuple(lst,2))
    return res
def getSizes(lst):
    res = xargsShellCMD('du',lst)
    res = collections.OrderedDict([x.split('\t')[::-1] for x in res.splitlines()])
    return res
########

def dict2kwarg(params):
    s = ' '.join('--%s %s' % (k,v ) for k,v in params.items())
    return s



def file__cat(files,ofname='temp.txt',silent=1,bufsize=1024*1024*10):
    with open(ofname,'wb') as wfd:
        for f in files:
            with open(f,'rb') as fd:
                shutil.copyfileobj(fd, wfd, bufsize)    
    return ofname

def file__header(fname,head = 10,silent=1,ofname = None):
    if ofname == 'auto':
        ofname = fname + '.head%d'%head
    cmd = 'head -n{head} {fname}'.format(**locals())
    if ofname is not None:
        cmd = cmd + '>{ofname}'.format(**locals())
    res = shellexec(cmd, silent=silent)
    res = pymisca.io.unicodeIO(buf=res)
    if ofname is not None:
        return ofname
    else:
        return res
   

def real__dir(fname=None,dirname=None,mode=0777):
    if dirname is None:
        assert fname is not None
        dirname = os.path.dirname(fname)
    else:
        assert fname is None
        
    if not os.path.exists(dirname) and dirname!='':
        os.makedirs(dirname,mode=mode)
    return dirname

def symlink(fname,ofname = None,
            relative = 0,
            silent=1,debug=0,**kwargs):
#     if ODIR is None
    if not os.path.exists(fname):
        warnings.warn('trying to symlink non-existent file:%s'%fname)
    if ofname is None:
        ofname = './.'
    ODIR = real__dir(fname=ofname)
    if relative:
        fname = os.path.abspath(fname)
    else:
        fname = os.path.relpath(fname,ODIR)
    
        
    cmd = 'ln -sf {fname} {ofname}'.format(**locals())
    shellexec(cmd,silent=silent,debug=debug)
    return ofname
def envSource(sfile,silent=0,dry=0,
              executable=None,outDict=None):
    if outDict is None:
        outDict = os.environ
#     import os
    '''Loading environment variables after running a script
    '''
    command = 'source %s&>/dev/null ;env -0 ' % sfile
    # print command
#     res = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=1)
    res = shellexec(command,silent=silent,executable=executable)
    for line in res.split('\x00'):
        (key, _, value) = line.strip().partition("=")
        if not silent:
            print key,'=',value
        if not dry:
            outDict[key] = value
    return outDict

def real__shell(executable=None):
    if executable is None:
        executable = os.environ.get('SHELL','/bin/bash')
    return executable

def silentShellexec(cmd,silent=1,**kwargs):
    res = shellexec(cmd=cmd, silent=silent,**kwargs)
    return res

def shellexec(cmd,debug=0,silent=0,executable=None,
              encoding='utf8',error='raise',
              shell = 1,
              **kwargs
             ):
    executable = real__shell(executable)
    if silent != 1:
        buf = '[CMD]{cmd}\n'.format(**locals())
        if hasattr(silent,'write'):
            silent.write(buf)
        else:
            sys.stdout.write(buf)
#         print (cmd)
    if debug:
        return 'dbg'
    else:
        try:
            res = subprocess.check_output(cmd,shell=shell,
                                         executable=executable,
                                         **kwargs)

#             p.stdin.close()
            if encoding is not None:
                res=  res.decode(encoding)
            
            res = res.strip()

        except subprocess.CalledProcessError as e:
            if error=='raise':
                raise RuntimeError(
                    "command '{}' return with error (code {}): {}\
                ".format(e.cmd, e.returncode, e.output))
            elif error=='ignore':
                
                res = 'FAIL'
                
                
    
         #### allow name to be returned
        return res
    
def getMD5sum(fname,silent=1):
    res = shellexec('md5sum %s'%fname,silent=silent)[:32]
    return res

def pipe__getResult(p, input = None, encoding='utf8', check=False):
    res = p.communicate(input=input)[0]
    suc = p.returncode==0
    if encoding is not None:
        res = res.decode(encoding)
        
    if not check:
        return suc, res
    if check:
        suc = suc & (res!='')
        assert suc,'return code {p.returncode} != 0 or output is empty' .format(**locals())
        return res
    
def pipe__getSafeResult(p,check=True,**kw):
    return pipe__getResult(p,check=check,**kw)

def shellpopen(cmd,
                 stdin=subprocess.PIPE,
                 stdout=subprocess.PIPE,
               debug=0,silent=0,executable=None,
                 shell = 1,
                 bufsize= 1,
                 **kwargs):
    executable = real__shell(executable)
    if not silent:
        sys.stdout.write(u'[CMD] %s\n'%cmd)
    if debug:
        return 'dbg'
    else:
        p = subprocess.Popen(
                     cmd,
                     shell=shell,
                     bufsize=bufsize,
                     executable=executable,
                     stdin=stdin,
                     stdout = stdout,

                    **kwargs)
        return p
#         res = p.communicate()[0]
#         return res,p.returncode




def pipe__cat(p=None,fname= None, **kwargs):
    if fname is None:
        fname = '-' 
    p = pysh.shellpopen('cat "{fname}"'.format(**locals()), **kwargs)
    return p



def pipe__wig2bed(p = None, stdin=None, fname = '-', ):
    assert fname is not None
    if p is not None:        
#         stdin = p.stdout
        pass
    else:
        p = pipe__cat(fname=fname)
    p = pysh.shellpopen('convert2bed -i wig',  stdin=p.stdout)
    return p


class ShellPipe(list):
    def __init__(self, 
                 p0 = None, 
                 fname=None):
        super(ShellPipe,self).__init__()
        if p0 is None:
            p0 = pysh.pipe__cat(fname=fname)
            cmd= 'cat %s'%fname
        else:
            assert fname is None,'conflict "fname" and "p0"'
            cmd = '' ### cannot capture cmd from an existing pipe
        self.p = self.p0 = p0
        self.addElement(p=self.p,
                        cmd=cmd)
        self.stdin = self.p0.stdin
        
    def addElement(self, p,cmd):
#         self.append(collections.OrderedDict(cmd=cmd))
        self.append(collections.OrderedDict(p=p, cmd=cmd))
        
    def checkResult(self, check=True, cmd='head'):
        self.p0.stdin.close()
        if cmd:
            self.chain(cmd,)
        res =  pysh.pipe__getResult( self.p, check=check)            
        return res
    
    def readIter(self,it,
                 delay = False,
                 lineSep = '',
#                  mapper=map
                ):
        it = (u'%s%s'%(x,lineSep) for x in it)
        
        if delay:
            mapper = itertools.imap()
        else:
            mapper = map
        return mapper(self.p0.stdin.write,it)

    def chain(self, cmd, stdin=None,**kw):
        if stdin is None:
            stdin = self.p.stdout
        self.p = pysh.shellpopen(cmd=cmd, stdin=stdin,**kw)
        self.addElement(p=self.p,cmd=cmd)


# shellexec = shellopen