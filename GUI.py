from OTBIC_app import main_func
from OTBIC_app import ONE_BAR_W, BAR_H, BAR_NUM_IN_ONE_CUT, CUT_AND_MERGE_MODE_S, CUT_AND_MERGE_MODE, SMALL_OBJ_RADIUS, BIG_OBJ_RADIUS, TITLE_TEXT_SCALE, TITLE_TEXT_WIDTH_MARGIN
from OTBIC_app import NOTE_COLOR_BLUE, NOTE_COLOR_RED, SLIDER_COLOR, SPINNER_COLOR, BACKGROUND_COLOR, OBJ_BORDER_COLOR, KIAI_COLOR, FIRST_BARLINE_COLOR, BARLINE_COLOR, SMALL_BARLINE_COLOR, BAR_NUM_COLOR, TEXT_COLOR, BOTTOM_LINE_COLOR
import os
from PyQt5 import QtGui, QtWidgets, QtCore
import sys
from os import startfile
import cv2
import numpy as np
#change able app varible
BAR_TEXT_Y=16
FAULT_TOLERANCE=1#fit rightmost note that x + BAR.bar_line_offset will exceed BAR_W
BAR_LINE_OFFSET_Y=10#for small bar line and notes layout
BAR_TEXT_SCALE=0.55
TITLE_TEXT_SCALE=1
TITLE_TEXT_WIDTH_MARGIN=50

#global variable
WIDTH=1280
HEIGHT=720
BUTTON_TEXT_1_SPACE=' '

OBJ_OFFSET=80
START_X=SMALL_OBJ_RADIUS
DRAW_BAR_H=BAR_H
DRAW_BAR_W=OBJ_OFFSET*12
SMALL_BARLINE_TOP_Y=int(DRAW_BAR_H/3)
Y=SMALL_BARLINE_TOP_Y+int((DRAW_BAR_H-SMALL_BARLINE_TOP_Y)/2)
##############################################################
COLOR_RED_NOTE_R=-1
COLOR_RED_NOTE_G=-1
COLOR_RED_NOTE_B=-1

COLOR_BLUE_NOTE_R=-1
COLOR_BLUE_NOTE_G=-1
COLOR_BLUE_NOTE_B=-1

COLOR_SLIDER_R=-1
COLOR_SLIDER_G=-1
COLOR_SLIDER_B=-1

COLOR_SPINNER_R=-1
COLOR_SPINNER_G=-1
COLOR_SPINNER_B=-1

COLOR_BACKGROUND_R=-1
COLOR_BACKGROUND_G=-1
COLOR_BACKGROUND_B=-1

COLOR_KIAI_R=-1
COLOR_KIAI_G=-1
COLOR_KIAI_B=-1

COLOR_BORDER_R=-1
COLOR_BORDER_G=-1
COLOR_BORDER_B=-1

COLOR_FIRST_BARLINE_R=-1
COLOR_FIRST_BARLINE_G=-1
COLOR_FIRST_BARLINE_B=-1

COLOR_BARLINE_R=-1
COLOR_BARLINE_G=-1
COLOR_BARLINE_B=-1

COLOR_SMALL_BARLINE_R=-1
COLOR_SMALL_BARLINE_G=-1
COLOR_SMALL_BARLINE_B=-1

COLOR_BOTTOM_LINE_R=-1
COLOR_BOTTOM_LINE_G=-1
COLOR_BOTTOM_LINE_B=-1

COLOR_BAR_NUM_R=-1
COLOR_BAR_NUM_G=-1
COLOR_BAR_NUM_B=-1

