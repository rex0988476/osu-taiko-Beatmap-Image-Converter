import cv2
import numpy as np
import decimal
import os
import shutil

##########variable
ONE_BAR_W=320
BAR_H=60
SMALL_OBJ_RADIUS=10
BIG_OBJ_RADIUS=15
#BAR_LINE_OFFSET_X=0
BAR_NUM_TEXT_Y_OFFSET=15
NOTE_COLOR_RED = (43, 68, 255) # BGR
NOTE_COLOR_BLUE = (255, 140, 66) # BGR
BACKGROUND_COLOR=(105,105,105)
FAULT_TOLERANCE=1#fit rightmost note that x + BAR.bar_line_offset will exceed BAR_W
#OFFSET_OF_FIRST_NOTE_IN_A_BAR=BAR_LINE_OFFSET_X
BAR_LINE_OFFSET_Y=10#for small bar line and notes layout
BAR_NUM_IN_ONE_CUT=4
SMALL_BARLINE_TOP_Y=int((BAR_H-(BAR_LINE_OFFSET_Y*2))/4)
SMALL_BARLINE_BOTTOM_Y=BAR_H-SMALL_BARLINE_TOP_Y
#ONE_BAR_LEFT_TOP_Y=0
#ONE_BAR_RIGHT_BOTTOM_Y=BAR_H
##########function

def clean_temp_folder():
    shutil.rmtree('./data')
    os.mkdir('./data')

def read_map_information(osu_file_name):#read .osu file and generate title.txt, timing_point.txt and hitobj.txt
    #read .osu file
    f=open(osu_file_name,'r',encoding='utf-8')
    texts=f.readlines()
    f.close()

    #open title.txt, timing_point.txt and hitobj.txt
    title_f=open('./data/title.txt','w')
    tp_f=open('./data/timing_point.txt','w')
    hitobj_f=open('./data/hitobj.txt','w')
    
    title=""
    artist=""
    mapper=""
    diff_name=""
    start_record_hit_obj=False
    start_record_time_point=False

    #parse .osu file
    i=0
    while i<len(texts):
        texts[i]=texts[i][:-1]

        #for title.txt
        if texts[i].find('Title:')!=-1:
            title=texts[i].split(':')[1]
        elif texts[i].find('Artist:')!=-1:
            artist=texts[i].split(':')[1]
        elif texts[i].find('Creator:')!=-1:
            mapper=texts[i].split(':')[1]
        elif texts[i].find('Version:')!=-1:
            diff_name=texts[i].split(':')[1]
        
        #for timing_point.txt
        if texts[i].find('[TimingPoints]')!=-1:
            start_record_time_point=True
        elif start_record_time_point:
            time_type=""#sv, bpm
            time_offset=-1
            s=texts[i].split(',')
            if len(s)==8:
                #sv
                if s[6]=="0":
                    pass
                #bpm
                elif s[6]=="1":
                    time_type="bpm"
                    time_offset=int(s[0])
                    bpm=round(decimal.Decimal(str(60000/float(s[1]))))# Decimal for exact float
                    time_signature=int(s[2])
                    tp_f.write(f'{time_offset},{time_type},{bpm},{time_signature}\n')

                #BPM=round(BPM,2)
                #print(BPM)

        #for hitobj.txt
        if texts[i].find('[HitObjects]')!=-1:
            start_record_hit_obj = True
            start_record_time_point = False
        elif start_record_hit_obj:
            #0: small red 
            #4: big red
            #2,8,10: small blue 
            #6,12,14: big blue
            s=texts[i].split(',')
            obj_offset=int(s[2])#ms
            obj_type=""#note, slider, spinner
            color=""#red, blue
            size=""#small, big
            length=-1
            end_offset=-1
            #note
            if s[3] in ["1","5"]:
                obj_type="note"
                #small red
                if s[4]=="0":
                    color="red"
                    size="small"
                #big red
                elif s[4]=="4":
                    color="red"
                    size="big"
                #small blue
                elif s[4] in ["2","8","10"]:
                    color="blue"
                    size="small"
                #big blue
                elif s[4] in ["6","12","14"]:
                    color="blue"
                    size="big"
                else:
                    print(f"#ERROR[note]: {texts[i]}")
                    exit(0)
            #slider
            elif s[3] in ["2","6"]:
                obj_type="slider"
                try:
                    length=int(s[7])
                except:
                    length=float(s[7])
            #spinner
            elif s[3] in ["12","8"]:
                obj_type="spinner"
                end_offset=int(s[5])
            else:
                print(f"#ERROR[obj_type]: {texts[i]}")
                exit(0)
            hitobj_f.write(f"{obj_offset},{obj_type},{color},{size},{length},{end_offset}\n")
        i+=1
    
    title_f.write(f'Title:{title}\n')
    title_f.write(f'Artist:{artist}\n')
    title_f.write(f'Mapper:{mapper}\n')
    title_f.write(f'Difficulty Name:{diff_name}\n')

    title_f.close()
    tp_f.close()
    hitobj_f.close()
    
