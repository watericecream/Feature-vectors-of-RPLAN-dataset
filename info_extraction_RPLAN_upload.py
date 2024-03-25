import os
import imageio.v2 as imageio
from svgpathtools import svg2paths
import numpy as np
global bai, rtd, tl, sl, PATH, oripath
h=w=256
bai=np.zeros((h,w,3))
bai.astype(int)
bai.fill(255)
#-------custom directory--------
PATH=r'C:\RPLAN'
#按照标签建立字典
rtd={0:'livingroom',1:'masterroom',2:'kitchen',3:'bathroom',
     4:'diningroom',5:'childroom',6:'studyroom',
     7:'secondroom',8:'guestroom',9:'balcony',10:'entrance',
     11:'storage',12:'wallin',13:'whole',14:'exteriorwall',
     15:'frontdoor',16:'interiorwall',17:'interiordoor'}
tl=list(rtd.keys())
sl=[0,1,2,3,4,5,6,7,8,9,10,11,12]
oripath=f'{PATH}/origin'
def extract_info(n_order):
    dic_sample = {}
    impath=f"{oripath}/{n_order}.png"
    path=f"{PATH}/temp"
    os.makedirs(path,exist_ok=True)
    for f in os.listdir(path):
        os.remove(f'{path}/{f}')
    img=imageio.imread(impath)
    imgs={}
    for r in rtd:
        t=rtd[r]
        temp=bai.copy()
        imgs[t]=temp
    for y in range(h):
        for x in range(w):
            tag=img[y][x][1]
            im_type=rtd[tag]
            imgs[im_type][y][x]=0
            imgs['whole'][y][x]=255-imgs['whole'][y][x]
    for t in imgs:
        d=imgs[t]
        imageio.imsave(f'{path}/{t}.bmp',d)
    pan=path[:2]
    os.system(f'{pan}')
    os.system(f'cd {path}')
    os.system(f'for %i in ({path}\\*) do potrace %i -b svg -a 0')
    whole=svg2paths(f'{path}/whole.svg')[0][0]
    svg_d = svg2paths(f"{path}/interiordoor.svg")[0]
    wholearea=whole.area()
    wholebox=list(whole.bbox())
    cen_x=(wholebox[0]+wholebox[1])/2
    cen_y=(wholebox[2]+wholebox[3])/2
    hbond_x=(wholebox[1]-wholebox[0])/2
    hbond_y=(wholebox[3]-wholebox[2])/2
    temp_area=1
    loopcontrol = 1
    for s in sl:
        rt=rtd[s]
        svg=svg2paths(f'{path}/{rt}.svg')[0]
        arltn=f'{rt}_areas'
        arlt=[]
        cenltn=f'{rt}_centroids'
        cenlt=[]
        drlt = []
        for t in svg:
            try:
                a=t.area()
                if a<1000:
                    pass
                else:
                    a=a/wholearea
                    arlt.append(a)
                    temp_area=temp_area-a
                    bx=list(t.bbox())
                    svg_cenx=(bx[0]+bx[1])/2
                    svg_ceny=(bx[2]+bx[3])/2
                    x=(cen_x-svg_cenx)/hbond_x
                    y=(cen_y-svg_ceny)/hbond_y
                    svg_cen=(x,y)
                    cenlt.append(svg_cen)
                    doornum_or = 0
                    for i in svg_d:
                        svg_con = t.intersect(i, justonemode=True)
                        if len(svg_con) != 0:
                            doornum_or += 1
                    drlt.append(doornum_or)
            except:
                print(f'No. {n_order} has error in room label')
                loopcontrol=0
                break
        if loopcontrol==0:break
        else:
            num=len(arlt)
            numn=f'{rt}_number'
            dic_sample[numn]=num
            dic_sample[arltn]=arlt
            dic_sample[cenltn]=cenlt
            drn=f'{rt}_door_number'
            dic_sample[drn]=drlt

    loopcontroll = 1
    dic_l = []
    door_room_num = []
    for d in svg_d:
        con_rooms = []
        for s in sl:
            rt = rtd[s]
            svg = svg2paths(f"{path}/{rt}.svg")[0]
            num = 1
            for t in svg:
                try:
                    a = t.area()
                    if a < 1000:
                        pass
                    else:
                        if len(svg) > 1:
                            roomname = f"{rt}{num}"
                        else:
                            roomname = rt
                        a = t.intersect(d, justonemode=True)
                        if len(a) != 0:
                            con_rooms.append(roomname)
                        num += 1
                except:
                    print(f"{n_order} has error in door label")
                    loopcontroll = 0
                    break
            if loopcontroll == 0:
                break
    
        if loopcontroll == 0:
            break
        else:
            con_rooms = tuple(con_rooms)
            dic_l.append(con_rooms)
            door_room_num.append(len(con_rooms))
            dic_sample['room_numbers_adjacent_to_door']=door_room_num
            dic_sample['room_types_adjacent_to_door']=dic_l
            dic_sample['door_number']=len(svg_d)
    for f in os.listdir(path):
        os.remove(f'{path}/{f}')
    if loopcontrol==0:
        with open(f'{oripath}/error.txt','a') as f:
            f.write(f'{n_order}\r')
        return 'Error'
    elif loopcontroll==0:
        with open(f'{oripath}/error.txt','a') as f:
            f.write(f'{n_order}\r')
        return 'Error'
    else:
        dic_sample['use_area']=1-temp_area
        return dic_sample

# put all sample ids you're calculating in this list
sample=[0,1,2,3,4,5]

# You can save every feature vector one by one like this to prevent possible interruption, which is recommended
os.makedirs(f'{PATH}/feature_vectors_of_rplan',exist_ok=True)
for n in sample:
    d=extract_info(n)
    np.save(f'{PATH}/feature_vectors_of_rplan/{n}.npy',d)

# You can also choose to save dictionary after calculate all samples like this, which is NOT recommended
''' 
dic_all={}
for n in sample:
    dic_all[n]=extract_info(n)
np.save(f'{PATH}/rplan_feature_vector.npy',dic_all)
'''

