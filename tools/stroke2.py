"""바깥 외곽선 굵기 통일 (4배로 키워서 정밀하게 계산 후 다시 줄임)"""
import numpy as np
from PIL import Image
from scipy import ndimage
T=np.array([107,68,42],float); U=4
def _ink(a):
    L=0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
    return (a[...,3]>128)&(L<110)&(a[...,0]>a[...,2])&(a[...,1]<0.75*a[...,0]+10)
def measure_big(a,ink=None):
    sil=a[...,3]>128
    if ink is None: ink=_ink(a)
    dist=ndimage.distance_transform_edt(sil); edge=sil&~ndimage.binary_erosion(sil)
    lab,n=ndimage.label(ink)
    ink_r=np.isin(lab,np.unique(lab[edge&ink]))&ink&(dist<20*U)
    inner=ink_r&ndimage.binary_dilation(sil&~ink&(dist>U))
    return float(np.median(dist[inner]))/U if inner.sum()>30*U else None
def measure(im):
    S=im.size[0]; a=np.array(im.convert('RGBA').resize((S*U,S*U),Image.LANCZOS)).astype(float)
    return measure_big(a)
def ink4(orig):
    import ink as I
    S=orig.size[0]; m,_=I.ink_mask(np.array(orig.convert('RGBA')).astype(float))
    return np.array(Image.fromarray((m*255).astype(np.uint8)).resize((S*U,S*U),Image.BILINEAR))>127
def unify(im,target=6.5,orig=None):
    S=im.size[0]; pad=8*U
    a0=np.array(im.convert('RGBA').resize((S*U,S*U),Image.LANCZOS)).astype(float)
    w=measure_big(a0,ink4(orig) if orig is not None else None)
    if w is None: return im,None
    a=np.zeros((S*U+2*pad,S*U+2*pad,4)); a[pad:pad+S*U,pad:pad+S*U]=a0
    al=a[...,3]/255; sil=al>0.5; k=(target-w)*U
    if k<0:
        d=ndimage.distance_transform_edt(sil)
        a[...,3]=np.minimum(al,np.clip(d+k+0.5,0,1))*255
    elif k>0:
        do=ndimage.distance_transform_edt(~sil)
        sa=np.clip(k-do+0.5,0,1); oa=al+sa*(1-al)
        a[...,:3]=np.where(oa[...,None]>0,(a[...,:3]*al[...,None]+T*sa[...,None]*(1-al[...,None]))/np.maximum(oa,1e-6)[...,None],a[...,:3])
        a[...,3]=oa*255
    img=Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA')
    bb=img.getchannel('A').getbbox(); c=img.crop(bb)
    lim=(S-4)*U
    if c.width>lim or c.height>lim:
        sc=lim/max(c.width,c.height); c=c.resize((round(c.width*sc),round(c.height*sc)),Image.LANCZOS)
    cx=(bb[0]+bb[2])/2-pad; cy=(bb[1]+bb[3])/2-pad
    o=Image.new('RGBA',(S*U,S*U),(0,0,0,0))
    x=int(round(min(max(cx-c.width/2,2*U),S*U-2*U-c.width))); y=int(round(min(max(cy-c.height/2,2*U),S*U-2*U-c.height)))
    o.paste(c,(x,y),c)
    return o.resize((S,S),Image.LANCZOS),w