def read_title_txt():
    f=open('./data/title.txt','r')
    s=f.readlines()
    f.close()
    name=s[0].split(':')[1][:-1]
    artist=s[1].split(':')[1][:-1]
    mapper_name=s[2].split(':')[1][:-1]
    difficulty_name=s[3].split(':')[1][:-1]
    return name,artist,mapper_name,difficulty_name

def read_timing_point_txt():
    tp_f=open('./data/timing_point.txt','r')
    s=tp_f.readlines()
    tp_f.close()
    bpm_list=[]
    sv_list=[]
    i=0
    while i<len(s):
        if s[i][-1]=='\n':
            s[i]=s[i][:-1]
        if s[i].split(',')[1]=="bpm":
            bpm_list.append({"offset":int(s[i].split(',')[0]),"bpm":int(s[i].split(',')[2]),"time_signature":int(s[i].split(',')[3])})
        elif s[i].split(',')[1]=="sv":
            sv_list.append({"offset":int(s[i].split(',')[0]),"kiai_mode":int(s[i].split(',')[2])})
        i+=1
    
    return bpm_list,sv_list

def read_hitobj_txt():
    hit_objs=[]
    f=open('./data/hitobj.txt','r')
    s=f.readlines()
    f.close()
    i=0
    while i<len(s):
        sp=s[i].split(',')
        offset=int(sp[0])
        obj_type=sp[1]
        color=sp[2]
        size=sp[3]
        try:
            slider_length=int(sp[4])
        except:
            slider_length=float(sp[4])
        spinner_end_offset=int(sp[5][:-1])
        #offset,obj_type,color,size,slider_length,spinner_end_offset
        hit_objs.append({'offset':offset,'obj_type':obj_type,'color':color,'size':size,'slider_length':slider_length,'spinner_end_offset':spinner_end_offset})
        i+=1
    return hit_objs

def calculate_total_bar_num(first_note_bar_start_offset,hit_obj_offset_list,one_bar_total_time):
    total_bar_num=1
    i=0
    while i<len(hit_obj_offset_list):
        #while int(first_note_bar_start_offset + one_bar_total_time)-FAULT_TOLERANCE <= hit_obj_offset_list[i]:
        while int(first_note_bar_start_offset + one_bar_total_time) <= hit_obj_offset_list[i]:
            first_note_bar_start_offset += one_bar_total_time
            total_bar_num+=1
        i+=1
    return total_bar_num

