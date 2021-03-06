from __future__ import absolute_import

from pymisca.header import *
from pymisca.tree import *
from pymisca.shell import *
from pymisca.logging_extra import *
from pymisca.io_extra import *
from pymisca.pandas_extra import *
from pymisca.numpy_extra import *
from pymisca.mp_extra import *
from pymisca.graphviz_extra import *
from pymisca.xml_extra import *
from pymisca.jupyter_extra import *
# from pymisca.pandas_extra import 
# from pymisca.atto_jobs import *
# from pymisca.module_wrapper import type__resolve, t

from pymisca.pandas_extra import pd, series2index
from pymisca.wraptool import Worker
from pymisca.ptn import WrapString,WrapTreeDict,path__norm,template__format,f,jf2
from pymisca.atto_string import AttoString,AttoStringDict,AttoStringList

import os, sys, subprocess, io, glob, inspect
import json, ast
import functools, itertools, copy,re
import collections, contextlib2
import urllib2,urllib,io    
import pymisca.fop as pyfop
import pymisca.pandas_extra as pypd
pd=pypd.pd
import pymisca.shell as pysh
from pymisca.shell import shellexec

import ast,simpleeval

_this_mod = pyext = sys.modules[__name__]

import pymisca.header as pyhead
import pymisca.header
# pyhead.mpl__setBackend(bkd='Agg') 
with pymisca.header.Suppress():
    pyhead.set__numpy__thread(vars(sys.modules['__main__']).get('NCORE',None))

import pymisca.numpy_extra as pynp
np = pynp.np

import pymisca.util__fileDict as util__fileDict
from pymisca.util__fileDict import *


import pymisca.oop as pyoop
util_obj = pyoop.util_obj

import pymisca.patch
import pymisca.graph

FrozenPath = pymisca.patch.FrozenPath

import pymisca.io_extra


import slugify

import datetime
import unicodedata

import configparser

_DICT_CLASS = collections.OrderedDict

##### pymisca.shell
dir__real = real__dir = pysh.real__dir

# def rgetattr(obj,attr):
#     _this_func = rgetattr
#     sp = attr.split('.',1)
#     if len(sp)==1:
#         l,r = sp[0],''
#     else:
#         l,r = sp
        
#     obj = getattr(obj,l)
#     if r:
#         obj = _this_func(obj,r)
#     return obj


def obj__dict__call(ax, d_ax,):
    for k,v in d_ax.items():
        rgetattr(ax,k)(v)
    return ax

import requests
import pymisca.sklearn_extra

import pymisca.atto_jobs
import dill
import path



# import shutil
# import tempfile
# class TempDirScope(object):
#     def __init__(self,getTempDirName = tempfile.mkdtemp,**kw):
# #         self._d = getTempDirName()
#         d = getTempDirName()
#         self._stack = pyext.getPathStack([d],**kw)
# #         for key in ['d','_root']:
# #             setattr(self,
# #                    key,
# #                    getattr())
#     def __getattr__(self,key):
# #         return getattr(self._stack,key)
#         return self._stack.__getattribute__(key)
#     def __enter__(self):
#         self._stack.__enter__()
#         return self._stack
# #         pass
#     def __exit__(self, *a,**kw):
#         self._stack.__exit__(*a,**kw)
#         shutil.rmtree(self.d)

def relFile__asModule(FNAME, MODULE_NAME = None, frame=None):
    FNAME = frame__relativeFile(FNAME,frame=frame__default(frame))
    return file__asModule(FNAME,MODULE_NAME)


def file__asModule(INPUT_FILE, MODULE_NAME=None):
    if MODULE_NAME is None:
        MODULE_NAME = get__anonModuleName()
    mod = pymisca.atto_jobs.AttoModule({"NAME":MODULE_NAME,
                                         "INPUT_FILE":INPUT_FILE})['MODULE']
    
    return mod

def file__importName(INPUT_FILE, NAME, frameDict= None, **kw):
    if frameDict is None:
        frameDict = get__frameDict(level=1)
    
    mod = file__asModule(INPUT_FILE,**kw)
    if isinstance(NAME,basestring):
        frameDict[NAME] = v = getattr(mod,NAME)
        return v
    elif isinstance(NAME,dict):
        for k,v in NAME.items():
            frameDict[v] = getattr(mod,k)
        return 


def dict__getDirJson(d):
    s = pyext.ppJson([(k,d[k]) for k in d \
                      if k.endswith("DIR") and k!="INPUTDIR"],
                     default=repr)   
    return s

def list__toHtmlRow(vals):
    res = '''
    <tr>
        {% for x in vals %}
         <td>{{x}}</td>
        {% endfor %}
    </tr>
    '''
    res = pyext.jf2(res)  
    return res


# def validate__fileTable(df,OUTDIR=None):
#     if OUTDIR is None:
#         OUTDIR = "."
#     OUTDIR = path.Path(OUTDIR).realpath()
#     with pyext.getPathStack([OUTDIR]):
#         if not isinstance(df,list):
#             it = pyext.df__iterdict(df)
#             it = list(it)
#         else:
#             it = df

#         for d in it:
#             d['FULL_PATH'] = OUTDIR / d['FILE_ACC']
# #             "{OUTDIR}/{FILE_ACC}".format(OUTDIR=OUTDIR,**d)
# #             exists = 
#             if pyext.os.path.exists(d['FULL_PATH']):
#                 d['FILE_ACC_HTML'] = pyext.tag__ahref(d['FILE_ACC'])
#                 d['SIZE'] = pyext.size__humanReadable( pyext.file__size(d['FULL_PATH'])) if d['FULL_PATH'].isfile() else "FOLDER"
#             else:
#                 d['FILE_ACC_HTML'] = d['FILE_ACC']
#                 d['FULL_PATH'] = "[DO-NOT-EXIST]"
#                 d['SIZE'] = -1
            
#     return it

def validate__fileTable(df,OUTDIR=None):
    if OUTDIR is None:
        OUTDIR = "."
    OUTDIR = path.Path(OUTDIR).realpath()
    with pyext.getPathStack([OUTDIR]):
        if not isinstance(df,list):
            it = pyext.df__iterdict(df)
            
            it = list(it)
        else:
            it = df

        for d in it:
            res = OUTDIR.glob(d['FILE_ACC'])
            if len(res) == 1:
                d['FULL_PATH'] = res[0]
                d['FILE_ACC_HTML'] = pyext.tag__ahref(d['FULL_PATH'].relpath(OUTDIR))
                if d['FULL_PATH'].isfile():
                    _size = pyext.file__size(d['FULL_PATH'])
                    d['SIZE'] = pyext.size__humanReadable( _size )
                    if _size < 10E6:
                        d['LINE_COUNT'] = pyext.file__lineCount(d['FULL_PATH'])
                    else:
                        d['LINE_COUNT'] = 'NA'
                else:
                    d['SIZE'] = "FOLDER"
                    d['LINE_COUNT'] = 'NA'

            else:
                d['FILE_ACC_HTML'] = d['FILE_ACC']
                d['FULL_PATH'] = "[DOES-NOT-EXIST]"
                d['SIZE'] = -1
                d['LINE_COUNT'] = 'NA'
            
    return it


def dicts__toHtmlTable(dicts,header=1,attrs=None):
    tups = []
    if header:
#         tups += [dicts[0].keys()]
        tups += [xml__tag("thead")(pyext.list__toHtmlRow( dicts[0].keys()) )] 
    tups += [pyext.list__toHtmlRow( x.values()) for x in dicts]
    res = tups
#     res = map(pyext.list__toHtmlRow, tups)
    res = pyext.rows__toHtmlTable(res,attrs)
    return res

