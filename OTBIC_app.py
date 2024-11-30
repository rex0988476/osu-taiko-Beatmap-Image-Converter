import cv2
import numpy as np
import decimal
import os
import shutil

##########variable
PRINT_PROCESS=False
ONE_BAR_W=320
BAR_H=60
SMALL_OBJ_RADIUS=10
BIG_OBJ_RADIUS=15
BAR_TEXT_Y=16
NOTE_COLOR_RED = (43, 68, 255) # BGR
NOTE_COLOR_BLUE = (255, 140, 66) # BGR
SLIDER_COLOR = (6, 184, 252) # BGR
SPINNER_COLOR=(42,176,67)# BGR
KIAI_COLOR = (17, 82, 141) # BGR
BACKGROUND_COLOR=(105,105,105)
TEXT_COLOR=(0,0,0)
BAR_NUM_COLOR=(255,0,0)
FIRST_BARLINE_COLOR=(0,0,255)
OBJ_BORDER_COLOR=(255,255,255)
SMALL_BARLINE_COLOR=(170,170,170)
BARLINE_COLOR=(230,230,230)
BOTTOM_LINE_COLOR=(230,230,230)
FAULT_TOLERANCE=1#fit rightmost note that x + BAR.bar_line_offset will exceed BAR_W
BAR_LINE_OFFSET_Y=10#for small bar line and notes layout
BAR_NUM_IN_ONE_CUT=4
SMALL_BARLINE_TOP_Y=int(BAR_H/3)
SMALL_BARLINE_BOTTOM_Y=BAR_H
BAR_TEXT_SCALE=0.55
TITLE_TEXT_SCALE=1
TITLE_TEXT_WIDTH_MARGIN=50
CUT_AND_MERGE_MODE_S=['minimize black','same bar num']#'minimize black' and 'same bar num'
CUT_AND_MERGE_MODE=CUT_AND_MERGE_MODE_S[0]
SLIDERMULTIPLIER=-1
DEFAULT_SV=1
##########function

def clean_temp_folder():
    shutil.rmtree('./data')
    os.mkdir('./data')

def read_map_information(osu_file_name):#read .osu file and generate title.txt, timing_point.txt and hitobj.txt
    #read .osu file
    f=open(osu_file_name,'r',encoding='utf-8')
    texts=f.readlines()
    f.close()

    #open
    title_f=open('./data/title.txt','w')
    tp_f=open('./data/timing_point.txt','w')
    hitobj_f=open('./data/hitobj.txt','w')
    slider_parameter_f=open('./data/slider_parameter.txt','w')
    
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

        #for slider_parameter.txt
        if texts[i].find('SliderMultiplier:')!=-1:
            slider_parameter_f.write(f"{texts[i].split(':')[1]}\n")
        elif start_record_time_point:
            #sv
            s=texts[i].split(',')
            if len(s)>=8:
                if s[6]=="0":
                    time_offset=int(s[0])
                    try:
                        sv=int(s[1])
                    except:
                        sv=float(s[1])
                    slider_parameter_f.write(f'{time_offset},{sv}\n')
                        


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
                    raise AssertionError(f"#ERROR[note]: {texts[i]}")
                
                hitobj_f.write(f"{obj_offset},{obj_type},{color},{size}\n")
            #slider
            elif s[3] in ["2","6"]:
                obj_type="slider"
                if s[4] in ["4","6","12","14"]:
                    size="big"
                else:
                    size="small"
                try:
                    length=int(s[7])
                except:
                    length=float(s[7])
                repeat_time=int(s[6])
                length=(repeat_time*length)
                hitobj_f.write(f"{obj_offset},{obj_type},{size},{length}\n")
            #spinner
            elif s[3] in ["12","8"]:
                obj_type="spinner"
                end_offset=int(s[5])
                hitobj_f.write(f"{obj_offset},{obj_type},{end_offset}\n")
            else:
                raise AssertionError(f"#ERROR[obj_type]: {texts[i]}")
            
            
        i+=1
    
    title_f.write(f'Title:{title}\n')
    title_f.write(f'Artist:{artist}\n')
    title_f.write(f'Mapper:{mapper}\n')
    title_f.write(f'Difficulty Name:{diff_name}\n')

    title_f.close()
    tp_f.close()
    hitobj_f.close()
    slider_parameter_f.close()
    
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
    kiai_sv_list=[]
    i=0
    while i<len(s):
        if s[i][-1]=='\n':
            s[i]=s[i][:-1]
        if s[i].split(',')[1]=="bpm":
            bpm_list.append({"offset":int(s[i].split(',')[0]),"bpm":int(s[i].split(',')[2]),"time_signature":int(s[i].split(',')[3])})
        elif s[i].split(',')[1]=="sv":
            kiai_sv_list.append({"offset":int(s[i].split(',')[0]),"kiai_mode":int(s[i].split(',')[2])})
        i+=1
    
    return bpm_list,kiai_sv_list

