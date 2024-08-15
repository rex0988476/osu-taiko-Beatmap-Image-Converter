import cv2
import numpy as np
import decimal
import os
import shutil

##########variable
BAR_W=320
BAR_H=60
#TIME_SIGNATURES=[]
TIME_SIGNATURE=4
SMALL_OBJ_RADIUS=10
BIG_OBJ_RADIUS=15
#NOTE_RADIUS=10
NOTE_COLOR_RED = (43, 68, 255) # BGR
NOTE_COLOR_BLUE = (255, 140, 66) # BGR
CURRENT_BAR_NUM=-1
BACKGROUND_COLOR=(105,105,105)
FAULT_TOLERANCE=1#fit rightmost note that x + BAR.small_obj_radius will exceed BAR_W
OFFSET_OF_FIRST_NOTE_IN_A_BAR=SMALL_OBJ_RADIUS
BAR_LINE_Y_OFFSET=10#for small bar line and notes layout
##########function

def clean_temp_folder():
    shutil.rmtree('./data')
    os.mkdir('./data')
    os.mkdir('./data/four_temp_bar')
    os.mkdir('./data/final_temp_bar')

def gen_black_bar_img():
    black_bar_img = np.full((BAR_H, BAR_W, 3),(0,0,0) , np.uint8)
    cv2.imwrite('./data/black_bar.png',black_bar_img)

def read_map_information(osu_file_name):#read .osu file and generate title.txt, bpm.txt and hitobj.txt
    HIT_OBJS=[]
    BPMS=[]
    
    #read .osu file
    f=open(osu_file_name,'r',encoding='utf-8')
    texts=f.readlines()
    f.close()

    #open title.txt, bpm.txt and hitobj.txt
    title_f=open('./data/title.txt','w')
    bpm_f=open('./data/bpm.txt','w')
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
        
        #for bpm.txt
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
                    BPMS.append([time_offset,time_type,bpm])
                    bpm_f.write(f'{time_offset},{time_type},{bpm}\n')

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
            HIT_OBJS.append([obj_offset,obj_type,color,size,length,end_offset])
            hitobj_f.write(f"{obj_offset},{obj_type},{color},{size},{length},{end_offset}\n")
            #print([obj_offset,obj_type,color,size,length,end_offset])
        i+=1
    
    title_f.write(f'Title:{title}\n')
    title_f.write(f'Artist:{artist}\n')
    title_f.write(f'Mapper:{mapper}\n')
    title_f.write(f'Difficulty Name:{diff_name}\n')

    title_f.close()
    bpm_f.close()
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

def read_bpm_txt():
    bpm_f=open('./data/bpm.txt','r')
    s=bpm_f.readline().split(',')
    bpm_start_offset=int(s[0])
    bpm=int(s[2])
    return bpm_start_offset,bpm

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

def offset_to_pix(note_offset):
    x = round(decimal.Decimal(str((note_offset-CURRENT_BAR_START_OFFSET)/ONE_BAR_TOTAL_TIME*BAR_W)))
    return x

def check_and_update_bar_start_offset_and_change_bar(note_offset,hb_index):
    global CURRENT_BAR_START_OFFSET
    global BAR_IMG_NUM_DRAW
    global BAR_IMG_NUM
    global HIT_OBJS
    HIT_OBJS[hb_index]['bar_name']=str(BAR_IMG_NUM)
    #current bar note end (one bar img end)
    while int(CURRENT_BAR_START_OFFSET + ONE_BAR_TOTAL_TIME)-FAULT_TOLERANCE <= note_offset:
        #update start offset
        CURRENT_BAR_START_OFFSET += ONE_BAR_TOTAL_TIME

        #HIT_OBJS + 'bar_name' key
        BAR_IMG_NUM += 1
        if BAR_IMG_NUM == 5:#4 bar per line, concat 4 bar img to one line img
            BAR_IMG_NUM = 1
        HIT_OBJS[hb_index]['bar_name']=str(BAR_IMG_NUM)
        BAR_IMG_NUM_DRAW+=1

