import os,sys,re,glob
import warnings
import itertools,functools
import pymisca.shell as pysh
import inspect
import sys,inspect
import operator
import collections
import sys
import types
_this_mod = sys.modules[__name__]

import base64

import json
import ast


import hashlib
def file__md5(fname):
    '''
    Source: https://stackoverflow.com/a/3431838/8083313
    '''
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def ppJson(d,**kw):
    '''
    Pretty print a dictionary
    '''
    s = json.dumps(d,indent=4, sort_keys=True,**kw)
    return s
def dppJson(d,default=repr,**kw):
    return ppJson(d,default=default,**kw)


def rgetattr(obj,attr):
    _this_func = rgetattr
    sp = attr.split('.',1)
    if len(sp)==1:
        l,r = sp[0],''
    else:
        l,r = sp
        
    obj = getattr(obj,l)
    if r:
        obj = _this_func(obj,r)
    return obj

def rgetattr_dft(obj,attr,dft):
    _this_func = rgetattr_dft
    sp = attr.split('.',1)
    if len(sp)==1:
        l,r = sp[0],''
    else:
        l,r = sp
        
    obj = getattr(obj, l, dft)
    if r:
        obj = _this_func(obj, r, dft)
    return obj       

# def frame__relativeFile(frame=None):
#     frame = frame__default(frame)
#     return name__lookup('__file__',frame=frame)

def frame__relativeFile(FNAME, frame=None):
    frame = frame__default(frame)
    __file__ = name__lookup('__file__',frame=frame,level=1)
    return os.path.join( os.path.dirname(os.path.realpath(__file__)), FNAME)



def frame__default(frame=None):
# def frame__parent(frame=None):
    if frame is None:
        frame = inspect.currentframe().f_back.f_back ####parent of caller by default
    else:
        pass    
    return frame
        
    
def ast__eval(expr, level=-1,kwargs = {},frame=None,dbg=0):
    
    node0 = ast.parse(expr,mode='eval',)
    frame = frame__default(frame)
    
    for node in ast.walk(node0):
        if isinstance(node, ast.Name):
            if node.id in kwargs:
                pass
            else:
                kwargs[node.id] = name__lookup( node.id,
                                               level=level+1 if level >=0 else -1,
                                              frame=frame)
    
    try:
        if dbg:
            print(json.dumps(kwargs.keys(),indent=4,default=repr))
        res = eval(compile(node0,'<ast>','eval'),kwargs)
    except Exception as e:
        assert 0,"Expr:%s.Error:%r"%(expr,e)
    finally:
        del frame
        del kwargs
        
    return res
        
def assertTrue(expr,msg='DefaultError'):
    assert expr==True,msg        
        
class mList(list):
    '''
    A list decorated with methods
    '''
    def map(self,f,*a):
        return map(f, self, *a)

def file__png__toHtmlSrc(FNAME):
    data_uri = base64.b64encode(open( FNAME, 'rb').read()).decode('utf-8')
    src = "data:image/png;base64,{0}".format(data_uri)
    return src
def file__image__toHtmlSrc(FNAME):
    if FNAME.endswith('.png'):
        src = file__png__toHtmlSrc(FNAME)
    else:
        assert 0,(FNAME,)
#     data_uri = base64.b64encode(open( FNAME, 'rb').read()).decode('utf-8')
#     src = "data:image/png;base64,{0}".format(data_uri)
    return src


def get__anonModuleName():
    i = 0
    while True:
        i += 1
        MODULE_NAME = "__anonymous__%d"%i
        if MODULE_NAME not in sys.modules:
            break
    return MODULE_NAME

def list__toR__vector(lst):
    res = "c(%s)"%(",".join(['"%s"'%x for x in lst]))
    return res

def list__call(lst,*args,**kwargs):
    _this = list__call
    if callable(lst):
        return lst(*args,**kwargs)
    elif isinstance(lst,list) or isinstance(lst,tuple):
        return type(lst)(_this(x,*args,**kwargs) for x in lst)
    else:
        return lst

def stringList__flatten(lst,strict=1,):
    _this = stringList__flatten
    if isinstance(lst,basestring):
        return [lst]
    elif isinstance(lst,list) or isinstance(lst,tuple):
        lst = sum((_this(x,strict) for x in lst),[])
        return lst
    else:
        if strict:
            assert 0,(type(lst),repr(lst))
        return [repr(lst)]

def sanitise__argName(s):
# def funcArgName_sanitised(s,):
    return re.sub("[^a-zA-Z0-9_]",'_',s)

