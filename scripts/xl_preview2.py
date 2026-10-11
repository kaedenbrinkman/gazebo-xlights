from xl_preview import *
START={'starry_night':2.0,'eye_of_sauron':1.0}
ALL=['rainbow_chase','rafter_spiral','wipe_up','twinkle','breathing','fire','christmas','candlelight_dinner','starry_night','slow_ember_glow','aurora','golden_hour','eye_of_sauron','lantern_fireflies']
cams=[Cam((330,-330,190),(0,0,55),45),Cam((0,70,60),(0,-94,48),105)]
import sys
for nm in (sys.argv[1:] or ALL):
    fr=np.load(f'build/anim_{nm}.npy');s=int(START.get(nm,0)*20);imgs=[]
    for f in range(s,s+100,2):   # 5 s @ 10 fps
        im=Image.fromarray(np.concatenate([cams[0].render(fr[f]),cams[1].render(fr[f])],1)).resize((1000,312),Image.LANCZOS)
        imgs.append(im)
    q=[i.quantize(colors=64,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for i in imgs]
    q[0].save(f'previews/{nm}.gif',save_all=True,append_images=q[1:],duration=100,loop=0,optimize=True)
    import os;print(nm,os.path.getsize(f'previews/{nm}.gif')//1024,'KB')
