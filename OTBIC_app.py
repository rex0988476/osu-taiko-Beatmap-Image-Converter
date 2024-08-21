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
BAR_TEXT_Y=16
NOTE_COLOR_RED = (43, 68, 255) # BGR
NOTE_COLOR_BLUE = (255, 140, 66) # BGR
YELLOW_COLOR = (6, 184, 252) # BGR
KIAI_COLOR = (17, 82, 141) # BGR
BACKGROUND_COLOR=(105,105,105)
FAULT_TOLERANCE=1#fit rightmost note that x + BAR.bar_line_offset will exceed BAR_W
#OFFSET_OF_FIRST_NOTE_IN_A_BAR=BAR_LINE_OFFSET_X
BAR_LINE_OFFSET_Y=10#for small bar line and notes layout
BAR_NUM_IN_ONE_CUT=4
#SMALL_BARLINE_TOP_Y=int((BAR_H-(BAR_LINE_OFFSET_Y*2))/4)
SMALL_BARLINE_TOP_Y=int(BAR_H/3)
SMALL_BARLINE_BOTTOM_Y=BAR_H
#ONE_BAR_LEFT_TOP_Y=0
#ONE_BAR_RIGHT_BOTTOM_Y=BAR_H
BAR_TEXT_SCALE=0.55
TITLE_TEXT_SCALE=1
TITLE_TEXT_WIDTH_MARGIN=50
CUT_AND_MERGE_MODE_S=['minimize black','same bar num']#'minimize black' and 'same bar num'
CUT_AND_MERGE_MODE=CUT_AND_MERGE_MODE_S[0]
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
    is_kiai_on=False
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
                    if s[7]=="1" and not is_kiai_on:#kiai on
                        is_kiai_on=True
                        time_offset=int(s[0])
                        time_type="sv"
                        
                        tp_f.write(f'{time_offset},{time_type},1\n')
                    elif s[7]=="0" and is_kiai_on:
                        is_kiai_on=False
                        time_offset=int(s[0])
                        time_type="sv"
                        tp_f.write(f'{time_offset},{time_type},0\n')

                #bpm
                elif s[6]=="1":
                    time_offset=int(s[0])
                    time_type="bpm"
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

def to_kiai_offset_pair(sv_list):
    sv_kiai_offset_pair_list=[]
    i=0
    while i+1<len(sv_list):
        sv_kiai_offset_pair_list.append({"start_offset":sv_list[i]['offset'],"end_offset":sv_list[i+1]['offset']})
        i+=2
    if len(sv_list)%2==1:
        sv_kiai_offset_pair_list.append({"start_offset":sv_list[i]['offset'],"end_offset":-1})

    return sv_kiai_offset_pair_list

def assign_notes_to_bpm(hit_objs,bpm_list):
    bpm_and_obj_list=[]
    i=0
    j=0
    while i<len(bpm_list):
        if bpm_list[i]['bpm']>0 and bpm_list[i]['time_signature']<=16 :
            bpm_start_offset=bpm_list[i]['offset']
            bpm=bpm_list[i]['bpm']
            time_signature=bpm_list[i]['time_signature']

            bpm_and_obj_list.append({"bpm_offset":bpm_start_offset,"bpm":bpm,"time_signature":time_signature,"hit_objs":[]})

            if i<len(bpm_list)-1:
                next_bpm_offset=bpm_list[i+1]['offset']
            else:
                next_bpm_offset=hit_objs[-1]['offset']+1

            while j<len(hit_objs) and hit_objs[j]['offset']<next_bpm_offset:
                bpm_and_obj_list[-1]["hit_objs"].append(hit_objs[j])
                j+=1
        i+=1
    return bpm_and_obj_list