def PlainFunction(f):
    f._plain =True
    return f
def is__plainFunction(f):
    return getattr(f,'_plain',False)

def func__setAs(other, setter, name=None):
    class temp():
        _name = name
    def dec(func):
#         functools.wraps(f)
        if temp._name is None:
            temp._name = func.__name__

        setter(other, temp._name, func)
        return func
    return dec    
def func__setAsAttr(other, *a):
    return  func__setAs(other, setattr,*a)
setAttr = func__setAsAttr

def func__setAsItem(other, *a):
    return  func__setAs(other, operator.setitem,*a)
setItem = func__setAsItem

from collections import Counter,OrderedDict
class OrderedCounter(Counter, OrderedDict):
    '''
    SOURCE:https://docs.python.org/3.4/library/collections.html?highlight=ordereddict#ordereddict-examples-and-recipes
    '''
    pass

def xml__tag(tag,attrs={}):
    def func(x,tag=tag,attrs=attrs):
        res = [tag]
        for k,v in attrs.items():
            res.append('%s="%s"'%(k,v))
        stag = ' '.join(res)
        s = u"<{stag}>{x}</{tag}>".format(**locals())
        return s
    return func

@setAttr(_this_mod,"q")
@setAttr(_this_mod,"quote")
def str__quote(s,q1='"'):
    q2 = q1[::-1]
    return "%s%s%s"%(q1,s,q2)


@setAttr(_this_mod, "renameVars")
def func__renameVars(varnames=['xxx','y']):
    def dec(f,varnames=varnames):
        # code = copy.copy(f.__code__)
        code = f.__code__
        if isinstance(varnames, list):
            _varnames = tuple(map(sanitise__argName,varnames))
        if isinstance(varnames, collections.MutableMapping):
            _varnames = tuple( sanitise__argName( varnames.get(x,x) ) 
                              for x in code.co_varnames[:])

        assert len(_varnames) == len(code.co_varnames),(_varnames, code.co_varnames)

        _code = types.CodeType(
            code.co_argcount,
            code.co_nlocals,
            code.co_stacksize,
            code.co_flags,
            code.co_code,
            code.co_consts,
            code.co_names,
            _varnames,  #     code.co_varnames,
            code.co_filename,
            code.co_name,
            code.co_firstlineno,
            code.co_lnotab,
            code.co_freevars,
            code.co_cellvars,
        )
        g = types.FunctionType( _code, 
                               f.__globals__, 
                               f.__name__, 
                               f.__defaults__, 
                               f.__closure__)
        g._parent = f
        g._native= False
        return g
    return dec
def func__getNative(f):
    while True:
        if not getattr(f,'_native',True):
            f = getattr(f,'_parent')
        else:
            break
    return f

#     return 
# def func__setAsAttr(other, name=None,setter=setattr):
#     class temp():
#         _name = name
#     def dec(func):
# #         functools.wraps(f)
#         if temp._name is None:
#             temp._name = func.__name__

#         setter(other, temp._name, func)
#         return func
#     return dec
# setAttr = func__setAsAttr

def func__setAsItem(other,name = None):
    
    pass
# _devnull
class Suppresser:
    devnull = open(os.devnull, "w")
    def __init__(self, suppress_stdout=False, suppress_stderr=False):
        self.suppress_stdout = suppress_stdout
        self.suppress_stderr = suppress_stderr
        self.original_stdout = None
        self.original_stderr = None
#         self.devnull = 

    def _switch(self, toSuppress=None):
        if toSuppress is None:
            toSuppress = self.original_stdout is None
        if self.suppress_stdout:
            if toSuppress:
                if sys.stdout is not self.devnull:
                    self.original_stdout, sys.stdout = sys.stdout, self.devnull
            else:
                if sys.stdout is self.devnull:
                    self.original_stdout, sys.stdout = None, self.original_stdout

        if self.suppress_stderr:
            if toSuppress:
                if sys.stdout is not self.devnull:
                    self.original_stderr, sys.stderr = sys.stderr, self.devnull
            else:
                if sys.stdout is self.devnull:
                    self.original_stderr, sys.stderr = None, self.original_stderr
        return 
    
    def close(self):
        self._switch(0)
        return self
    
    def suppress(self):
        self._switch(1)
        return self
#     def suppress(self):
#         self._switch(1)
        
    def __enter__(self):
        import sys, os
        pass
#         print '[pas'
#         self._switch()
    
    def __exit__(self, *args, **kwargs):
        import sys
        self._switch()
        