def read_hitobj_txt():
    hit_objs=[]
    f=open('./data/hitobj.txt','r')
    s=f.readlines()
    f.close()
    i=0
    while i<len(s):
        if s[i][-1]=='\n':
            s[i]=s[i][:-1]
        sp=s[i].split(',')
        offset=int(sp[0])
        obj_type=sp[1]
        if obj_type=="note":
            color=sp[2]
            size=sp[3]
            hit_objs.append({'offset':offset,'obj_type':obj_type,'color':color,'size':size})
        elif obj_type=="slider":
            size=sp[2]
            try:
                slider_length=int(sp[3])
            except:
                slider_length=float(sp[3])
            hit_objs.append({'offset':offset,'obj_type':obj_type,'size':size,'length':slider_length})
        elif obj_type=="spinner":
            spinner_end_offset=int(sp[2])
            hit_objs.append({'offset':offset,'obj_type':obj_type,'end_offset':spinner_end_offset})
        i+=1
    return hit_objs

def read_slider_parameter_txt():
    global SLIDERMULTIPLIER
    slider_parameters=[]
    slider_parameter_f=open('./data/slider_parameter.txt','r')
    s=slider_parameter_f.readlines()
    i=0
    while i<len(s):
        s[i]=s[i][:-1]
        if i==0:
            try:
                SLIDERMULTIPLIER = int(s[i])
            except:
                SLIDERMULTIPLIER = float(s[i])
        else:
            offset=int(s[i].split(',')[0])
            sv=-100/float(s[i].split(',')[1])
            slider_parameters.append({'offset':offset,'sv':sv})
        i+=1
    return slider_parameters

def check_and_fix_first_bpm_offset(hit_objs,bpm_list):
    first_obj_offset=hit_objs[0]['offset']
    fix_first_bpm_offset=bpm_list[0]['offset']

    bpm = bpm_list[0]['bpm']
    time_signature = bpm_list[0]['time_signature']
    one_beat_time=60000/bpm
    one_bar_total_time=one_beat_time*time_signature
    
    if first_obj_offset<fix_first_bpm_offset:
        while first_obj_offset<int(fix_first_bpm_offset):#may need FAULT_TOLERANCE too, not sure yet
            #print(fix_first_bpm_offset,first_obj_offset)
            fix_first_bpm_offset-=one_bar_total_time
        bpm_list[0]['offset']=fix_first_bpm_offset

    return bpm_list

def calculate_slider_end_time(hit_objs,bpm_list,slider_parameters):
    #end time formula: length / (SliderMultiplier * 100 * SV) * beatLength
    hit_objs_with_sliders=[]
    i=0
    while i<len(hit_objs):
        if hit_objs[i]['obj_type']=="slider":
            j=0
            while j<len(bpm_list):
                if bpm_list[j]['offset']>hit_objs[i]['offset']:
                    break
                j+=1
            #bpm_start_index=j-1
            bpm = bpm_list[j-1]['bpm']
            beatLength = 60000/bpm #one_beat_time

            j=0
            while j<len(slider_parameters):
                if slider_parameters[j]['offset']>hit_objs[i]['offset']:
                    break
                j+=1
            #sv_start_index=j-1
            if len(slider_parameters)==0:
                sv=DEFAULT_SV
            else:
                sv = slider_parameters[j-1]['sv']
            
            end_offset = hit_objs[i]['offset'] + (hit_objs[i]['length'] / (SLIDERMULTIPLIER * 100 * sv)) * beatLength

            #print(hit_objs[i]['offset'],end_offset)

            hit_objs_with_sliders.append({'offset':hit_objs[i]['offset'],'obj_type':"slider",'size':hit_objs[i]['size'],'end_offset':end_offset})
        else:
            hit_objs_with_sliders.append(hit_objs[i])

        i+=1
    return hit_objs_with_sliders

def to_kiai_offset_pair(kiai_sv_list):
    sv_kiai_offset_pair_list=[]
    i=0
    while i+1<len(kiai_sv_list):
        sv_kiai_offset_pair_list.append({"start_offset":kiai_sv_list[i]['offset'],"end_offset":kiai_sv_list[i+1]['offset']})
        i+=2
    if len(kiai_sv_list)%2==1:
        sv_kiai_offset_pair_list.append({"start_offset":kiai_sv_list[i]['offset'],"end_offset":-1})

    return sv_kiai_offset_pair_list