def assign_kiai_to_bpm(parameters_to_assign_kiai_to_bpm,sv_kiai_offset_pair_list):
    bpm_and_kiai_offset_list=[]# [{"bpm_start_offset":,"bpm_end_offset":,"kiais":[{"start_offset":,"end_offset":,}]}]
    i=0
    while i<len(parameters_to_assign_kiai_to_bpm):
        bpm_and_kiai_offset_list.append({"bpm_start_offset":parameters_to_assign_kiai_to_bpm[i]['bpm_start_offset'],"bpm_end_offset":parameters_to_assign_kiai_to_bpm[i]['bpm_end_offset'],"bar_total_time":parameters_to_assign_kiai_to_bpm[i]['bar_total_time'],"bar_w":parameters_to_assign_kiai_to_bpm[i]['bar_w'],"kiais":[]})
        j=0
        while j<len(sv_kiai_offset_pair_list):
            kiai_start_offset=-1
            kiai_end_offset=-1
            if parameters_to_assign_kiai_to_bpm[i]['bpm_start_offset']<sv_kiai_offset_pair_list[j]['end_offset'] and parameters_to_assign_kiai_to_bpm[i]['bpm_start_offset']>=sv_kiai_offset_pair_list[j]['start_offset']:
                kiai_start_offset=parameters_to_assign_kiai_to_bpm[i]['bpm_start_offset']
                
                if parameters_to_assign_kiai_to_bpm[i]['bpm_end_offset']<=sv_kiai_offset_pair_list[j]['end_offset']:
                    kiai_end_offset=parameters_to_assign_kiai_to_bpm[i]['bpm_end_offset']

                else: #parameters_to_assign_kiai_to_bpm[i]['bpm_end_offset']>=sv_kiai_offset_pair_list[j]['end_offset']:
                    kiai_end_offset=sv_kiai_offset_pair_list[j]['end_offset']

            elif parameters_to_assign_kiai_to_bpm[i]['bpm_end_offset']<sv_kiai_offset_pair_list[j]['end_offset'] and parameters_to_assign_kiai_to_bpm[i]['bpm_end_offset']>=sv_kiai_offset_pair_list[j]['start_offset']:
                kiai_end_offset=parameters_to_assign_kiai_to_bpm[i]['bpm_end_offset']
                kiai_start_offset=sv_kiai_offset_pair_list[j]['start_offset']

            elif parameters_to_assign_kiai_to_bpm[i]['bpm_start_offset']<=sv_kiai_offset_pair_list[j]['start_offset'] and parameters_to_assign_kiai_to_bpm[i]['bpm_end_offset']>=sv_kiai_offset_pair_list[j]['end_offset']:
                kiai_start_offset=sv_kiai_offset_pair_list[j]['start_offset']
                kiai_end_offset=sv_kiai_offset_pair_list[j]['end_offset']

            if kiai_start_offset!=-1 and kiai_end_offset!=-1 and kiai_start_offset!=kiai_end_offset:
                bpm_and_kiai_offset_list[-1]['kiais'].append({"start_offset":kiai_start_offset,"end_offset":kiai_end_offset})

            j+=1
        i+=1
    return bpm_and_kiai_offset_list

def calculate_one_bar_total_time(bpm,time_signature):
    one_beat_time=60000/bpm
    one_bar_total_time=one_beat_time*time_signature
    return one_bar_total_time

def calculate_total_bar_num(first_note_bar_start_offset,one_bar_total_time,last_obj_offset=-1,next_bpm_start_offset=-1):
    total_bar_num=1
    if last_obj_offset!=-1:
        while int(first_note_bar_start_offset + one_bar_total_time) < last_obj_offset:
            first_note_bar_start_offset += one_bar_total_time
            total_bar_num+=1

    elif next_bpm_start_offset!=-1:
        #while int(first_note_bar_start_offset + one_bar_total_time) < next_bpm_start_offset:
        while abs(int(first_note_bar_start_offset + one_bar_total_time) - next_bpm_start_offset) > FAULT_TOLERANCE:
            pre_diff=abs(int(first_note_bar_start_offset + one_bar_total_time) - next_bpm_start_offset)
            #print(abs(int(first_note_bar_start_offset + one_bar_total_time) - next_bpm_start_offset))
            first_note_bar_start_offset += one_bar_total_time
            cur_diff=abs(int(first_note_bar_start_offset + one_bar_total_time) - next_bpm_start_offset)
            if abs(pre_diff-FAULT_TOLERANCE)<abs(cur_diff-FAULT_TOLERANCE):
                break
            total_bar_num+=1
    return total_bar_num