#     def __enter__(self):
#         import sys, os        
#         if self.suppress_stdout:
#             self.original_stdout, sys.stdout = sys.stdout, self.devnull
# #             sys.stdout = self.devnull

#         if self.suppress_stderr:
#             self.original_stderr, sys.stderr = sys.stderr, self.devnull
# #             self.original_stderr = sys.stderr
# #             sys.stderr = self.devnull

#     def __exit__(self, *args, **kwargs):
#         import sys
#         # Restore streams
#         if self.suppress_stdout:
#             sys.stdout = self.original_stdout

#         if self.suppress_stderr:
#             sys.stderr = self.original_stderr

class Suppress:
    def __init__(self, suppress_stdout=1, suppress_stderr=1):
        self.suppress_stdout = suppress_stdout
        self.suppress_stderr = suppress_stderr
        self.original_stdout = None
        self.original_stderr = None

    def __enter__(self):
        import sys, os
        devnull = open(os.devnull, "w")

        # Suppress streams
        if self.suppress_stdout:
            self.original_stdout = sys.stdout
            sys.stdout = devnull

        if self.suppress_stderr:
            self.original_stderr = sys.stderr
            sys.stderr = devnull

    def __exit__(self, *args, **kwargs):
        import sys
        # Restore streams
        if self.suppress_stdout:
            sys.stdout = self.original_stdout

        if self.suppress_stderr:
            sys.stderr = self.original_stderr


def module__toModule(mod):
    res = collections.OrderedDict()
    res['NAME']=mod.__name__
    res['INPUT_FILE'] = getattr(mod,"__file__",None)
    res['MODULE']=mod
    return res

def get__defaultModuleDict():
#     import sys
    d = {}
    for k,v in sys.modules.items():
        if v is not None:
            d[k] = module__toModule(v)
        else:
            pass
#             sys.stderr.write(k + '\n')
    return d
#     return {k:module__toModule(v) for k,v in sys.modules.items() if v is not None
           
#            }

def module__getClasses(mod):
    '''https://stackoverflow.com/a/1796247/8083313
    '''
    if isinstance(mod,basestring):
        mod = sys.modules[mod]
    clsmembers = dict(inspect.getmembers(mod, inspect.isclass))
    return clsmembers



# import inspect
def name__lookup(name,frame=None,level=1, 
#                  getter="dict"
                ):
    '''
    if level==0, get the calling frame
    if level > 0, walk back <level> levels from the calling frame
    '''
    if frame is None:
        frame = inspect.currentframe()
    errMsg = ("Unable to lookup name {name} within level {level}".format(**locals()))
    
    i = 0
    while i != level:
        i+=1;
#     for i in range(level):
        if name in frame.f_locals:
            val = frame.f_locals[name]
            del frame
            return val
        
        frame = frame.f_back
        assert frame is not None,errMsg
        
    del frame        
    assert 0,errMsg
    
    
def get__frameDict(frame=None,level=0, getter="dict"):
    return get__frame(frame,level=level+1,getter=getter)

def get__frameName(frame=None,level=0, getter="func_name"):
    return get__frame(frame,level=level+1,getter=getter)
    
def get__frame(frame=None,level=0, getter="dict"):
    '''
    if level==0, get the calling frame
    if level > 0, walk back <level> levels from the calling frame
    '''
    if frame is None:
        frame = inspect.currentframe().f_back

    for i in range(level):
        frame = frame.f_back
    _getter  = {
        "dict":lambda x:x.f_locals,
        "func_name":lambda x:x.f_code.co_name
    }[getter]
    context = _getter(frame)
#     context = frame.f_locals
    del frame
    return context

def runtime__dict():
    import __main__
    res = vars(__main__)
    return res

def runtime__file(silent=1):
    dct = runtime__dict()
    res = dct['__file__']
    if not silent:
        sys.stdout.write (res+'\n')
    return res


def set__numpy__thread(NCORE = None):
    if NCORE is None:
#     if 'NCORE' not in locals():
        warnings.warn("[WARN] NUMPY is not limited cuz NCORE is not set")
    else:
        #     print (')
        keys = '''
        OMP_NUM_THREADS: openmp,
        OPENBLAS_NUM_THREADS: openblas,
        MKL_NUM_THREADS: mkl,
        VECLIB_MAXIMUM_THREADS: accelerate,
        NUMEXPR_NUM_THREADS: numexpr
        '''.strip().splitlines()
        keys = [ x.split(':')[0] for x in keys]


        try:
            ipy = get_ipython()
        except:
            ipy = None

        for key in keys:
            val = str(NCORE)
            if ipy:
                ipy.magic('env {key}={val}'.format(**locals()))
            os.environ[key] = val

