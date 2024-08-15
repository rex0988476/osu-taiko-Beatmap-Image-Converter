import cv2
import numpy as np
import decimal
import os
import shutil

##########variable
ONE_BAR_W=320
#BAR_W=320
BAR_H=60
#TIME_SIGNATURES=[]
TIME_SIGNATURE=4
SMALL_OBJ_RADIUS=10
BIG_OBJ_RADIUS=15
BAR_LINE_OFFSET_X=BIG_OBJ_RADIUS
BAR_NUM_TEXT_Y_OFFSET=15
#NOTE_RADIUS=10
NOTE_COLOR_RED = (43, 68, 255) # BGR
NOTE_COLOR_BLUE = (255, 140, 66) # BGR
CURRENT_BAR_NUM=-1
BACKGROUND_COLOR=(105,105,105)
FAULT_TOLERANCE=1#fit rightmost note that x + BAR.bar_line_offset will exceed BAR_W
OFFSET_OF_FIRST_NOTE_IN_A_BAR=BAR_LINE_OFFSET_X
BAR_LINE_OFFSET_Y=10#for small bar line and notes layout
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

def calculate_total_bar_num(first_note_bar_start_offset,hit_obj_offset_list):
    total_bar_num=1
    i=0
    while i<len(hit_obj_offset_list):
        while int(first_note_bar_start_offset + ONE_BAR_TOTAL_TIME)-FAULT_TOLERANCE <= hit_obj_offset_list[i]:
            first_note_bar_start_offset += ONE_BAR_TOTAL_TIME
            total_bar_num+=1
        i+=1
    return total_bar_num