def draw_barline(img, bar_w, time_signature, total_bar_num, bar_num_draw,bpm=-1):
    ori_time_signature=time_signature 
    if time_signature<=4: #if time_signature <= 4 (4/4) then double small bar line
        time_signature*=2
    one_beat_pix=ONE_BAR_W/time_signature

    i=0
    while i<total_bar_num:
        cv2.line(img, (ONE_BAR_W*i,0), (ONE_BAR_W*i,BAR_H), (230,230,230), 2) #bar line
        #small bar line
        j=1
        while (ONE_BAR_W*i)+(j*one_beat_pix) < ONE_BAR_W*(i+1):
            cv2.line(img, (round(decimal.Decimal(str((ONE_BAR_W*i)+(j*one_beat_pix)))),SMALL_BARLINE_TOP_Y+BAR_LINE_OFFSET_Y), (round(decimal.Decimal(str((ONE_BAR_W*i)+(j*one_beat_pix)))),SMALL_BARLINE_BOTTOM_Y+BAR_LINE_OFFSET_Y), (170,170,170), 1)
            j+=1
        #bar num
        cv2.putText(img,f'{bar_num_draw}',((ONE_BAR_W*i)+5,BAR_NUM_TEXT_Y_OFFSET),cv2.FONT_HERSHEY_SIMPLEX,0.55,(255,0,0),2)
        bar_num_draw+=1
        i+=1

    #bpm and time signature
    if bpm!=-1:
        bpm_ts_text=f'BPM: {bpm}, ({ori_time_signature}/4)'
        cv2.putText(img,bpm_ts_text,(80,BAR_NUM_TEXT_Y_OFFSET),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,0,0),2)
    #bottom line
    cv2.line(img, (0,BAR_H-1), (bar_w,BAR_H-1), (230,230,230), 1)
    return img,bar_num_draw