COLOR_TEXT_R=-1
COLOR_TEXT_G=-1
COLOR_TEXT_B=-1
##############################################################
#main widget
class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        #title
        self.setWindowTitle('Osu Taiko Beatmap Image Converter')

        #icon
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        
        #set window size
        self.width_=WIDTH
        self.height_=HEIGHT
        self.resize(self.width_, self.height_)
        self.setFixedSize(self.width(), self.height())
        
        self.osu_file_path=""
        self.osu_file_folder_path=""
        self.osu_file_name=""

        #id == index+1
        self.timing_point_list=[]#{"id":id,"id_label":bpm_id_label,"offset":-1,"offset_line_edit":bpm_start_offset_line_edit,"bpm":-1,"bpm_line_edit":bpm_bpm_line_edit,"time_signature":-1,"time_signature_line_edit":bpm_time_signature_line_edit,"widget":bpm_widget}
        self.tp_list=[]#{"offset":,"bpm":,"time_signature":}
        self.setting_parameters={"one_bar_w":ONE_BAR_W,"one_bar_h":DRAW_BAR_H,"bar_num_in_one_cut":BAR_NUM_IN_ONE_CUT,"cut_and_merge_mode":CUT_AND_MERGE_MODE}
        self.color_setting_parameters={}

        #color
        self.read_color('init')
        self.img=""

        #style sheet
        self.style()
        
        self.main_box = QtWidgets.QWidget(self)
        self.main_box.setGeometry(0,0,self.width_,self.height_)
        self.main_box.setStyleSheet(self.style_box)
        self.main_layout = QtWidgets.QFormLayout(self.main_box)

        self.ui_setting=QtWidgets.QWidget()
        #self.ui_color_setting=Color_setting_window()
        self.ui_color_setting=QtWidgets.QWidget()


        #first ui
        self.start_ui()
    
    def style(self):
        #2a2226
        #54454c
        self.style_box = '''
            background:#2a2226;
            border:1px solid #000;
            font-size:18px;
            color:#ffffff;
            font-family:Verdana;
            border-color:#2a2226;
            margin:1px
        '''
        #382e32
        #ac396d
        self.style_btn = '''
            QPushButton{
                background:#54454c;
                border-color:#54454c;
                font-size:18px;
                color:#ffffff;
                border:1px solid #000;
                border-radius:10px;
                padding:5px;
            }
            QPushButton:pressed{
                background:#ac396d;
                border-color:#ac396d;
            }
            QPushButton:disabled{
                background:#0d0d0d;
                border-color:#0d0d0d;
                color:#1f1f1f;
            }
        '''
        self.style_text_edit = '''
            background:#1f1f1f;
            border:1px solid #000;
            font-size:18px;
            color:#ed2553;
            font-family:Verdana;
            border-color:#1f1f1f;
            margin:1px
        '''
        self.style_line_edit = '''
            background:#000000;
            border:1px solid #000;
            font-size:18px;
            color:#ffffff;
            font-family:Verdana;
            border-color:#ffffff;
            margin:1px
        '''
        
    def start_ui(self):
        self.setWindowTitle('Osu Taiko Beatmap Image Converter')
        while self.main_layout.rowCount()>0:
            self.main_layout.removeRow(0)
        #
        self.osu_file_name_label = ScrollLabel(self)
        self.osu_file_name_label.setStyleSheet(self.style_box)
        self.osu_file_name_label.setText(self.osu_file_path)
        
        #
        chosse_osu_file_btn_line_widget=QtWidgets.QWidget()
        chosse_osu_file_btn_line_layout=QtWidgets.QHBoxLayout(chosse_osu_file_btn_line_widget)

        self.chosse_osu_file_btn=QtWidgets.QPushButton(self)
        self.chosse_osu_file_btn.setText('Choose .osu file')
        self.chosse_osu_file_btn.setStyleSheet(self.style_btn)
        self.chosse_osu_file_btn.clicked.connect(self.open_osu_file)

        chosse_osu_file_btn_line_layout.addWidget(self.chosse_osu_file_btn)
        #
        auto_manual_btn_line_widget=QtWidgets.QWidget()
        auto_manual_btn_line_layout=QtWidgets.QHBoxLayout(auto_manual_btn_line_widget)

        self.automatic_btn=QtWidgets.QPushButton(self)
        self.automatic_btn.setText('Automatic')
        self.automatic_btn.setStyleSheet(self.style_btn)
        self.automatic_btn.clicked.connect(self.change_to_automatic)
        if len(self.osu_file_path)==0:
            self.automatic_btn.setEnabled(False)
        
        self.manual_btn=QtWidgets.QPushButton(self)
        self.manual_btn.setText('Manual')
        self.manual_btn.setStyleSheet(self.style_btn)
        self.manual_btn.clicked.connect(self.change_to_manual)
        if len(self.osu_file_path)==0:
            self.manual_btn.setEnabled(False)
        
        auto_manual_btn_line_layout.addWidget(self.automatic_btn,stretch=1)
        auto_manual_btn_line_layout.addWidget(self.manual_btn,stretch=1)
        #

        #
        self.main_layout.addRow(self.osu_file_name_label)
        self.main_layout.addRow(chosse_osu_file_btn_line_widget)
        self.main_layout.addRow(auto_manual_btn_line_widget)

    def change_to_automatic(self):
        self.setWindowTitle('Osu Taiko Beatmap Image Converter: Automatic mode')
        while self.main_layout.rowCount()>0:
            self.main_layout.removeRow(0)

        #
        self.osu_file_is_label = ScrollLabel(self)
        self.osu_file_is_label.setStyleSheet(self.style_box)
        self.osu_file_is_label.setText("Your .osu file is:")

        self.main_layout.addRow(self.osu_file_is_label)
        #
        self.osu_file_name_label = ScrollLabel(self)
        self.osu_file_name_label.setStyleSheet(self.style_box)
        self.osu_file_name_label.setText(self.osu_file_path)
        
        self.main_layout.addRow(self.osu_file_name_label)
        #
        output_setting_btn_line_widget=QtWidgets.QWidget()
        output_setting_btn_line_layout=QtWidgets.QHBoxLayout(output_setting_btn_line_widget)

        self.output_setting_btn=QtWidgets.QPushButton(self)
        self.output_setting_btn.setText('Output Setting')
        self.output_setting_btn.setStyleSheet(self.style_btn)
        self.output_setting_btn.clicked.connect(self.change_setting_window)

        output_setting_btn_line_layout.addWidget(self.output_setting_btn,stretch=1)
    
        self.main_layout.addRow(output_setting_btn_line_widget)
        #
        convert_btn_line_widget=QtWidgets.QWidget()
        convert_btn_line_layout=QtWidgets.QHBoxLayout(convert_btn_line_widget)

        self.convert_btn=QtWidgets.QPushButton(self)
        self.convert_btn.setText('Convert')
        self.convert_btn.setStyleSheet(self.style_btn)
        self.convert_btn.clicked.connect(lambda:self.start_convert('auto'))

        convert_btn_line_layout.addWidget(self.convert_btn,stretch=1)

        self.main_layout.addRow(convert_btn_line_widget)
        #
        back_to_menu_btn_line_widget=QtWidgets.QWidget()
        back_to_menu_btn_line_layout=QtWidgets.QHBoxLayout(back_to_menu_btn_line_widget)

        self.back_to_menu_btn=QtWidgets.QPushButton(self)
        self.back_to_menu_btn.setText('Back to menu')
        self.back_to_menu_btn.setStyleSheet(self.style_btn)
        self.back_to_menu_btn.clicked.connect(self.start_ui)

        back_to_menu_btn_line_layout.addWidget(self.back_to_menu_btn,stretch=1)

        self.main_layout.addRow(back_to_menu_btn_line_widget)

    def change_to_manual(self):
        self.setWindowTitle('Osu Taiko Beatmap Image Converter: Manual mode')
        self.timing_point_list=[]

        while self.main_layout.rowCount()>0:
            self.main_layout.removeRow(0)

        #
        self.osu_file_is_label = QtWidgets.QLabel(self)
        self.osu_file_is_label.setStyleSheet(self.style_box)
        self.osu_file_is_label.setText("Your .osu file is:")

        self.main_layout.addRow(self.osu_file_is_label)
        #
        self.osu_file_name_label = ScrollLabel(self)
        self.osu_file_name_label.setStyleSheet(self.style_box)
        self.osu_file_name_label.setText(self.osu_file_path)
        
        self.main_layout.addRow(self.osu_file_name_label)
        #
        self.scroll_widget = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QFormLayout(self.scroll_widget)

        self.scroll_area=QtWidgets.QScrollArea(self)

        self.main_layout.addRow(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        #
        add_bpm_btn_line_widget=QtWidgets.QWidget()
        add_bpm_btn_line_layout=QtWidgets.QHBoxLayout(add_bpm_btn_line_widget)

        self.add_bpm_btn=QtWidgets.QPushButton(self)
        self.add_bpm_btn.setText('Add new bpm timing point')
        self.add_bpm_btn.setStyleSheet(self.style_btn)
        self.add_bpm_btn.clicked.connect(self.add_bpm)

        add_bpm_btn_line_layout.addWidget(self.add_bpm_btn,stretch=1)

        self.main_layout.addRow(add_bpm_btn_line_widget)
        #
        delete_line_widget=QtWidgets.QWidget()
        delete_line_layout=QtWidgets.QHBoxLayout(delete_line_widget)

        self.delete_bpm_btn=QtWidgets.QPushButton(self)
        self.delete_bpm_btn.setText('Delete bpm timing point')
        self.delete_bpm_btn.setStyleSheet(self.style_btn)
        self.delete_bpm_btn.clicked.connect(self.delete_bpm)

        self.current_del_timing_point_id_box=QtWidgets.QComboBox(self)
        self.current_del_timing_point_id_box.setStyleSheet(self.style_line_edit)

        delete_line_layout.addWidget(self.delete_bpm_btn,stretch=1)
        delete_line_layout.addWidget(self.current_del_timing_point_id_box,stretch=1)

        self.main_layout.addRow(delete_line_widget)
        #
        output_setting_btn_line_widget=QtWidgets.QWidget()
        output_setting_btn_line_layout=QtWidgets.QHBoxLayout(output_setting_btn_line_widget)

        self.output_setting_btn=QtWidgets.QPushButton(self)
        self.output_setting_btn.setText('Output Setting')
        self.output_setting_btn.setStyleSheet(self.style_btn)
        self.output_setting_btn.clicked.connect(self.change_setting_window)

        output_setting_btn_line_layout.addWidget(self.output_setting_btn,stretch=1)
    
        self.main_layout.addRow(output_setting_btn_line_widget)
        #
        convert_btn_line_widget=QtWidgets.QWidget()
        convert_btn_line_layout=QtWidgets.QHBoxLayout(convert_btn_line_widget)

        self.convert_btn=QtWidgets.QPushButton(self)
        self.convert_btn.setText('Convert')
        self.convert_btn.setStyleSheet(self.style_btn)
        self.convert_btn.clicked.connect(lambda:self.start_convert('manual'))

        convert_btn_line_layout.addWidget(self.convert_btn,stretch=1)

        self.main_layout.addRow(convert_btn_line_widget)
        #
        back_to_menu_btn_line_widget=QtWidgets.QWidget()
        back_to_menu_btn_line_layout=QtWidgets.QHBoxLayout(back_to_menu_btn_line_widget)

        self.back_to_menu_btn=QtWidgets.QPushButton(self)
        self.back_to_menu_btn.setText('Back to menu')
        self.back_to_menu_btn.setStyleSheet(self.style_btn)
        self.back_to_menu_btn.clicked.connect(self.start_ui)

        back_to_menu_btn_line_layout.addWidget(self.back_to_menu_btn,stretch=1)

        self.main_layout.addRow(back_to_menu_btn_line_widget)

    def delete_bpm(self):
        tpid=self.current_del_timing_point_id_box.currentText()
        if tpid!="":
            #delete
            self.scroll_layout.removeRow(int(tpid)-1)
            del self.timing_point_list[int(tpid)-1]

            #update timing_point_list and current_del_timing_point_id_box
            self.current_del_timing_point_id_box.clear()
            i=0
            while i<len(self.timing_point_list):
                self.timing_point_list[i]['id']=str(i+1)
                self.timing_point_list[i]['id_label'].setText(str(i+1))
                self.current_del_timing_point_id_box.addItem(str(i+1))
                i+=1

    def add_bpm(self):
        bpm_widget=QtWidgets.QWidget()
        bpm_layout=QtWidgets.QHBoxLayout(bpm_widget)

        bpm_id_name_label=QtWidgets.QLabel(self)
        bpm_id_name_label.setText('Timing point:')
        bpm_id_label=QtWidgets.QLabel(self)
        

        bpm_start_offset_label=QtWidgets.QLabel(self)
        bpm_start_offset_label.setText('Start offset:')
        bpm_start_offset_line_edit=QtWidgets.QLineEdit(self)
        bpm_start_offset_line_edit.setStyleSheet(self.style_line_edit)

        bpm_bpm_label=QtWidgets.QLabel(self)
        bpm_bpm_label.setText('Bpm:')
        bpm_bpm_line_edit=QtWidgets.QLineEdit(self)
        bpm_bpm_line_edit.setStyleSheet(self.style_line_edit)

        bpm_time_signature_label=QtWidgets.QLabel(self)
        bpm_time_signature_label.setText('Time signature:')
        bpm_time_signature_line_edit=QtWidgets.QLineEdit(self)
        bpm_time_signature_line_edit.setStyleSheet(self.style_line_edit)

        bpm_layout.addWidget(bpm_id_name_label,stretch=1)
        bpm_layout.addWidget(bpm_id_label,stretch=1)
        bpm_layout.addWidget(bpm_start_offset_label,stretch=1)
        bpm_layout.addWidget(bpm_start_offset_line_edit,stretch=1)
        bpm_layout.addWidget(bpm_bpm_label,stretch=1)
        bpm_layout.addWidget(bpm_bpm_line_edit,stretch=1)
        bpm_layout.addWidget(bpm_time_signature_label,stretch=1)
        bpm_layout.addWidget(bpm_time_signature_line_edit,stretch=1)

        self.scroll_layout.addRow(bpm_widget)
        
        id=str(len(self.timing_point_list)+1)
        self.timing_point_list.append({"id":id,"id_label":bpm_id_label,"offset":-1,"offset_line_edit":bpm_start_offset_line_edit,"bpm":-1,"bpm_line_edit":bpm_bpm_line_edit,"time_signature":-1,"time_signature_line_edit":bpm_time_signature_line_edit,"widget":bpm_widget})#{"id":,"offset":,"bpm":,"time_signature":"widget":widget}
        bpm_id_label.setText(id)
        self.current_del_timing_point_id_box.addItem(id)

    def check_timing_point_list_is_valid(self):
        try:
            i=0
            while i<len(self.timing_point_list):
                if len(self.timing_point_list[i]['offset_line_edit'].text())==0 or int(self.timing_point_list[i]['offset_line_edit'].text()) <0:
                    return False
                elif len(self.timing_point_list[i]['bpm_line_edit'].text())==0 or int(self.timing_point_list[i]['bpm_line_edit'].text()) <0:
                    return False
                elif len(self.timing_point_list[i]['time_signature_line_edit'].text())==0 or int(self.timing_point_list[i]['time_signature_line_edit'].text()) <0:
                    return False
                i+=1
            return True
        except:
            return False
        
    def open_osu_file(self):
        osu_file_path , filterType = QtWidgets.QFileDialog.getOpenFileName(filter='OSU (*.osu)')
        if osu_file_path !="":
            self.osu_file_path=osu_file_path
            s=osu_file_path.split('/')
            self.osu_file_folder_path=""
            i=0
            while i<len(s)-1:
                self.osu_file_folder_path+=s[i]
                self.osu_file_folder_path+='/'
                i+=1
            self.osu_file_name=s[i]

            self.osu_file_name_label.setText(osu_file_path)
            self.automatic_btn.setEnabled(True)
            self.manual_btn.setEnabled(True)

    def get_tp_list(self):
        self.tp_list=[]
        i=0
        while i<len(self.timing_point_list):
            self.tp_list.append({'offset':int(self.timing_point_list[i]['offset_line_edit'].text()),'bpm':int(self.timing_point_list[i]['bpm_line_edit'].text()),'time_signature':int(self.timing_point_list[i]['time_signature_line_edit'].text())})
            i+=1

    def sort_tp_list_by_offset(self):
        self.tp_list = sorted(self.tp_list,key = lambda e:e.__getitem__('offset'))

    def start_convert(self,mode):
        self.get_color_setting_parameters()
        if mode == "auto":
            main_func('auto',self.osu_file_folder_path,self.osu_file_name,setting_parameters=self.setting_parameters,color_setting_parameters=self.color_setting_parameters)
        elif mode == "manual" and self.check_timing_point_list_is_valid():
            self.get_tp_list()
            self.sort_tp_list_by_offset()
            main_func('manual',self.osu_file_folder_path,self.osu_file_name,tp_list=self.tp_list,setting_parameters=self.setting_parameters,color_setting_parameters=self.color_setting_parameters)

    def change_setting_window(self):
        self.ui_setting=QtWidgets.QWidget()
        self.ui_setting.setWindowTitle('Osu Taiko Beatmap Image Converter: Setting')
        self.ui_setting.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.ui_setting.setStyleSheet(self.style_box)
        w=960
        h=720
        self.ui_setting.setGeometry(self.x()+90,self.y()+90,w,h)
        self.ui_setting.setFixedSize(self.ui_setting.width(), self.ui_setting.height())
        
        self.setting_layout = QtWidgets.QFormLayout(self.ui_setting)
        #
        first_line_widget=QtWidgets.QWidget()
        first_line_layout=QtWidgets.QHBoxLayout(first_line_widget)

        self.setting_one_bar_w_label=QtWidgets.QLabel(self.ui_setting)
        self.setting_one_bar_w_label.setText('One bar width(pix):')

        self.setting_one_bar_w_line_edit=QtWidgets.QLineEdit(self.ui_setting)
        self.setting_one_bar_w_line_edit.setStyleSheet(self.style_line_edit)
        self.setting_one_bar_w_line_edit.setText(f'{self.setting_parameters["one_bar_w"]}')
        
        self.setting_one_bar_h_label=QtWidgets.QLabel(self.ui_setting)
        self.setting_one_bar_h_label.setText('One bar height(pix):')

        self.setting_one_bar_h_line_edit=QtWidgets.QLineEdit(self.ui_setting)
        self.setting_one_bar_h_line_edit.setStyleSheet(self.style_line_edit)
        self.setting_one_bar_h_line_edit.setText(f'{self.setting_parameters["one_bar_h"]}')

        first_line_layout.addWidget(self.setting_one_bar_w_label,stretch=1)
        first_line_layout.addWidget(self.setting_one_bar_w_line_edit,stretch=1)
        first_line_layout.addWidget(self.setting_one_bar_h_label,stretch=1)
        first_line_layout.addWidget(self.setting_one_bar_h_line_edit,stretch=1)

        #
        second_line_widget=QtWidgets.QWidget()
        second_line_layout=QtWidgets.QHBoxLayout(second_line_widget)

        self.setting_bar_num_in_one_cut_label=QtWidgets.QLabel(self.ui_setting)
        self.setting_bar_num_in_one_cut_label.setText('One line bar num:')

        self.setting_bar_num_in_one_cut_line_edit=QtWidgets.QLineEdit(self.ui_setting)
        self.setting_bar_num_in_one_cut_line_edit.setStyleSheet(self.style_line_edit)
        self.setting_bar_num_in_one_cut_line_edit.setText(f'{self.setting_parameters["bar_num_in_one_cut"]}')
        
        self.setting_merge_mode_label=QtWidgets.QLabel(self.ui_setting)
        self.setting_merge_mode_label.setText('Merge mode:')

        self.setting_merge_mode_box=QtWidgets.QComboBox(self)
        self.setting_merge_mode_box.setStyleSheet(self.style_line_edit)
        self.setting_merge_mode_box.addItems(CUT_AND_MERGE_MODE_S)
        self.setting_merge_mode_box.setCurrentText(self.setting_parameters['cut_and_merge_mode'])

        second_line_layout.addWidget(self.setting_bar_num_in_one_cut_label,stretch=1)
        second_line_layout.addWidget(self.setting_bar_num_in_one_cut_line_edit,stretch=1)
        second_line_layout.addWidget(self.setting_merge_mode_label,stretch=1)
        second_line_layout.addWidget(self.setting_merge_mode_box,stretch=1)
        #
        third_line_widget=QtWidgets.QWidget()
        third_line_layout=QtWidgets.QHBoxLayout(third_line_widget)

        self.setting_color_setting_btn=QtWidgets.QPushButton(self.ui_setting)
        self.setting_color_setting_btn.setText('Color setting')
        self.setting_color_setting_btn.setStyleSheet(self.style_btn)
        self.setting_color_setting_btn.clicked.connect(self.change_color_setting_window)

        third_line_layout.addWidget(self.setting_color_setting_btn)
        #
        fourth_line_widget=QtWidgets.QWidget()
        fourth_line_layout=QtWidgets.QHBoxLayout(fourth_line_widget)

        self.setting_cancel_btn=QtWidgets.QPushButton(self.ui_setting)
        self.setting_cancel_btn.setText('Cancel')
        self.setting_cancel_btn.setStyleSheet(self.style_btn)
        self.setting_cancel_btn.clicked.connect(lambda:self.destroy_and_update_setting_window('cancel'))

        self.setting_change_btn=QtWidgets.QPushButton(self.ui_setting)
        self.setting_change_btn.setText('Change')
        self.setting_change_btn.setStyleSheet(self.style_btn)
        self.setting_change_btn.clicked.connect(lambda:self.destroy_and_update_setting_window('change'))

        fourth_line_layout.addWidget(self.setting_cancel_btn,stretch=1)
        fourth_line_layout.addWidget(self.setting_change_btn,stretch=1)
        #
        self.setting_layout.addRow(first_line_widget)
        self.setting_layout.addRow(second_line_widget)
        self.setting_layout.addRow(third_line_widget)
        self.setting_layout.addRow(fourth_line_widget)
        self.ui_setting.show()

    def destroy_and_update_setting_window(self,type_):
        try:
            if type_=='change' and self.setting_one_bar_w_line_edit.text()!="" and int(self.setting_one_bar_w_line_edit.text())>0 and self.setting_one_bar_h_line_edit.text()!="" and int(self.setting_one_bar_h_line_edit.text())>0 and self.setting_bar_num_in_one_cut_line_edit.text()!="" and int(self.setting_bar_num_in_one_cut_line_edit.text())>0:
                self.setting_parameters['one_bar_w']=int(self.setting_one_bar_w_line_edit.text())
                self.setting_parameters['one_bar_h']=int(self.setting_one_bar_h_line_edit.text())
                self.setting_parameters['bar_num_in_one_cut']=int(self.setting_bar_num_in_one_cut_line_edit.text())
                self.setting_parameters['cut_and_merge_mode']=self.setting_merge_mode_box.currentText()
                
            elif type_=='cancel':
                pass
            self.ui_setting.close() 
        except:
            pass    

    def change_color_setting_window(self):
        self.ui_color_setting=QtWidgets.QWidget()
        #self.ui_color_setting=Color_setting_window()
        self.ui_color_setting.setWindowTitle('Osu Taiko Beatmap Image Converter: Color setting')
        self.ui_color_setting.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.ui_color_setting.setStyleSheet(self.style_box)
        w=DRAW_BAR_W
        h=720
        self.ui_color_setting.setGeometry(self.x()+180,self.y()+180,w,h)
        self.ui_color_setting.setFixedSize(self.ui_color_setting.width(), self.ui_color_setting.height())
        
        self.color_setting_layout = QtWidgets.QFormLayout(self.ui_color_setting)
        #
        self.bar_img_label = QtWidgets.QLabel(self)
        self.draw_bar()
        self.update_bar_img_label()

        self.color_setting_layout.addRow(self.bar_img_label)
        #
        self.color_setting_scroll_widget = QtWidgets.QWidget()
        self.color_setting_scroll_layout = QtWidgets.QFormLayout(self.color_setting_scroll_widget)

        self.color_setting_scroll_area=QtWidgets.QScrollArea(self)

        self.color_setting_layout.addRow(self.color_setting_scroll_area)
        self.color_setting_scroll_area.setWidgetResizable(True)
        self.color_setting_scroll_area.setWidget(self.color_setting_scroll_widget)
        #0
        zero_line_widget=QtWidgets.QWidget()
        zero_line_layout=QtWidgets.QHBoxLayout(zero_line_widget)

        self.color_setting_obj_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_obj_name_label.setText('Object')

        self.color_setting_r_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_r_name_label.setText('R')

        self.color_setting_g_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_g_name_label.setText('G')

        self.color_setting_b_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_b_name_label.setText('B')

        self.color_setting_to_default_color_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_to_default_color_btn.setText('Default')
        self.color_setting_to_default_color_btn.setStyleSheet(self.style_btn)
        self.color_setting_to_default_color_btn.clicked.connect(lambda:self.to_default_color(''))

        zero_line_layout.addWidget(self.color_setting_obj_name_label,stretch=1)
        zero_line_layout.addWidget(self.color_setting_r_name_label,stretch=1)
        zero_line_layout.addWidget(self.color_setting_g_name_label,stretch=1)
        zero_line_layout.addWidget(self.color_setting_b_name_label,stretch=1)
        zero_line_layout.addWidget(self.color_setting_to_default_color_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(zero_line_widget)
        #1
        first_line_widget=QtWidgets.QWidget()
        first_line_layout=QtWidgets.QHBoxLayout(first_line_widget)

        self.color_setting_red_note_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_red_note_name_label.setText('Red note:')

        self.color_setting_red_note_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_red_note_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_red_note_r_line_edit.setText(f'{COLOR_RED_NOTE_R}')

        self.color_setting_red_note_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_red_note_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_red_note_g_line_edit.setText(f'{COLOR_RED_NOTE_G}')

        self.color_setting_red_note_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_red_note_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_red_note_b_line_edit.setText(f'{COLOR_RED_NOTE_B}')

        self.color_setting_red_note_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_red_note_change_btn.setText('Change')
        self.color_setting_red_note_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_red_note_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('red_note'))

        first_line_layout.addWidget(self.color_setting_red_note_name_label,stretch=1)
        first_line_layout.addWidget(self.color_setting_red_note_r_line_edit,stretch=1)
        first_line_layout.addWidget(self.color_setting_red_note_g_line_edit,stretch=1)
        first_line_layout.addWidget(self.color_setting_red_note_b_line_edit,stretch=1)
        first_line_layout.addWidget(self.color_setting_red_note_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(first_line_widget)
        #2
        second_line_widget=QtWidgets.QWidget()
        second_line_layout=QtWidgets.QHBoxLayout(second_line_widget)

        self.color_setting_blue_note_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_blue_note_name_label.setText('Blue note:')

        self.color_setting_blue_note_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_blue_note_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_blue_note_r_line_edit.setText(f'{COLOR_BLUE_NOTE_R}')

        self.color_setting_blue_note_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_blue_note_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_blue_note_g_line_edit.setText(f'{COLOR_BLUE_NOTE_G}')

        self.color_setting_blue_note_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_blue_note_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_blue_note_b_line_edit.setText(f'{COLOR_BLUE_NOTE_B}')

        self.color_setting_blue_note_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_blue_note_change_btn.setText('Change')
        self.color_setting_blue_note_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_blue_note_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('blue_note'))

        second_line_layout.addWidget(self.color_setting_blue_note_name_label,stretch=1)
        second_line_layout.addWidget(self.color_setting_blue_note_r_line_edit,stretch=1)
        second_line_layout.addWidget(self.color_setting_blue_note_g_line_edit,stretch=1)
        second_line_layout.addWidget(self.color_setting_blue_note_b_line_edit,stretch=1)
        second_line_layout.addWidget(self.color_setting_blue_note_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(second_line_widget)
        #3
        third_line_widget=QtWidgets.QWidget()
        third_line_layout=QtWidgets.QHBoxLayout(third_line_widget)

        self.color_setting_slider_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_slider_name_label.setText('Slider:')

        self.color_setting_slider_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_slider_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_slider_r_line_edit.setText(f'{COLOR_SLIDER_R}')

        self.color_setting_slider_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_slider_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_slider_g_line_edit.setText(f'{COLOR_SLIDER_G}')

        self.color_setting_slider_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_slider_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_slider_b_line_edit.setText(f'{COLOR_SLIDER_B}')

        self.color_setting_slider_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_slider_change_btn.setText('Change')
        self.color_setting_slider_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_slider_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('slider'))

        third_line_layout.addWidget(self.color_setting_slider_name_label,stretch=1)
        third_line_layout.addWidget(self.color_setting_slider_r_line_edit,stretch=1)
        third_line_layout.addWidget(self.color_setting_slider_g_line_edit,stretch=1)
        third_line_layout.addWidget(self.color_setting_slider_b_line_edit,stretch=1)
        third_line_layout.addWidget(self.color_setting_slider_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(third_line_widget)
        #4
        fourth_line_widget=QtWidgets.QWidget()
        fourth_line_layout=QtWidgets.QHBoxLayout(fourth_line_widget)

        self.color_setting_spinner_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_spinner_name_label.setText('Spinner:')

        self.color_setting_spinner_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_spinner_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_spinner_r_line_edit.setText(f'{COLOR_SPINNER_R}')

        self.color_setting_spinner_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_spinner_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_spinner_g_line_edit.setText(f'{COLOR_SPINNER_G}')

        self.color_setting_spinner_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_spinner_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_spinner_b_line_edit.setText(f'{COLOR_SPINNER_B}')

        self.color_setting_spinner_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_spinner_change_btn.setText('Change')
        self.color_setting_spinner_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_spinner_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('spinner'))

        fourth_line_layout.addWidget(self.color_setting_spinner_name_label,stretch=1)
        fourth_line_layout.addWidget(self.color_setting_spinner_r_line_edit,stretch=1)
        fourth_line_layout.addWidget(self.color_setting_spinner_g_line_edit,stretch=1)
        fourth_line_layout.addWidget(self.color_setting_spinner_b_line_edit,stretch=1)
        fourth_line_layout.addWidget(self.color_setting_spinner_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(fourth_line_widget)
        #5
        fifth_line_widget=QtWidgets.QWidget()
        fifth_line_layout=QtWidgets.QHBoxLayout(fifth_line_widget)

        self.color_setting_background_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_background_name_label.setText('Background:')

        self.color_setting_background_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_background_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_background_r_line_edit.setText(f'{COLOR_BACKGROUND_R}')

        self.color_setting_background_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_background_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_background_g_line_edit.setText(f'{COLOR_BACKGROUND_G}')

        self.color_setting_background_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_background_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_background_b_line_edit.setText(f'{COLOR_BACKGROUND_B}')

        self.color_setting_background_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_background_change_btn.setText('Change')
        self.color_setting_background_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_background_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('background'))

        fifth_line_layout.addWidget(self.color_setting_background_name_label,stretch=1)
        fifth_line_layout.addWidget(self.color_setting_background_r_line_edit,stretch=1)
        fifth_line_layout.addWidget(self.color_setting_background_g_line_edit,stretch=1)
        fifth_line_layout.addWidget(self.color_setting_background_b_line_edit,stretch=1)
        fifth_line_layout.addWidget(self.color_setting_background_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(fifth_line_widget)
        #6
        sixth_line_widget=QtWidgets.QWidget()
        sixth_line_layout=QtWidgets.QHBoxLayout(sixth_line_widget)

        self.color_setting_kiai_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_kiai_name_label.setText('Kiai:')

        self.color_setting_kiai_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_kiai_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_kiai_r_line_edit.setText(f'{COLOR_KIAI_R}')

        self.color_setting_kiai_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_kiai_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_kiai_g_line_edit.setText(f'{COLOR_KIAI_G}')

        self.color_setting_kiai_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_kiai_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_kiai_b_line_edit.setText(f'{COLOR_KIAI_B}')

        self.color_setting_kiai_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_kiai_change_btn.setText('Change')
        self.color_setting_kiai_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_kiai_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('kiai'))

        sixth_line_layout.addWidget(self.color_setting_kiai_name_label,stretch=1)
        sixth_line_layout.addWidget(self.color_setting_kiai_r_line_edit,stretch=1)
        sixth_line_layout.addWidget(self.color_setting_kiai_g_line_edit,stretch=1)
        sixth_line_layout.addWidget(self.color_setting_kiai_b_line_edit,stretch=1)
        sixth_line_layout.addWidget(self.color_setting_kiai_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(sixth_line_widget)
        #7
        seventh_line_widget=QtWidgets.QWidget()
        seventh_line_layout=QtWidgets.QHBoxLayout(seventh_line_widget)

        self.color_setting_border_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_border_name_label.setText('Border:')

        self.color_setting_border_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_border_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_border_r_line_edit.setText(f'{COLOR_BORDER_R}')

        self.color_setting_border_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_border_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_border_g_line_edit.setText(f'{COLOR_BORDER_G}')

        self.color_setting_border_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_border_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_border_b_line_edit.setText(f'{COLOR_BORDER_B}')

        self.color_setting_border_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_border_change_btn.setText('Change')
        self.color_setting_border_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_border_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('border'))

        seventh_line_layout.addWidget(self.color_setting_border_name_label,stretch=1)
        seventh_line_layout.addWidget(self.color_setting_border_r_line_edit,stretch=1)
        seventh_line_layout.addWidget(self.color_setting_border_g_line_edit,stretch=1)
        seventh_line_layout.addWidget(self.color_setting_border_b_line_edit,stretch=1)
        seventh_line_layout.addWidget(self.color_setting_border_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(seventh_line_widget)
        #8
        eighth_line_widget=QtWidgets.QWidget()
        eighth_line_layout=QtWidgets.QHBoxLayout(eighth_line_widget)

        self.color_setting_first_barline_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_first_barline_name_label.setText('First barline:')

        self.color_setting_first_barline_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_first_barline_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_first_barline_r_line_edit.setText(f'{COLOR_FIRST_BARLINE_R}')

        self.color_setting_first_barline_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_first_barline_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_first_barline_g_line_edit.setText(f'{COLOR_FIRST_BARLINE_G}')

        self.color_setting_first_barline_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_first_barline_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_first_barline_b_line_edit.setText(f'{COLOR_FIRST_BARLINE_B}')

        self.color_setting_first_barline_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_first_barline_change_btn.setText('Change')
        self.color_setting_first_barline_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_first_barline_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('first_barline'))

        eighth_line_layout.addWidget(self.color_setting_first_barline_name_label,stretch=1)
        eighth_line_layout.addWidget(self.color_setting_first_barline_r_line_edit,stretch=1)
        eighth_line_layout.addWidget(self.color_setting_first_barline_g_line_edit,stretch=1)
        eighth_line_layout.addWidget(self.color_setting_first_barline_b_line_edit,stretch=1)
        eighth_line_layout.addWidget(self.color_setting_first_barline_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(eighth_line_widget)
        #9
        ninth_line_widget=QtWidgets.QWidget()
        ninth_line_layout=QtWidgets.QHBoxLayout(ninth_line_widget)

        self.color_setting_barline_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_barline_name_label.setText('Barline:')

        self.color_setting_barline_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_barline_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_barline_r_line_edit.setText(f'{COLOR_BARLINE_R}')

        self.color_setting_barline_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_barline_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_barline_g_line_edit.setText(f'{COLOR_BARLINE_G}')

        self.color_setting_barline_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_barline_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_barline_b_line_edit.setText(f'{COLOR_BARLINE_B}')

        self.color_setting_barline_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_barline_change_btn.setText('Change')
        self.color_setting_barline_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_barline_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('barline'))

        ninth_line_layout.addWidget(self.color_setting_barline_name_label,stretch=1)
        ninth_line_layout.addWidget(self.color_setting_barline_r_line_edit,stretch=1)
        ninth_line_layout.addWidget(self.color_setting_barline_g_line_edit,stretch=1)
        ninth_line_layout.addWidget(self.color_setting_barline_b_line_edit,stretch=1)
        ninth_line_layout.addWidget(self.color_setting_barline_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(ninth_line_widget)
        #10
        tenth_line_widget=QtWidgets.QWidget()
        tenth_line_layout=QtWidgets.QHBoxLayout(tenth_line_widget)

        self.color_setting_small_barline_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_small_barline_name_label.setText('Small barline:')

        self.color_setting_small_barline_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_small_barline_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_small_barline_r_line_edit.setText(f'{COLOR_SMALL_BARLINE_R}')

        self.color_setting_small_barline_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_small_barline_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_small_barline_g_line_edit.setText(f'{COLOR_SMALL_BARLINE_G}')

        self.color_setting_small_barline_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_small_barline_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_small_barline_b_line_edit.setText(f'{COLOR_SMALL_BARLINE_B}')

        self.color_setting_small_barline_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_small_barline_change_btn.setText('Change')
        self.color_setting_small_barline_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_small_barline_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('small_barline'))

        tenth_line_layout.addWidget(self.color_setting_small_barline_name_label,stretch=1)
        tenth_line_layout.addWidget(self.color_setting_small_barline_r_line_edit,stretch=1)
        tenth_line_layout.addWidget(self.color_setting_small_barline_g_line_edit,stretch=1)
        tenth_line_layout.addWidget(self.color_setting_small_barline_b_line_edit,stretch=1)
        tenth_line_layout.addWidget(self.color_setting_small_barline_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(tenth_line_widget)
        #11
        eleventh_line_widget=QtWidgets.QWidget()
        eleventh_line_layout=QtWidgets.QHBoxLayout(eleventh_line_widget)

        self.color_setting_bottom_line_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_bottom_line_name_label.setText('Bottom line:')

        self.color_setting_bottom_line_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_bottom_line_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_bottom_line_r_line_edit.setText(f'{COLOR_BOTTOM_LINE_R}')

        self.color_setting_bottom_line_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_bottom_line_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_bottom_line_g_line_edit.setText(f'{COLOR_BOTTOM_LINE_G}')

        self.color_setting_bottom_line_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_bottom_line_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_bottom_line_b_line_edit.setText(f'{COLOR_BOTTOM_LINE_B}')

        self.color_setting_bottom_line_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_bottom_line_change_btn.setText('Change')
        self.color_setting_bottom_line_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_bottom_line_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('bottom_line'))

        eleventh_line_layout.addWidget(self.color_setting_bottom_line_name_label,stretch=1)
        eleventh_line_layout.addWidget(self.color_setting_bottom_line_r_line_edit,stretch=1)
        eleventh_line_layout.addWidget(self.color_setting_bottom_line_g_line_edit,stretch=1)
        eleventh_line_layout.addWidget(self.color_setting_bottom_line_b_line_edit,stretch=1)
        eleventh_line_layout.addWidget(self.color_setting_bottom_line_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(eleventh_line_widget)
        #12
        twelfth_line_widget=QtWidgets.QWidget()
        twelfth_line_layout=QtWidgets.QHBoxLayout(twelfth_line_widget)

        self.color_setting_bar_num_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_bar_num_name_label.setText('Bar num:')

        self.color_setting_bar_num_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_bar_num_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_bar_num_r_line_edit.setText(f'{COLOR_BAR_NUM_R}')

        self.color_setting_bar_num_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_bar_num_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_bar_num_g_line_edit.setText(f'{COLOR_BAR_NUM_G}')

        self.color_setting_bar_num_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_bar_num_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_bar_num_b_line_edit.setText(f'{COLOR_BAR_NUM_B}')

        self.color_setting_bar_num_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_bar_num_change_btn.setText('Change')
        self.color_setting_bar_num_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_bar_num_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('bar_num'))

        twelfth_line_layout.addWidget(self.color_setting_bar_num_name_label,stretch=1)
        twelfth_line_layout.addWidget(self.color_setting_bar_num_r_line_edit,stretch=1)
        twelfth_line_layout.addWidget(self.color_setting_bar_num_g_line_edit,stretch=1)
        twelfth_line_layout.addWidget(self.color_setting_bar_num_b_line_edit,stretch=1)
        twelfth_line_layout.addWidget(self.color_setting_bar_num_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(twelfth_line_widget)
        #13
        thirteenth_line_widget=QtWidgets.QWidget()
        thirteenth_line_layout=QtWidgets.QHBoxLayout(thirteenth_line_widget)

        self.color_setting_text_name_label=QtWidgets.QLabel(self.ui_color_setting)
        self.color_setting_text_name_label.setText('Text:')

        self.color_setting_text_r_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_text_r_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_text_r_line_edit.setText(f'{COLOR_TEXT_R}')

        self.color_setting_text_g_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_text_g_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_text_g_line_edit.setText(f'{COLOR_TEXT_G}')

        self.color_setting_text_b_line_edit=QtWidgets.QLineEdit(self.ui_color_setting)
        self.color_setting_text_b_line_edit.setStyleSheet(self.style_line_edit)
        self.color_setting_text_b_line_edit.setText(f'{COLOR_TEXT_B}')

        self.color_setting_text_change_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_text_change_btn.setText('Change')
        self.color_setting_text_change_btn.setStyleSheet(self.style_btn)
        self.color_setting_text_change_btn.clicked.connect(lambda:self.update_color_and_draw_bar('text'))

        thirteenth_line_layout.addWidget(self.color_setting_text_name_label,stretch=1)
        thirteenth_line_layout.addWidget(self.color_setting_text_r_line_edit,stretch=1)
        thirteenth_line_layout.addWidget(self.color_setting_text_g_line_edit,stretch=1)
        thirteenth_line_layout.addWidget(self.color_setting_text_b_line_edit,stretch=1)
        thirteenth_line_layout.addWidget(self.color_setting_text_change_btn,stretch=1)

        self.color_setting_scroll_layout.addRow(thirteenth_line_widget)
        #
        color_setting_load_save_btn_line_widget=QtWidgets.QWidget()
        color_setting_load_save_btn_line_layout=QtWidgets.QHBoxLayout(color_setting_load_save_btn_line_widget)

        self.color_setting_load_color_txt_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_load_color_txt_btn.setText('Load from color_setting.txt')
        self.color_setting_load_color_txt_btn.setStyleSheet(self.style_btn)
        self.color_setting_load_color_txt_btn.clicked.connect(lambda:self.read_color(''))

        self.color_setting_save_color_txt_close_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_save_color_txt_close_btn.setText('Save to color_setting.txt')
        self.color_setting_save_color_txt_close_btn.setStyleSheet(self.style_btn)
        self.color_setting_save_color_txt_close_btn.clicked.connect(self.save_color)

        color_setting_load_save_btn_line_layout.addWidget(self.color_setting_load_color_txt_btn,stretch=1)
        color_setting_load_save_btn_line_layout.addWidget(self.color_setting_save_color_txt_close_btn,stretch=1)
        #
        color_setting_close_btn_line_widget=QtWidgets.QWidget()
        color_setting_close_btn_line_layout=QtWidgets.QHBoxLayout(color_setting_close_btn_line_widget)

        self.color_setting_close_btn=QtWidgets.QPushButton(self.ui_color_setting)
        self.color_setting_close_btn.setText('Close')
        self.color_setting_close_btn.setStyleSheet(self.style_btn)
        self.color_setting_close_btn.clicked.connect(self.destroy_color_setting_window)

        color_setting_close_btn_line_layout.addWidget(self.color_setting_close_btn,stretch=1)
        #
        self.color_setting_layout.addRow(color_setting_load_save_btn_line_widget)
        self.color_setting_layout.addRow(color_setting_close_btn_line_widget)
        self.ui_color_setting.show()

    def destroy_color_setting_window(self):
        self.ui_color_setting.close()

    def update_color_and_draw_bar(self,obj):
        global COLOR_RED_NOTE_R
        global COLOR_RED_NOTE_G
        global COLOR_RED_NOTE_B
        
        global COLOR_BLUE_NOTE_R
        global COLOR_BLUE_NOTE_G
        global COLOR_BLUE_NOTE_B
        
        global COLOR_SLIDER_R
        global COLOR_SLIDER_G
        global COLOR_SLIDER_B
        
        global COLOR_SPINNER_R
        global COLOR_SPINNER_G
        global COLOR_SPINNER_B
        
        global COLOR_BACKGROUND_R
        global COLOR_BACKGROUND_G
        global COLOR_BACKGROUND_B
        
        global COLOR_KIAI_R
        global COLOR_KIAI_G
        global COLOR_KIAI_B
        
        global COLOR_BORDER_R
        global COLOR_BORDER_G
        global COLOR_BORDER_B
        
        global COLOR_FIRST_BARLINE_R
        global COLOR_FIRST_BARLINE_G
        global COLOR_FIRST_BARLINE_B
        
        global COLOR_BARLINE_R
        global COLOR_BARLINE_G
        global COLOR_BARLINE_B
        
        global COLOR_SMALL_BARLINE_R
        global COLOR_SMALL_BARLINE_G
        global COLOR_SMALL_BARLINE_B
        
        global COLOR_BOTTOM_LINE_R
        global COLOR_BOTTOM_LINE_G
        global COLOR_BOTTOM_LINE_B
        
        global COLOR_BAR_NUM_R
        global COLOR_BAR_NUM_G
        global COLOR_BAR_NUM_B
        
        global COLOR_TEXT_R
        global COLOR_TEXT_G
        global COLOR_TEXT_B
        need_draw=False
        try:
            if obj=='red_note':
                if int(self.color_setting_red_note_r_line_edit.text())>=0 and int(self.color_setting_red_note_r_line_edit.text())<=255 and int(self.color_setting_red_note_g_line_edit.text())>=0 and int(self.color_setting_red_note_g_line_edit.text())<=255 and int(self.color_setting_red_note_b_line_edit.text())>=0 and int(self.color_setting_red_note_b_line_edit.text())<=255:
                    COLOR_RED_NOTE_R=int(self.color_setting_red_note_r_line_edit.text())
                    COLOR_RED_NOTE_G=int(self.color_setting_red_note_g_line_edit.text())
                    COLOR_RED_NOTE_B=int(self.color_setting_red_note_b_line_edit.text())
                    need_draw=True
            elif obj=='blue_note':
                if int(self.color_setting_blue_note_r_line_edit.text())>=0 and int(self.color_setting_blue_note_r_line_edit.text())<=255 and int(self.color_setting_blue_note_g_line_edit.text())>=0 and int(self.color_setting_blue_note_g_line_edit.text())<=255 and int(self.color_setting_blue_note_b_line_edit.text())>=0 and int(self.color_setting_blue_note_b_line_edit.text())<=255:
                    COLOR_BLUE_NOTE_R=int(self.color_setting_blue_note_r_line_edit.text())
                    COLOR_BLUE_NOTE_G=int(self.color_setting_blue_note_g_line_edit.text())
                    COLOR_BLUE_NOTE_B=int(self.color_setting_blue_note_b_line_edit.text())
                    need_draw=True
            elif obj=='slider':
                if int(self.color_setting_slider_r_line_edit.text())>=0 and int(self.color_setting_slider_r_line_edit.text())<=255 and int(self.color_setting_slider_g_line_edit.text())>=0 and int(self.color_setting_slider_g_line_edit.text())<=255 and int(self.color_setting_slider_b_line_edit.text())>=0 and int(self.color_setting_slider_b_line_edit.text())<=255:
                    COLOR_SLIDER_R=int(self.color_setting_slider_r_line_edit.text())
                    COLOR_SLIDER_G=int(self.color_setting_slider_g_line_edit.text())
                    COLOR_SLIDER_B=int(self.color_setting_slider_b_line_edit.text())
                    need_draw=True
            elif obj=='spinner':
                if int(self.color_setting_spinner_r_line_edit.text())>=0 and int(self.color_setting_spinner_r_line_edit.text())<=255 and int(self.color_setting_spinner_g_line_edit.text())>=0 and int(self.color_setting_spinner_g_line_edit.text())<=255 and int(self.color_setting_spinner_b_line_edit.text())>=0 and int(self.color_setting_spinner_b_line_edit.text())<=255:
                    COLOR_SPINNER_R=int(self.color_setting_spinner_r_line_edit.text())
                    COLOR_SPINNER_G=int(self.color_setting_spinner_g_line_edit.text())
                    COLOR_SPINNER_B=int(self.color_setting_spinner_b_line_edit.text())
                    need_draw=True
            elif obj=='background':
                if int(self.color_setting_background_r_line_edit.text())>=0 and int(self.color_setting_background_r_line_edit.text())<=255 and int(self.color_setting_background_g_line_edit.text())>=0 and int(self.color_setting_background_g_line_edit.text())<=255 and int(self.color_setting_background_b_line_edit.text())>=0 and int(self.color_setting_background_b_line_edit.text())<=255:
                    COLOR_BACKGROUND_R=int(self.color_setting_background_r_line_edit.text())
                    COLOR_BACKGROUND_G=int(self.color_setting_background_g_line_edit.text())
                    COLOR_BACKGROUND_B=int(self.color_setting_background_b_line_edit.text())
                    need_draw=True
            elif obj=='kiai':
                if int(self.color_setting_kiai_r_line_edit.text())>=0 and int(self.color_setting_kiai_r_line_edit.text())<=255 and int(self.color_setting_kiai_g_line_edit.text())>=0 and int(self.color_setting_kiai_g_line_edit.text())<=255 and int(self.color_setting_kiai_b_line_edit.text())>=0 and int(self.color_setting_kiai_b_line_edit.text())<=255:
                    COLOR_KIAI_R=int(self.color_setting_kiai_r_line_edit.text())
                    COLOR_KIAI_G=int(self.color_setting_kiai_g_line_edit.text())
                    COLOR_KIAI_B=int(self.color_setting_kiai_b_line_edit.text())
                    need_draw=True
            elif obj=='border':
                if int(self.color_setting_border_r_line_edit.text())>=0 and int(self.color_setting_border_r_line_edit.text())<=255 and int(self.color_setting_border_g_line_edit.text())>=0 and int(self.color_setting_border_g_line_edit.text())<=255 and int(self.color_setting_border_b_line_edit.text())>=0 and int(self.color_setting_border_b_line_edit.text())<=255:
                    COLOR_BORDER_R=int(self.color_setting_border_r_line_edit.text())
                    COLOR_BORDER_G=int(self.color_setting_border_g_line_edit.text())
                    COLOR_BORDER_B=int(self.color_setting_border_b_line_edit.text())
                    need_draw=True
            elif obj=='first_barline':
                if int(self.color_setting_first_barline_r_line_edit.text())>=0 and int(self.color_setting_first_barline_r_line_edit.text())<=255 and int(self.color_setting_first_barline_g_line_edit.text())>=0 and int(self.color_setting_first_barline_g_line_edit.text())<=255 and int(self.color_setting_first_barline_b_line_edit.text())>=0 and int(self.color_setting_first_barline_b_line_edit.text())<=255:
                    COLOR_FIRST_BARLINE_R=int(self.color_setting_first_barline_r_line_edit.text())
                    COLOR_FIRST_BARLINE_G=int(self.color_setting_first_barline_g_line_edit.text())
                    COLOR_FIRST_BARLINE_B=int(self.color_setting_first_barline_b_line_edit.text())
                    need_draw=True
            elif obj=='barline':
                if int(self.color_setting_barline_r_line_edit.text())>=0 and int(self.color_setting_barline_r_line_edit.text())<=255 and int(self.color_setting_barline_g_line_edit.text())>=0 and int(self.color_setting_barline_g_line_edit.text())<=255 and int(self.color_setting_barline_b_line_edit.text())>=0 and int(self.color_setting_barline_b_line_edit.text())<=255:
                    COLOR_BARLINE_R=int(self.color_setting_barline_r_line_edit.text())
                    COLOR_BARLINE_G=int(self.color_setting_barline_g_line_edit.text())
                    COLOR_BARLINE_B=int(self.color_setting_barline_b_line_edit.text())
                    need_draw=True
            elif obj=='small_barline':
                if int(self.color_setting_small_barline_r_line_edit.text())>=0 and int(self.color_setting_small_barline_r_line_edit.text())<=255 and int(self.color_setting_small_barline_g_line_edit.text())>=0 and int(self.color_setting_small_barline_g_line_edit.text())<=255 and int(self.color_setting_small_barline_b_line_edit.text())>=0 and int(self.color_setting_small_barline_b_line_edit.text())<=255:
                    COLOR_SMALL_BARLINE_R=int(self.color_setting_small_barline_r_line_edit.text())
                    COLOR_SMALL_BARLINE_G=int(self.color_setting_small_barline_g_line_edit.text())
                    COLOR_SMALL_BARLINE_B=int(self.color_setting_small_barline_b_line_edit.text())
                    need_draw=True
            elif obj=='bottom_line':
                if int(self.color_setting_bottom_line_r_line_edit.text())>=0 and int(self.color_setting_bottom_line_r_line_edit.text())<=255 and int(self.color_setting_bottom_line_g_line_edit.text())>=0 and int(self.color_setting_bottom_line_g_line_edit.text())<=255 and int(self.color_setting_bottom_line_b_line_edit.text())>=0 and int(self.color_setting_bottom_line_b_line_edit.text())<=255:
                    COLOR_BOTTOM_LINE_R=int(self.color_setting_bottom_line_r_line_edit.text())
                    COLOR_BOTTOM_LINE_G=int(self.color_setting_bottom_line_g_line_edit.text())
                    COLOR_BOTTOM_LINE_B=int(self.color_setting_bottom_line_b_line_edit.text())
                    need_draw=True
            elif obj=='bar_num':
                if int(self.color_setting_bar_num_r_line_edit.text())>=0 and int(self.color_setting_bar_num_r_line_edit.text())<=255 and int(self.color_setting_bar_num_g_line_edit.text())>=0 and int(self.color_setting_bar_num_g_line_edit.text())<=255 and int(self.color_setting_bar_num_b_line_edit.text())>=0 and int(self.color_setting_bar_num_b_line_edit.text())<=255:
                    COLOR_BAR_NUM_R=int(self.color_setting_bar_num_r_line_edit.text())
                    COLOR_BAR_NUM_G=int(self.color_setting_bar_num_g_line_edit.text())
                    COLOR_BAR_NUM_B=int(self.color_setting_bar_num_b_line_edit.text())
                    need_draw=True
            elif obj=='text':
                if int(self.color_setting_text_r_line_edit.text())>=0 and int(self.color_setting_text_r_line_edit.text())<=255 and int(self.color_setting_text_g_line_edit.text())>=0 and int(self.color_setting_text_g_line_edit.text())<=255 and int(self.color_setting_text_b_line_edit.text())>=0 and int(self.color_setting_text_b_line_edit.text())<=255:
                    COLOR_TEXT_R=int(self.color_setting_text_r_line_edit.text())
                    COLOR_TEXT_G=int(self.color_setting_text_g_line_edit.text())
                    COLOR_TEXT_B=int(self.color_setting_text_b_line_edit.text())
                    need_draw=True
            if need_draw:
                self.draw_bar()
                self.update_bar_img_label()
        except:
            pass

    def draw_bar(self):
        background_color=(COLOR_BACKGROUND_B,COLOR_BACKGROUND_G,COLOR_BACKGROUND_R)
        note_color_red=(COLOR_RED_NOTE_B,COLOR_RED_NOTE_G,COLOR_RED_NOTE_R)
        note_color_blue=(COLOR_BLUE_NOTE_B,COLOR_BLUE_NOTE_G,COLOR_BLUE_NOTE_R)
        slider_color=(COLOR_SLIDER_B,COLOR_SLIDER_G,COLOR_SLIDER_R)
        spinner_color=(COLOR_SPINNER_B,COLOR_SPINNER_G,COLOR_SPINNER_R)
        kiai_color=(COLOR_KIAI_B,COLOR_KIAI_G,COLOR_KIAI_R)
        border_color=(COLOR_BORDER_B,COLOR_BORDER_G,COLOR_BORDER_R)
        first_barline_color=(COLOR_FIRST_BARLINE_B,COLOR_FIRST_BARLINE_G,COLOR_FIRST_BARLINE_R)
        barline_color=(COLOR_BARLINE_B,COLOR_BARLINE_G,COLOR_BARLINE_R)
        small_barline_color=(COLOR_SMALL_BARLINE_B,COLOR_SMALL_BARLINE_G,COLOR_SMALL_BARLINE_R)
        bottom_line_color=(COLOR_BOTTOM_LINE_B,COLOR_BOTTOM_LINE_G,COLOR_BOTTOM_LINE_R)
        bar_num_color=(COLOR_BAR_NUM_B,COLOR_BAR_NUM_G,COLOR_BAR_NUM_R)
        text_color=(COLOR_TEXT_B,COLOR_TEXT_G,COLOR_TEXT_R)

        bar_img = np.full((DRAW_BAR_H, DRAW_BAR_W, 3), background_color , np.uint8)
        #kiai
        bar_img[:,OBJ_OFFSET*4+START_X:OBJ_OFFSET*8+START_X]=np.full((DRAW_BAR_H, OBJ_OFFSET*4, 3), kiai_color , np.uint8)
        #barline
        i=0
        while i<12:
            if i==0:
                cv2.line(bar_img, (START_X+OBJ_OFFSET*i,0), (START_X+OBJ_OFFSET*i,DRAW_BAR_H), first_barline_color, 4)
                #bar num
                cv2.putText(bar_img,'123',(START_X+OBJ_OFFSET*i+5,BAR_TEXT_Y),cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,bar_num_color,2)

                #bpm and time signature
                bpm_ts_text='BPM: 180, (4/4)'
                #resize
                retval, baseLine = cv2.getTextSize(bpm_ts_text,cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,2)
                cv2.putText(bar_img,bpm_ts_text,(int(OBJ_OFFSET*4/2)-int(retval[0]/2)+START_X,BAR_TEXT_Y),cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,text_color,2)

            elif i%4==0:
                cv2.line(bar_img, (START_X+OBJ_OFFSET*i,0), (START_X+OBJ_OFFSET*i,DRAW_BAR_H), barline_color, 2)
                if i==4:
                    cv2.putText(bar_img,'456',(START_X+OBJ_OFFSET*i+5,BAR_TEXT_Y),cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,bar_num_color,2)
                else:
                    cv2.putText(bar_img,'7890',(START_X+OBJ_OFFSET*i+5,BAR_TEXT_Y),cv2.FONT_HERSHEY_SIMPLEX,BAR_TEXT_SCALE,bar_num_color,2)
            else:
                cv2.line(bar_img, (START_X+OBJ_OFFSET*i,SMALL_BARLINE_TOP_Y), (START_X+OBJ_OFFSET*i,DRAW_BAR_H), small_barline_color, 1)
            i+=1
        #bottom line
        cv2.line(bar_img, (0,DRAW_BAR_H-1), (DRAW_BAR_W,DRAW_BAR_H-1), bottom_line_color, 1)
        #r
        cv2.circle(bar_img,(START_X,Y),SMALL_OBJ_RADIUS,note_color_red,-1)
        cv2.circle(bar_img,(START_X,Y),SMALL_OBJ_RADIUS,border_color,1)

        cv2.circle(bar_img,(START_X+OBJ_OFFSET,Y),BIG_OBJ_RADIUS,note_color_red,-1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET,Y),BIG_OBJ_RADIUS,border_color,1)
        #b
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*2,Y),SMALL_OBJ_RADIUS,note_color_blue,-1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*2,Y),SMALL_OBJ_RADIUS,border_color,1)

        cv2.circle(bar_img,(START_X+OBJ_OFFSET*3,Y),BIG_OBJ_RADIUS,note_color_blue,-1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*3,Y),BIG_OBJ_RADIUS,border_color,1)
        #slider
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*5,Y),SMALL_OBJ_RADIUS,slider_color,-1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*5,Y),SMALL_OBJ_RADIUS,border_color,1)
        cv2.rectangle(bar_img, (START_X+OBJ_OFFSET*4, Y-SMALL_OBJ_RADIUS), (START_X+OBJ_OFFSET*5, Y+SMALL_OBJ_RADIUS), border_color, 1)
        cv2.rectangle(bar_img, (START_X+OBJ_OFFSET*4, Y-SMALL_OBJ_RADIUS+1), (START_X+OBJ_OFFSET*5, Y+SMALL_OBJ_RADIUS-1), slider_color, -1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*4,Y),SMALL_OBJ_RADIUS,slider_color,-1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*4,Y),SMALL_OBJ_RADIUS,border_color,1)

        cv2.circle(bar_img,(START_X+OBJ_OFFSET*7,Y),BIG_OBJ_RADIUS,slider_color,-1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*7,Y),BIG_OBJ_RADIUS,border_color,1)
        cv2.rectangle(bar_img, (START_X+OBJ_OFFSET*6, Y-BIG_OBJ_RADIUS), (START_X+OBJ_OFFSET*7, Y+BIG_OBJ_RADIUS), border_color, 1)
        cv2.rectangle(bar_img, (START_X+OBJ_OFFSET*6, Y-BIG_OBJ_RADIUS+1), (START_X+OBJ_OFFSET*7, Y+BIG_OBJ_RADIUS-1), slider_color, -1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*6,Y),BIG_OBJ_RADIUS,slider_color,-1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*6,Y),BIG_OBJ_RADIUS,border_color,1)
        #spinner
        cv2.line(bar_img, (START_X+OBJ_OFFSET*9-5,Y-5), (START_X+OBJ_OFFSET*9+5,Y+5), spinner_color, 3)
        cv2.line(bar_img, (START_X+OBJ_OFFSET*9+5,Y-5), (START_X+OBJ_OFFSET*9-5,Y+5), spinner_color, 3)
        cv2.line(bar_img, (START_X+OBJ_OFFSET*8,Y), (START_X+OBJ_OFFSET*9,Y), spinner_color, 2)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*8,Y),BIG_OBJ_RADIUS,spinner_color,-1)
        cv2.circle(bar_img,(START_X+OBJ_OFFSET*8,Y),BIG_OBJ_RADIUS,border_color,1)
        ##################
        
        title_img = np.full((DRAW_BAR_H, DRAW_BAR_W, 3), background_color , np.uint8)
        text='Artist - Name [Difficulty] by Mapper'

        #resize
        text_scale=TITLE_TEXT_SCALE#size
        retval, baseLine = cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,text_scale,2)
        while retval[0] + TITLE_TEXT_WIDTH_MARGIN*2 >= DRAW_BAR_W:
            text_scale-=0.01
            retval, baseLine = cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,text_scale,2)

        #draw text
        cv2.putText(title_img,text,(int((DRAW_BAR_W/2) - (retval[0]/2)),retval[1] + int((DRAW_BAR_H-retval[1])/2)),cv2.FONT_HERSHEY_SIMPLEX,text_scale,text_color,2)

        #
        self.img=cv2.vconcat([title_img,bar_img])

    def update_bar_img_label(self):
        height, width, channel = self.img.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(self.img.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)
        self.bar_img_label.setPixmap(QtGui.QPixmap(qImg))

    def read_color(self,mode=''):
        global COLOR_RED_NOTE_R
        global COLOR_RED_NOTE_G
        global COLOR_RED_NOTE_B
        
        global COLOR_BLUE_NOTE_R
        global COLOR_BLUE_NOTE_G
        global COLOR_BLUE_NOTE_B
        
        global COLOR_SLIDER_R
        global COLOR_SLIDER_G
        global COLOR_SLIDER_B
        
        global COLOR_SPINNER_R
        global COLOR_SPINNER_G
        global COLOR_SPINNER_B
        
        global COLOR_BACKGROUND_R
        global COLOR_BACKGROUND_G
        global COLOR_BACKGROUND_B
        
        global COLOR_KIAI_R
        global COLOR_KIAI_G
        global COLOR_KIAI_B
        
        global COLOR_BORDER_R
        global COLOR_BORDER_G
        global COLOR_BORDER_B
        
        global COLOR_FIRST_BARLINE_R
        global COLOR_FIRST_BARLINE_G
        global COLOR_FIRST_BARLINE_B
        
        global COLOR_BARLINE_R
        global COLOR_BARLINE_G
        global COLOR_BARLINE_B
        
        global COLOR_SMALL_BARLINE_R
        global COLOR_SMALL_BARLINE_G
        global COLOR_SMALL_BARLINE_B
        
        global COLOR_BOTTOM_LINE_R
        global COLOR_BOTTOM_LINE_G
        global COLOR_BOTTOM_LINE_B
        
        global COLOR_BAR_NUM_R
        global COLOR_BAR_NUM_G
        global COLOR_BAR_NUM_B
        
        global COLOR_TEXT_R
        global COLOR_TEXT_G
        global COLOR_TEXT_B
        try:
            f=open('./color_setting.txt','r')
            s=f.readlines()
            f.close()
            i=0
            while i<len(s):
                if s[i][-1]=='\n':
                    s[i]=s[i][:-1]
                i+=1
            COLOR_RED_NOTE_R=int(s[0].split(',')[1])     
            COLOR_RED_NOTE_G=int(s[0].split(',')[2])     
            COLOR_RED_NOTE_B=int(s[0].split(',')[3])

            COLOR_BLUE_NOTE_R=int(s[1].split(',')[1])     
            COLOR_BLUE_NOTE_G=int(s[1].split(',')[2])     
            COLOR_BLUE_NOTE_B=int(s[1].split(',')[3])

            COLOR_SLIDER_R=int(s[2].split(',')[1])     
            COLOR_SLIDER_G=int(s[2].split(',')[2])     
            COLOR_SLIDER_B=int(s[2].split(',')[3])

            COLOR_SPINNER_R=int(s[3].split(',')[1])     
            COLOR_SPINNER_G=int(s[3].split(',')[2])     
            COLOR_SPINNER_B=int(s[3].split(',')[3])

            COLOR_BACKGROUND_R=int(s[4].split(',')[1])     
            COLOR_BACKGROUND_G=int(s[4].split(',')[2])     
            COLOR_BACKGROUND_B=int(s[4].split(',')[3])

            COLOR_KIAI_R=int(s[5].split(',')[1])     
            COLOR_KIAI_G=int(s[5].split(',')[2])     
            COLOR_KIAI_B=int(s[5].split(',')[3])

            COLOR_BORDER_R=int(s[6].split(',')[1])     
            COLOR_BORDER_G=int(s[6].split(',')[2])     
            COLOR_BORDER_B=int(s[6].split(',')[3])

            COLOR_FIRST_BARLINE_R=int(s[7].split(',')[1])     
            COLOR_FIRST_BARLINE_G=int(s[7].split(',')[2])     
            COLOR_FIRST_BARLINE_B=int(s[7].split(',')[3])

            COLOR_BARLINE_R=int(s[8].split(',')[1])     
            COLOR_BARLINE_G=int(s[8].split(',')[2])     
            COLOR_BARLINE_B=int(s[8].split(',')[3])

            COLOR_SMALL_BARLINE_R=int(s[9].split(',')[1])     
            COLOR_SMALL_BARLINE_G=int(s[9].split(',')[2])     
            COLOR_SMALL_BARLINE_B=int(s[9].split(',')[3])

            COLOR_BOTTOM_LINE_R=int(s[10].split(',')[1])     
            COLOR_BOTTOM_LINE_G=int(s[10].split(',')[2])     
            COLOR_BOTTOM_LINE_B=int(s[10].split(',')[3])

            COLOR_BAR_NUM_R=int(s[11].split(',')[1])     
            COLOR_BAR_NUM_G=int(s[11].split(',')[2])     
            COLOR_BAR_NUM_B=int(s[11].split(',')[3])

            COLOR_TEXT_R=int(s[12].split(',')[1])     
            COLOR_TEXT_G=int(s[12].split(',')[2])     
            COLOR_TEXT_B=int(s[12].split(',')[3])
        except:
            #pass
            if mode=='':
                self.to_default_color()
            elif mode=='init':
                self.to_default_color('init')
        if mode=='':
            self.update_color_line_edit()
            self.draw_bar()
            self.update_bar_img_label()

    def to_default_color(self,mode=''):
        global COLOR_RED_NOTE_R
        global COLOR_RED_NOTE_G
        global COLOR_RED_NOTE_B
        
        global COLOR_BLUE_NOTE_R
        global COLOR_BLUE_NOTE_G
        global COLOR_BLUE_NOTE_B
        
        global COLOR_SLIDER_R
        global COLOR_SLIDER_G
        global COLOR_SLIDER_B
        
        global COLOR_SPINNER_R
        global COLOR_SPINNER_G
        global COLOR_SPINNER_B
        
        global COLOR_BACKGROUND_R
        global COLOR_BACKGROUND_G
        global COLOR_BACKGROUND_B
        
        global COLOR_KIAI_R
        global COLOR_KIAI_G
        global COLOR_KIAI_B
        
        global COLOR_BORDER_R
        global COLOR_BORDER_G
        global COLOR_BORDER_B
        
        global COLOR_FIRST_BARLINE_R
        global COLOR_FIRST_BARLINE_G
        global COLOR_FIRST_BARLINE_B
        
        global COLOR_BARLINE_R
        global COLOR_BARLINE_G
        global COLOR_BARLINE_B
        
        global COLOR_SMALL_BARLINE_R
        global COLOR_SMALL_BARLINE_G
        global COLOR_SMALL_BARLINE_B
        
        global COLOR_BOTTOM_LINE_R
        global COLOR_BOTTOM_LINE_G
        global COLOR_BOTTOM_LINE_B
        
        global COLOR_BAR_NUM_R
        global COLOR_BAR_NUM_G
        global COLOR_BAR_NUM_B
        
        global COLOR_TEXT_R
        global COLOR_TEXT_G
        global COLOR_TEXT_B

        COLOR_RED_NOTE_R=NOTE_COLOR_RED[2]
        COLOR_RED_NOTE_G=NOTE_COLOR_RED[1]
        COLOR_RED_NOTE_B=NOTE_COLOR_RED[0]

        COLOR_BLUE_NOTE_R=NOTE_COLOR_BLUE[2]
        COLOR_BLUE_NOTE_G=NOTE_COLOR_BLUE[1]
        COLOR_BLUE_NOTE_B=NOTE_COLOR_BLUE[0]

        COLOR_SLIDER_R=SLIDER_COLOR[2]
        COLOR_SLIDER_G=SLIDER_COLOR[1]
        COLOR_SLIDER_B=SLIDER_COLOR[0]

        COLOR_SPINNER_R=SPINNER_COLOR[2]
        COLOR_SPINNER_G=SPINNER_COLOR[1]
        COLOR_SPINNER_B=SPINNER_COLOR[0]

        COLOR_BACKGROUND_R=BACKGROUND_COLOR[2]
        COLOR_BACKGROUND_G=BACKGROUND_COLOR[1]
        COLOR_BACKGROUND_B=BACKGROUND_COLOR[0]

        COLOR_KIAI_R=KIAI_COLOR[2]
        COLOR_KIAI_G=KIAI_COLOR[1]
        COLOR_KIAI_B=KIAI_COLOR[0]

        COLOR_BORDER_R=OBJ_BORDER_COLOR[2]
        COLOR_BORDER_G=OBJ_BORDER_COLOR[1]
        COLOR_BORDER_B=OBJ_BORDER_COLOR[0]

        COLOR_FIRST_BARLINE_R=FIRST_BARLINE_COLOR[2]
        COLOR_FIRST_BARLINE_G=FIRST_BARLINE_COLOR[1]
        COLOR_FIRST_BARLINE_B=FIRST_BARLINE_COLOR[0]

        COLOR_BARLINE_R=BARLINE_COLOR[2]
        COLOR_BARLINE_G=BARLINE_COLOR[1]
        COLOR_BARLINE_B=BARLINE_COLOR[0]

        COLOR_SMALL_BARLINE_R=SMALL_BARLINE_COLOR[2]
        COLOR_SMALL_BARLINE_G=SMALL_BARLINE_COLOR[1]
        COLOR_SMALL_BARLINE_B=SMALL_BARLINE_COLOR[0]

        COLOR_BOTTOM_LINE_R=BOTTOM_LINE_COLOR[2]
        COLOR_BOTTOM_LINE_G=BOTTOM_LINE_COLOR[1]
        COLOR_BOTTOM_LINE_B=BOTTOM_LINE_COLOR[0]

        COLOR_BAR_NUM_R=BAR_NUM_COLOR[2]
        COLOR_BAR_NUM_G=BAR_NUM_COLOR[1]
        COLOR_BAR_NUM_B=BAR_NUM_COLOR[0]

        COLOR_TEXT_R=TEXT_COLOR[2]
        COLOR_TEXT_G=TEXT_COLOR[1]
        COLOR_TEXT_B=TEXT_COLOR[0]
        
        if mode=='':
            self.update_color_line_edit()
            self.draw_bar()
            self.update_bar_img_label()

    def save_color(self):
        f=open('./color_setting.txt','w')
        f.write(f'RED NOTE     ,{COLOR_RED_NOTE_R},{COLOR_RED_NOTE_G},{COLOR_RED_NOTE_B}\n')
        f.write(f'BLUE NOTE    ,{COLOR_BLUE_NOTE_R},{COLOR_BLUE_NOTE_G},{COLOR_BLUE_NOTE_B}\n')
        f.write(f'SLIDER       ,{COLOR_SLIDER_R},{COLOR_SLIDER_G},{COLOR_SLIDER_B}\n')
        f.write(f'SPINNER      ,{COLOR_SPINNER_R},{COLOR_SPINNER_G},{COLOR_SPINNER_B}\n')
        f.write(f'BACKGROUND   ,{COLOR_BACKGROUND_R},{COLOR_BACKGROUND_G},{COLOR_BACKGROUND_B}\n')
        f.write(f'KIAI         ,{COLOR_KIAI_R},{COLOR_KIAI_G},{COLOR_KIAI_B}\n')
        f.write(f'BORDER       ,{COLOR_BORDER_R},{COLOR_BORDER_G},{COLOR_BORDER_B}\n')
        f.write(f'FIRST BARLINE,{COLOR_FIRST_BARLINE_R},{COLOR_FIRST_BARLINE_G},{COLOR_FIRST_BARLINE_B}\n')
        f.write(f'BARLINE      ,{COLOR_BARLINE_R},{COLOR_BARLINE_G},{COLOR_BARLINE_B}\n')
        f.write(f'SMALL BARLINE,{COLOR_SMALL_BARLINE_R},{COLOR_SMALL_BARLINE_G},{COLOR_SMALL_BARLINE_B}\n')
        f.write(f'BOTTOM LINE  ,{COLOR_BOTTOM_LINE_R},{COLOR_BOTTOM_LINE_G},{COLOR_BOTTOM_LINE_B}\n')
        f.write(f'BAR NUM      ,{COLOR_BAR_NUM_R},{COLOR_BAR_NUM_G},{COLOR_BAR_NUM_B}\n')
        f.write(f'TEXT         ,{COLOR_TEXT_R},{COLOR_TEXT_G},{COLOR_TEXT_B}\n')
        f.close()

    def update_color_line_edit(self):
        self.color_setting_red_note_r_line_edit.setText(f'{COLOR_RED_NOTE_R}')
        self.color_setting_red_note_g_line_edit.setText(f'{COLOR_RED_NOTE_G}')
        self.color_setting_red_note_b_line_edit.setText(f'{COLOR_RED_NOTE_B}')

        self.color_setting_blue_note_r_line_edit.setText(f'{COLOR_BLUE_NOTE_R}')
        self.color_setting_blue_note_g_line_edit.setText(f'{COLOR_BLUE_NOTE_G}')
        self.color_setting_blue_note_b_line_edit.setText(f'{COLOR_BLUE_NOTE_B}')

        self.color_setting_slider_r_line_edit.setText(f'{COLOR_SLIDER_R}')
        self.color_setting_slider_g_line_edit.setText(f'{COLOR_SLIDER_G}')
        self.color_setting_slider_b_line_edit.setText(f'{COLOR_SLIDER_B}')

        self.color_setting_spinner_r_line_edit.setText(f'{COLOR_SPINNER_R}')
        self.color_setting_spinner_g_line_edit.setText(f'{COLOR_SPINNER_G}')
        self.color_setting_spinner_b_line_edit.setText(f'{COLOR_SPINNER_B}')

        self.color_setting_background_r_line_edit.setText(f'{COLOR_BACKGROUND_R}')
        self.color_setting_background_g_line_edit.setText(f'{COLOR_BACKGROUND_G}')
        self.color_setting_background_b_line_edit.setText(f'{COLOR_BACKGROUND_B}')

        self.color_setting_kiai_r_line_edit.setText(f'{COLOR_KIAI_R}')
        self.color_setting_kiai_g_line_edit.setText(f'{COLOR_KIAI_G}')
        self.color_setting_kiai_b_line_edit.setText(f'{COLOR_KIAI_B}')

        self.color_setting_border_r_line_edit.setText(f'{COLOR_BORDER_R}')
        self.color_setting_border_g_line_edit.setText(f'{COLOR_BORDER_G}')
        self.color_setting_border_b_line_edit.setText(f'{COLOR_BORDER_B}')

        self.color_setting_first_barline_r_line_edit.setText(f'{COLOR_FIRST_BARLINE_R}')
        self.color_setting_first_barline_g_line_edit.setText(f'{COLOR_FIRST_BARLINE_G}')
        self.color_setting_first_barline_b_line_edit.setText(f'{COLOR_FIRST_BARLINE_B}')

        self.color_setting_barline_r_line_edit.setText(f'{COLOR_BARLINE_R}')
        self.color_setting_barline_g_line_edit.setText(f'{COLOR_BARLINE_G}')
        self.color_setting_barline_b_line_edit.setText(f'{COLOR_BARLINE_B}')

        self.color_setting_small_barline_r_line_edit.setText(f'{COLOR_SMALL_BARLINE_R}')
        self.color_setting_small_barline_g_line_edit.setText(f'{COLOR_SMALL_BARLINE_G}')
        self.color_setting_small_barline_b_line_edit.setText(f'{COLOR_SMALL_BARLINE_B}')

        self.color_setting_bottom_line_r_line_edit.setText(f'{COLOR_BOTTOM_LINE_R}')
        self.color_setting_bottom_line_g_line_edit.setText(f'{COLOR_BOTTOM_LINE_G}')
        self.color_setting_bottom_line_b_line_edit.setText(f'{COLOR_BOTTOM_LINE_B}')

        self.color_setting_bar_num_r_line_edit.setText(f'{COLOR_BAR_NUM_R}')
        self.color_setting_bar_num_g_line_edit.setText(f'{COLOR_BAR_NUM_G}')
        self.color_setting_bar_num_b_line_edit.setText(f'{COLOR_BAR_NUM_B}')

        self.color_setting_text_r_line_edit.setText(f'{COLOR_TEXT_R}')
        self.color_setting_text_g_line_edit.setText(f'{COLOR_TEXT_G}')
        self.color_setting_text_b_line_edit.setText(f'{COLOR_TEXT_B}')

    def get_color_setting_parameters(self):
        self.color_setting_parameters['red_note']=(COLOR_RED_NOTE_B,COLOR_RED_NOTE_G,COLOR_RED_NOTE_R)
        self.color_setting_parameters['blue_note']=(COLOR_BLUE_NOTE_B,COLOR_BLUE_NOTE_G,COLOR_BLUE_NOTE_R)
        self.color_setting_parameters['slider']=(COLOR_SLIDER_B,COLOR_SLIDER_G,COLOR_SLIDER_R)
        self.color_setting_parameters['spinner']=(COLOR_SPINNER_B,COLOR_SPINNER_G,COLOR_SPINNER_R)
        self.color_setting_parameters['background']=(COLOR_BACKGROUND_B,COLOR_BACKGROUND_G,COLOR_BACKGROUND_R)
        self.color_setting_parameters['kiai']=(COLOR_KIAI_B,COLOR_KIAI_G,COLOR_KIAI_R)
        self.color_setting_parameters['border']=(COLOR_BORDER_B,COLOR_BORDER_G,COLOR_BORDER_R)
        self.color_setting_parameters['first_barline']=(COLOR_FIRST_BARLINE_B,COLOR_FIRST_BARLINE_G,COLOR_FIRST_BARLINE_R)
        self.color_setting_parameters['barline']=(COLOR_BARLINE_B,COLOR_BARLINE_G,COLOR_BARLINE_R)
        self.color_setting_parameters['small_barline']=(COLOR_SMALL_BARLINE_B,COLOR_SMALL_BARLINE_G,COLOR_SMALL_BARLINE_R)
        self.color_setting_parameters['bottom_line']=(COLOR_BOTTOM_LINE_B,COLOR_BOTTOM_LINE_G,COLOR_BOTTOM_LINE_R)
        self.color_setting_parameters['bar_num']=(COLOR_BAR_NUM_B,COLOR_BAR_NUM_G,COLOR_BAR_NUM_R)
        self.color_setting_parameters['text']=(COLOR_TEXT_B,COLOR_TEXT_G,COLOR_TEXT_R)

    def closeEvent(self,event):
        if self.ui_setting.isVisible():
            self.ui_setting.close()
        if self.ui_color_setting.isVisible():
            self.ui_color_setting.close()

# class for scrollable label
class ScrollLabel(QtWidgets.QScrollArea):
 
    # constructor
    def __init__(self, *args, **kwargs):
        QtWidgets.QScrollArea.__init__(self, *args, **kwargs)
 
        # making widget resizable
        self.setWidgetResizable(True)

        self.main_box = QtWidgets.QWidget(self)
        self.setWidget(self.main_box)
        self.main_layout = QtWidgets.QFormLayout(self.main_box)
        self.label = QtWidgets.QLabel(self)
        self.main_layout.addRow(self.label)
 
    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

if __name__ == '__main__':
    OTBIC_app = QtWidgets.QApplication(sys.argv)
    Form = MyWidget()
    Form.show()
    sys.exit(OTBIC_app.exec_())