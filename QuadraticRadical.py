from copy import deepcopy
import sys
import inspect
from random import randint
from time import sleep
gcd=lambda x,y:x if y==0 else gcd(y,x%y)
p=[]
def euler(n):
    vis=[False]*n
    for i in range(2,n):
        if not vis[i]:
            p.append(i)
        for j in p:
            if i*j<n:
                vis[i*j]=True
            else:
                break
            if i%j==0:
                break
euler(10000000)
print('Preprocessing completed.')
def breakdown(n):
    res={}
    for i in p:
        if n==1:
            break
        if n%i==0:
            res[i]=0
        while n%i==0:
            res[i]+=1
            n//=i
    return res
class QuadraticRadical:
    def __init__(self,
                 numer:int=0,
                 roots:dict[int, int]=None,
                 denom:int=1):
        if roots==None:
            roots={}
        if denom==0:
            raise ZeroDivisionError('division by zero')
        if 1 not in roots:
            roots[1]=numer
        else:
            roots[1]+=numer
        roots={i:roots[i] for i in roots if i!=0 and roots[i]!=0}
        #print(roots)
        for i in roots:
            if i<0:
                raise ValueError('Negative square root is not supported: %d'%i)
        self.n,self.d=roots,denom
        self.simplify()
    @classmethod
    def fromstr(cls, s):
        n,d=s.split('/')
        n=n.removeprefix('(').removesuffix(')')
        tmp=['']
        for x,i in enumerate(n):
            if i in '+-':
                if x==0:
                    tmp[-1]+=i
                else:
                    tmp.append(i)
            else:
                tmp[-1]+=i
        dct={}
        for i in tmp:
            if '√' not in i:
                dct[1]=int(i)
            else:
                v,k=i.split('√')
                dct[int(k)]=int(v)
        return cls(0,dct,int(d))
    def simplify(self):
        #negative
        if self.d<0:
            self.d=-self.d
            self.n={i:-self.n[i] for i in self.n}
        #simplify root
        n={}
        for i in self.n:#{12:1}
            nk,nv=i,self.n[i]
            for j,k in breakdown(i).items():#{2:2,3:1}
                cnt=k//2#1,0
                nk//=j**(cnt*2)
                nv*=j**cnt
            if nk in n:
                n[nk]+=nv
            else:
                n[nk]=nv
        self.n=n#{3:2}
        #reduction
        g=1      
        for i in self.n:
            g1=gcd(self.n[i],self.d)
            if g1==1:
                break
            if g==1:
                g=g1
            else:
                if gcd(g,g1)==1:
                    break
                else:
                    g=gcd(g,g1)
        else:
            self.d//=g
            self.n={i:self.n[i]//g for i in self.n}
    def __repr__(self):
        n,d=self.n,self.d
        if len(n)==0:
            return '0'
        if d==1:
            res='%s'
        else:
            if isinstance(d, int) and d>1:
                res='%s/'+str(d)
            else:
                res='%s/('+str(d)+')'
        sec=''
        for i in sorted(n):
            if sec!='' and n[i]>0:
                sec+='+'
            if i==1:
                sec+=str(n[i])
            else:
                if n[i]==-1:
                    sec+='-'
                elif n[i]!=1:
                    sec+=str(n[i])
                sec+='√%d'%(i)
        if len(n)>1:
            sec='(%s)'%sec
        ret=res%sec
        return ret
    def __str__(self):
        ret=repr(self)
        if len(ret)>200:
            ret=ret[0:200]+'...'+ret[-200:]
        return ret
    # +
    def __roftacd(self,num):
        for i in self.n:
            self.n[i]*=num
        self.d*=num
    def __add__(self,other):
        if isinstance(other,int):
            return self.__class__(other,deepcopy(self.n),self.d)
        if isinstance(other,self.__class__):
            if self.d==other.d:
                n=deepcopy(self.n)
                for i in other.n:
                    if i not in n:
                        n[i]=other.n[i]
                    else:
                        n[i]+=other.n[i]
                return self.__class__(0,n,self.d)
            else:
                a,b=deepcopy(self),deepcopy(other)
                a.__roftacd(other.d)
                b.__roftacd(self.d)
                return a+b
    def __radd__(self,other):
        return self+other
    def __iadd__(self,other):
        return self+other
    # -
    def __neg__(self):
        return self.__class__(0,{i:-self.n[i] for i in self.n},self.d)
    def __sub__(self,other):
        return self+(-other)
    def __rsub__(self,other):
        return -self+other
    def __isub__(self,other):
        return self-other
    # *
    def __mul__(self,other):
        if isinstance(other,int):
            return self.__class__(0,{i:self.n[i]*other for i in self.n},self.d)
        if isinstance(other,self.__class__):
            res=0
            for i in other.n:
                res+=self.__class__(0,
                                    {j*i:self.n[j]*other.n[i] for j in self.n},
                                    self.d*other.d)
            return res
    def __rmul__(self,other):
        return self*other
    def __imul__(self,other):
        return self*other
    # /
    def __findsolve(self,seq,quick=True):
        PN={i:1 for i in seq}
        K=list(seq.keys())
        V=[False for i in K]
        x=0
        res=[]
        cntL, cntE, cntG=0,0,0
        step=0
        while x>=0:
            #print(x,PN,K,V)
            if x==len(K):
                A=self.__class__(0,deepcopy(seq))
                B=self.__class__(0,deepcopy({i:seq[i]*PN[i] for i in PN}))
                C=A*B
                #print(PN,B,C,sep='\n')
                #__import__('time').sleep(0.1)
                if len(C.n)<len(seq):
                    res.append(B)
                    cntL+=1
                    if quick:
                        return res
                elif len(C.n)==len(seq):
                    cntE+=1
                else:
                    cntG+=1
                x-=1
                step+=1
                #if step%100==0:
                    #print('[%d/%d] L%d E%d G%d'%(step,2**len(seq),cntL,cntE,cntG))
                    #sleep(0.02)
                continue
            if PN[K[x]]==1:
                if not V[x]:
                    PN[K[x]]=-1
                    V[x]=True
                    x+=1
                    continue
                else:
                    V[x]=False
                    x-=1
            elif PN[K[x]]==-1:
                PN[K[x]]=1
                x+=1
        #print('L%d E%d G%d'%(cntL,cntE,cntG))
        return res
    def __recur(self,n,d,x=0):
        if len(d.n)==1:
            print('*'*(x+1))
            if 1 not in d.n:
                newn=n*d
                newd=d*d
                return newn,newd
            else:
                return n,d
        #print(n,d)
        sol=self.__findsolve(deepcopy(d.n),1)
        #print(sol)
        if len(sol)==0:
            return None
        for i in sol:
            newn=n*i
            newd=d*i
            #print('*'*(x+1),i,newn,newd)
            res=self.__recur(newn,newd,x+1)
            if res is None:
                continue
            return res
    def __invert__(self):
        if len(self.n)==0:
            ZeroDivisionError('division by zero')
        invn,invd=self.__class__(self.d),self.__class__(0,deepcopy(self.n))
        th=invd[0]*invd[1]+invd[3]#当计算1/(√2+√3+√5+√7+√11+√13)时用这个
        #print(invd*th)
        r=self.__recur(invn*th,invd*th)
        if r is None:
            return self.__class__()
        n,d=r
        #print(n,d)
        return self.__class__(0,deepcopy(n.n),d.n[1])
    '''
    def __invert__(self):
        if len(self.n)==0:
            ZeroDivisionError('dbz')
        n,d=self.__class__(self.d),self.__class__(0,deepcopy(self.n))
        while len(d.n)>1:
            print(n,d)
            newd=deepcopy(d)
            for i in reversed(newd.n):
                newd.n[i]*=-1
                D=d*newd
                if len(D.n)<len(d.n):
                    break
            print(newd)
            n*=newd
            d=D
        print(n,d)
    #'''
    def reciprocal(self):
        return ~self
    def __truediv__(self,other):
        if isinstance(other,int):
            return self.__class__(0,deepcopy(self.n),self.d*other)
        if isinstance(other,self.__class__):
            return self*~other
    def __rtruediv__(self,other):#other/self
        return ~self*other
    def __itruediv__(self,other):
        return self/other
    def __getitem__(self,idx):
        K=list(self.n.keys())[idx]
        return self.__class__(0,{K:self.n[K]},self.d)
seq=[2,3,5,7,11,13,17]
dc={i:1 for x,i in enumerate(seq)}
a=QuadraticRadical(0,dc)
#print(a._QuadraticRadical__findsolve(dc))
#print(a[0])
c=~a
print(a,c)