##########code
def main_func(osu_file_folder_path,osu_file_name):
    osu_file_path=osu_file_folder_path+osu_file_name

    #init folder
    clean_temp_folder()

    #read .osu and parse to title.txt, timing_point.txt and hitobj.txt
    #read_map_information(FILE_FOLDER_PATH+OSU_FILE_NAME)
    read_map_information(osu_file_path)
    

    #read timing_point.txt
    bpm_list,sv_list=read_timing_point_txt()
    bpm_start_offset=bpm_list[0]['offset']
    bpm=bpm_list[0]['bpm']
    time_signature=bpm_list[0]['time_signature']

    #read hitobj.txt
    HIT_OBJS=read_hitobj_txt()

    #assign notes to their corresponding bpm segments
    bpm_and_obj_list=[]
    #bpm_and_obj_list: [{"bpm_offset":,"bpm":,"time_signature":,"hit_objs":[{"offset":,"obj_type":,"color":,"size":,"slider_length":,"spinner_end_offset":}]}]
    i=0
    j=0
    while i<len(bpm_list):
        bpm_start_offset=bpm_list[i]['offset']
        bpm=bpm_list[i]['bpm']
        time_signature=bpm_list[i]['time_signature']
        
        bpm_and_obj_list.append({"bpm_offset":bpm_start_offset,"bpm":bpm,"time_signature":time_signature,"hit_objs":[]})

        if i<len(bpm_list)-1:
            next_bpm_offset=bpm_list[i+1]['offset']
        else:
            next_bpm_offset=HIT_OBJS[-1]['offset']+1

        while j<len(HIT_OBJS) and HIT_OBJS[j]['offset']<next_bpm_offset:
            bpm_and_obj_list[i]["hit_objs"].append(HIT_OBJS[j])
            j+=1

        i+=1
    
    ###########################################################################
    img_and_parameter_list=[]#{"img":,"total_bar_num":,"last_bar_end_offset":}
    bar_num_draw=1
    k=0
    while k<len(bpm_and_obj_list):
        bpm=bpm_and_obj_list[k]['bpm']
        bpm_start_offset=bpm_and_obj_list[k]['bpm_offset']
        time_signature=bpm_and_obj_list[k]['time_signature']

        #calculate beat time(ms)
        one_beat_time=60000/bpm
        one_bar_total_time=one_beat_time*time_signature
        
        first_note_bar_start_offset = bpm_start_offset
        #calculate first barline offset (first have obj's bar) for first bpm
        if k==0:
            i=0
            while bpm_start_offset+(one_bar_total_time*(i+1))<bpm_and_obj_list[k]['hit_objs'][0]['offset']:
                i+=1
            first_note_bar_start_offset = bpm_start_offset + one_bar_total_time * i

        hit_obj_offset_list=[]
        i=0
        while i<len(bpm_and_obj_list[k]['hit_objs']):
            hit_obj_offset_list.append(bpm_and_obj_list[k]['hit_objs'][i]['offset'])
            i+=1
        total_bar_num=calculate_total_bar_num(first_note_bar_start_offset,hit_obj_offset_list,one_bar_total_time)
        bar_w=total_bar_num*ONE_BAR_W
        bar_total_time=total_bar_num*one_bar_total_time
        #draw bar line start ##############################################################
        img = np.full((BAR_H, bar_w, 3), BACKGROUND_COLOR , np.uint8)
        img , bar_num_draw = draw_barline(img,bar_w,time_signature,total_bar_num,bar_num_draw,bpm)
        #draw bar line end##############################################################
        #draw obj start##############################################################
        i=len(bpm_and_obj_list[k]['hit_objs'])-1
        while i>=0:
            x = round(decimal.Decimal(str((bpm_and_obj_list[k]['hit_objs'][i]['offset']-first_note_bar_start_offset)/bar_total_time*bar_w)))
            if bpm_and_obj_list[k]['hit_objs'][i]['obj_type']=="note":
                if bpm_and_obj_list[k]['hit_objs'][i]['color']=="red":
                    if bpm_and_obj_list[k]['hit_objs'][i]['size']=="small":
                        cv2.circle(img, (x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), SMALL_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                        cv2.circle(img, (x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), SMALL_OBJ_RADIUS, (255,255,255), 1)
                    elif bpm_and_obj_list[k]['hit_objs'][i]['size']=="big":
                        cv2.circle(img, (x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), BIG_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                        cv2.circle(img, (x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), BIG_OBJ_RADIUS, (255,255,255), 1)
                elif bpm_and_obj_list[k]['hit_objs'][i]['color']=="blue":
                    if bpm_and_obj_list[k]['hit_objs'][i]['size']=="small":
                        cv2.circle(img, (x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), SMALL_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                        cv2.circle(img, (x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), SMALL_OBJ_RADIUS, (255,255,255), 1)
                    elif bpm_and_obj_list[k]['hit_objs'][i]['size']=="big":
                        cv2.circle(img, (x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), BIG_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                        cv2.circle(img, (x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), BIG_OBJ_RADIUS, (255,255,255), 1)
            i-=1
        #draw obj end##############################################################
        #last_bar_end_offset = first_note_bar_start_offset + total_bar_num * one_bar_total_time
        #original last_bar_end_offset means "last have obj's bar end offset", there may have some no obj bar after that untill next bpm come, so we need to calculate it and generate empty bar img
        empty_bar_num=0
        if k<len(bpm_and_obj_list)-1:#last bpm don't need to calculate it, just finish.
            i=total_bar_num
            #while int(first_note_bar_start_offset + i*one_bar_total_time)-FAULT_TOLERANCE <= bpm_and_obj_list[k+1]['bpm_offset']:
            while int(first_note_bar_start_offset + i*one_bar_total_time) <= bpm_and_obj_list[k+1]['bpm_offset']:
                i+=1
            empty_bar_num=i-1-total_bar_num
        
        if empty_bar_num>0:
            empty_bar_img = np.full((BAR_H, empty_bar_num*ONE_BAR_W, 3), BACKGROUND_COLOR , np.uint8)
            empty_bar_img, bar_num_draw = draw_barline(empty_bar_img,bar_w,time_signature,empty_bar_num,bar_num_draw)
            img=cv2.hconcat([img,empty_bar_img])

        img_and_parameter_list.append({"img":img,"left_bar_num":total_bar_num + empty_bar_num,"start_offset":first_note_bar_start_offset,"last_bar_end_offset":first_note_bar_start_offset + (total_bar_num * one_bar_total_time)})
        #cv2.imwrite(f'./bpm_{k}.png',img)
        k+=1
    
    #cut and merge start#######################################################
    #print(img_and_parameter_list[0]['start_offset'],img_and_parameter_list[0]['last_bar_end_offset'])
    #print(img_and_parameter_list[1]['start_offset'],img_and_parameter_list[1]['last_bar_end_offset'])
    #print(img_and_parameter_list[2]['start_offset'],img_and_parameter_list[2]['last_bar_end_offset'])
    #exit(0)
    reconstruct_imgs=[]
    j=0
    while j<len(img_and_parameter_list):
        if img_and_parameter_list[j]['left_bar_num']>0:
            bar_img = img_and_parameter_list[j]['img']
            cut_img_list=[]
            img_w=bar_img.shape[1]
            i=0
            while (i+1)*ONE_BAR_W*BAR_NUM_IN_ONE_CUT <= img_w:
                cut_img_list.append(bar_img[:, i*ONE_BAR_W*BAR_NUM_IN_ONE_CUT: (i+1)*ONE_BAR_W*BAR_NUM_IN_ONE_CUT])
                i+=1

            total_bar_num=int(img_w/ONE_BAR_W)
            if total_bar_num<BAR_NUM_IN_ONE_CUT:
                total_bar_num+=BAR_NUM_IN_ONE_CUT
            left_bar_num=total_bar_num%BAR_NUM_IN_ONE_CUT

            if left_bar_num>0:
                cut_img_list.append(bar_img[:, i*ONE_BAR_W*BAR_NUM_IN_ONE_CUT:])#last cut img
                if j<len(img_and_parameter_list)-1:#not last bpm img
                    i=j+1
                    while i<len(img_and_parameter_list):#find other bpm img to concat
                        if img_and_parameter_list[i]['left_bar_num']>0:
                            if img_and_parameter_list[i]['left_bar_num']>= (BAR_NUM_IN_ONE_CUT-left_bar_num):
                                #black_img = np.full((BAR_H, (ONE_BAR_W*BAR_NUM_IN_ONE_CUT)-cut_img_list[i].shape[1], 3), (0,0,0) , np.uint8)
                                pre_cut_img = img_and_parameter_list[i]['img'][:, 0: ONE_BAR_W* (BAR_NUM_IN_ONE_CUT-left_bar_num)]
                                img_and_parameter_list[i]['img'] = img_and_parameter_list[i]['img'][:, ONE_BAR_W* (BAR_NUM_IN_ONE_CUT-left_bar_num):]
                                img_and_parameter_list[i]['left_bar_num']-=(BAR_NUM_IN_ONE_CUT-left_bar_num)
                                cut_img_list[-1]=cv2.hconcat([cut_img_list[-1],pre_cut_img])
                                left_bar_num=BAR_NUM_IN_ONE_CUT
                                break
                            else:
                                pre_cut_img = img_and_parameter_list[i]['img']
                                img_and_parameter_list[i]['img'] = img_and_parameter_list[i]['img'][:, ONE_BAR_W*img_and_parameter_list[i]['left_bar_num']:]
                                left_bar_num += img_and_parameter_list[i]['left_bar_num']
                                img_and_parameter_list[i]['left_bar_num']=0
                                cut_img_list[-1]=cv2.hconcat([cut_img_list[-1],pre_cut_img])
                        i+=1
                    if left_bar_num<BAR_NUM_IN_ONE_CUT:
                        black_img = np.full((BAR_H, ONE_BAR_W*(BAR_NUM_IN_ONE_CUT-left_bar_num), 3), (0,0,0) , np.uint8)
                        cut_img_list[-1]=cv2.hconcat([cut_img_list[-1],black_img])
                else:
                    black_img = np.full((BAR_H, ONE_BAR_W*(BAR_NUM_IN_ONE_CUT-left_bar_num), 3), (0,0,0) , np.uint8)
                    cut_img_list[-1]=cv2.hconcat([cut_img_list[-1],black_img])

            reconstruct_img=cut_img_list[0]
            i=1
            while i<len(cut_img_list):
                reconstruct_img=cv2.vconcat([reconstruct_img,cut_img_list[i]])
                i+=1

            reconstruct_imgs.append(reconstruct_img)
            #cv2.imwrite('./img.png',img)
        j+=1

    reconstruct_img=reconstruct_imgs[0]
    i=1
    while i<len(reconstruct_imgs):
        reconstruct_img=cv2.vconcat([reconstruct_img,reconstruct_imgs[i]])
        i+=1
    #cv2.imwrite('./img.png',reconstruct_img)
    #img cut and merge end#######################################################
    #title generate and merge start##############################################

    #read title.txt
    name,artist,mapper_name,difficulty_name=read_title_txt()

    width_margin=50
    height_margin=0
    text=f'{artist} - {name} [{difficulty_name}] by {mapper_name}'
    text_scale=1#size
    #create img
    title_img = np.full((BAR_H, BAR_NUM_IN_ONE_CUT*ONE_BAR_W, 3), BACKGROUND_COLOR , np.uint8)

    #resize
    retval, baseLine = cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,text_scale,2)
    if retval[0] + 2*width_margin >= BAR_NUM_IN_ONE_CUT*ONE_BAR_W:
        while retval[0] + 2*width_margin >= BAR_NUM_IN_ONE_CUT*ONE_BAR_W:
            text_scale-=0.01
            retval, baseLine = cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,text_scale,2)
    else:
        width_margin = int((BAR_NUM_IN_ONE_CUT*ONE_BAR_W - retval[0])/2)
    height_margin = retval[1] + int((BAR_H-retval[1])/2)

    #draw text
    cv2.putText(title_img,text,(width_margin,height_margin),cv2.FONT_HERSHEY_SIMPLEX,text_scale,(0,0,0),2)

    #merge
    img = cv2.vconcat([title_img,reconstruct_img])

    cv2.imwrite(f'./output folder/{osu_file_name[:-4]}.png',img)
    #title generate and merge end##############################################
    #print(total_bar_num*ONE_BAR_W,img.shape)
    

FILE_FOLDER_PATH='./osu file input folder/'
#OSU_FILE_NAME='Umeboshi Chazuke - ICHIBANBOSHIROCKET (_gt) [INNER ONI].osu'
#OSU_FILE_NAME='DJ Raisei - when ____ disappears from the world (Raphalge) [Inner Oni].osu'
#OSU_FILE_NAME='Yorushika - Replicant (Hivie) [Mirror].osu'
#OSU_FILE_NAME='Kobaryo - New Game Plus (Love Plus rmx) (JarvisGaming) [go play Rabbit and Steel].osu'
#OSU_FILE_NAME='iyowa - Issen Kounen (Cut Ver.) (_gt) [A Thousand Bars].osu'
#OSU_FILE_NAME='Rin - Mythic set ~ Heart-Stirring Urban Legends (tasuke912) [Oni].osu'
OSU_FILE_NAME_LIST=['Umeboshi Chazuke - ICHIBANBOSHIROCKET (_gt) [INNER ONI].osu',
                    'DJ Raisei - when ____ disappears from the world (Raphalge) [Inner Oni].osu',
                    'Yorushika - Replicant (Hivie) [Mirror].osu',
                    'Kobaryo - New Game Plus (Love Plus rmx) (JarvisGaming) [go play Rabbit and Steel].osu',
                    'Rin - Mythic set ~ Heart-Stirring Urban Legends (tasuke912) [Oni].osu']
i=0
while i<len(OSU_FILE_NAME_LIST):
    main_func(FILE_FOLDER_PATH,OSU_FILE_NAME_LIST[i])
    i+=1