def mpl__setBackend(bkd='agg',
                   whitelist = ['module://ipykernel.pylab.backend_inline']):
#     exception = '
#     print ('debug',"matplotlib" in sys.modules)
#     if "matplotlib" not in sys.modules:
#     if 1:
    if bkd is None:
        bkd = 'agg'
    import matplotlib
    bkdCurr = matplotlib.get_backend()
    if (bkdCurr != bkd) and (bkdCurr not in whitelist):
        matplotlib.use(bkd)

def base__check(BASE='BASE',strict=0,silent=0,
#                 default=None
               ):
#     if default is None:
#         default = ''
    default = ''
    res = os.environ.get(BASE, default)
    
    if res == '':
        if strict:
            raise Exception('variable ${BASE} not set'.format(**locals()))
        else:
#             PWD =  os.getcwd()
            PWD = pysh.shellexec("pwd -L").strip()
#             if not silent:
            warnings.warn('[WARN] variable ${BASE} not set,defaulting to PWD:{PWD}'.format(**locals()))
            os.environ[BASE] = PWD
    if not silent:
        print('[%s]=%s'%(BASE,os.environ[BASE]))
    return os.environ[BASE]
#     print('[BASE]=%s'%os.environ[BASE])
    
def base__file(fname='', 
               BASE=None, HOST='BASE', 
               baseFile = 1,
               force = False,silent= 1, asDIR=0):
    
    '''find a file according under the directory of environment variable: $BASE 
    '''
    if fname is None:
        fname = ''
        
    if baseFile == 0:
        return fname
    elif isinstance(baseFile,basestring):
        BASE=baseFile
    
    if not isinstance(BASE, basestring):
        BASE = base__check(strict = 1,silent=silent)
#        BASE  = os.environ.get( HOST,None)
#        assert BASE is not None
    BASE = BASE.rstrip('/')
    fname = fname.strip()
    res = os.path.join(BASE,fname)
    if BASE.startswith('/'):
        existence = os.path.exists(res)
        if not force:
            assert existence,'BASE={BASE},res={res}'.format(**locals())
        else:
            if not existence:
                if asDIR:
                    pysh.shellexec('mkdir -p {res}'.format(**locals()), silent=silent)
                else:
                    pysh.shellexec('touch {res}'.format(**locals()), silent=silent)
                
        with open('%s/TOUCHED.list' % BASE, 'a') as f:
            f.write(fname +'\n')
    return res        

def execBaseFile(fname,**kw):
    fname = base__file(fname,**kw)
    g= vars(sys.modules['__main__'])
#     g = __main__.globals()
    res = execfile(fname, g, g)
#     exec(open(fname).read(), g)
    return
    
def list__nTuple(lst,n,silent=1):
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
nTuple = list__nTuple

def it__window(seq, n=2,step=1,fill=None,keep=0):
    '''Returns a sliding window (of width n) over data from the iterable
   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...  
   Adapted from: https://stackoverflow.com/a/6822773/8083313
'''   
    it = iter(seq)
    result = tuple(itertools.islice(it, n))    
    if len(result) < n:
        result = result + (fill,) * (n-len(result))
        if keep:
            yield result
        else:
            pass
        return
    else:
        yield result
#     else:

    while True:        
        elem = tuple( next(it, fill) for _ in range(step))
        result = result[step:] + elem        
        if elem[-1] is fill:
            if keep:
                yield result
            break
        yield result
    pass    
window = it__window

def it__len(it):
    it,_it = itertools.tee(it)
    i = -1
    for i, _ in enumerate(_it):
        pass
    return it, i + 1

def self__install(
    lst=['/data/repos/pymisca'
                  ]):
    if isinstance(lst,basestring):
        lst = [lst]
    CMDS =[ 'cd {DIR} && python2 setup.py install --user &>LOG && echo DONE'.format(DIR=x) for x in lst]
    res = map(pysh.shellexec,CMDS)
    print (res)
    
    
class columns(object):
    gtf = ['SEQID','SOURCE','TYPE','START','END','SCORE','STRAND','PHASE','ATTRIBUTES']
    

columns.bed = bedHeader = [
 'chrom',
 'start',
 'end',
 'acc',
 'score',
 'strand',
 'FC',
 'neglogPval',
 'neglogQval',
 'summit',
 'img']
    
columns.betty = bettyHeader = ['OLD_DATA_ACC','SPEC_PATHOGEN','SPEC_HOST','TREATMENT','LIB_STRATEGY']