def draw_kiai(bar_img,bpm_and_kiai_offset_list):
    accumulate_pre_bar_w=0
    i=0
    while i<len(bpm_and_kiai_offset_list):
        bar_total_time=bpm_and_kiai_offset_list[i]['bar_total_time']
        bar_w=bpm_and_kiai_offset_list[i]['bar_w']
        j=0
        while j<len(bpm_and_kiai_offset_list[i]['kiais']):
            start_x = round(decimal.Decimal(str((bpm_and_kiai_offset_list[i]['kiais'][j]['start_offset']-bpm_and_kiai_offset_list[i]['bpm_start_offset'])/bar_total_time*bar_w)))
            end_x = round(decimal.Decimal(str((bpm_and_kiai_offset_list[i]['kiais'][j]['end_offset']-bpm_and_kiai_offset_list[i]['bpm_start_offset'])/bar_total_time*bar_w)))
            kiai_img = np.full((BAR_H, end_x-start_x , 3), KIAI_COLOR , np.uint8)
            bar_img[:,start_x+accumulate_pre_bar_w:end_x+accumulate_pre_bar_w]=kiai_img
            j+=1
        accumulate_pre_bar_w+=bar_w
        i+=1
    return bar_img

def draw_barline(img, bar_w_sum,parameters_to_draw_bar_line):
    accumulate_pre_bar_w=0
    bar_num_draw=1
    k=0
    while k<len(parameters_to_draw_bar_line):
        bar_w=parameters_to_draw_bar_line[k]['bar_w']
        bpm=parameters_to_draw_bar_line[k]['bpm']
        time_signature=parameters_to_draw_bar_line[k]['time_signature']
        total_bar_num=parameters_to_draw_bar_line[k]['total_bar_num']
        bar_w_ratio=parameters_to_draw_bar_line[k]['bar_w_ratio']

        ori_time_signature=time_signature 
        if time_signature<=4: #if time_signature <= 4 (4/4) then double small bar line
            time_signature*=2
        one_beat_pix=ONE_BAR_W/time_signature

        i=0
        while i<total_bar_num:
            cv2.line(img, (ONE_BAR_W*i+accumulate_pre_bar_w,0), (ONE_BAR_W*i+accumulate_pre_bar_w,BAR_H), (230,230,230), 2) #bar line
            #small bar line
            j=1
            while (ONE_BAR_W*i)+(j*one_beat_pix) < ONE_BAR_W*(i+1) * bar_w_ratio:
                cv2.line(img, (round(decimal.Decimal(str((ONE_BAR_W*i)+accumulate_pre_bar_w+(j*one_beat_pix)))),SMALL_BARLINE_TOP_Y), (round(decimal.Decimal(str((ONE_BAR_W*i)+accumulate_pre_bar_w+(j*one_beat_pix)))),SMALL_BARLINE_BOTTOM_Y), (170,170,170), 1)
                j+=1
            if parameters_to_draw_bar_line[k]['is_need_draw_bpm']>=1:
                #bar num
                cv2.putText(img,f'{bar_num_draw}',((ONE_BAR_W*i)+5+accumulate_pre_bar_w,BAR_TEXT_Y),cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,(255,0,0),2)
            bar_num_draw+=1
            i+=1

        #bpm and time signature
        if parameters_to_draw_bar_line[k]['is_need_draw_bpm']:
            bpm_ts_text=f'BPM: {bpm}, ({ori_time_signature}/4)'
            #resize
            retval, baseLine = cv2.getTextSize(bpm_ts_text,cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,2)
            cv2.putText(img,bpm_ts_text,(int(ONE_BAR_W/2)-int(retval[0]/2)+accumulate_pre_bar_w,BAR_TEXT_Y),cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,(0,0,0),2)
        
        accumulate_pre_bar_w+=bar_w
            
        k+=1
    
    #bottom line
    cv2.line(img, (0,BAR_H-1), (bar_w_sum,BAR_H-1), (230,230,230), 1)
    return img

