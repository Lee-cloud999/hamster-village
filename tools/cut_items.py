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