def fix_slider_and_spinner(hit_objs,bpm_list):#if slider cross several bpms, then it need to be divide into these bpms
    hit_objs_with_fix_slider_and_spinners=[]
    i=0
    while i<len(hit_objs):
        if hit_objs[i]['obj_type']=="note":
            hit_objs_with_fix_slider_and_spinners.append(hit_objs[i])
        elif hit_objs[i]['obj_type']=="slider":
            #print(f"o:{hit_objs[i]['offset']},e:{hit_objs[i]['end_offset']}")
            j=0
            while j<len(bpm_list):
                if bpm_list[j]['offset']>hit_objs[i]['offset']:
                    break
                j+=1
            j-=1
            start_slider_bpm_index=j
            j=0
            while j<len(bpm_list):
                if bpm_list[j]['offset']>hit_objs[i]['end_offset']:
                    break
                j+=1
            j-=1
            end_slider_bpm_index=j

            obj_type="slider"
            #print(end_slider_bpm_index,start_slider_bpm_index)
            size=hit_objs[i]['size']
            k=start_slider_bpm_index
            j=0
            while j<=end_slider_bpm_index-start_slider_bpm_index:#new slider num
                if k==start_slider_bpm_index:
                    offset=hit_objs[i]['offset']
                    have_head=True
                else:
                    offset=bpm_list[k]['offset']
                    have_head=False
                if k==end_slider_bpm_index:
                    end_offset=hit_objs[i]['end_offset']
                    have_tail=True
                else:
                    end_offset=bpm_list[k]['offset']
                    have_tail=False
                hit_objs_with_fix_slider_and_spinners.append({'offset':offset,'obj_type':obj_type,'size':size,'end_offset':end_offset,'have_head':have_head,'have_tail':have_tail})
                k+=1
                j+=1
        elif hit_objs[i]['obj_type']=="spinner":
            j=0
            while j<len(bpm_list):
                if bpm_list[j]['offset']>hit_objs[i]['offset']:
                    break
                j+=1
            j-=1
            start_spinner_bpm_index=j
            j=0
            while j<len(bpm_list):
                if bpm_list[j]['offset']>hit_objs[i]['end_offset']:
                    break
                j+=1
            j-=1
            end_spinner_bpm_index=j

            obj_type="spinner"
            k=start_spinner_bpm_index
            j=0
            while j<=end_spinner_bpm_index-start_spinner_bpm_index:#new spinner num
                if k==start_spinner_bpm_index:
                    offset=hit_objs[i]['offset']
                    have_head=True
                else:
                    offset=bpm_list[k]['offset']
                    have_head=False
                if k==end_spinner_bpm_index:
                    end_offset=hit_objs[i]['end_offset']
                    have_tail=True
                else:
                    end_offset=bpm_list[k]['offset']
                    have_tail=False
                hit_objs_with_fix_slider_and_spinners.append({'offset':offset,'obj_type':obj_type,'end_offset':end_offset,'have_head':have_head,'have_tail':have_tail})
                k+=1
                j+=1
        i+=1
    return hit_objs_with_fix_slider_and_spinners

def assign_objs_to_bpm(hit_objs,bpm_list):
    bpm_and_obj_list=[]
    
    i=0
    j=0
    while i<len(bpm_list):
        if bpm_list[i]['bpm']>0 and bpm_list[i]['bpm']<=1000 and bpm_list[i]['time_signature']<=16 :#NO WEIRD BPM AND TIME SIGNATURE PLEASE.
            bpm_start_offset=bpm_list[i]['offset']
            bpm=bpm_list[i]['bpm']
            time_signature=bpm_list[i]['time_signature']
            bpm_and_obj_list.append({"bpm_offset":bpm_start_offset,"bpm":bpm,"time_signature":time_signature,"hit_objs":[]})
            if i<len(bpm_list)-1:
                next_bpm_offset=bpm_list[i+1]['offset']
            else:
                if hit_objs[-1]['obj_type']=="note":
                    next_bpm_offset=hit_objs[-1]['offset']+1
                else:
                    next_bpm_offset=hit_objs[-1]['end_offset']+1

            while j<len(hit_objs) and hit_objs[j]['offset']<next_bpm_offset:
                bpm_and_obj_list[-1]["hit_objs"].append(hit_objs[j])#{'offset':offset,'obj_type':obj_type,'color':color,'size':size}
                j+=1
            if PRINT_PROCESS:
                print(f'{i+1}/{len(bpm_list)}(in)')
        else:
            if PRINT_PROCESS:
                print(f'{i+1}/{len(bpm_list)}(out)')
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
        while int(first_note_bar_start_offset + one_bar_total_time) < last_obj_offset + FAULT_TOLERANCE:
            first_note_bar_start_offset += one_bar_total_time
            total_bar_num+=1

    elif next_bpm_start_offset!=-1:
        #if first_note_bar_start_offset==6098543:
        #    print(one_bar_total_time)
        #    print(first_note_bar_start_offset+one_bar_total_time,next_bpm_start_offset,abs(int(first_note_bar_start_offset + one_bar_total_time) - next_bpm_start_offset))
        #    print(first_note_bar_start_offset+(one_bar_total_time*2),next_bpm_start_offset,abs(int(first_note_bar_start_offset + (one_bar_total_time*2)) - next_bpm_start_offset))
        #    print(first_note_bar_start_offset+(one_bar_total_time*3),next_bpm_start_offset,abs(int(first_note_bar_start_offset + (one_bar_total_time*3)) - next_bpm_start_offset))
        while int(first_note_bar_start_offset + one_bar_total_time) < next_bpm_start_offset:
        #while abs(int(first_note_bar_start_offset + one_bar_total_time) - next_bpm_start_offset) > FAULT_TOLERANCE:
            #pre_diff=abs(int(first_note_bar_start_offset + one_bar_total_time) - next_bpm_start_offset)
            first_note_bar_start_offset += one_bar_total_time
            #cur_diff=abs(int(first_note_bar_start_offset + one_bar_total_time) - next_bpm_start_offset)
            #if abs(pre_diff-FAULT_TOLERANCE)<abs(cur_diff-FAULT_TOLERANCE):
            #    break
            total_bar_num+=1
    return total_bar_num