@pyext.setAttr( _this_mod,"rows__toHtmlTable")
def rows__toTable(rows,attrs=None):
    if attrs is None:
        attrs = dict(border=1)
        pass
    
    res = '''<table border="1">
            {% for _row in rows %}
            {{_row}}
            {% endfor %}
    </table>'''    
    
    res = '''{% for _row in rows %}
            {{_row}}
            {% endfor %}'''        
    res = xml__tag("table",attrs)(res)
    return pyext.jf2(res)

def file__getReadable__ModifiedTime(fname, level='min'):
    dt = pymisca.shell.file__getModifiedTime(fname)
    if level == 'min':
        s = pyext.date__formatIso(dt)
        s = s.rsplit(':',2)[0]
    else:
        assert 0,(level,)
    return s

@pyext.setAttr(_this_mod,'tag__ahref')
def tag__href(fname,text=None
         ):
    text  = text or fname
    res = '''
    <a href="{fname}">{text}</a>
    '''.strip().format(**locals())
    return res

def scriptDict__toRawModuleDict(SCRIPTS, raw=True,**kw):
    return scriptDict__toModuleDict(SCRIPTS,raw=raw,**kw)
def scriptDict__toModuleDict(SCRIPTS,suffixes=['.py','.pyc','.pyson'],raw=0):
    MODULES = d = SCRIPTS.copy()
    for k in d:
        if k in ["__self__"]:
            continue
            
        v = d[k]
        if v in ["__debug__", "<stdin>"]:
            continue
            
        if suffixes:
            if not any([v.endswith(s) for s in suffixes]): continue
        mod = pymisca.atto_jobs.AttoModule({"NAME":k,
                                      "INPUT_FILE":d[k]})
        if raw:
            mod = mod['MODULE']
        d[k] = mod
#         ["MODULE"]
    return MODULES

# import time
# import functools

# def setAttr(other, name=None):
#     class temp():
#         _name = name
#     def dec(func):
#         if temp._name is None:
#             temp._name = func.__name__
# #         assert 0,(other,temp._name,func)
#         setattr(other,temp._name,func)
#         return func
#     return dec

# import datetime
import textwrap
def str__wrap(s,width=20):
    s = textwrap.wrap(s,width=width)
    s = '\n'.join(s)
    return s

def series__sanitise(ser):
    res = ser.str.upper()
    res = res.str.replace('[^a-zA-Z_0-9]','_')
    return res
from pymisca.date_extra import *




def url__download(url,chunk_size=8192):
    '''https://stackoverflow.com/a/16696317/8083313'''
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return local_filename



def lastLine(res):
    return res.splitlines()[-1]

def getErrorInfo():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    del fname
    return locals()

def path__toSafePath(FNAME):
    FNAME = FNAME.replace('\\','')
    return FNAME


def df__toSTATUS(indVenn,xlab='dataset_1',ylab='dataset_2'):
#     df = pd.Series(np.nan,index=indVenn['indAny']).to_frame('STATUS');
#     df.index.name='INDEX'
    
    df = indVenn[['indAll','indnot1','indnot2']]
    df = df.melt(var_name='STATUS', value_name='INDEX').dropna(subset=['INDEX']).set_index('INDEX')
#     .dropna()
#     for key in ['indAll','indnot1','indnot2']:
#         df.loc[df.index.isin(indVenn[key]),'STATUS'] = key
    df['STATUS'] = df['STATUS'].map({'indAll':'in both datasets',
                      'indnot1': 'not in %s'%xlab,
                     'indnot2':'not in %s'%ylab}.get).dropna()
    # df = df.sort_values('STATUS')
    df = df.sort_index()
    return df

def df__fillna(dfc,fill=['NA']):
    vals = dfc.values
    idx = dfc.isnull().values
    for x,y in zip(*np.where(idx)):
        vals[x,y] = fill
    dfc = pd.DataFrame(vals,columns=dfc.columns,index=dfc.index)
    return dfc

def fastq__readCountAppx(FNAME,readLength):
    
    fileSizeInByte = pyext.file__size(FNAME)
    readCount = fileSizeInByte // (2 * readLength + 60)
    return readCount

def size__humanReadable(bytes,units=['','K','M','G','T', 'P','E'],suffix='B',fmt='{0:.2f}',):
    """ Returns a human readable string reprentation of bytes,
    Source: https://stackoverflow.com/a/43750422/8083313"""
    return \
        fmt.format(bytes) + units[0] + suffix if bytes < 1024 \
        else size__humanReadable(bytes/1024., units[1:],suffix,fmt)

def datenow():
    res  = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    return res

def fname__tograph(fnames,sep='-',as_df=1,**kwargs):
    lst = fnames
    lst = map(pyext.getBname, lst)
    lst = map(lambda x:x.split(sep),lst)
    graph = pymisca.graph.graph_build(lst,as_df = as_df, sep=sep , **kwargs)
    return graph


def dir__asJsonDB(DIR):    
    dfc = pyext.dir__indexify(DIR).query('EXT=="json"')
    with pyext.getPathStack([DIR],):
        DB = collections.OrderedDict([(x,pyext.readData(x)) for  x in dfc['FILEACC']])
    return DB

def jsonDB__eval(DB, expr, glb={}, lc={}):
    d = dict(DB=DB)
    
    d.update(lc)
    res = simpleeval.SimpleEval(names=d).eval(expr)
#     res = ast.literal_eval(expr, glb, d)
#     res = ast.literal_eval(expr)
    return res
def dict__key__func(d,key,func,*a,**kw):
    _ = d[key] = func(d[key],*a,**kw)
    return _

def pathDF__combineMetaTsv(pathDF,COLS=None,
                           addFname_COL='SUBCSV_FNAME', FILE_KEY='FULL_PATH',**kw):
    '''
    pathDF = pyext.dir__indexify(DIR).query('EXT=="tsv"').query('BASENAME.str.match("[^_]")')
    '''
    if COLS is None:
        COLS= '''
        DATA_ACC
        OLD_DATA_ACC
        FNAME
        TAG
        TREATMENT
        LIB_STRATEGY
        SPEC_PATH
        SPEC_HOST
        '''.replace('\t','').replace(' ','').strip().splitlines()

    # COLS = 'DATA_ACC	OLD_DATA_ACC	SPEC_PATH	SPEC_HOST	TREATMENT	LIB_STRATEGY	FNAME	TAG'.split('\t')
    dfs = [pyext.readData(x,
                          addFname=pyext.os.path.basename,
                          addFname_COL=addFname_COL,**kw
                         ) for x in pathDF[FILE_KEY]]
    
    COLS = list(COLS)+[addFname_COL]
    print(COLS)
    dfs.insert(0,pd.DataFrame(columns=COLS))
    df = pd.concat(dfs,axis=0)[COLS]
    df.insert(0,addFname_COL,df.pop(addFname_COL))
    return df
#     df

#     dupDf = df.query('OLD_DATA_ACC.duplicated(0)')
#     print(dupDf.shape)
#     df = uniqDf = df.drop_duplicates(subset=['OLD_DATA_ACC'])
#     df['DATA_ACC_INT']  = df['OLD_DATA_ACC'].str.extract('[H]?(\d{8,9})',expand=False,)
#     return df


def dir__isin(PWD,DIR):
    return re.match( DIR +'.*$', PWD)  is not None


def dir__getGenomeFasta(DIR,
                        globSeq=['*.fasta','*.fa','*.fna'],
                        singleFile=True,
                       ):
    return dir__globSequences(DIR,globSeq=globSeq,singleFile=singleFile)

def dir__globSequences(DIR,globSeq=None,singleFile=0):
    '''Find a single 
    '''
    DIR = pyext.os.path.realpath(DIR)
    assert pyext.os.path.exists(DIR)
    with pyext.FrozenPath(DIR) as d:
        res = None