def draw_obj(img,bar_w_sum,bpm_and_obj_list,parameters_to_draw_bar_obj):
    accumulate_pre_bar_w=bar_w_sum
    j=len(bpm_and_obj_list)-1
    while j>=0:
        bar_w=parameters_to_draw_bar_obj[j]['bar_w']
        first_note_bar_start_offset=parameters_to_draw_bar_obj[j]['offset']
        bar_total_time=parameters_to_draw_bar_obj[j]['bar_total_time']
        accumulate_pre_bar_w-=bar_w
        i=len(bpm_and_obj_list[j]['hit_objs'])-1
        while i>=0:
            x = round(decimal.Decimal(str((bpm_and_obj_list[j]['hit_objs'][i]['offset']-first_note_bar_start_offset)/bar_total_time*bar_w)))
            if bpm_and_obj_list[j]['hit_objs'][i]['obj_type']=="note":
                if bpm_and_obj_list[j]['hit_objs'][i]['color']=="red":
                    if bpm_and_obj_list[j]['hit_objs'][i]['size']=="small":
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, (255,255,255), 1)
                    elif bpm_and_obj_list[j]['hit_objs'][i]['size']=="big":
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, (255,255,255), 1)
                elif bpm_and_obj_list[j]['hit_objs'][i]['color']=="blue":
                    if bpm_and_obj_list[j]['hit_objs'][i]['size']=="small":
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, (255,255,255), 1)
                    elif bpm_and_obj_list[j]['hit_objs'][i]['size']=="big":
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, (255,255,255), 1)
            i-=1
        #accumulate_pre_bar_w+=bar_w
        j-=1
    
    return img

def to_accumulate_one_bar_w_list(parameters_to_accumulate_bar_w):
    accumulate_one_bar_w_list=[]
    accumulate_one_bar_w_list.append(0)
    accumulate_one_bar_w=0
    i=0
    while i<len(parameters_to_accumulate_bar_w):
        left_bar_num=parameters_to_accumulate_bar_w[i]["left_bar_num"]
        j=0
        while j<left_bar_num:
            if j==left_bar_num-1:
                accumulate_one_bar_w+=parameters_to_accumulate_bar_w[i]['last_bar_w']
            else:
                accumulate_one_bar_w+=ONE_BAR_W
            accumulate_one_bar_w_list.append(accumulate_one_bar_w)
            j+=1
        i+=1
    return accumulate_one_bar_w_list

