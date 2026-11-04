"""Makes the app icons and launch screens from assets/icon-1024.png and assets/mascot.png."""
import os
from PIL import Image, ImageDraw
import numpy as np
here=os.path.dirname(os.path.abspath(__file__));A=os.path.join(here,'..')
icon=Image.open(os.path.join(A,'assets','icon-1024.png')).convert('RGB')        # App Store icons must have no transparency
bee=Image.open(os.path.join(A,'assets','mascot.png')).convert('RGBA')
# iOS app icon
icon.save(os.path.join(A,'ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png'))
# honey gradient + honeycomb + bee: launch screen
def honey(w,h):
    y,x=np.mgrid[0:h,0:w];t=np.clip((x/w)*.45+(y/h)*.55,0,1)[...,None]
    g=(np.array([255,224,74.])*(1-t)+np.array([255,154,31.])*t).astype(np.uint8)
    im=Image.fromarray(g,'RGB').convert('RGBA');m=Image.new('L',(w,h),0);d=ImageDraw.Draw(m);s=max(w,h)/1024*4.4;tw,th=56*s,97*s
    for j in range(-1,int(h/th)+2):
        for i in range(-1,int(w/tw)+2):
            ox,oy=i*tw,j*th;P=lambda px,py:(ox+px*s,oy+py*s)
            d.line([P(28,1),P(54,16),P(54,47),P(28,62),P(2,47),P(2,16),P(28,1)],fill=255,width=max(2,int(2.5*s/2)));d.line([P(28,62),P(28,97)],fill=255,width=max(2,int(2.5*s/2)))
    l=Image.new('RGBA',(w,h),(255,255,255,0));l.putalpha(m.point(lambda v:int(v*.38)));im.alpha_composite(l);return im
def splash(w,h,frac):
    im=honey(w,h);bw=int(min(w,h)*frac);b=bee.resize((bw,int(bee.height*bw/bee.width)),Image.LANCZOS);im.alpha_composite(b,((w-b.width)//2,(h-b.height)//2));return im.convert('RGB')
sp=splash(2732,2732,.22)
for n in ['splash-2732x2732.png','splash-2732x2732-1.png','splash-2732x2732-2.png']:sp.save(os.path.join(A,'ios/App/App/Assets.xcassets/Splash.imageset',n))
# Android launcher icons (legacy + round) and adaptive foreground
res=os.path.join(A,'android/app/src/main/res')
for d,sz in {'mdpi':48,'hdpi':72,'xhdpi':96,'xxhdpi':144,'xxxhdpi':192}.items():
    p=os.path.join(res,'mipmap-'+d);ic=icon.resize((sz,sz),Image.LANCZOS)
    ic.save(os.path.join(p,'ic_launcher.png'))
    mk=Image.new('L',(sz,sz),0);ImageDraw.Draw(mk).ellipse([0,0,sz-1,sz-1],fill=255);r=Image.new('RGBA',(sz,sz));r.paste(ic,(0,0),mk);r.save(os.path.join(p,'ic_launcher_round.png'))
    fs=int(sz*108/48);fg=Image.new('RGBA',(fs,fs),(0,0,0,0));inner=int(fs*.62);fg.paste(icon.resize((inner,inner),Image.LANCZOS),((fs-inner)//2,(fs-inner)//2));fg.save(os.path.join(p,'ic_launcher_foreground.png'))
# Android splash screens
for f in os.listdir(res):
    if f.startswith('drawable'):
        p=os.path.join(res,f,'splash.png')
        if os.path.exists(p):w,h=Image.open(p).size;splash(w,h,.3).save(p)
print('icons and splash screens done')