#         print (d.files())
        for ptn in globSeq:
            res = d.glob(ptn)
            if res:
                if singleFile:
                    assert len(res)==1,'{res}\n{d}/{ptn}'.format(**locals())
                break
        assert res is not None,'No files matched in {DIR} with glob sequences {globSeq}'.format(**locals())
        res = (res)[0]
    return res

def dir__indexSubdirectory(INPUTDIR,depth=1,
                           opt_type='-type d',
                           opt_exec='-exec du -s --apparent-size {} +',
                          silent=0,):
    with pyext.getPathStack([INPUTDIR]):    
        INPUTDIR = INPUTDIR.rstrip('/')
        CMD = 'find ./ -mindepth {depth} -maxdepth {depth} {opt_type} {opt_exec}'.format(**locals())
        buf = pyext.shellexec(CMD,silent=silent)
        dfc = pyext.read__buffer(buf,ext='tsv',header=None,columns=['SIZE','FILEACC'])
        if len(dfc.columns)==0:
            dfc.index.name='FILEACC'
            dfc = dfc.reset_index()
#             dfc.columns = ['FILEACC',]
        
        dfc['FILEACC'] = dfc['FILEACC'].str.replace('^./','')
        dfc['DIR_PARENT'] = pyext.os.path.realpath(INPUTDIR)
        dfc['FILE_FULL_PATH'] = pyext.df__format(dfc,'{DIR_PARENT}/{FILEACC}')

    return dfc

def dir__indexify(DIR,silent=1,OPTS=None,OPTS_exec = 'du -al --apparent-size', checkEmpty=True,excludeHidden=True,TYPE='f'):
    if OPTS is None:
        OPTS = ''
#     find . -type f -exec du -a {} +
#     cmd = 'cd %s ; du -a --apparent-size .' % DIR
    DIR = DIR.rstrip('/')
    with pyext.getPathStack([DIR]):    
        cmd = 'find ./ {OPTS} -type {TYPE} '.format(**locals())
        if OPTS_exec:
            cmd += '-exec {OPTS_exec} "{{}}" +'.format(**locals())

        COLS = ['SIZE','EXT','REL_PATH','FULL_PATH','BASENAME','FILEACC','REALDIR','DIR']
        res = pd.DataFrame([], columns=COLS)
        resBuf = pysh.shellexec(cmd,silent=silent)
        res = res.append(
            pyext.read__buffer(resBuf,columns=['SIZE','FILEACC'],header=None,ext='tsv'),
    #         axis=0,
        )

        if res.empty:
            DIR = os.path.realpath(DIR)
            assert not checkEmpty,'DIR={DIR} is empty'.format(**locals())
            return res
#     res = res.append(res_)
    
#     if res.empty:
#         res = pd.DataFrame([],columns=['SIZE','FILEACC','REL_PATH','REALDIR','FULL_PATH'])
#         return res
#     res['FILEACC'] = map(os.path.normpath,res['FILEACC'])
    res['FILEACC'] = res['FILEACC'].map(os.path.normpath)#.astype('unicode')
    res['DIRACC'] = res['FILEACC'].map(os.path.dirname)
    res['SIZE'] = res['SIZE'].astype(int)
    
    res['REL_PATH'] = pyext.df__format(res,'{DIR}/{FILEACC}',DIR=DIR)
    res['REALDIR'] = res['DIR'] = os.path.realpath(DIR)
    res['FULL_PATH'] = pyext.df__format(res,'{DIR}/{FILEACC}',)
    res['FULL_DIR_PATH'] = pyext.df__format(res,'{DIR}/{DIRACC}',)
    
    res['BASENAME']  = res['FILEACC'].map(pyext.os.path.basename)#.astype('unicode')
    res['EXT'] = res['BASENAME'].str.rsplit('.',1).str.get(-1)
    res['BNAME'] = res['BASENAME'].str.rsplit('.').str.get(0)
    
    res = pd.DataFrame(res)
#     res['BASENAME'] = res['BASENAME'].astype(unicode)
    if excludeHidden and not res.empty:
#         res=  res.loc[ ~res['BASENAME'].str.match("^\.")]
        res = res.query('~BASENAME.str.match("^\.").values')
        
        if res.empty:
            assert not checkEmpty,'DIR={DIR} is empty'.format(**locals())
            return res
#         assert 0,pyext.pd._version.get_versions()
#         res = res.query('~BASENAME.str.match("^\.")')
#         try:
#             res = res.query('~BASENAME.str.match("^\.")')
# #             pyext.np.save('_dbg.npy',)
# #             res.to_pickle('__dbg.pk')
# #             res = res.query('~BASENAME.astype("str").str.startswith(".")')

# #             print res.eval('BASENAME')
#             pass
#             assert 0,'test'
#         except Exception as e:
            
#             print(res.dtypes)
# #             print(res['BASENAME'].dtype)
#             print(res[['BASENAME']])
#             raise e


        
#     res['REL_PATH'] = pyext.df__format(res,'{DIR}/{FILEACC}')

#     res['FULL_PATH'] = map(os.path.normpath,
#                            pyext.df__format(res,'{DIR}/{FILEACC}'))
#     res['EXT'] = 
#     indDF.fileacc.apply(pyext.splitPath,level=level).str.get(0)
#     ['DIR',['/'],'FILEACC'])
    res = res.set_index('FULL_PATH',drop=0)
    res.index.name = 'INDEX'
    
    return res

def arr__exp2m1(X):
    res = np.power(2,X) - 1
    return res
exp2m1 = arr__exp2m1

###### 
def lastLine(buf):
    return buf.splitlines()[-1].strip()

from difflib import SequenceMatcher
def str__longestCommonSubstring(string1,string2):
    '''
    ### source: https://stackoverflow.com/a/39404777/8083313
    '''
    matcher = SequenceMatcher(None, string1, string2)
    match = matcher.find_longest_match(0, len(string1), 0, len(string2))
    return match

def dict__autoFill(TO, FROM, keys = None):
    if keys is None:
        keys = TO.keys()
    for key in keys:
        if TO[key] is None:
            #### only fill None
            res = FROM.get(key,None)
            if res is None:
                assert 0,'cannot find "%s" from dict:%s ' %(key, FROM)
            else:
                TO[key] = res
    return TO.copy()

def func__inDIR(func,DIR='.', debug=0):
    pysh.shellexec('mkdir -p %s' %DIR,silent=1-debug)    
#     ODIR = pyext.os.getcwd()
    ODIR = os.getenv('PWD')
    if debug:
        print ('[ODIR]')
        print (ODIR)
        print (pysh.shellexec('pwd -L'))
    with pymisca.patch.FrozenPath(DIR):
        res = func()
        return res
    
#     try:
#         pyext.os.chdir(DIR)
# #         print (pysh.shellexec('pwd'))
#         res = func()
#         return res

#     finally:
#         pyext.os.chdir(ODIR)
        
# def df__iterdict(df):
#     it = df.itertuples()
#     it = (x.__dict__ for x in it)
#     return it

# def df__iterdict(df):
#     it = df.itertuples()
#     it = (x.__dict__ for x in it)
#     return it

def df__iterdict(self, into=dict):
    '''
    ### See github issue https://github.com/pandas-dev/pandas/issues/25973#issuecomment-482994387
    '''
    it = self.iterrows()
    for index, series in it:
        d = series.to_dict(into=into)
        d['index'] = index
        yield d

def df__asMapper(dfc,key1,key2):
    res = dfc.eval('({key1},{key2})'.format(**locals()))
    res = dict(zip(*res))
    return res
df2mapper=  df__asMapper
        

def iter__toSoft(it):
    for line in it:
        if line:
            if line[0] in list('!^'):
                yield line
def iter__toFile(it,fname,lineSep='\n'):
    assert 0,'Obsolete, use pymisca.io_extra.it__toFile() instead'
    opened = 0
    if not hasattr(fname,'write'):
        f = io.open(fname,'w',encoding='utf8')
        opened =  1
    else:
        f = fname
        
    if 1:
