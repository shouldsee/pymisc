
import pymisca.models as pymod
import pymisca.numpy_extra as pynp
import pymisca.ext as pyext
import copy
import functools
np  = pynp.np
def _betas(i,start=0.,step=1.):
    res = start + i * step
    return res

class callback__stopAndTurn(object):
    def __init__(self, interval = 1, cluMin = 2, burnin = 10,
                 afterTurn = 50,
                 turning = False,
                 start=None,step = None,
                betas = None):
        self.interval = interval
        self.cluMin  = cluMin
        self.burnin = burnin
        if betas is None:
            assert start is not None
            assert step is not None
            betas = functools.partial( _betas, start=start,step=step)
#             betas = lambda i: start + i * step
        self.turning = turning
        self.betas = betas
        self.lastTurn = None
        self.right= None
        self.left = None
        self.stats = []
        self.betaHist = []
        self.cluNum = []
        self.H = []
        self.clusterH = []
#         self.mode = 'lr'
        self.mode = 'r'
        self.interval = 1
        self.mdls = []
#     def betas(self,i ):
#         res =  self.start
        
    def __getstate__(self):
        d = dict(self.__dict__)
#         del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d) # I *think* this is a safe way to do it
        
    def saveModel(self,  *args):
        iteration, weight, distributions, log_likelihood, log_proba = args
        if not iteration % self.interval:
            mdl = pymod.MixtureModel(weights=weight,
                                   dists= distributions,
                                   lastLL = log_likelihood,)
            self.mdls.append( 
                [ iteration, copy.deepcopy(mdl) ]
                      )
        return args      
    def __call__(self,*args):
        iteration, weight, distributions, log_likelihood, log_proba = args
        if iteration > self.burnin:
#             if not iteration % self.interval:
            cluNum = len(set(np.argmax(log_proba,axis=1)))
            self.cluNum.append(cluNum)
#             stat = cluNum
            part = pynp.logsumexp(log_proba,axis=1,keepdims=1)
            proba = np.exp(log_proba - part)
            H = pyext.entropise(proba,normed=1,axis=1).sum(axis=1,keepdims=1)
            stat = H.std()
            resp = proba/proba.sum(axis=0,keepdims=1) 
            clusterH = (H * resp).sum(axis=0)
            beta = distributions[0].beta
            self.betaHist.append(beta)
            self.stats.append(stat)
#             self.H.append(H.ravel())
            self.clusterH.append(clusterH)
            self.saveModel(*args)
            
            if not self.turning:
                beta = self.betas(iteration)
                if self.right is None:
                    if cluNum >= self.cluMin:
                        self.rightIter  = self.lastTurn = iteration

                        print ('[cbk]iter={iteration}: beta={beta:.3E} \
                        Cluster multiplexing'.format(**locals()))
                        self.right = beta
                    
            else:
                if self.right is None:
                    if cluNum >= self.cluMin:
                        self.rightIter  = self.lastTurn = iteration

                        print ('[cbk]iter={iteration}: Now going left.'.format(**locals()))
                        self.right = beta
                elif self.left is None:
                    if cluNum < self.cluMin:
                        self.lastTurn = iteration
                        self.leftIter = self.rightIter *2 - iteration
                        self.left = beta
                        print ('[cbk]iter={iteration}: Now going right.'.format(**locals()))
                        self.going = 'right'

                if self.right is None:
                    beta = self.betas(iteration)
        #             self.turnBeta = beta
                else:
                    if self.left is None:
                        self.going = 'left'

                    if self.going == 'left':
                        vit = self.rightIter - ( iteration -  self.lastTurn)
                        beta = self.betas(vit)
                    else:
                        vit =  self.leftIter + (  iteration - self.lastTurn  )
                        beta = self.betas(vit)

        #                     self.lastTurn = iteration
        #                 beta = np.random.uniform(self.left,self.right)
                    if (beta > self.right) and ('l' in self.mode):
                        self.going = 'left'
                        self.lastTurn = iteration
                        print ('going %s' % self.going)

                    if beta < self.left and ('r' in self.mode):
                        self.going = 'right'
                        self.lastTurn = iteration
                        print ('going %s' % self.going)

#                     args = (-1, ) + args[1:]
        elif iteration <= self.burnin:
            beta = self.betas(iteration)
        
        for d in distributions:
            d.beta = beta
        return args
    
import pymisca.vis_util as pyvis
plt = pyvis.plt
def qc__vmf(mdl=None,
            callback = None,
            nMax=-1,
            xunit = None,
           ):
    if callback is None:
        assert mdl is not None
        callback = mdl.callback
#     n = 4000
#     xmax = 1.0
    fig,ax = plt.subplots(1,1,figsize=[14,10])
    if xunit is not None:
        xs = getattr(callback,xunit)
    else:
        xs = np.arange(len(callback.betaHist))
    axs = pyvis.qc_2var(*np.broadcast_arrays(np.array(xs)[:,None], 
                                             callback.clusterH)
                       ,nMax=nMax,axs=[None,ax,None,None])

    plt.sca(axs[1])
    # plt.figure()
    ax = plt.gca()
    plt.plot(xs,callback.stats,'ro')
    ax.set_xlim(0,None)
#     plt.plot(xs[-nMax:],callback.stats[-nMax:],'ro')
    tax = ax.twinx()
    tax.plot(xs,callback.cluNum,'go')
#     tax.plot(xs[-nMax:],callback.cluNum[-nMax:],'go')
    # tax.set_xlim(0,0.4)
    tax.set_ylim(0,25)