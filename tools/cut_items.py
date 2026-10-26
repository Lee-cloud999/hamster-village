import sys,numpy as np
from PIL import Image
from scipy import ndimage
def cut(img):
    a=np.array(img.convert('RGB')).astype(np.int16)
    light=(a.min(2)>228)
    # background = light pixels connected to the border
    lab,n=ndimage.label(light)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border))
    fg=~bg
    # keep the largest object only
    lab2,n2=ndimage.label(fg)
    if n2>1:
        sz=ndimage.sum(np.ones_like(lab2),lab2,range(1,n2+1)); fg=lab2==(np.argmax(sz)+1)
    fg=ndimage.binary_fill_holes(fg)
    # trim the pale fringe: erode 1px, soft edge
    fg=ndimage.binary_erosion(fg,iterations=2)
    alpha=ndimage.gaussian_filter(fg.astype(float),0.8)
    alpha=np.clip((alpha-0.15)/0.7,0,1)
    rgba=np.dstack([a.astype(np.uint8),(alpha*255).astype(np.uint8)])
    im=Image.fromarray(rgba,'RGBA')
    return im.crop(im.getchannel('A').getbbox())
def place(item,frac,S=256):
    m=int(S*frac); it=item.copy(); it.thumbnail((m,m),Image.LANCZOS)
    c=Image.new('RGBA',(S,S),(0,0,0,0)); c.paste(it,((S-it.width)//2,(S-it.height)//2),it); return c

def cut_multi(img,minfrac=0.01):
    """흰 배경 제거, 큰 덩어리와 일정 크기 이상 조각(김, 꼬리표 등)은 함께 남김"""
    a=np.array(img.convert('RGB')).astype(np.int16)
    light=(a.min(2)>228)
    lab,n=ndimage.label(light)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    fg=~np.isin(lab,list(border))
    lab2,n2=ndimage.label(fg)
    if n2>1:
        sz=ndimage.sum(np.ones_like(lab2),lab2,range(1,n2+1)); keep=[i+1 for i,v in enumerate(sz) if v>=sz.max()*minfrac]
        fg=np.isin(lab2,keep)
    fg=ndimage.binary_fill_holes(fg)
    fg=ndimage.binary_erosion(fg,iterations=2)
    alpha=ndimage.gaussian_filter(fg.astype(float),0.8); alpha=np.clip((alpha-0.15)/0.7,0,1)
    im=Image.fromarray(np.dstack([a.astype(np.uint8),(alpha*255).astype(np.uint8)]),'RGBA')
    return im.crop(im.getchannel('A').getbbox())

def clear_holes(im,min_px=40,mean_min=249,std_max=3.7):
    """막힌 칸(잎 사이 틈, 손잡이 고리 안, 안경알 등)에 남은 흰 배경을 투명하게. 크레용 결이 있는 흰 칠(하이라이트·김)은 남김"""
    a=np.array(im.convert('RGBA')).astype(float)
    opaque=a[...,3]>200; white=(a[...,:3].min(2)>232)&opaque
    lab,n=ndimage.label(white); hole=np.zeros(white.shape,bool)
    for k in range(1,n+1):
        m=lab==k
        if m.sum()<min_px: continue
        px=a[...,:3][m]
        if px.mean()>=mean_min and px.std()<=std_max: hole|=m
    if hole.any():
        hole=ndimage.binary_dilation(hole,iterations=1)
        soft=ndimage.gaussian_filter(hole.astype(float),0.8)
        a[...,3]=a[...,3]*(1-np.clip(soft*1.3,0,1))
    return Image.fromarray(a.astype(np.uint8),'RGBA')