#     with io.open(fname,'w',encoding='utf8') as f:
        for i,line in enumerate(it):
            if i ==0:
                _type = type(line)
            if lineSep is not None:
                line = line.strip() + _type(lineSep)
            f.write(line)
    if opened:
        f.close()
    
            


def kwarg2dict(res,d = None,silent=1,lineSep='\n'):
    if d is None:
        d = collections.OrderedDict()
    for line in res.strip().split(lineSep):
        sp = line.strip().partition("=")
        if sp[1]=='=':
            (key, _, value) = sp
            key = key.strip()
            value =value.strip()
            d[key] = value
            if not silent:
                print (sp)
                print(key,'=',value)
    return d

def fileDict__load(fname):
    fdir = pyext.os.path.dirname(fname) 
#     with open(fname,'r') as f:
#         dd = json.load_ordered(f,)
#     if os.stat(fname).st_size == 0:
#         dd = collections.OrderedDict()
#     else:
    if 1:
        dd = pd.read_json(fname, typ='records'
                         ).to_dict(into=collections.OrderedDict)
        dd = collections.OrderedDict([(k,
                                       pyext.os.path.join(fdir,v)) 
                                      for k,v in dd.items()])
    dd = pyoop.util_obj(**dd)
    return dd

json.load_ordered  = functools.partial(json.load,
                                    object_pairs_hook=collections.OrderedDict,)
json.loads_ordered = functools.partial(json.loads,
                                    object_pairs_hook=collections.OrderedDict,)


def arr__l2norm(x,axis=None,keepdims=0):
    res = np.sum(x**2,axis=axis,keepdims=keepdims)**0.5
    return res

def list__randomChoice(lst,as_list=0, **kw):
    idx = np.random.choice(range(len(lst)),**kw)
    res = map(lst.__getitem__,idx)
    if not as_list:
        res = np.array(res)
    return res


def list__paste0(ss,sep=None,na_rep=None,castF=unicode):
    '''Analogy to R paste0
    '''
    if sep is None:
        sep=u''
    
    L = max([len(e) for e in ss])
    it = itertools.izip(*[itertools.cycle(e) for e in ss])
    def _castF(s):
        if isinstance(s,str):
            s = s.decode('utf8')
        else:
            pass
        return castF(s)

    res = [castF(sep).join(_castF(s) for s in next(it) ) for i in range(L)]
#     res = pd.Series(res)
    return res
pasteB = paste0 = list__paste0

#### obsolete ###
# def df__paste0(df,keys,
# #                sep='',
#                sep = '',
# #                headerFmt='[{key}]',
#                debug=0,):
#     '''Calling paste0 with df.eval()
#     sep: accept '{key}' as keyword, try sep='[{key}]'
# '''
# #     if 'index' in keys:        
# #     vals = df.get(keys).values
# #     for key, val in zip(keys,vals):
# #         lst += [['[%s]'%key], val]
#     lst = []
#     lstStr = ''
#     sep0 = ''
#     for i, key in enumerate(keys):
#         if i==0:
#             fmt = '{key},'
#         else:
#             fmt = '["%s"], {key},' % sep
#         lstStr += fmt.format(**locals())
#     cmd = 'list(@pyext.paste0([{lstStr}],sep="{sep0}"))'.format(**locals())
#     if debug:
#         print (cmd)
#     res = df.eval(cmd)
#     res = pd.Series(res,index=df.index)
# #     res = pyutil.paste0(lst, sep=sep)
#     return res

def df__paste0(df,keys,sep="",**kw):
    return df__format(df, 
                      sep.join(["{%s}"%x for x in keys ]),
                     **kw)

def df__format(df,fmt, formatter = None, **kwargs):
    if formatter is None:
        formatter = lambda d: pyext.template__format(fmt, d)
        
    '''Format for each row of a pd.Dataframe
    '''
    it = pyext.df__iterdict(df)
    res = []
    for d in it:
#         d['index'] = d.pop('Index')
        d.update(kwargs)#
        val = formatter(d)
#         val = pyext.template__format(fmt,d)
#         val = fmt.format(**d)
        res.append(val)
    return res


def dfJob__symlink(dfc,
                  FILECOL,
                   ODIR,
                  level = 1,
                  copy=True):
    if copy:
        dfc =dfc.copy()
#     FILECOL = 'RPKMFile'
#     ODIR = '/home/feng/repos/jbrowse/data/links'
    dfc['INFILE'] = dfc[FILECOL]
    print (dfc.shape)
    dfc = dfc.dropna(subset = [FILECOL])
    dfc = dfc.query('~index.isnull()')
    print( dfc.shape)
#     dfc['EXT'] = dfc['INFILE'].apply(pyext.splitPath,level=level).str.get(-1)
    dfc['EXT'] = dfc['INFILE'].str.rsplit('.',1).str.get(-1)
#     apply(pyext.splitPath,level=level).str.get(-1)
    dfc['OFNAME'] = pyext.df__format(dfc,'{ODIR}/{index}.{EXT}',ODIR=ODIR)
    ##### Symlink .bw files to a directory
    pyext.shellexec('mkdir -p %s'%ODIR)
    dfc['CMD'] = pyext.df__format(dfc,
                                  fmt='ln -sf "{INFILE}" "{OFNAME}" && echo "{OFNAME}"',
#                                   ODIR=ODIR
                                 )
    return dfc
# def fileDict__save(fname=None,d=None,keys=None):
#     assert d is not None,'set d=locals() if unsure'
#     d = collections.OrderedDict(d)
#     if keys is not None:
#         d  = pyext.dictFilter(d,keys)
    
#     if isinstance(fname,basestring):
#         if os.path.exists(fname):
#             if os.stat(fname).st_size != 0:
#                 with open(fname,'r') as f:
#                     res = pyext.json.load_ordered(f,)
#                     res.update(d)
#                     d = res
                
#     res = pyext.json.dumps(d)
#     res = res + type(res)('\n')    
#     if isinstance(fname,basestring):
#         with open(fname,'w') as f:
#             f.write(res)
#         return fname
#     elif fname is None:
#         f = sys.stdout
#         f.write(res)
#     else:
#         f = fname
#         f.write(res)
#         return f
    
# def dictFilter(oldd,keys):
#     d =collections.OrderedDict( 
#         ((k,v) for k,v in oldd.iteritems() if k in keys) 
#     )
#     return d

class envDict(collections.OrderedDict):
    def __init__(self, *args,**kwargs):
        super(envDict,self).__init__(*args,**kwargs)
    def __getattribute__(self,name):
#         res = super(envDict,self).__getattribute__(name)
        try:
            res = super(envDict,self).__getattribute__(name)
        except AttributeError as e:
            res = self.get(name,None)
            if res is None:
                raise e
        return res
#     def __setattr__
#     def __setattr__(self,name,value):
#         super(envDict, self).__setitem__(name, value)
#         res = self.__dict__.get(name,None)
#         res = super(envDict,self).__dict__.get(name,None)
#         res = getattr( super(envDict,self), name, None)
#         .__getattr__(name)
#         if res is not None:
#             pass
#         else:
#             res = self.get(name,None)
#         return res

def unique(lst):
    """Generate unique items from sequence in the order of first occurrence.
    adapted from: https://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python
    """
    seen = list()
    for val in lst:
        yes = any((val is _val for _val in seen))
        if yes:
            continue
        seen.append(val)
        yield val
        
def index2frame(index,val=True,name=None):
    '''
    initialise frame from index with value
    '''
    index = pd.Index(index,name=name)
    track = pd.DataFrame([val]*len(index),index=index)
#     track = index.to_frame()
#     track.loc[:,:]=val
    return track    
  

