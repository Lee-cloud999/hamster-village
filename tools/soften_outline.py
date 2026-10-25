from PIL import Image
import numpy as np, sys, os
from scipy import ndimage
SRC=sys.argv[1];OUT=sys.argv[2];os.makedirs(OUT,exist_ok=True)
T=np.array([176,128,92],float)   # 부드러운 연갈색
PROTECT={'fence_6','snack_3','snack_1','bowl_1','bowl_5','snack_5','bowl_2','hammock_5','bed_6','hammock_4','bed_5'}
COOL={'wheel_2'}
ACORN={'snack_1','bowl_1'}
def run(p,name):
    a=np.array(Image.open(p).convert('RGBA')).astype(float)
    r,g,b,al=a[...,0],a[...,1],a[...,2],a[...,3]
    L=0.299*r+0.587*g+0.114*b
    sil=al>40
    # 1) 바깥 테두리: 실루엣 가장자리 4px 안의 어두운 선은 전부 연갈색
    rim=(al>0)&~ndimage.binary_erosion(sil,iterations=4)
    w_rim=np.clip((150-L)/45,0,1)*rim
    # 2) 안쪽 선: 어두운 갈색·검정 선 (가늘거나 굵어도), 보호 그림은 건너뜀
    if name in ACORN:
        # 도토리: 모자처럼 굵게 칠한 진한 부분은 두고, 가는 선만 연갈색
        dark=(L<78)&sil
        yy,xx=np.mgrid[-3:4,-3:4];disk=(yy**2+xx**2)<=9
        thick=ndimage.binary_opening(dark,structure=disk)
        thin=dark&~ndimage.binary_dilation(thick,iterations=1)
        zone=ndimage.binary_dilation(thin,iterations=1)&(L<120)
        w_in=np.clip((125-L)/50,0,1)*zone
        # 선이 만나는 곳에 남은 작은 진한 점도 지우기
        left=(L<80)&sil&(w_in<0.5)&~thick
        lab,n=ndimage.label(left)
        if n:
            sz=ndimage.sum(left,lab,range(1,n+1));small=np.isin(lab,1+np.where(sz<150)[0])
            small=ndimage.binary_dilation(small,iterations=1)&(L<120)
            w_in=np.maximum(w_in,np.clip((125-L)/50,0,1)*small)
        # 도토리 사이 틈에 낀 아주 진한 덩어리(선이 뭉친 곳)도 연갈색
        blob=ndimage.binary_dilation((L<52)&sil,iterations=1)&(L<95)
        w_in=np.maximum(w_in,np.clip((105-L)/45,0,1)*blob)
    elif name in PROTECT: w_in=np.zeros_like(L)
    else:
        warm=(r>=b-5)
        cool=((b>r+10)&(L<115)) if name in COOL else np.zeros_like(sil)   # 회전목마 파란 말의 남색 선
        line=(((L<120)&warm)|cool)&sil
        w_in=np.clip((130-L)/40,0,1)*line
    w=np.maximum(w_rim,w_in)
    for k in range(3):a[...,k]=a[...,k]*(1-w)+T[k]*w
    return Image.fromarray(a.clip(0,255).astype(np.uint8),'RGBA')
for f in sorted(os.listdir(SRC)):
    if f.endswith('.webp'):run(SRC+f,f[:-5]).save(OUT+f,'WEBP',quality=90,method=6)