def cut_and_merge(bar_img, accumulate_one_bar_w_list):
    bar_w_start_x=0
    bar_w_end_x=0
    cut_img_list=[]
    j=0
    #
    index_offset=0
    while (j+1)*BAR_NUM_IN_ONE_CUT+index_offset<len(accumulate_one_bar_w_list):
        bar_w_start_x=accumulate_one_bar_w_list[BAR_NUM_IN_ONE_CUT*j+index_offset]
        bar_w_end_x=accumulate_one_bar_w_list[BAR_NUM_IN_ONE_CUT*(j+1)+index_offset]
        cut_img=bar_img[:, bar_w_start_x:bar_w_end_x]

        if bar_w_end_x-bar_w_start_x<BAR_NUM_IN_ONE_CUT*ONE_BAR_W:

            if CUT_AND_MERGE_MODE=='same bar num':
                black_img = np.full((BAR_H, (BAR_NUM_IN_ONE_CUT*ONE_BAR_W)-(bar_w_end_x-bar_w_start_x), 3), (0,0,0) , np.uint8)
                cut_img=cv2.hconcat([cut_img,black_img])

            elif CUT_AND_MERGE_MODE=='minimize black': 
                while bar_w_end_x-bar_w_start_x<BAR_NUM_IN_ONE_CUT*ONE_BAR_W and BAR_NUM_IN_ONE_CUT*(j+1)+index_offset<len(accumulate_one_bar_w_list)-1:
                    index_offset+=1
                    bar_w_end_x=accumulate_one_bar_w_list[BAR_NUM_IN_ONE_CUT*(j+1)+index_offset]
                if bar_w_end_x-bar_w_start_x>BAR_NUM_IN_ONE_CUT*ONE_BAR_W:
                    index_offset-=1
                    bar_w_end_x=accumulate_one_bar_w_list[BAR_NUM_IN_ONE_CUT*(j+1)+index_offset]

                cut_img=bar_img[:, bar_w_start_x:bar_w_end_x]
                black_img = np.full((BAR_H, (BAR_NUM_IN_ONE_CUT*ONE_BAR_W)-(bar_w_end_x-bar_w_start_x), 3), (0,0,0) , np.uint8)
                cut_img=cv2.hconcat([cut_img,black_img])
        cut_img_list.append(cut_img)
        j+=1
        
    if j*BAR_NUM_IN_ONE_CUT+index_offset<len(accumulate_one_bar_w_list)-1:#last
        bar_w_start_x=accumulate_one_bar_w_list[j*BAR_NUM_IN_ONE_CUT+index_offset]
        cut_img=bar_img[:, bar_w_start_x:]
        black_img = np.full((BAR_H, (BAR_NUM_IN_ONE_CUT*ONE_BAR_W)-(bar_img.shape[1]-bar_w_start_x), 3), (0,0,0) , np.uint8)
        cut_img=cv2.hconcat([cut_img,black_img])
        cut_img_list.append(cut_img)

    merge_bar_img=cut_img_list[0]
    i=1
    while i<len(cut_img_list):
        merge_bar_img=cv2.vconcat([merge_bar_img,cut_img_list[i]])
        i+=1
    return merge_bar_img

def create_title_img(artist,name,difficulty_name,mapper_name):
    title_img = np.full((BAR_H, BAR_NUM_IN_ONE_CUT*ONE_BAR_W, 3), BACKGROUND_COLOR , np.uint8)
    text=f'{artist} - {name} [{difficulty_name}] by {mapper_name}'

    #resize
    text_scale=TITLE_TEXT_SCALE#size
    retval, baseLine = cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,text_scale,2)
    while retval[0] + TITLE_TEXT_WIDTH_MARGIN*2 >= BAR_NUM_IN_ONE_CUT*ONE_BAR_W:
        text_scale-=0.01
        retval, baseLine = cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,text_scale,2)

    #draw text
    cv2.putText(title_img,text,(int((BAR_NUM_IN_ONE_CUT*ONE_BAR_W/2) - (retval[0]/2)),retval[1] + int((BAR_H-retval[1])/2)),cv2.FONT_HERSHEY_SIMPLEX,text_scale,(0,0,0),2)

    return title_img