def calculate_note_position():
    global HIT_OBJS
    # HIT_OBJS + 'bar_num' and 'pix_position_x' key
    error_report_f=open('./error_report.txt','w')
    i=0
    while i<len(HIT_OBJS) :
        check_and_update_bar_start_offset_and_change_bar(HIT_OBJS[i]['offset'],i)
        if HIT_OBJS[i]['obj_type']=="note":
            x = offset_to_pix(HIT_OBJS[i]['offset'])
            #if x+BAR.small_obj_radius>BAR_W or x<0:
            #    error_report_f.write(f"{i},{x},{HIT_OBJS[i][0]},{CURRENT_BAR_START_OFFSET+ONE_BAR_TOTAL_TIME},{int(CURRENT_BAR_START_OFFSET+ONE_BAR_TOTAL_TIME)},{BAR_IMG_NUM_DRAW}\n")
            HIT_OBJS[i]['bar_num']=BAR_IMG_NUM_DRAW
            #print(BAR_IMG_NUM_DRAW,BAR_IMG_NUM)
            #if i==2:
            #    exit(0)
            HIT_OBJS[i]['pix_position_x']=x
        else:#WIP
            HIT_OBJS[i]['bar_num']=-1
            HIT_OBJS[i]['pix_position_x']=-1
        i+=1
    error_report_f.close()

def draw_object_to_bar():
    global BAR
    global ONE_LINE_IMG_NUM

    i=len(HIT_OBJS)-1
    BAR.draw_barline(HIT_OBJS[i]['bar_num'])
    cur_bar_num=HIT_OBJS[i]['bar_num']#to draw on left top
    cur_bar_name=int(HIT_OBJS[i]['bar_name'])#1~4, to save
    is_first=True
    while i>=0:
        if HIT_OBJS[i]['obj_type']=="note":
            if HIT_OBJS[i]['color']=="red":
                if HIT_OBJS[i]['size']=="small":
                    cv2.circle(BAR.img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+HIT_OBJS[i]['pix_position_x'], int(BAR.h/2)+BAR_LINE_Y_OFFSET), SMALL_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                    cv2.circle(BAR.img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+HIT_OBJS[i]['pix_position_x'], int(BAR.h/2)+BAR_LINE_Y_OFFSET), SMALL_OBJ_RADIUS, (255,255,255), 1)
                elif HIT_OBJS[i]['size']=="big":
                    cv2.circle(BAR.img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+HIT_OBJS[i]['pix_position_x'], int(BAR.h/2)+BAR_LINE_Y_OFFSET), BIG_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                    cv2.circle(BAR.img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+HIT_OBJS[i]['pix_position_x'], int(BAR.h/2)+BAR_LINE_Y_OFFSET), BIG_OBJ_RADIUS, (255,255,255), 1)
            elif HIT_OBJS[i]['color']=="blue":
                if HIT_OBJS[i]['size']=="small":
                    cv2.circle(BAR.img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+HIT_OBJS[i]['pix_position_x'], int(BAR.h/2)+BAR_LINE_Y_OFFSET), SMALL_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                    cv2.circle(BAR.img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+HIT_OBJS[i]['pix_position_x'], int(BAR.h/2)+BAR_LINE_Y_OFFSET), SMALL_OBJ_RADIUS, (255,255,255), 1)
                elif HIT_OBJS[i]['size']=="big":
                    cv2.circle(BAR.img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+HIT_OBJS[i]['pix_position_x'], int(BAR.h/2)+BAR_LINE_Y_OFFSET), BIG_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                    cv2.circle(BAR.img, (OFFSET_OF_FIRST_NOTE_IN_A_BAR+HIT_OBJS[i]['pix_position_x'], int(BAR.h/2)+BAR_LINE_Y_OFFSET), BIG_OBJ_RADIUS, (255,255,255), 1)
        i-=1
        while cur_bar_num > HIT_OBJS[i]['bar_num'] and HIT_OBJS[i]['bar_num']!=-1:
            #save img
            BAR.save_img(cur_bar_name)
            cur_bar_name-=1

            if cur_bar_name==0:
                cur_bar_name=4
                if is_first:
                    is_first=False
                    four_bar_img_to_one_img(ONE_LINE_IMG_NUM,is_last=True)
                    
                else:
                    four_bar_img_to_one_img(ONE_LINE_IMG_NUM)
                ONE_LINE_IMG_NUM+=1

            #create new bar
            BAR=Bar(BAR_W,BAR_H,BACKGROUND_COLOR,TIME_SIGNATURE,SMALL_OBJ_RADIUS)
            cur_bar_num-=1
            BAR.draw_barline(cur_bar_num)