def list__realise(lst, d=None, cls=basestring,check = 1):
    assert d is not None
    res = []
    for x in lst:
        if isinstance(x,cls):
            y = d.get(x,x)
            if (check) and (y is x):
                print ('[WARN] cannot realise:"%s"'% y)
        else:
            y = x 
        res.append(y)
    return res
#     res = [ d.get(x,x) for x in lst ]
    
def arr__polyFit(x,y, deg=1, **kwargs):
    x,y = map(np.ravel,np.broadcast_arrays(x,y))
    isNA = np.isnan(x) | np.isnan(y) 
    fit = np.polyfit(x[~ isNA], y[~isNA], deg=deg, **kwargs)
    return fit

def getBname(fname):
    '''
    Extract "bar" from "/foo/bar.ext"
    '''
    bname = fname.rstrip('/').split('/')[-1].rsplit('.',1)[0]
    return bname

basename = getBname ###legacy


# def base__touch(fname):

# print ('[__main__]',__main__)

# def execBaseFile(fname,):
#     fname = pyext.base__file(fname)
#     g= vars(sys.modules['__main__'])
# #     g = __main__.globals()
#     res = execfile(fname, g, g)
# #     exec(open(fname).read(), g)
#     return

def sanitise__column(col):
    col = col.replace(' ','_').replace('-','_').upper()
    return col

def df__sanitiseColumns(dfc):
    cols = dfc.columns
    res = cols.map(sanitise__column)
    dfc = dfc.rename(columns=dict(zip(cols,res)))
    return dfc




def it__toExcel(it,ofname,engine='xlsxwriter',sheetFunc=lambda k:'__'.join(k),
                silent=0,**kwargs):
    f = pd.ExcelWriter(ofname,engine=engine,**kwargs)
    for k,mm in it:
        ali = sheetFunc(k)
        if not silent:
            print ('[writing]%s'%ali)

        mm.to_excel(f,sheet_name=ali,engine='xlsxwriter')
    f.close()            
    return ofname

def index__sortFactor(ind,level=None,inplace=False,dtype = None):
    '''sort a particular level of the multiIndex and change the labels accordingly
'''
#     ind.levels[i]
    ilvl = ind.levels[level]
    if dtype is not None:
        ilvl = ilvl.astype(dtype)
    silvl, od = ilvl.sort_values(return_indexer=1)
    np.argsort(od)
    iod = np.argsort(od)
    print  ind.labels[level]
    print (map(iod.__getitem__, ind.labels[level]))
    
    ind = ind.set_labels( map(iod.__getitem__, ind.labels[level]),level=level,inplace=inplace)
    ind = ind.set_levels(silvl, level=level,inplace=inplace)
    return ind

def index__set_level_dtype(ind,level=None, dtype=None,inplace=False):
    if dtype is None:
        pass
    else:
        ind.set_levels( ind.levels[level].astype(dtype),level=level,inplace=inplace)
    return ind

def to_tsv(df,fname,header= None,index=None, **kwargs):
    df.to_csv(fname,sep='\t',header= header, index= index, **kwargs)
    return fname

def file__read__configSections(inputFile):

    config = configparser.ConfigParser( allow_no_value= True,strict=False)
    config.optionxform=unicode
    config.read(inputFile)
    d = pyext._DICT_CLASS(config)
    d.pop('DEFAULT')

    def section__serialise(sec):
        lst = []
        for k,v in sec.iteritems():
            assert v is None, pyext.ppJson(dict(sec=sec,v=v,k=k,
                           MSG='configSection file cannot contain "="'))
            lst.append(k)
        buf = '\n'.join(lst,)
        return buf

    for k in d:
        pyext.dict__key__func(d,k,section__serialise)
    return d

# def file__callback(fname,callback,mode='r'):
#     if isinstance(fname,basestring):
#         with open(fname,mode) as f:
#             res = callback(f)
#     else:
#         f = fname
#         res = callback(f)
#     return res

# def file__notEmpty(fpath):  
#     '''
#     Source: https://stackoverflow.com/a/15924160/8083313
#     '''
#     return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

# def file__link(IN,OUT,force=0, forceIn = False, link='link',relative=1):
    
#     linker = getattr(os,link)
    
#     #### Make sure input is not an empty file
#     if not file__notEmpty(IN) and link !='symlink':
#         if not forceIn:
#             return IN
#     if os.path.abspath(OUT) == os.path.abspath(IN):
#         return OUT
        
# #     if os.path.exists(OUT):
#     if os.path.isfile(OUT) or os.path.islink(OUT):
#         if force:
# #             assert os.path.isfile(OUT) or os.path.islink(OUT)
#             os.remove(OUT)
# #             print ('removed[OUT]%s'%OUT)
#         else:
#             assert 'OUTPUT already exists:%s'%OUT
#     else:
#         pass
    
    
#     try:
#         if link=='symlink':
#             IN  =os.path.realpath(IN)
            
# #             OUT = os.path.realpath(OUT)
# #             OUT = os.path
#             if relative:
#                 IN = os.path.relpath( IN,os.path.dirname(OUT))
#         linker(IN,OUT)
#     except Exception as e:
#         d = dict(PWD=os.getcwdu(),
#                  IN=IN,
#                  OUT=OUT)
#         print(json.dumps(d,indent=4))
# #         print ('[PWD]%s'%os.getcwdu())
# #         print('l')
#         raise e
        
#     return OUT


# def file__rename(d,force=0, copy=1, **kwargs):
#     for k,v in d.items():
#         DIR = os.path.dirname(v)
#         if DIR:
#             if not os.path.exists(DIR):
#                 os.makedirs(DIR)
#         file__link(k,v,force=force,**kwargs)
#         if not copy:
#             if os.path.isfile(k):
#                 os.remove(k)
                
def file__wsv2tsv(FNAME,silent=0):
    res = pyext.shellexec("sed 's/[ \t]\+/\t/g' {FNAME} | sed 's/[ \t]\+$//g'> {FNAME}.tsv".format(**locals()),
                   silent=silent)
    FNAME = '%s.tsv'%FNAME
    return FNAME
            
# def file__backup(IN)
def read__buffer(buf,**kwargs):
    res = pyext.readData(pymisca.io_extra.unicodeIO(buf=buf),**kwargs)
    return res
def read__npy(FNAME,allow_pickle=1, **kw):
    return np.load(FNAME,allow_pickle=allow_pickle, **kw)

def read__commentjson(FILE):
    
    buf =  pyext.readData( FILE, ext='it')
    buf = ''.join(buf)
    return simpleeval.EvalWithCompoundTypes().eval(buf)    
    
#     # buf =  pyext.readData('src/H00000000-rna-0620-B.json',ext='it')
#     buf = '\n'.join([x for x in buf if x.find('#')==-1])
#     DB_PIPE = pyext.read__buffer(buf,ext='json',)
#     return DB_PIPE

from pymisca.shell import read_json

# def read_json(fname,
#              object_pairs_hook=collections.OrderedDict,
#               parser = json,
#              **kwargs):
#     kwargs.update(dict(object_pairs_hook=object_pairs_hook,))
# #     if hasattr(fname,'read'):
# #         func = json.loads
# #         res = func(fname.read(),**kwargs)
# #     else:
#     if 1:
#         func = parser.load
#         res = pyext.file__callback(
#             fname,
#             functools.partial(
#                 func,**kwargs
#             )
#         )
#     return res

def job__baseScript(scriptPath,baseFile=1,**kwargs):
    return job__script(scriptPath,baseFile=baseFile,**kwargs)

def job__scriptCMD(CMD, opts = '', **kwargs):
    assert opts == '','"opts" will be overridden'
    
    sp = dict(enumerate(CMD.split(None,1)))
    scriptPath = sp[0]
    opts = sp.get(1,opts)
    return job__script(scriptPath, opts=opts, **kwargs)

