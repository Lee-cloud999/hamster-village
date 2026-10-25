from PIL import Image
import numpy as np, sys, os
from scipy import ndimage
SRC=sys.argv[1] if len(sys.argv)>1 else '/home/claude/hamster-village/press/sprites/';OUT=sys.argv[2] if len(sys.argv)>2 else 'soft/'
T=np.array([176,128,92],float)   # 부드러운 연갈색
EDGE_ONLY={'fence_6.webp','snack_3.webp','snack_1.webp','bowl_1.webp','bowl_5.webp','snack_5.webp','bowl_2.webp','hammock_5.webp','bed_6.webp'}
def soften(p,edge_only=False):
    a=np.array(Image.open(p).convert('RGBA')).astype(float)
    r,g,b,al=a[...,0],a[...,1],a[...,2],a[...,3]
    L=0.299*r+0.587*g+0.114*b
    brown=(r-b>22)&(r>=g)
    dark=(L<105)&brown&(al>0)
    thick=ndimage.binary_opening(dark,structure=np.ones((6,6)))
    line=dark&~ndimage.binary_dilation(thick,iterations=1)
    # soft weight by darkness, extend 1px for antialias
    zone=ndimage.binary_dilation(line,iterations=1)&(L<150)&brown
    if edge_only:
        sil=al>20
        rim=sil&~ndimage.binary_erosion(sil,iterations=4)
        zone=zone&rim&(r-b>40)
    w=np.clip((150-L)/90,0,1)*zone
    for k in range(3):a[...,k]=a[...,k]*(1-w)+T[k]*w
    return Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA')
for f in sorted(os.listdir(SRC)):
    soften(SRC+f,f in EDGE_ONLY).save(OUT+f,'WEBP',quality=90,method=6)