def four_bar_img_to_one_img(img_num,is_last=False,t=0):
    if not is_last:
        img1=cv2.imread('./data/four_temp_bar/1.png')
        img2=cv2.imread('./data/four_temp_bar/2.png')
        img3=cv2.imread('./data/four_temp_bar/3.png')
        img4=cv2.imread('./data/four_temp_bar/4.png')
        if t==1:
            cv2.imshow('image', img2)
            key=cv2.waitKey(0)
            cv2.destroyAllWindows()
        one_line_img=cv2.hconcat([img1,img2,img3,img4])
        cv2.imwrite(f'./data/final_temp_bar/{img_num}.png',one_line_img)
    else:
        img=cv2.imread(f'./data/four_temp_bar/1.png')
        i=2
        while i<=LAST_BAR_NAME:
            img_t=cv2.imread(f'./data/four_temp_bar/{i}.png')
            img=cv2.hconcat([img,img_t])
            i+=1
        img_black=cv2.imread(f'./data/black_bar.png')
        while i<=4:
            img=cv2.hconcat([img,img_black])
            i+=1
        cv2.imwrite(f'./data/final_temp_bar/{img_num}.png',img)

def concat_one_line_imgs():
    all_one_line_imgs_name=os.listdir('./data/final_temp_bar/')
    #sort by name
    sorted_all_one_line_imgs_name=[]
    i=len(all_one_line_imgs_name)
    while i>0:
        index=all_one_line_imgs_name.index(f'{i}.png')
        sorted_all_one_line_imgs_name.append(all_one_line_imgs_name[index])
        i-=1
    #concat
    final_img=cv2.imread(f'./data/final_temp_bar/{sorted_all_one_line_imgs_name[0]}')
    i=1
    while i<len(sorted_all_one_line_imgs_name):
        img=cv2.imread(f'./data/final_temp_bar/{sorted_all_one_line_imgs_name[i]}')
        final_img=cv2.vconcat([final_img,img])
        i+=1
    cv2.imwrite(f'./data/bar.png',final_img)

def concat_title_and_bar():
    timg=cv2.imread('./data/title.png')
    bimg=cv2.imread('./data/bar.png')
    result=cv2.vconcat([timg,bimg])
    cv2.imwrite(f'./output folder/{OSU_FILE_NAME[:-4]}.png',result)

##########class

class Title():
    def __init__(self,w,h,color,name,artist,mapper_name,difficulty_name,hp=-1,od=-1,difficulty=-1):
        self.w=w
        self.h=h
        self.color=color
        self.img=""
        self.init_bg()
        self.name=name#str, beatmap name
        self.artist=artist#str, song artist name
        self.mapper_name=mapper_name#str, beatmap name
        self.difficulty_name=difficulty_name#str, beatmap difficulty name
        #self.hp=hp#str, beatmap hp drain rate
        #self.od=od#str, beatmap overall difficulty
        #self.difficulty=difficulty#float, >0, star rating of beatmap
        self.width_margin=50
        self.height_margin=0
        self.text=f'{self.artist} - {self.name} [{self.difficulty_name}] by {self.mapper_name}'
        self.text_scale=1#size
        self.draw_information()

    def init_bg(self):
        self.img = np.full((self.h, self.w, 3), self.color , np.uint8)

    def resize_text(self):
        retval, baseLine = cv2.getTextSize(self.text,cv2.FONT_HERSHEY_SIMPLEX,self.text_scale,2)
        if retval[0] + 2*self.width_margin >= self.w:
            while retval[0] + 2*self.width_margin >= self.w:
                self.text_scale-=0.01
                retval, baseLine = cv2.getTextSize(self.text,cv2.FONT_HERSHEY_SIMPLEX,self.text_scale,2)
        else:
            self.width_margin = int((self.w - retval[0])/2)
        self.height_margin = retval[1] + int((self.h-retval[1])/2)
        #print(retval,self.w,self.text_scale,self.height_margin)

    def draw_information(self):
        self.resize_text()
        cv2.putText(self.img,self.text,(self.width_margin,self.height_margin),cv2.FONT_HERSHEY_SIMPLEX,self.text_scale,(0,0,0),2)
    
    def save_img(self):
        cv2.imwrite('./data/title.png',self.img)