def get_offset_list(first_note_bar_start_offset,one_bar_total_time,last_obj_offset=-1,next_bpm_start_offset=-1):
    offset_list=[]
    offset_list.append(int(first_note_bar_start_offset))
    if last_obj_offset!=-1:
        while int(first_note_bar_start_offset + one_bar_total_time) < last_obj_offset + FAULT_TOLERANCE:
            first_note_bar_start_offset += one_bar_total_time
            offset_list.append(int(first_note_bar_start_offset))
            #offset_list.append(round(decimal.Decimal(str(first_note_bar_start_offset))))
    elif next_bpm_start_offset!=-1:
        while int(first_note_bar_start_offset + one_bar_total_time) < next_bpm_start_offset:
            first_note_bar_start_offset += one_bar_total_time
            offset_list.append(int(first_note_bar_start_offset))
            #offset_list.append(round(decimal.Decimal(str(first_note_bar_start_offset))))
    return offset_list

def create_bar_num_offset_table_txt(parameters_to_create_bar_num_offset_table,osu_file_name):
    f=open(f'./output folder/{osu_file_name[:-4]}_bar_num_offset_table.txt','w')
    f.write(f'bar num, offset\n')
    bar_num_draw=1
    k=0
    while k<len(parameters_to_create_bar_num_offset_table):
        i=0
        while i<len(parameters_to_create_bar_num_offset_table[k]['offset_list']):
            #ms to m:s:ms
            m=parameters_to_create_bar_num_offset_table[k]["offset_list"][i]//1000//60
            if len(str(m))==1:
                m=f'0{str(m)}'
            s=parameters_to_create_bar_num_offset_table[k]["offset_list"][i]//1000%60
            if len(str(s))==1:
                s=f'0{str(s)}'
            ms=parameters_to_create_bar_num_offset_table[k]["offset_list"][i]%1000
            if len(str(ms))==2:
                ms=f'0{str(ms)}'
            elif len(str(ms))==1:
                ms=f'00{str(ms)}'
            f.write(f'{bar_num_draw}, {m}:{s}:{ms}\n')
            bar_num_draw+=1
            i+=1
        k+=1
    f.close()

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
            #print(i,j,bar_img.shape,start_x+accumulate_pre_bar_w,end_x+accumulate_pre_bar_w,bar_img[:,start_x+accumulate_pre_bar_w:end_x+accumulate_pre_bar_w].shape)
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
        last_bar_w_ratio=parameters_to_draw_bar_line[k]['last_bar_w_ratio']

        ori_time_signature=time_signature 
        if time_signature<=4: #if time_signature <= 4 (4/4) then double small bar line
            time_signature*=2
        one_beat_pix=ONE_BAR_W/time_signature

        i=0
        while i<total_bar_num:
            #bar line
            if i==0:
                cv2.line(img, (ONE_BAR_W*i+accumulate_pre_bar_w,0), (ONE_BAR_W*i+accumulate_pre_bar_w,BAR_H), FIRST_BARLINE_COLOR, 4) 
            else:
                cv2.line(img, (ONE_BAR_W*i+accumulate_pre_bar_w,0), (ONE_BAR_W*i+accumulate_pre_bar_w,BAR_H), BARLINE_COLOR, 2)
            #small bar line
            if i==total_bar_num-1:
                j=1
                while (ONE_BAR_W*i)+(j*one_beat_pix) < ONE_BAR_W*i + ONE_BAR_W*last_bar_w_ratio:
                    cv2.line(img, (round(decimal.Decimal(str((ONE_BAR_W*i)+accumulate_pre_bar_w+(j*one_beat_pix)))),SMALL_BARLINE_TOP_Y), (round(decimal.Decimal(str((ONE_BAR_W*i)+accumulate_pre_bar_w+(j*one_beat_pix)))),SMALL_BARLINE_BOTTOM_Y), SMALL_BARLINE_COLOR, 1)
                    j+=1
            else:
                j=1
                while (ONE_BAR_W*i)+(j*one_beat_pix) < ONE_BAR_W*(i+1):
                    cv2.line(img, (round(decimal.Decimal(str((ONE_BAR_W*i)+accumulate_pre_bar_w+(j*one_beat_pix)))),SMALL_BARLINE_TOP_Y), (round(decimal.Decimal(str((ONE_BAR_W*i)+accumulate_pre_bar_w+(j*one_beat_pix)))),SMALL_BARLINE_BOTTOM_Y), SMALL_BARLINE_COLOR, 1)
                    j+=1
            #bar num
            if i<total_bar_num-1 or last_bar_w_ratio==1:
                cv2.putText(img,f'{bar_num_draw}',((ONE_BAR_W*i)+5+accumulate_pre_bar_w,BAR_TEXT_Y),cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,BAR_NUM_COLOR,2)
            bar_num_draw+=1
            i+=1

        #bpm and time signature
        if parameters_to_draw_bar_line[k]['is_need_draw_bpm']:
            bpm_ts_text=f'BPM: {bpm}, ({ori_time_signature}/4)'
            #resize
            retval, baseLine = cv2.getTextSize(bpm_ts_text,cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,2)
            cv2.putText(img,bpm_ts_text,(int(ONE_BAR_W/2)-int(retval[0]/2)+accumulate_pre_bar_w,BAR_TEXT_Y),cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,TEXT_COLOR,2)
        
        accumulate_pre_bar_w+=bar_w
            
        k+=1
    
    #bottom line
    cv2.line(img, (0,BAR_H-1), (bar_w_sum,BAR_H-1), BOTTOM_LINE_COLOR, 1)
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
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, OBJ_BORDER_COLOR, 1)
                    elif bpm_and_obj_list[j]['hit_objs'][i]['size']=="big":
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, NOTE_COLOR_RED, -1)
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, OBJ_BORDER_COLOR, 1)
                elif bpm_and_obj_list[j]['hit_objs'][i]['color']=="blue":
                    if bpm_and_obj_list[j]['hit_objs'][i]['size']=="small":
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, OBJ_BORDER_COLOR, 1)
                    elif bpm_and_obj_list[j]['hit_objs'][i]['size']=="big":
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, NOTE_COLOR_BLUE, -1)
                        cv2.circle(img, (x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, OBJ_BORDER_COLOR, 1)
            if bpm_and_obj_list[j]['hit_objs'][i]['obj_type']=="slider":
                start_x = x
                end_x = round(decimal.Decimal(str((bpm_and_obj_list[j]['hit_objs'][i]['end_offset']-first_note_bar_start_offset)/bar_total_time*bar_w)))
                if bpm_and_obj_list[j]['hit_objs'][i]['size']=="small":
                    if bpm_and_obj_list[j]['hit_objs'][i]['have_tail']==True:
                        cv2.circle(img,(end_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, SLIDER_COLOR,-1)
                        cv2.circle(img,(end_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SMALL_OBJ_RADIUS, OBJ_BORDER_COLOR,1)
                    cv2.rectangle(img, (start_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y-SMALL_OBJ_RADIUS), (end_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y+SMALL_OBJ_RADIUS), OBJ_BORDER_COLOR, 1)
                    cv2.rectangle(img, (start_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y-SMALL_OBJ_RADIUS+1), (end_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y+SMALL_OBJ_RADIUS-1), SLIDER_COLOR, -1)
                    if bpm_and_obj_list[j]['hit_objs'][i]['have_head']==True:
                        cv2.circle(img,(start_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y),SMALL_OBJ_RADIUS,SLIDER_COLOR,-1)
                        cv2.circle(img,(start_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y),SMALL_OBJ_RADIUS,OBJ_BORDER_COLOR,1)
                elif bpm_and_obj_list[j]['hit_objs'][i]['size']=="big":
                    if bpm_and_obj_list[j]['hit_objs'][i]['have_tail']==True:
                        cv2.circle(img,(end_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, SLIDER_COLOR,-1)
                        cv2.circle(img,(end_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), BIG_OBJ_RADIUS, OBJ_BORDER_COLOR,1)
                    cv2.rectangle(img, (start_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y-BIG_OBJ_RADIUS), (end_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y+BIG_OBJ_RADIUS), OBJ_BORDER_COLOR, 1)
                    cv2.rectangle(img, (start_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y-BIG_OBJ_RADIUS+1), (end_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y+BIG_OBJ_RADIUS-1), SLIDER_COLOR, -1)
                    if bpm_and_obj_list[j]['hit_objs'][i]['have_head']==True:
                        cv2.circle(img,(start_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y),BIG_OBJ_RADIUS,SLIDER_COLOR,-1)
                        cv2.circle(img,(start_x+accumulate_pre_bar_w, int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y),BIG_OBJ_RADIUS,OBJ_BORDER_COLOR,1)
            if bpm_and_obj_list[j]['hit_objs'][i]['obj_type']=="spinner":
                start_x = x
                end_x = round(decimal.Decimal(str((bpm_and_obj_list[j]['hit_objs'][i]['end_offset']-first_note_bar_start_offset)/bar_total_time*bar_w)))
                if bpm_and_obj_list[j]['hit_objs'][i]['have_tail']==True:
                    cv2.line(img, (end_x-5+accumulate_pre_bar_w,int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y-5), (end_x+5+accumulate_pre_bar_w,int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y+5), SPINNER_COLOR, 3)
                    cv2.line(img, (end_x+5+accumulate_pre_bar_w,int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y-5), (end_x-5+accumulate_pre_bar_w,int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y+5), SPINNER_COLOR, 3)
                cv2.line(img, (start_x+accumulate_pre_bar_w,int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), (end_x+accumulate_pre_bar_w,int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y), SPINNER_COLOR, 2)
                if bpm_and_obj_list[j]['hit_objs'][i]['have_head']==True:
                    cv2.circle(img,(start_x+accumulate_pre_bar_w,int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y),BIG_OBJ_RADIUS,SPINNER_COLOR,-1)
                    cv2.circle(img,(start_x+accumulate_pre_bar_w,int((SMALL_BARLINE_BOTTOM_Y-(SMALL_BARLINE_TOP_Y))/2)+SMALL_BARLINE_TOP_Y),BIG_OBJ_RADIUS,OBJ_BORDER_COLOR,1)
            i-=1
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
        if PRINT_PROCESS:
            print(f'{(j+1)*BAR_NUM_IN_ONE_CUT+index_offset}/{len(accumulate_one_bar_w_list)}')
        
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
        if PRINT_PROCESS:
            print(f'{i}/{len(cut_img_list)}')
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
    cv2.putText(title_img,text,(int((BAR_NUM_IN_ONE_CUT*ONE_BAR_W/2) - (retval[0]/2)),retval[1] + int((BAR_H-retval[1])/2)),cv2.FONT_HERSHEY_SIMPLEX,text_scale,TEXT_COLOR,2)

    return title_img

##########code
def main_func(mode,osu_file_folder_path,osu_file_name,tp_list={},setting_parameters={},color_setting_parameters={}):
    osu_file_path=osu_file_folder_path+osu_file_name
    if PRINT_PROCESS:
        print(osu_file_name)
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
    
    if color_setting_parameters!={}:
        global NOTE_COLOR_BLUE, NOTE_COLOR_RED, SLIDER_COLOR, SPINNER_COLOR, BACKGROUND_COLOR, OBJ_BORDER_COLOR, KIAI_COLOR, FIRST_BARLINE_COLOR, BARLINE_COLOR, SMALL_BARLINE_COLOR, BAR_NUM_COLOR, TEXT_COLOR, BOTTOM_LINE_COLOR
        NOTE_COLOR_RED=color_setting_parameters['red_note']
        NOTE_COLOR_BLUE=color_setting_parameters['blue_note']
        SLIDER_COLOR=color_setting_parameters['slider']
        SPINNER_COLOR=color_setting_parameters['spinner']
        BACKGROUND_COLOR=color_setting_parameters['background']
        KIAI_COLOR=color_setting_parameters['kiai']
        OBJ_BORDER_COLOR=color_setting_parameters['border']
        FIRST_BARLINE_COLOR=color_setting_parameters['first_barline']
        BARLINE_COLOR=color_setting_parameters['barline']
        SMALL_BARLINE_COLOR=color_setting_parameters['small_barline']
        BOTTOM_LINE_COLOR=color_setting_parameters['bottom_line']
        BAR_NUM_COLOR=color_setting_parameters['bar_num']
        TEXT_COLOR=color_setting_parameters['text']
    
    #init folder
    if PRINT_PROCESS:
        print('clean_temp_folder')
    clean_temp_folder()

    #read .osu and parse to title.txt, timing_point.txt and hitobj.txt
    if PRINT_PROCESS:
        print('read_map_information')
    read_map_information(osu_file_path)

    #read timing_point.txt
    if PRINT_PROCESS:
        print('read_timing_point_txt')
    bpm_list,kiai_sv_list=read_timing_point_txt()

    #read hitobj.txt
    if PRINT_PROCESS:
        print('read_hitobj_txt')
    hit_objs=read_hitobj_txt()

    #check and fix if first obj offset < first bpm offset :(
    if PRINT_PROCESS:
        print('check_and_fix_first_bpm_offset')
    if mode == 'manual':
        tp_list=check_and_fix_first_bpm_offset(hit_objs,tp_list)
    else:
        bpm_list=check_and_fix_first_bpm_offset(hit_objs,bpm_list)

    #read slider_parameter.txt
    if PRINT_PROCESS:
        print('read_slider_parameter_txt')
    slider_parameters=read_slider_parameter_txt()

    #calculate slider end time
    if PRINT_PROCESS:
        print('calculate_slider_end_time')
    if mode == 'manual':
        hit_objs_with_sliders=calculate_slider_end_time(hit_objs,tp_list,slider_parameters)
    else:
        hit_objs_with_sliders=calculate_slider_end_time(hit_objs,bpm_list,slider_parameters)
    

    #if slider cross several bpms, then it need to be divide into these bpms
    if PRINT_PROCESS:
        print('fix_slider_and_spinner')
    if mode == 'manual':
        hit_objs_with_fix_slider_and_spinners=fix_slider_and_spinner(hit_objs_with_sliders,tp_list)
    else:
        hit_objs_with_fix_slider_and_spinners=fix_slider_and_spinner(hit_objs_with_sliders,bpm_list)

    #assign notes to their corresponding bpm segments
    if PRINT_PROCESS:
        print('assign_objs_to_bpm')
    #bpm_and_obj_list: [{"bpm_offset":,"bpm":,"time_signature":,"hit_objs":[{"offset":,"obj_type":,"color":,"size":,"slider_length":,"spinner_end_offset":}]}]
    if mode == 'manual':
        bpm_and_obj_list=assign_objs_to_bpm(hit_objs_with_fix_slider_and_spinners,tp_list)
    else:
        bpm_and_obj_list=assign_objs_to_bpm(hit_objs_with_fix_slider_and_spinners,bpm_list)
    
    #skip empty bpm before first object and after last obj
    if PRINT_PROCESS:
        print('skip empty bpm')
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
    if PRINT_PROCESS:
        print('generate 4 parameters list')
    parameters_to_create_bar_num_offset_table=[]
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

        
        #calculate total bar num & create bar num offset table
        total_bar_num=1
        offset_list=[]
        if k<len(bpm_and_obj_list)-1:#if not last bpm, end point = next bpm start offset
            total_bar_num=calculate_total_bar_num(first_note_bar_start_offset,one_bar_total_time,next_bpm_start_offset=bpm_and_obj_list[k+1]['bpm_offset'])
            offset_list=get_offset_list(first_note_bar_start_offset,one_bar_total_time,next_bpm_start_offset=bpm_and_obj_list[k+1]['bpm_offset'])
            bpm_end_offset=bpm_and_obj_list[k+1]['bpm_offset']
        
        else:#if is last bpm, end point = last object offset
            if bpm_and_obj_list[k]['hit_objs'][-1]['obj_type']=='note':
                last_obj_offset=bpm_and_obj_list[k]['hit_objs'][-1]['offset']
            else:
                last_obj_offset=bpm_and_obj_list[k]['hit_objs'][-1]['end_offset']
            total_bar_num=calculate_total_bar_num(first_note_bar_start_offset,one_bar_total_time,last_obj_offset=last_obj_offset)
            offset_list=get_offset_list(first_note_bar_start_offset,one_bar_total_time,last_obj_offset=last_obj_offset)
            bpm_end_offset=(one_bar_total_time*total_bar_num)+first_note_bar_start_offset

        #calculate total bar time and bar_w
        bar_total_time=total_bar_num*one_bar_total_time
        bar_w=total_bar_num*ONE_BAR_W

        is_need_draw_bpm=True
        last_bar_w_ratio=1
        last_bar_w=ONE_BAR_W
        if k<len(bpm_and_obj_list)-1:#check next bpm start offset - this bpm start offset is or not < one bar total time
            if total_bar_num==1:
                if bpm_and_obj_list[k+1]['bpm_offset']-bpm_and_obj_list[k]['bpm_offset'] < one_bar_total_time and abs((bpm_and_obj_list[k+1]['bpm_offset']-bpm_and_obj_list[k]['bpm_offset'])-one_bar_total_time)>=FAULT_TOLERANCE:
                    is_need_draw_bpm=False
                    last_bar_w_ratio=(bpm_and_obj_list[k+1]['bpm_offset']-bpm_and_obj_list[k]['bpm_offset'])/one_bar_total_time
                    bar_total_time=int(last_bar_w_ratio*one_bar_total_time)
                    bar_w=int(last_bar_w_ratio*ONE_BAR_W)
                    last_bar_w=bar_w
            else:
                bar_end_offset_minus_one_bar = first_note_bar_start_offset + (total_bar_num-1)*one_bar_total_time
                if bpm_and_obj_list[k+1]['bpm_offset']- bar_end_offset_minus_one_bar < one_bar_total_time and abs((bpm_and_obj_list[k+1]['bpm_offset']-bar_end_offset_minus_one_bar)-one_bar_total_time)>=FAULT_TOLERANCE:
                    last_bar_w_ratio=(bpm_and_obj_list[k+1]['bpm_offset']-bar_end_offset_minus_one_bar)/one_bar_total_time
                    
                    bar_total_time-=one_bar_total_time
                    bar_total_time+=int(last_bar_w_ratio*one_bar_total_time)
                    
                    bar_w-=ONE_BAR_W
                    bar_w+=int(last_bar_w_ratio*ONE_BAR_W)

                    last_bar_w=int(last_bar_w_ratio*ONE_BAR_W)

        parameters_to_create_bar_num_offset_table.append({'offset_list':offset_list})
        parameters_to_assign_kiai_to_bpm.append({"bpm_start_offset":first_note_bar_start_offset,"bpm_end_offset":bpm_end_offset,"bar_total_time":bar_total_time,"bar_w":bar_w})
        parameters_to_draw_bar_line.append({"bar_w":bar_w,"bpm":bpm,"time_signature":time_signature,"total_bar_num":total_bar_num,"last_bar_w_ratio":last_bar_w_ratio,"is_need_draw_bpm":is_need_draw_bpm})
        parameters_to_draw_bar_obj.append({"bar_w":bar_w,"offset":first_note_bar_start_offset,"bar_total_time":bar_total_time})
        parameters_to_accumulate_bar_w.append({"left_bar_num":total_bar_num,"last_bar_w":last_bar_w})

        if PRINT_PROCESS:
            print(f'{k+1}/{len(bpm_and_obj_list)}')

        k+=1
    bar_w_sum=0
    i=0
    while i<len(parameters_to_draw_bar_line):
        bar_w_sum+=parameters_to_draw_bar_line[i]['bar_w']
        i+=1
    
    #create bar_num_offset_table.txt
    if PRINT_PROCESS:
        print('create_bar_num_offset_table_txt')
    create_bar_num_offset_table_txt(parameters_to_create_bar_num_offset_table,osu_file_name)

    #get kiai offset pair (on and off)
    if PRINT_PROCESS:
        print('to_kiai_offset_pair')
    sv_kiai_offset_pair_list=to_kiai_offset_pair(kiai_sv_list)

    #assign kiai to bpm
    if PRINT_PROCESS:
        print('assign_kiai_to_bpm')
    #bpm_and_kiai_offset_list: [{"bpm_start_offset":,"bpm_end_offset":,"bar_total_time":,"bar_w":,"kiais":[{"start_offset":,"end_offset":,}]}]
    bpm_and_kiai_offset_list=assign_kiai_to_bpm(parameters_to_assign_kiai_to_bpm,sv_kiai_offset_pair_list)

    bar_img = np.full((BAR_H, bar_w_sum, 3), BACKGROUND_COLOR , np.uint8)

    #draw kiai
    if PRINT_PROCESS:
        print('draw_kiai')
    bar_img = draw_kiai(bar_img,bpm_and_kiai_offset_list)

    #draw barline
    if PRINT_PROCESS:
        print('draw_barline')
    bar_img = draw_barline(bar_img,bar_w_sum,parameters_to_draw_bar_line)
    
    #draw obj
    if PRINT_PROCESS:
        print('draw_obj')
    bar_img = draw_obj(bar_img,bar_w_sum,bpm_and_obj_list,parameters_to_draw_bar_obj)
    
    #accumulate every bar_w for cut
    if PRINT_PROCESS:
        print('to_accumulate_one_bar_w_list')
    accumulate_one_bar_w_list=to_accumulate_one_bar_w_list(parameters_to_accumulate_bar_w)
    
    #cut and merge
    if PRINT_PROCESS:
        print('cut_and_merge')
    merge_bar_img=cut_and_merge(bar_img,accumulate_one_bar_w_list)
    
    #title generate and merge

    #read title.txt
    if PRINT_PROCESS:
        print('read_title_txt')
    name,artist,mapper_name,difficulty_name=read_title_txt()
    
    #create img
    if PRINT_PROCESS:
        print('create_title_img')
    title_img = create_title_img(name,artist,difficulty_name,mapper_name)
    
    #merge
    if PRINT_PROCESS:
        print('merge')
    img = cv2.vconcat([title_img,merge_bar_img])

    #save
    if PRINT_PROCESS:
        print('save')
    cv2.imwrite(f'./output folder/{osu_file_name[:-4]}.png',img)

FILE_FOLDER_PATH='./osu file input folder/'
TEST_MODE=0
if TEST_MODE==1:
    main_func('auto',FILE_FOLDER_PATH,'iyowa - Issen Kounen (Cut Ver.) (_gt) [A Thousand Bars].osu')
elif TEST_MODE==2:
    osu_files=os.listdir(FILE_FOLDER_PATH)
    i=0
    while i<len(osu_files):
        main_func('auto',FILE_FOLDER_PATH,osu_files[i])
        i+=1