def job__safeBaseScriptCMD(CMD, baseFile=1, check =True, **kwargs):
    return job__scriptCMD(CMD, check = check, baseFile=baseFile,**kwargs)

def job__safeScriptCMD(CMD,check = True, **kwargs):
    return job__scriptCMD(CMD, check = check, **kwargs)
# def job__baseScript

def job__script(scriptPath, ODIR=None, 
                opts='', ENVDIR = None, 
                silent= 1,
                DATENOW = '.',
#                 verbose = 1,
                interpreter = '',
                baseFile= 0,
                baseOut = 1,
                check = False,
                inplace=False,
                prefix = 'results',
               ):
#     verbose = 2 - silent
    
    base__check(silent=silent)
    BASE = os.environ['BASE'].rstrip('/')    
    baseLog = base__file('LOG',force=1)
#    if baseFile:
    scriptPath = pyext.base__file(scriptPath,baseFile=baseFile)
    scriptBase = pyext.getBname(scriptPath,)    
    scriptFile = os.path.basename(scriptPath)
#     if ODIR is None:
#         ODIR = scriptBase
#     ODIR = ODIR.rstrip('/')
    prefix = prefix.rstrip('/')

    if DATENOW is None:
        DATENOW =pyext.datenow()
    if ODIR is None:
        ODIR = pyext.base__file('{prefix}/{scriptBase}/{DATENOW}'.format(**locals()),
#                                prefix=prefix,
                               baseFile=baseOut,
                               asDIR=True,force=1)
#         ODIR = '{BASE}/{prefix}/{scriptBase}/{DATENOW}'.format(**locals())
    
    isoTime = pyext.datetime.datetime.now().isoformat()
    tempDIR = pyext.base__file('.scripts/{isoTime}'.format(**locals()),
                               asDIR = True,
                               force = 1,
                               baseFile=baseOut)
    
    scriptTemp = os.path.join(tempDIR, scriptFile)
#     ('{tempDIR}/{scriptFile}')
    JOBCMD = '{scriptTemp} {opts}'.format(**locals())

#     JOBCMD = '{interpreter} ./{scriptFile} {opts}'.format(**locals())
    
    if silent < 2:
        sys.stdout.write(  u'[JOBCMD]{JOBCMD}\n'.format(**locals()).replace(tempDIR,'') )
    
    if inplace:
        ODIR = '$PWD'
    
    CMD='''
mkdir -p {ODIR} || exit 1
time {{ 
    set -e;      
    cat {scriptPath} | tee {ODIR}/{scriptFile} | tee {scriptTemp} > /dev/null
    chmod +x {scriptTemp} 

    cd {ODIR}; 
    {JOBCMD}
    touch {ODIR}/DONE; 
}} 2>&1 | tee {ODIR}/{scriptFile}.log | tee -a {baseLog};
exit ${{PIPESTATUS[0]}}; 
'''.format(**vars())
    
    if ENVDIR is not None:
        CMD = 'source {ENVDIR}/bin/activate\n'.format(**locals()) + CMD

    p = pysh.shellpopen(CMD,silent=silent)
#     res, err  = pysh.pipe__getResult(p)
#     success = (err == 0)
    suc,res = pysh.pipe__getResult(p)
    
    if check:
        assert suc,res        
        return res
    else:
        return suc, res
    
# def ppJson(d,**kw):
#     '''
#     Pretty print a dictionary
#     '''
#     s = json.dumps(d,indent=4, sort_keys=True,**kw)
#     return s
# def dppJson(d,default=repr,**kw):
#     return ppJson(d,default=default,**kw)

def is_ipython():
    try:
        get_ipython
        return 1
    except:
        return 0
hasIPD = is_ipython()

if hasIPD:
    import IPython.display as ipd

def showMD(s):
    if pyext.hasIPD:
        ipd.display(ipd.Markdown(s))
        
def MDFile(fname):
    s='[{0}]({0})'.format(fname)
    return showMD(s)


def printlines(lst,fname = None,
                mode='w',
               callback=MDFile,encoding='utf8',
              lineSep='\n',castF=unicode):
    s = castF(lineSep).join(map(castF,lst))
    if fname is None:
        print(s)
    else:
# f = open('test', 'w')
# f.write(foo.encode('utf8'))
# f.close()
        with open(fname,mode) as f:
            print >>f,s.encode(encoding)
#         if callback is None:
#             callback = 
#         if callback is not None:
#             res = callback(fname)
        return fname
        

# def nTuple(lst,n,silent=1):
#     """ntuple([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]
    
#     Group a list into consecutive n-tuples. Incomplete tuples are
#     discarded e.g.
    
#     >>> group(range(10), 3)
#     [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
#     """
#     if not silent:
#         L = len(lst)
#         if L % n != 0:
#             print '[WARN] nTuple(): list length %d not of multiples of %d, discarding extra elements'%(L,n)
#     return zip(*[lst[i::n] for i in range(n)])

def get__LeafFiles(DIR):
    ''' Drill down to leaf files of a directory tree if the path is unique.
    '''
    assert os.path.exists(DIR),'%s not exist'%DIR
    DIR = DIR.rstrip('/')
    if not os.path.isdir(DIR):
        return [DIR]
    else:
        cmd = 'ls -LR %s'%DIR
        res = subprocess.check_output(cmd,shell=1)
        res = re.split(r'([^\n]*):',res)[1:]
        it = pyext.nTuple(res,2,silent=0)
        DIR, ss = it[0];
        for dd,ss in it[1:]:
            NEWDIR, ALI = dd.rsplit('/',1)
            assert NEWDIR == DIR, 'Next directory %s not contained in %s'%(dd,DIR)
            DIR = dd 
        res = [ '%s/%s'%(DIR,x) for x in LinesNotEmpty(ss)]
        return res
LeafFiles  = get__LeafFiles  
def LeafDict(d):
    ''' Walking to leaves of a nested dictionary
    '''
    if isinstance(d,dict):
        res = [pyext.LeafDict(dd) for dd in d.values()]
        res = sum(res,[])
        return res
    else:
        if isinstance(d,list):
            pass
        else:
            d = [d]
        return d
    
def LinesNotEmpty(sub):
    sub = [ x for x in sub.splitlines() if x]
    return sub

def meta__label(geneMeta,geneInfo,indexName='GeneAcc'):
    geneInfo = geneInfo.copy()
    geneInfo.index = geneInfo.index.str.split('.').str.get(0)
    geneInfo = pyext.mergeByIndex( geneInfo, geneMeta,how='left')
    geneInfo.index.name = indexName
    return geneInfo

def dict2flat(dct,sep='_',concat='='): 
    ''' Pack a depth-1 dictionary into flat string
    '''
    s = sep.join(['%s%s%s'%(k,concat,v) for k,v in dct.items()])
    return s

def mergeByIndex(left,right,how='outer',as_index = 0, **kwargs):
    dcts = [{'name': getattr(left,'name','left')},
            {'name': getattr(right,'name','right')},
           ]
    suffixes = ['_%s'%x for x in map(pyext.dict2flat,dcts)]

    df = pd.DataFrame.merge(left,right,
                       how = how,
                        left_index=True,
                        right_index=True,
                       suffixes= suffixes
                      )
    if as_index:
        df = df.iloc[:,:1]
    return df