class Bar():
    def __init__(self,w,h,color,time_signature,small_obj_radius):
        self.w=w #int, 0~, bar img width
        self.h=h #int, 0~, bar img height
        self.color=color #(int,int,int), 0~255, BGR for bar img background color
        self.time_signature=time_signature #int, 0~, metronome ex: "4"/4, "3"/4...

        self.img = "" #bar img
        self.init_bg() #creat bar img
        self.small_obj_radius=small_obj_radius#int, 1~, radius of small note, for draw barline

    def init_bg(self):
        self.img = np.full((self.h, self.w, 3), self.color , np.uint8)

    # draw barline with time signature on bar img
    def draw_barline(self,bar_num_draw):
        small_barline_top_y=int((self.h-(self.small_obj_radius*2))/4)
        small_barline_bottom_y=self.h-small_barline_top_y
        
        cv2.line(self.img, (self.small_obj_radius,0), (self.small_obj_radius,self.h), (230,230,230), 2) #bar line

        time_signature=self.time_signature
        if self.time_signature<=4: #if time_signature <= 4 (4/4) then double small bar line
            time_signature*=2
        one_beat_pix=self.w/time_signature

        #small bar line
        i=1
        while self.small_obj_radius+i*one_beat_pix<self.w:
            cv2.line(self.img, (round(decimal.Decimal(str(self.small_obj_radius+i*one_beat_pix))),small_barline_top_y+BAR_LINE_Y_OFFSET), (round(decimal.Decimal(str(self.small_obj_radius+i*one_beat_pix))),small_barline_bottom_y+BAR_LINE_Y_OFFSET), (170,170,170), 1)
            i+=1

        #bottom line
        cv2.line(self.img, (0,self.h-1), (self.w,self.h-1), (230,230,230), 1)
        #bar num
        cv2.putText(self.img,f'{bar_num_draw}',(15,15),cv2.FONT_HERSHEY_SIMPLEX,0.55,(255,0,0),2)

    def save_img(self,img_num):
        cv2.imwrite(f'./data/four_temp_bar/{img_num}.png',self.img)

HIT_OBJS=[]
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
    global BAR
    global ONE_BAR_TOTAL_TIME
    global CURRENT_BAR_START_OFFSET
    global LAST_BAR_NAME
    #global OSU_FILE_NAME
    #global FILE_FOLDER_PATH

    #init folder
    clean_temp_folder()

    #creat black bar img for last line that may have less than 4 bar to concat.
    gen_black_bar_img()

    #read .osu and parse to title.txt, bpm.txt and hitobj.txt
    #read_map_information(FILE_FOLDER_PATH+OSU_FILE_NAME)
    read_map_information(osu_file_path)

    #read title.txt
    name,artist,mapper_name,difficulty_name=read_title_txt()

    #read bpm.txt
    bpm_start_offset,bpm=read_bpm_txt()

    #read hitobj.txt
    HIT_OBJS=read_hitobj_txt()

    #create and save title img
    TITLE=Title(BAR_W*4,BAR_H,BACKGROUND_COLOR,name,artist,mapper_name,difficulty_name)
    TITLE.save_img()

    #calculate beat time(ms)
    one_beat_time=60000/bpm
    ONE_BAR_TOTAL_TIME=one_beat_time*4

    #calculate first barline offset (first have obj's bar)
    i=0
    while bpm_start_offset+(ONE_BAR_TOTAL_TIME*(i+1))<HIT_OBJS[0]['offset']:
        i+=1
    first_note_bar_start_offset = bpm_start_offset + ONE_BAR_TOTAL_TIME * i
    CURRENT_BAR_START_OFFSET = first_note_bar_start_offset

    #calculate all notes's bar num and position x (not + radius yet)
    calculate_note_position()
    LAST_BAR_NAME=int(HIT_OBJS[-1]['bar_name'])
    f=open('t.txt','w')
    i=0
    while i<len(HIT_OBJS):
        f.write(f"{i},{HIT_OBJS[i]['bar_num']},{HIT_OBJS[i]['bar_name']}\n")
        #print(i,HIT_OBJS[i]['bar_num'],HIT_OBJS[i]['bar_name'])
        i+=1

    #create bar
    #BAR=Bar(BAR_W,BAR_H,BACKGROUND_COLOR,TIME_SIGNATURES,SMALL_OBJ_RADIUS)
    BAR=Bar(BAR_W,BAR_H,BACKGROUND_COLOR,TIME_SIGNATURE,SMALL_OBJ_RADIUS)

    #draw all object
    draw_object_to_bar()

    #last bar
    BAR.save_img(1)
    four_bar_img_to_one_img(ONE_LINE_IMG_NUM,t=0)
    concat_one_line_imgs()
    concat_title_and_bar()

    #cv2.imshow('image', title.img)
    #key=cv2.waitKey(0)
    #cv2.destroyAllWindows()

FILE_FOLDER_PATH='./osu file input folder/'
OSU_FILE_NAME='Umeboshi Chazuke - ICHIBANBOSHIROCKET (_gt) [INNER ONI].osu'
OSU_FILE_NAME='DJ Raisei - when ____ disappears from the world (Raphalge) [Inner Oni].osu'
OSU_FILE_NAME='Yorushika - Replicant (Hivie) [Mirror].osu'
OSU_FILE_NAME='Kobaryo - New Game Plus (Love Plus rmx) (JarvisGaming) [go play Rabbit and Steel].osu'
main_func(FILE_FOLDER_PATH+OSU_FILE_NAME)