##########code
def main_func(mode,osu_file_folder_path,osu_file_name,tp_list={},setting_parameters={}):
    osu_file_path=osu_file_folder_path+osu_file_name
    global ONE_BAR_W
    global BAR_H
    global BAR_NUM_IN_ONE_CUT
    global SMALL_BARLINE_TOP_Y
    global SMALL_BARLINE_BOTTOM_Y
    global CUT_AND_MERGE_MODE
    
    if setting_parameters != {}:
        ONE_BAR_W = setting_parameters['one_bar_w']
        BAR_H = setting_parameters['one_bar_h']
        SMALL_BARLINE_TOP_Y=int(BAR_H/3)
        SMALL_BARLINE_BOTTOM_Y=BAR_H

        BAR_NUM_IN_ONE_CUT = setting_parameters['bar_num_in_one_cut']
        CUT_AND_MERGE_MODE = setting_parameters['cut_and_merge_mode']
    
    #init folder
    clean_temp_folder()

    #read .osu and parse to title.txt, timing_point.txt and hitobj.txt
    read_map_information(osu_file_path)
    

    #read timing_point.txt
    bpm_list,sv_list=read_timing_point_txt()

    #read hitobj.txt
    hit_objs=read_hitobj_txt()

    #assign notes to their corresponding bpm segments
    #bpm_and_obj_list: [{"bpm_offset":,"bpm":,"time_signature":,"hit_objs":[{"offset":,"obj_type":,"color":,"size":,"slider_length":,"spinner_end_offset":}]}]
    if mode == 'manual':
        bpm_and_obj_list=assign_notes_to_bpm(hit_objs,tp_list)
    else:
        bpm_and_obj_list=assign_notes_to_bpm(hit_objs,bpm_list)
    
    #skip empty bpm before first object and after last obj
    while len(bpm_and_obj_list)>0:
        if len(bpm_and_obj_list[-1]['hit_objs'])==0:
            del bpm_and_obj_list[-1]
        else:
            break
    while len(bpm_and_obj_list)>0:
        if len(bpm_and_obj_list[0]['hit_objs'])==0:
            del bpm_and_obj_list[0]
        else:
            break
    
    parameters_to_assign_kiai_to_bpm=[]
    parameters_to_draw_bar_line=[]
    parameters_to_draw_bar_obj=[]
    parameters_to_accumulate_bar_w=[]
    k=0
    while k<len(bpm_and_obj_list):
        bpm=bpm_and_obj_list[k]['bpm']
        bpm_start_offset=bpm_and_obj_list[k]['bpm_offset']
        time_signature=bpm_and_obj_list[k]['time_signature']

        #calculate beat time(ms)
        one_bar_total_time = calculate_one_bar_total_time(bpm,time_signature)
        
        #calculate first barline offset (first have obj's bar) for first bpm
        if k==0:
            i=0
            while bpm_start_offset+(one_bar_total_time*(i+1))<=bpm_and_obj_list[k]['hit_objs'][0]['offset']:
                i+=1
            first_note_bar_start_offset = bpm_start_offset + one_bar_total_time * i
        else:
            first_note_bar_start_offset = bpm_start_offset

        #calculate total bar num
        total_bar_num=1
        if k<len(bpm_and_obj_list)-1:#if not last bpm, end point = next bpm start offset
            total_bar_num=calculate_total_bar_num(first_note_bar_start_offset,one_bar_total_time,next_bpm_start_offset=bpm_and_obj_list[k+1]['bpm_offset'])
            bpm_end_offset=bpm_and_obj_list[k+1]['bpm_offset']
        
        else:#if is last bpm, end point = last object offset
            last_obj_offset=bpm_and_obj_list[k]['hit_objs'][-1]['offset']
            total_bar_num=calculate_total_bar_num(first_note_bar_start_offset,one_bar_total_time,last_obj_offset=last_obj_offset)
            bpm_end_offset=(one_bar_total_time*total_bar_num)+first_note_bar_start_offset

        #calculate total bar time and bar_w
        bar_total_time=total_bar_num*one_bar_total_time
        bar_w=total_bar_num*ONE_BAR_W

        is_need_draw_bpm=True
        bar_w_ratio=1
        last_bar_w=ONE_BAR_W
        if k<len(bpm_and_obj_list)-1 and total_bar_num==1:#check next bpm start offset - this bpm start offset is or not < one bar total time
            if bpm_and_obj_list[k+1]['bpm_offset']-bpm_and_obj_list[k]['bpm_offset'] < one_bar_total_time and abs((bpm_and_obj_list[k+1]['bpm_offset']-bpm_and_obj_list[k]['bpm_offset'])-one_bar_total_time)>=FAULT_TOLERANCE:
                #print(bpm_and_obj_list[k+1]['bpm_offset'],bpm_and_obj_list[k]['bpm_offset'],bpm_and_obj_list[k+1]['bpm_offset']-bpm_and_obj_list[k]['bpm_offset'],one_bar_total_time,abs((bpm_and_obj_list[k+1]['bpm_offset']-bpm_and_obj_list[k]['bpm_offset'])-one_bar_total_time),FAULT_TOLERANCE)
                is_need_draw_bpm=False
                bar_w_ratio=(bpm_and_obj_list[k+1]['bpm_offset']-bpm_and_obj_list[k]['bpm_offset'])/one_bar_total_time
                bar_total_time=int(bar_w_ratio*one_bar_total_time)
                bar_w=int(bar_w_ratio*ONE_BAR_W)
                last_bar_w=bar_w

        #draw bar line
        parameters_to_assign_kiai_to_bpm.append({"bpm_start_offset":first_note_bar_start_offset,"bpm_end_offset":bpm_end_offset,"bar_total_time":bar_total_time,"bar_w":bar_w})
        parameters_to_draw_bar_line.append({"bar_w":bar_w,"bpm":bpm,"time_signature":time_signature,"total_bar_num":total_bar_num,"bar_w_ratio":bar_w_ratio,"is_need_draw_bpm":is_need_draw_bpm})
        parameters_to_draw_bar_obj.append({"bar_w":bar_w,"offset":first_note_bar_start_offset,"bar_total_time":bar_total_time})
        parameters_to_accumulate_bar_w.append({"left_bar_num":total_bar_num,"last_bar_w":last_bar_w})

        k+=1
    bar_w_sum=0
    i=0
    while i<len(parameters_to_draw_bar_line):
        bar_w_sum+=parameters_to_draw_bar_line[i]['bar_w']
        i+=1
    
    #get kiai offset pair (on and off)
    sv_kiai_offset_pair_list=to_kiai_offset_pair(sv_list)

    #assign kiai to bpm
    #bpm_and_kiai_offset_list: [{"bpm_start_offset":,"bpm_end_offset":,"bar_total_time":,"bar_w":,"kiais":[{"start_offset":,"end_offset":,}]}]
    bpm_and_kiai_offset_list=assign_kiai_to_bpm(parameters_to_assign_kiai_to_bpm,sv_kiai_offset_pair_list)

    bar_img = np.full((BAR_H, bar_w_sum, 3), BACKGROUND_COLOR , np.uint8)

    #draw kiai
    bar_img = draw_kiai(bar_img,bpm_and_kiai_offset_list)

    #draw barline
    bar_img = draw_barline(bar_img,bar_w_sum,parameters_to_draw_bar_line)
    
    #draw obj
    bar_img = draw_obj(bar_img,bar_w_sum,bpm_and_obj_list,parameters_to_draw_bar_obj)
    
    #accumulate every bar_w for cut
    accumulate_one_bar_w_list=to_accumulate_one_bar_w_list(parameters_to_accumulate_bar_w)
    
    #cut and merge
    merge_bar_img=cut_and_merge(bar_img,accumulate_one_bar_w_list)
    
    #title generate and merge

    #read title.txt
    name,artist,mapper_name,difficulty_name=read_title_txt()
    
    #create img
    title_img = create_title_img(name,artist,mapper_name,difficulty_name)
    
    #merge
    img = cv2.vconcat([title_img,merge_bar_img])

    #save
    cv2.imwrite(f'./output folder/{osu_file_name[:-4]}.png',img)

FILE_FOLDER_PATH='./osu file input folder/'
OSU_FILE_NAME_LIST=['Umeboshi Chazuke - ICHIBANBOSHIROCKET (_gt) [INNER ONI].osu',
                    'DJ Raisei - when ____ disappears from the world (Raphalge) [Inner Oni].osu',
                    'Yorushika - Replicant (Hivie) [Mirror].osu',
                    'Kobaryo - New Game Plus (Love Plus rmx) (JarvisGaming) [go play Rabbit and Steel].osu',
                    'Rin - Mythic set ~ Heart-Stirring Urban Legends (tasuke912) [Oni].osu',
                    'technoplanet - Macuilxochitl (Latin Jazz Mix) (Dusk-) [MAXIMUM].osu',
                    'Camellia - OOPARTS (Paradise_) [Antikythera].osu']
osu_files=os.listdir(FILE_FOLDER_PATH)
#main_func('auto',FILE_FOLDER_PATH,'Camellia - OOPARTS (Paradise_) [Antikythera].osu')
#i=0
#while i<len(osu_files):
#    main_func(FILE_FOLDER_PATH,osu_files[i])
#    i+=1