if __name__=='__main__':
    def test_d(d):
        try:
            return LeafFiles(d)
        except Exception as e:
            print e
    ##### To be refactored to work everywhere
    d = '/home/feng/test_envs/tdir/something/A/B/C/D/'
    test_d(d)
    d = '/home/feng/test_envs/tdir/something/'
    print test_d(d)
    d = '/home/feng/syno3/PW_HiSeq_data/ChIP-seq/Raw_data/182C/Bd_ELF3-44645602/FASTQ_Generation_2018-06-06_03_43_21Z-101158414/182C_721_L001-ds.e1f926b50b5f4efd99bcffeca5fb75a0'
    print test_d(d)
    d = '/home/feng/syno3/PW_HiSeq_data/ChIP-seq/Raw_data/182C/Bd_ELF3-44645602/FASTQ_Generation_2018-06-06_03_43_21Z-101158414/182C_721_L001-ds.e1f926b50b5f4efd99bcffeca5fb75a0/Bd-ELF3OX-SD-ZT16-_S2_L001_R1_001.fastq.gz'
    # print test_d(d)
    LeafFiles(d)

def log2p1(x):
    return np.log2(1. + x)

def log2p1_ln2(x):
    y  = np.log2(1 + np.log(2)*x)
    return y

def entropise(ct,axis=None, normed=0):
    ''' Transform count into -p *logP, summation of which is entropy
'''
    if not normed:
        p = ct/np.sum(ct,axis=axis,keepdims=True)
    else:
        p = ct
    logP = np.nan_to_num(np.log2(p))
    r = p * - logP    
    return r

def getH(proba,axis = None):
    part = pynp.logsumexp(proba, axis=axis,keepdims=1)
    proba = proba - part
    proba = np.exp(proba)
    H = entropise(proba,axis=axis,normed=1).sum(axis=axis)    
    return H

def canonic_npy(s):
    f = lambda s: s if s.endswith('.npy') else '%s.npy'%s
    res = pyfop.safeMap(f,s)        
    return res

dict__update = util__fileDict.dict__update

def dict__wrap(d):
    for k in d.keys():
        d[k] = [d[k]]
    return d
def dict__combine(dcts):
    for i,d in enumerate(dcts): 
        if i==0:
            res = dict__wrap(d)
        else:
            dict__wrap(d)
            for k in d.keys():
                if k not in res.keys():
                    res[k] = d[k]
                else:
                    res[k] += d[k]
    return res

# ##### Multiprocessing map
# import multiprocessing as mp
# def mp_map(f,lst,n_cpu=1, chunksize= None, callback = None, 
#            NCORE=None,
# #            kwds = {}, 
#            **kwargs):
#     if NCORE is not None:
#         n_cpu = NCORE
#     if n_cpu > 1:
#         p = mp.Pool(n_cpu,**kwargs)
#         OUTPUT=p.map_async(f,lst, chunksize=chunksize, 
# #                            kwds = kwds,
#                            callback = callback).get(999999999999999999) ## appx. 7.6E11 years
# #         OUTPUT = p.map(f,lst)
#         p.close()
#         p.join()
#     else:
#         OUTPUT = map(f,lst)
#     return OUTPUT

def MapWithCache(f,it,ALI='Test',nCPU=1,force=0):
    print ('[MSG] Mapping function:   Under cahce alias: %s'%(ALI))
    fmt = '%s_%%05d'%(ALI)
    def cb(resLst):
        for i,res in enumerate(resLst):
            fname = canonic_npy([fmt%i])[0]
            np.save(fname,res)    
            print 'Saving to %s'%fname
        return resLst
    fname = canonic_npy([fmt%0])[0]
    print (fname)
    if os.path.exists(fname) and not force:
        res = np.load(fname).tolist()
        p = None
    else:        
        p = mp.pool.ThreadPool(nCPU)        
        res = p.map_async(f,it,callback=cb)
    return res,p


#### Data Reader
##### Import data
#### Guesses

import urllib
import io

def readBaseFile(fname,baseFile=1, **kwargs):
    res = pyext.readData(fname,baseFile=baseFile, **kwargs)
    return res

def read__dill(fname, **kwargs):
    with open(fname,'rb') as f:
        return dill.load(f, **kwargs)
    
def readData(
    fname, 
    ext=None, callback=None, 
    addFname=0, addFname_COL='fname',
    guess_index=1, columns = None,
    localise = False,
    remote = None,
    as_buffer = False,
    baseFile = 0,
    comment='#', 
    **kwargs):
            
    if ext is not None:
        pass
        fhead = fname
    else:
        fhead,ext = pyext.guess_ext(fname,check = 1)
        
    if isinstance(fname,basestring):
        #if baseFile:
        fname= pyext.base__file(fname,baseFile=baseFile)
        if remote is None:
            protocols = [ 'http://','ftp://' ] 
            if fname[:4] in [ x[:4] for x in protocols ]:
                remote = True
        if remote:
            f = fname = io.BytesIO(urllib.urlopen(fname).read())
            if localise:
                fname = pyext.localise(fname)
            
        
    if as_buffer:
        fname = pymisca.io_extra.unicodeIO(buf=fname)
        
#     ext = ext or guess_ext(fname,check=1)[1]
#     kwargs['comment'] = comment    
    class space:
        fheadd = fhead
        _guess_index=guess_index
    
    
        
    def case(ext,):

        if ext == 'csv':
            res = pd.read_csv(fname, comment = comment, **kwargs)
        elif ext in ['tsv','tab','bed','bdg','narrowPeak',
                     'summit','promoter',
                     'count', ### stringtie output
                     'txt', ### cufflinks output
                     'stringtie',
                     'star-quantseq',
                     'excel',
                    ]:
            res = pd.read_csv(fname, comment = comment, sep='\t', **kwargs)
#             res = pd.read_table(fname, comment = comment, **kwargs)
            if ext in ['count', 'stringtie','tab',]:
                res.rename(columns={'Gene ID':'gene_id',
                                   'Gene Name':'gene_name',
                                   },inplace=True)
            ### for tophat
            for col in ['tracking_id','Gene ID']:
                if col in res.columns:
                    res['gene_id'] =res[col]
#             if 'tracking_id' in res.columns:
#                 res['gene_id'] = res['tracking_id']
#             if 'Gene ID' in res.columns
            if ext == 'cufflinks':
                pass
        elif ext == 'dill':
            res = pyext.read__dill(fname,**kwargs)
            space._guess_index=0
        elif ext == 'pk':
            res = pd.read_pickle(fname,**kwargs)
        elif ext == 'pandas-json':
            res = pd.read_json(fname,**kwargs)
        elif ext == 'json':
            res = pyext.read_json(fname,**kwargs)
            space._guess_index=0
        elif ext == 'npy':
            res = np.load(fname,**kwargs)
            space._guess_index=0
        elif ext == 'it':
            res = fname
            if not hasattr(res,'readline'):
                res = open(res,'r')
                res = pymisca.io_extra.unicodeIO(handle=res)
#             res = ( x for x in fname)
            space._guess_index=0
            
#             .tolist()
        else:
            space.fheadd, ext = pyext.guess_ext( space.fheadd, check=1)            
            res = case(ext,)[0]
#             if ext is None:
#         elif ext is None:            
#         or ext=='txt':
#         else:
#             assert 0,"case not specified for: %s"%ext
        if remote:
            f.close()
        return res,ext
    
    try:    
            
        res,ext = case(ext)
        if ext in ['npy',]:
            guess_index=0
            
    except pd.errors.EmptyDataError as e:
        if columns is None:
            print('[ERR] Cannot guess columns from the empty datafile: %s'%fname)
            raise e
        else:
            res = pd.DataFrame({},columns=columns)
            
    if columns is not None:
        _columns = res.columns.tolist()
        L = min(len(columns),len(_columns))
        _columns[:L] = columns[:L]
        res.columns = _columns
        
    if space._guess_index:
        res = pyext.guessIndex(res)
    if callback is not None:
        res = callback(res)
#         res = res.apply(callback)
    if addFname != 0:
        if callable(addFname):
            fname = addFname(fname)
        res[addFname_COL]=fname
    return res


def guess_ext(fname,check = 1):
#     print fname
    gp = fname.rsplit('.',1)
    if len(gp)>1:
        fname,ext = gp
