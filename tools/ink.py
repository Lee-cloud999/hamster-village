"""아이템 외곽선(붉은 갈색 크레용 선)을 진갈색 #6b442a 하나로 통일. 크레용 결(밝기 변화)은 살림.
선만 고르는 방법: 아주 어둡고 붉은 픽셀 + 바깥 테두리와 이어진 것 + 넓게 칠한 면(흙·그늘)은 제외(선이 만나 생긴 작은 덩어리는 포함)"""
import numpy as np
from PIL import Image
from scipy import ndimage
T=np.array([107,68,42],float)
def ink_mask(a):
    r,g,b,al=a[...,0],a[...,1],a[...,2],a[...,3]
    sil=al>20; L=0.299*r+0.587*g+0.114*b
    cand=sil&(r<175)&(L<72)&(r-b>40)&(g<0.45*r)
    rim=sil&~ndimage.binary_erosion(sil,iterations=max(3,int(min(a.shape[:2])*0.025)))
    lab,n=ndimage.label(cand)
    keep=np.isin(lab,np.unique(lab[rim&cand]))&cand
    R=max(3,int(min(a.shape[:2])/52)); yy,xx=np.mgrid[-R:R+1,-R:R+1]; disk=(yy**2+xx**2)<=R*R
    thick=ndimage.binary_opening(cand,structure=disk)
    tl,tn=ndimage.label(thick)
    if tn:
        tsz=ndimage.sum(thick,tl,range(1,tn+1))
        big=np.isin(tl,1+np.where(tsz>(R*5)**2)[0])
        keep&=~ndimage.binary_dilation(big,iterations=2)
    keep=ndimage.binary_dilation(keep,iterations=1)&sil&(L<100)&(r>=b)&(g<0.55*r)
    return keep,L
def recolor(im):
    a=np.array(im.convert('RGBA')).astype(float)
    keep,L=ink_mask(a)
    w=np.clip((120-L)/45,0,1)*keep
    ref=np.median(L[keep]) if keep.any() else 55
    shade=np.clip(L/ref,0.6,1.5)[...,None]
    new=np.clip(T*shade,0,255)
    a[...,:3]=a[...,:3]*(1-w[...,None])+new*w[...,None]
    return Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA')

def ink_mask_soft(a):
    """소품용: 외곽선이 연한 갈색(밝기 70~110)이라 기준을 넓힘. 바깥 테두리와 이어진 가는 선만"""
    r,g,b,al=a[...,0],a[...,1],a[...,2],a[...,3]
    sil=al>20; L=0.299*r+0.587*g+0.114*b
    cand=sil&(L<100)&(r-b>35)&(r>g+20)
    edge=sil&~ndimage.binary_erosion(sil,iterations=2)
    lab,n=ndimage.label(cand)
    keep=np.isin(lab,np.unique(lab[edge&cand]))&cand
    R=max(3,int(min(a.shape[:2])/52)); yy,xx=np.mgrid[-R:R+1,-R:R+1]; disk=(yy**2+xx**2)<=R*R
    thick=ndimage.binary_opening(cand,structure=disk)
    tl,tn=ndimage.label(thick)
    if tn:
        tsz=ndimage.sum(thick,tl,range(1,tn+1))
        big=np.isin(tl,1+np.where(tsz>(R*4)**2)[0])
        keep&=~ndimage.binary_dilation(big,iterations=2)
    keep=ndimage.binary_dilation(keep,iterations=1)&sil&(L<120)&(r>b+20)
    return keep,L
def recolor_soft(im):
    a=np.array(im.convert('RGBA')).astype(float)
    keep,L=ink_mask_soft(a)
    w=np.clip((135-L)/45,0,1)*keep
    ref=np.median(L[keep]) if keep.any() else 70
    shade=np.clip(L/ref,0.6,1.5)[...,None]
    new=np.clip(T*shade,0,255)
    a[...,:3]=a[...,:3]*(1-w[...,None])+new*w[...,None]
    return Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA')
