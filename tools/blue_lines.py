from PIL import Image
import numpy as np, sys, os
from scipy import ndimage
T=np.array([176,128,92],float)
src,mode,names=sys.argv[1],sys.argv[2],sys.argv[3].split(',')
yy,xx=np.mgrid[-4:5,-4:5];disk=(yy**2+xx**2)<=16
yy2,xx2=np.mgrid[-6:7,-6:7];disk2=(yy2**2+xx2**2)<=36
for n in names:
    a=np.array(Image.open(src+n+'.webp').convert('RGBA')).astype(float)
    r,g,b,al=a[...,0],a[...,1],a[...,2],a[...,3];L=0.299*r+0.587*g+0.114*b
    sil=al>40
    cool=(b>r+8)&sil
    if mode=='water':
        core=ndimage.binary_opening(cool&(L>150),iterations=2)
        near=ndimage.binary_dilation(core,iterations=7)
        line=(cool|((np.abs(r-b)<25)&sil))&(L<135)&near
        zone=ndimage.binary_dilation(line,iterations=1)&(L<160)&(b>=r-25)&sil
        w=np.clip((165-L)/45,0,1)*zone
    else: # 얇은 남색 선만 (굵게 칠한 남색 면은 그대로)
        neutral=(np.abs(r-b)<22)&sil
        dark=(cool|neutral)&(L<118)
        thick=ndimage.binary_opening(dark,structure=disk2)
        thin=dark&~ndimage.binary_dilation(thick,iterations=1)
        zone=ndimage.binary_dilation(thin,iterations=1)&(cool|neutral)&(L<140)
        w=np.clip((150-L)/40,0,1)*zone
    for k in range(3):a[...,k]=a[...,k]*(1-w)+T[k]*w
    Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA').save('post/'+n+'.webp','WEBP',quality=90,method=6)
