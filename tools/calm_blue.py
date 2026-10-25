from PIL import Image
import numpy as np, colorsys, sys
SRC=sys.argv[2] if len(sys.argv)>2 else '/home/claude/hamster-village/press/sprites/'
items=sys.argv[1].split(',');AMT=float(sys.argv[3]) if len(sys.argv)>3 else 0.45
for n in items:
    im=Image.open(SRC+n+'.webp').convert('RGBA');a=np.array(im).astype(float)/255
    hsv=np.array(Image.fromarray((a[...,:3]*255).astype(np.uint8)).convert('HSV')).astype(float)/255
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    blue=(h>0.52)&(h<0.75)&(s>0.25)
    # 부드럽게: 파란 부분만 채도 45% 낮추고, 진한 남색은 살짝 밝게
    w=np.clip((s-0.25)/0.15,0,1)*blue
    s2=s*(1-AMT*w); v2=np.where(blue, v+(1-v)*0.18*w*(v<0.6), v)
    hsv2=np.stack([h,s2,v2],-1)
    rgb=np.array(Image.fromarray((hsv2*255).clip(0,255).astype(np.uint8),'HSV').convert('RGB')).astype(float)/255
    out=np.concatenate([rgb,a[...,3:]],-1)
    Image.fromarray((out*255).astype(np.uint8),'RGBA').save('calm/'+n+'.webp','WEBP',quality=90,method=6)