HIT_OBJS=[]
BPMS=[]
BAR=""
ONE_BAR_TOTAL_TIME=-1
CURRENT_BAR_START_OFFSET=-1
LAST_BAR_NAME=-1
BAR_IMG_NUM_DRAW=1 #[1~], current draw bar num
BAR_IMG_NUM=1 #[1~4], four bar imgs count and file name
ONE_LINE_IMG_NUM=1 #[1~], one line bar imgs count and file name
##########code
def main_func(osu_file_path):
    global HIT_OBJS
    global BPMS
    global BAR
    global ONE_BAR_TOTAL_TIME
    global CURRENT_BAR_START_OFFSET
    global LAST_BAR_NAME
    #global OSU_FILE_NAME
    #global FILE_FOLDER_PATH

    #init folder
    clean_temp_folder()

    #read .osu and parse to title.txt, timing_point.txt and hitobj.txt
    #read_map_information(FILE_FOLDER_PATH+OSU_FILE_NAME)
    read_map_information(osu_file_path)

    #read timing_point.txt
    BPMS,sv_list=read_timing_point_txt()
    bpm_start_offset=BPMS[0]['offset']
    bpm=BPMS[0]['bpm']
    time_signature=BPMS[0]['time_signature']

    #read hitobj.txt
    HIT_OBJS=read_hitobj_txt()

    #calculate beat time(ms)
    one_beat_time=60000/bpm
    ONE_BAR_TOTAL_TIME=one_beat_time*4

    #calculate first barline offset (first have obj's bar)
    i=0
    while bpm_start_offset+(ONE_BAR_TOTAL_TIME*(i+1))<HIT_OBJS[0]['offset']:
        i+=1
    first_note_bar_start_offset = bpm_start_offset + ONE_BAR_TOTAL_TIME * i
    CURRENT_BAR_START_OFFSET = first_note_bar_start_offset

    hit_obj_offset_list=[]

    i=0
    while i<len(HIT_OBJS):
        hit_obj_offset_list.append(HIT_OBJS[i]['offset'])
        i+=1
    total_bar_num=calculate_total_bar_num(first_note_bar_start_offset,hit_obj_offset_list)
    BAR_W=total_bar_num*ONE_BAR_W
    BAR_TOTAL_TIME=total_bar_num*ONE_BAR_TOTAL_TIME
    #draw bar line start ##############################################################
    img = np.full((BAR_H, BAR_W, 3), BACKGROUND_COLOR , np.uint8)
    small_barline_top_y=int((BAR_H-(BAR_LINE_OFFSET_Y*2))/4)
    small_barline_bottom_y=BAR_H-small_barline_top_y

    #time_signature=4
    if time_signature<=4: #if time_signature <= 4 (4/4) then double small bar line
        time_signature*=2
    one_beat_pix=ONE_BAR_W/time_signature

    i=0
    while i<total_bar_num:
        cv2.line(img, ((ONE_BAR_W*i)+BAR_LINE_OFFSET_X,0), ((ONE_BAR_W*i)+BAR_LINE_OFFSET_X,BAR_H), (230,230,230), 2) #bar line
        #small bar line
        j=1
        while (ONE_BAR_W*i)+BAR_LINE_OFFSET_X+(j*one_beat_pix) < ONE_BAR_W*(i+1):
            cv2.line(img, (round(decimal.Decimal(str((ONE_BAR_W*i)+BAR_LINE_OFFSET_X+(j*one_beat_pix)))),small_barline_top_y+BAR_LINE_OFFSET_Y), (round(decimal.Decimal(str((ONE_BAR_W*i)+BAR_LINE_OFFSET_X+(j*one_beat_pix)))),small_barline_bottom_y+BAR_LINE_OFFSET_Y), (170,170,170), 1)
            j+=1
        #bar num
        cv2.putText(img,f'{i+1}',((ONE_BAR_W*i)+BAR_LINE_OFFSET_X+5,BAR_NUM_TEXT_Y_OFFSET),cv2.FONT_HERSHEY_SIMPLEX,0.55,(255,0,0),2)
        i+=1

    #bottom line
    cv2.line(img, (0,BAR_H-1), (BAR_W,BAR_H-1), (230,230,230), 1)
    #draw bar line end##############################################################
    #draw obj start##############################################################
    i=len(hit_obj_offset_list)-1
    while i>=0:
        x = round(decimal.Decimal(str((hit_obj_offset_list[i]-CURRENT_BAR_START_OFFSET)/BAR_TOTAL_TIME*BAR_W)))
        if HIT_OBJS[i]['obj_type']=="note":
            if HIT_OBJS[i]['color']=="red":
                if HIT_OBJS[i]['size']=="small":
                    cv2.circle(img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), SMALL_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                    cv2.circle(img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), SMALL_OBJ_RADIUS, (255,255,255), 1)
                elif HIT_OBJS[i]['size']=="big":
                    cv2.circle(img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), BIG_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                    cv2.circle(img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), BIG_OBJ_RADIUS, (255,255,255), 1)
            elif HIT_OBJS[i]['color']=="blue":
                if HIT_OBJS[i]['size']=="small":
                    cv2.circle(img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), SMALL_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                    cv2.circle(img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), SMALL_OBJ_RADIUS, (255,255,255), 1)
                elif HIT_OBJS[i]['size']=="big":
                    cv2.circle(img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), BIG_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                    cv2.circle(img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+x, int(BAR_H/2)+BAR_LINE_OFFSET_Y), BIG_OBJ_RADIUS, (255,255,255), 1)
        i-=1
    #draw obj end##############################################################
    #cv2.imwrite('./img.png',img)
    #cut and merge start#######################################################
    bar_img = img
    cut_img_list=[]
    bar_num_in_one_cut=4
    one_bar_left_top_y=0
    one_bar_right_bottom_y=BAR_H
    img_w=bar_img.shape[1]
    i=0
    while (i+1)*ONE_BAR_W*bar_num_in_one_cut+BAR_LINE_OFFSET_X <= img_w:
        cut_img_list.append(bar_img[one_bar_left_top_y:one_bar_right_bottom_y, i*ONE_BAR_W*bar_num_in_one_cut+BAR_LINE_OFFSET_X: (i+1)*ONE_BAR_W*bar_num_in_one_cut+BAR_LINE_OFFSET_X])
        i+=1
    left_bar_num=int(img_w/ONE_BAR_W%bar_num_in_one_cut)

    if left_bar_num>0:
        cut_img_list.append(bar_img[one_bar_left_top_y:one_bar_right_bottom_y, i*ONE_BAR_W*bar_num_in_one_cut+BAR_LINE_OFFSET_X:])#last cut img

    bar_img=cut_img_list[0]
    
    i=1
    while i<len(cut_img_list)-1:
        bar_img=cv2.vconcat([bar_img,cut_img_list[i]])
        i+=1

    if left_bar_num>0:
        black_img = np.full((BAR_H, (ONE_BAR_W*bar_num_in_one_cut)-cut_img_list[i].shape[1], 3), (0,0,0) , np.uint8)
        cut_img_list[i]=cv2.hconcat([cut_img_list[i],black_img])
    bar_img=cv2.vconcat([bar_img,cut_img_list[i]])

    #cv2.imwrite('./img.png',img)

    #img cut and merge end#######################################################
    #title generate and merge start##############################################

    #read title.txt
    name,artist,mapper_name,difficulty_name=read_title_txt()

    width_margin=50
    height_margin=0
    text=f'{artist} - {name} [{difficulty_name}] by {mapper_name}'
    text_scale=1#size
    #create img
    title_img = np.full((BAR_H, bar_num_in_one_cut*ONE_BAR_W, 3), BACKGROUND_COLOR , np.uint8)

    #resize
    retval, baseLine = cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,text_scale,2)
    if retval[0] + 2*width_margin >= bar_num_in_one_cut*ONE_BAR_W:
        while retval[0] + 2*width_margin >= bar_num_in_one_cut*ONE_BAR_W:
            text_scale-=0.01
            retval, baseLine = cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,text_scale,2)
    else:
        width_margin = int((bar_num_in_one_cut*ONE_BAR_W - retval[0])/2)
    height_margin = retval[1] + int((BAR_H-retval[1])/2)

    #draw text
    cv2.putText(title_img,text,(width_margin,height_margin),cv2.FONT_HERSHEY_SIMPLEX,text_scale,(0,0,0),2)

    #merge
    img = cv2.vconcat([title_img,bar_img])

    cv2.imwrite(f'./output folder/{OSU_FILE_NAME[:-4]}.png',img)
    #title generate and merge end##############################################
    #print(total_bar_num*ONE_BAR_W,img.shape)
    

FILE_FOLDER_PATH='./osu file input folder/'
#OSU_FILE_NAME='Umeboshi Chazuke - ICHIBANBOSHIROCKET (_gt) [INNER ONI].osu'
OSU_FILE_NAME='DJ Raisei - when ____ disappears from the world (Raphalge) [Inner Oni].osu'
#OSU_FILE_NAME='Yorushika - Replicant (Hivie) [Mirror].osu'
#OSU_FILE_NAME='Kobaryo - New Game Plus (Love Plus rmx) (JarvisGaming) [go play Rabbit and Steel].osu'
#OSU_FILE_NAME='iyowa - Issen Kounen (Cut Ver.) (_gt) [A Thousand Bars].osu'
main_func(FILE_FOLDER_PATH+OSU_FILE_NAME)