buf = '''
table genePredExt
"A gene prediction with some additional info."
    (
    string name;        	"Name of gene (usually transcript_id from GTF)"
    string chrom;       	"Chromosome name"
    char[1] strand;     	"+ or - for strand"
    uint txStart;       	"Transcription start position"
    uint txEnd;         	"Transcription end position"
    uint cdsStart;      	"Coding region start"
    uint cdsEnd;        	"Coding region end"
    uint exonCount;     	"Number of exons"
    uint[exonCount] exonStarts; "Exon start positions"
    uint[exonCount] exonEnds;   "Exon end positions"
    int score;            	"Score"
    string name2;       	"Alternate name (e.g. gene_id from GTF)"
    string cdsStartStat; 	"Status of CDS start annotation (none, unknown, incomplete, or complete)"
    string cdsEndStat;   	"Status of CDS end annotation (none, unknown, incomplete, or complete)"
    lstring exonFrames; 	"Exon frame offsets {0,1,2}"
    )
'''
columns.genepred = COLUMNS_GENEPREDEXT =  re.findall('.*\s+([a-zA-Z0-9]+);.*',buf)

def str__re__findReplace(ele, ptn, rep, context={}):
    '''
    return an input-output tuple if matched
    '''
    if rep is not None:
        assert getattr(ptn,"pattern",ptn).endswith('$')
        if context:
            rep = rep.format(context)
        
    if next(re.finditer(ptn,ele),None) is not None:
        if rep is not None:
            out = re.sub(ptn,rep,ele)
        else:
            out = ele
        return (ele,out)
#         print (ele,out)
    else:
        return None
    
@setAttr(str__re__findReplace,'_tester')
def _func():
    lst = ['/work/reference-database/salmonella-typhimurium/G00000001/ANNOTATION_FASTA',
     '/work/reference-database/salmonella-typhimurium/G00000001/QUADRON_OUTPUT',
     '/work/reference-database/salmonella-typhimurium/G00000001/src',
     '/work/reference-database/salmonella-typhimurium/G00000001/GENOME.STAR_INDEX',
     '/work/reference-database/salmonella-typhimurium/G00000001/GENOME.BOWTIE1_INDEX',
     '/work/reference-database/salmonella-typhimurium/G00000001/ANNOTATION.gtf',
     '/work/reference-database/salmonella-typhimurium/G00000001/GENOME.fasta',
     '/work/reference-database/salmonella-typhimurium/G00000001/G00000001-stypm.html',
     '/work/reference-database/salmonella-typhimurium/G00000001/ANNOTATION.genepred',
     '/work/reference-database/salmonella-typhimurium/G00000001/GENOME.fasta.fai',
     '/work/reference-database/salmonella-typhimurium/G00000001/G00000001-stypm.ipynb',
     '/work/reference-database/salmonella-typhimurium/G00000001/ANNOTATION.gff']

    ptn = '(GENOME)(.fasta)$'
    rep = r'10\2'
    rep = rep.format(**locals())

    expect = [None,
     None,
     None,
     None,
     None,
     None,
     ('/work/reference-database/salmonella-typhimurium/G00000001/GENOME.fasta',
      '/work/reference-database/salmonella-typhimurium/G00000001/10.fasta'),
     None,
     None,
     None,
     None,
     None]


    res = [str__re__findReplace(ele, ptn, rep) for ele in lst]
    assert res==expect
    
# import glob
# import os
def re__globFindReplace(ptn,rep=None,globber=None,context={},pad=0):
    if globber  is None:
        globber = os.path.join(os.path.dirname(ptn),'*')
    lst = glob.glob(globber)
    out = []
    for ele in lst: 
        res = str__re__findReplace(ele, ptn, rep, context) 
        if pad:
#             print (res
            out += [ res ]
        elif res is not None:
            out += [ res ]
    return out    
re__findReplace = re__globFindReplace


def reGlob__str2dict(ptn,globber=None,context={},pad = 0):
    dirname = os.path.dirname(ptn)
    if globber is None:
        globber = os.path.join(dirname,'*')
    lst = glob.glob(globber)
    out = []
    for ele in lst: 
        res = re.search(ptn,ele)
        
#         if not res and not pad:
#             continue
#         else:
        if res:
            d = res.groupdict()
            d.update(enumerate(res.groups()))
            d['dirname'] = dirname
            out+=[(ele,d)]
        else:
            if pad:
                out +=[None]
            else:
                pass
            
    return out


if __name__ == '__main__':
    str__re__findReplace._tester()
