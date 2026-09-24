#!/usr/bin/env python3
"""Experimental Bubl four-fisheye -> equirectangular stitcher."""
import argparse,json,sys
from pathlib import Path
import cv2, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "calibration"))
from extract_calibration import extract
NAMES=["topLeft","topRight","bottomLeft","bottomRight"]

def split(im):
    h,w=im.shape[:2]; hh,hw=h//2,w//2
    return {"topLeft":im[:hh,:hw],"topRight":im[:hh,hw:],
            "bottomLeft":im[hh:,:hw],"bottomRight":im[hh:,hw:]}

def rays(W,H):
    x=(np.arange(W,dtype=np.float32)+.5)/W
    y=(np.arange(H,dtype=np.float32)+.5)/H
    lon,lat=np.meshgrid((x*2-1)*np.pi,(.5-y)*np.pi)
    c=np.cos(lat)
    return np.stack([c*np.sin(lon),np.sin(lat),c*np.cos(lon)],-1).astype(np.float32)

def mapping(r,camera,shape,model,mode):
    R=np.asarray(camera["orientation"]["R"],np.float32)
    M=R if mode=="R" else R.T
    q=r@M.T; x,y,z=q[...,0],q[...,1],q[...,2]
    th=np.arccos(np.clip(z,-1,1)); ph=np.arctan2(y,x)
    tm=np.deg2rad(float(camera["fov"]))/2
    rn=th/max(tm,1e-8) if model=="equidistant" else np.sin(th/2)/max(np.sin(tm/2),1e-8)
    h,w=shape[:2]; cc=camera["centre"]; cx=float(cc["x"])*w; cy=float(cc["y"])*h
    rp=rn*(min(w,h)/2)
    mx=cx+rp*np.cos(ph); my=cy-rp*np.sin(ph)
    ok=(th<=tm)&(mx>=0)&(mx<w-1)&(my>=0)&(my<h-1)
    wt=np.clip(1-rn,0,1)**2; wt[~ok]=0
    return mx.astype(np.float32),my.astype(np.float32),ok,wt.astype(np.float32)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("jpg");p.add_argument("thm");p.add_argument("-o","--output",required=True)
    p.add_argument("--width",type=int,default=4096);p.add_argument("--height",type=int,default=2048)
    p.add_argument("--model",choices=["equidistant","equisolid"],default="equidistant")
    p.add_argument("--matrix",choices=["R","RT"],default="RT")
    p.add_argument("--blend",choices=["none","feather"],default="feather")
    p.add_argument("--debug-dir")
    a=p.parse_args()
    if a.width <= 0 or a.height <= 0:
        p.error("width and height must be positive")
    im=cv2.imread(a.jpg)
    if im is None:
        p.error(f"cannot read JPEG: {a.jpg}")
    if min(im.shape[:2]) < 4:
        p.error("source image is too small for a four-view mosaic")
    qs=split(im); C=extract(a.thm); rr=rays(a.width,a.height)
    if any(name not in C["cameras"] for name in NAMES):
        p.error("calibration is missing one or more camera entries")
    acc=np.zeros((a.height,a.width,3),np.float32);ws=np.zeros((a.height,a.width),np.float32)
    first=np.zeros_like(acc);have=np.zeros((a.height,a.width),bool);cov=np.zeros_like(have,dtype=np.uint8)
    dd=Path(a.debug_dir) if a.debug_dir else None
    if dd:
        dd.mkdir(parents=True,exist_ok=True)
        (dd/"calibration.json").write_text(json.dumps(C,indent=2))
    for n in NAMES:
        mx,my,ok,wt=mapping(rr,C["cameras"][n],qs[n].shape,a.model,a.matrix)
        v=cv2.remap(qs[n],mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        new=ok&~have;first[new]=v[new];have|=ok;cov+=ok.astype(np.uint8)
        acc+=v.astype(np.float32)*wt[...,None];ws+=wt
        if dd:
            s=v.copy();s[~ok]=0;cv2.imwrite(str(dd/f"camera_{n}.jpg"),s)
            cv2.imwrite(str(dd/f"quadrant_{n}.jpg"),qs[n])
    feather=np.clip(acc/np.maximum(ws,1e-8)[...,None],0,255).astype(np.uint8)
    feather[ws<=0]=0
    no_blend=np.clip(first,0,255).astype(np.uint8)
    out=no_blend if a.blend=="none" else feather
    if not cv2.imwrite(a.output,out,[cv2.IMWRITE_JPEG_QUALITY,95]):
        p.error(f"cannot write output: {a.output}")
    if dd:
        cv2.imwrite(str(dd/"coverage.png"),np.clip(cov/4*255,0,255).astype(np.uint8))
        cv2.imwrite(str(dd/"no_blend.jpg"),no_blend)
        cv2.imwrite(str(dd/"feather.jpg"),feather)
    print("Experimental geometry: validate model/matrix/quadrant orientation visually.")

if __name__=="__main__": main()
