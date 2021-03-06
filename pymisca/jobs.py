import numpy  as np
import pymisca.model_collection.mixture_vmf
_mod1 = pymisca.model_collection.mixture_vmf
qc__vmf = _mod1.qc__vmf

import pymisca.ext as pyext
# import pymisca.shell as pysh
import pymisca.callbacks
import pymisca.models 
# as pycbk
from pymisca.shell import job__shellexec

import pymisca.shell as pysh

import hashlib
import pymisca.fop
# import funcy

def EMMixture__anneal(data,start,end,
                       K = 30,
                       nIter=200,
#                        verbose=1,
                       verbose=4,
                       seed=0,
                       ofname='mdl0.npy',
                       baseDist = None,
                      callbacks = [],
                      **kwargs
                       
                      ):
    assert baseDist is not None
    if isinstance(baseDist,basestring):
        baseDist = getattr(pymisca.models, baseDist)
        
    
    np.random.seed(seed)
#     rstate = np.random.RandomState(seed).get_state()
    D = data.shape[1]
    # betas = np.linspace(0,1000,nIter)
    betas = np.linspace(start,end,nIter)
    
    callback_beta = pymisca.callbacks.callback__stopAndTurn(
        betas=betas)
    callbacks += [callback_beta]
#     callbacks.append(pymisca.callbacks.weight__entropise)
#     callback = pymisca.fop.composeF(callback, pymisca.callbacks.weight__entropise)

    mdl = mdl0 = pymisca.models.EMMixtureModel(
        dists=[ baseDist(D=D) for i in range(K)]
        ).random_init()

    hist = mdl.fit(X=data,verbose=3,
                   max_iters=nIter,min_iters = nIter,
                   callbacks=callbacks,
                   **kwargs

    #                callback=lambda *x:pyext.sys.stdout.write(str(x))
                  )
    mdl.hist  = hist
    mdl.callback = callback_beta
    if ofname is not None:
        np.save(ofname, mdl0)
    return mdl


vmfMixture__anneal = pyext.functools.partial(EMMixture__anneal, 
                        baseDist = 'vmfDistribution')



def job__cluster__mixtureVMF__incr(
    tdf,
    K = 20,
    randomState=0,
    nIter=100,
    nStart=1,
    start=0.1,
    end= 24.0,
    step = None,
    betas = None,
    init_method='random',
    meanNorm=1,
    normalizeSample=0,
    weighted=True,

    alias = 'mdl',
    verbose=0,
):
    data = tdf
    mod = pymisca.model_collection.mixture_vmf
    
    np.random.seed(randomState)
#     betas = lambda i: (i + 1) * 0.00015 + 0.15
#     if betas is not None:
#         nIter = len(betas)

    if step is None:
        step = (end-start)/nIter
    callback = mod.callback__stopAndTurn(
        betas = betas,
        start = start,
        step  = step)
    
#     callback = pyfop.composeF(callback__stopAndTurn(betas=betas),
# #                              callback__stopOnClu(interval=1)
#                              )
    
    ##### casting DataFrame to Array
    if hasattr(data,'values'):
        data0 = data
        data = data.values
    else:
        data0 = None
        
    if 1:
        if meanNorm:
            data = data - data.mean(axis=1,keepdims=1)
    #         data = pyext.meanNorm(data)
        if normalizeSample:
            NORM = pyext.arr__l2norm(data,axis=1,keepdims=0)
            NORM[NORM == 0.] = 1.
            data = data/NORM[:,None]
        
    if data0 is None:
        data0 = data
    else:
        data0.loc[:,:] = data

    mdl0 = mdl = mod.MixtureVMF(
        init_method = init_method,
                        NCORE = 1,
                        meanNorm=0,
#                          beta = betas(0),
                        beta = start,
                         weighted =  weighted,
                         normalizeSample=0,
                        kappa = None,
                        K = K,)
        
    res = mdl.fit(
        data0,verbose=verbose,
                  nStart=nStart,
                  callback = callback,
                  min_iters = nIter,
                  max_iters = nIter,
                  sample_weights=None,
                 )    
    np.save(alias + '.npy',mdl0,)
    return mdl0



def wigFile__filter(ifname, ODIR='.', ofname = None, awk='$5>20'):

    if ofname is None:
        ofname=  pyext.getBname(ifname) + '.bed'
    p = pipe__wig2bed(fname=ifname)
    p = pysh.shellpopen("awk '{awk}' | tee \"{ODIR}/{ofname}\" | head ".format(**locals()), p.stdout,)
    
    
    resHead = pysh.pipe__getSafeResult(p)
    return ofname

def pipe__it2wig2bed(**kw):
    p = pysh.ShellPipe()
    p.chain('convert2bed -iwig')
    p.chain('tee test.out')
    p.chain("awk '$5 > 10' ")
    return p

def dir__toHashDir(DIR=None,pathDF = None,
                   suffix='hashed-sha256', hashFunc = lambda x:hashlib.sha256(x).hexdigest(),
                   copy = 1,force=1,
                  **kwargs):
    if pathDF is None:
        assert DIR is not None
        pathDF = pyext.dir__indexify(DIR,**kwargs)
    else:
        if DIR is None:
            DIR = pathDF['DIR'][0]
    res = pathDF
    OUTDIR = DIR.rstrip('/') + '-' + suffix

    res['EXT'] = res['EXT'].map(pyext.os.path.basename)
    res['DATA_ACC'] = res['FILEACC'].str.split('/',1).str.get(0)
    res['SHA256'] = res['FILEACC'].map(hashFunc)
    res['FULL_PATH_HASHED'] = pyext.df__format(res,'{OUTDIR}/{DATA_ACC}-{SHA256}.{EXT}',OUTDIR=OUTDIR)
    mapper = pyext.df__asMapper(res,'FULL_PATH','FULL_PATH_HASHED')
    pyext.file__rename(mapper, copy=copy,force=force)
    
    totalSize = pyext.size__humanReadable(res['SIZE'].sum()*1024**1)
    msg = 'Hashed {res.shape} items, of total size {totalSize}'.format(**locals())    
    return res,msg