#         ext = gp[-1]
    else:
        fname = fname
        ext = None
    if check:
        assert ext is not None,"Can't guess filetype of: '%s'"%fname
        
    return (fname,ext)

def guess_sep(fname):
    ''' Guess separator from extension
'''
    basename,ext = fname.rsplit('.',1)
    if ext == 'csv':
        sep = ','
    elif ext in ['tsv','tab','bed','bdg','narrowPeak',
                'summit','promoter',]:
        sep = '\t'
    else:
        raise Exception("Cannot guess separator of file type: \
        '.%s'"%ext)
    return sep


def splitPath(fname,level=1,
#               sep=u'/'
             ):
    if level is not None:
        tail = []
        head = fname
#         level_ = 
        if level < 0:
            head = head[::-1]
        for i in range(abs(level)):
#             if level > 0 :
            head,tail_ = os.path.split(head)
            tail += [tail_]
#             if level < 0:
#                 tail_, head = os.path.split(head)
#                 tail += [tail_]
                
#         tail = os.path.join(*tail[:: -cmp(level,0)])
        tail = os.path.join(*tail[:: -1])
        if level < 0:
            head,tail = head[::-1],tail[::-1]
            head,tail=tail,head
    else:
        head = u''
        tail = fname
        
    return head, tail
# sep.join(tail[::-1])

def guessIndex(df):
    if df[df.columns[0]].dtype == 'O':
        df.set_index(df.columns[0],inplace=True)
    return df

def uri__resolve(uri,baseFile = 0, level=None):
    #if baseFile:
    uri = pyext.base__file( uri,baseFile=baseFile)
            
    assert len(uri) > 0
    remote = False
    protocols = [ 'http://','ftp://','https://',] 
    if uri[:4] in [ x[:4] for x in protocols ]:
        remote = True
    if not remote:
#     if uri[0] in [ '.','/' ]:
        uri = 'file://' + uri
    
#     if level is not None:
#         uri = pyext.splitPath(
#             uri, level=level)
    return uri
        

def localise(uri,ofname= None,silent = 1, level=1, baseFile = 0,prefix='-LC -'):
    uri = pyext.uri__resolve(uri, baseFile=baseFile)
    if ofname is None:
        head, ofname = pyext.splitPath(
            uri, level=level)
        
    ddir =  os.path.dirname(ofname)
    if ddir:
        if not os.path.exists(ddir):
            os.makedirs( ddir )
    cmd = 'curl {prefix} "{uri}" -o {ofname}'.format(**locals()).format(**locals())
    log = pysh.shellexec(cmd,silent=silent)
    return ofname


def file__size(uri,baseFile=0,silent=1):
    '''
    Get file size from header of response
    Source: https://stackoverflow.com/a/4498128/8083313
    '''
    uri = pyext.uri__resolve(uri, baseFile=baseFile)
#     uri = urllib.quote(uri.replace('\\','')    
    if uri.startswith('file://'):
        fname = uri.replace('file://','')
        if not os.path.exists(fname):
            res = 0
        else:
            res = os.path.getsize(fname)
    else:
        #### Use curl if file is not local
        CMD = "curl -sI {uri} | awk '/Content-Length/ {{ print $2 }}'".format(**locals())
        res = pysh.shellexec(CMD,silent=silent).strip()
        
    if not res:
        res = 0
    res = int(res)
    return res



#### Class defs


class Directory(object):
# class Directory(pymisca.patch.FrozenPath):
    def __init__(self, 
                 DIR, baseFile=0, 
                 *args,**kwargs):
#         super(Directory,self).__init__(*args,**kwargs)
        assert isinstance(DIR,basestring)
        self.DIR_ = DIR
        self.baseFile = baseFile
        
    def toJSON(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return self.toJSON()

    def __setstate__(self, d):
        self.__dict__.update(d) # I *think* this is a safe way to do it
            
    @property
    def DIR(self):
        DIR = self.DIR_
        if self.baseFile:
            DIR = pyext.base__file(self.DIR_, self.baseFile)
        else:
            pass
        return DIR
        
    def getFiles(self,key):
        key = os.path.join( self.DIR, key)
        res  =glob.glob(key)
        res = sorted(res)
        return res
    
    def getFile(self,key,default= None,commonprefix=None,common_prefix=1,raw=0):
        '''
        raise Exception if file cannot be found
        '''
        
        #### legacy
        if commonprefix is not None:
            common_prefix = commonprefix
        #### legacy
            
        res = self.getFiles(key)
        if len(res) == 0:
#             if force:
            if default is not None:
                return default
        
            raise Exception('File does not exists:%s in %s' % (key, self.DIR_))                        
        elif len(res)==1:
            res = res[0]
        else:
            if common_prefix:
                res = os.path.commonprefix(res)

        return res
            
    def hasFile(self,key,force=0):
        key = os.path.join( self.DIR, key)
        res = os.path.exists(key)
        return res
    
#### pynorm
def dist2ppf(vals):
    '''Estimate percentile locations from a sample from distribution
'''
    ### for some reason you need to argsort twice.....
    idx = np.argsort(np.ravel(vals)).argsort()
#     od = idx.argsort()
#     idx = od
#     idx = np.arange(len(vals))[od]
    per = (idx+0.5)/(max(idx)+1)
    if isinstance(vals,pd.Series):
        per = pd.Series(per,index=vals.index, name=vals.name)
    return per
####


def funcs__reduceWithPath(funcNames,force=1,funcDict=None, outDir='.',
                          stack_kw = {}, initial=None
                         ):
    '''
    Evaluate a list of functions according to their names
    '''
    if funcDict is None:
        funcDict = pyext.runtime__dict()
        
    _stack_kw = dict(printOnExit=False,debug=False)
    _stack_kw.update(stack_kw)

    stack  = pyext.contextlib2.ExitStack()
    d = pyext.FrozenPath(outDir)
    d = d.abspath()
    resList = []
    for i,funcName in enumerate(funcNames):
        d = d/funcName
        for k,v in _stack_kw.items():
            setattr(d,k,v)
            
        d.makedirs_p()
        
        stack.enter_context(d)
        if 1:
            func = funcDict[funcName]
            if i==0:
                lastRes = initial
            try:
                lastRes = func(lastRes,force=force)
            except Exception as e:
                print ('[errored] in:"%s"'%d)
                raise e
        resList.append( lastRes )
        
    stack.close()
    return lastRes

def arr2d__pctransform(xs,ys,silent=1,ax=None,index=None):
    X = np.vstack([xs,ys]).T
    pca = pymisca.sklearn_extra.pca__fitPlot( X,silent=silent,ax=ax)
    mdl = pymisca.sklearn_extra.pca__alignToPrior(mdl=pca, prior=[[1,1],[-1,1]],silent=silent)[0]    
    coords = mdl.transform(X)
    columns = ['PC{i}'.format(i=i) for i in range(X.shape[1])]
    coords = pd.DataFrame(coords,index,columns)
    return coords, mdl

#### ported from util.py
def saveFigDict(figs,DIR=None,exts=['svg'],silent=1,
                transparent=False,
               **kwargs):
    if DIR is None:
        DIR = os.environ.get('HOME',None)
        assert DIR is not None, 'cannot get environment variable:$HOME'
        DIR = '%s/cache/plots' % (DIR)
    DIR = path.Path(DIR).makedirs_p()
    ofnames = []
    for bname,fig in figs.items():
        noEXT = DIR / bname
        for ext in exts:
            ofname = '%s.%s'%(noEXT,ext)           
            fig.savefig(ofname,
                        bbox_inches='tight',
                        transparent= transparent,
                        facecolor=fig.get_facecolor(),
                        **kwargs
                       )
            ofnames += [ofname]
    fignames = ofnames
    l = locals()
    return {x: l.get(x) for x in ['DIR','fignames']}
