from OTBIC_app import main_func, ONE_BAR_W, BAR_H, BAR_NUM_IN_ONE_CUT, CUT_AND_MERGE_MODE_S, CUT_AND_MERGE_MODE
import os
from PyQt5 import QtGui, QtWidgets, QtCore
import sys
from os import startfile

#change able app varible
#ONE_BAR_W=320
#BAR_H=60
#SMALL_OBJ_RADIUS=10
#BIG_OBJ_RADIUS=15
BAR_TEXT_Y=16
NOTE_COLOR_RED = (43, 68, 255) # BGR
NOTE_COLOR_BLUE = (255, 140, 66) # BGR
BACKGROUND_COLOR=(105,105,105)
FAULT_TOLERANCE=1#fit rightmost note that x + BAR.bar_line_offset will exceed BAR_W
BAR_LINE_OFFSET_Y=10#for small bar line and notes layout
#BAR_NUM_IN_ONE_CUT=4
#SMALL_BARLINE_TOP_Y=int((BAR_H-(BAR_LINE_OFFSET_Y*2))/4)
#SMALL_BARLINE_BOTTOM_Y=BAR_H-SMALL_BARLINE_TOP_Y
BAR_TEXT_SCALE=0.55
TITLE_TEXT_SCALE=1
TITLE_TEXT_WIDTH_MARGIN=50

#global variable
WIDTH=1280
HEIGHT=720
BUTTON_TEXT_1_SPACE=' '

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
        self.setting_parameters={"one_bar_w":ONE_BAR_W,"one_bar_h":BAR_H,"bar_num_in_one_cut":BAR_NUM_IN_ONE_CUT,"cut_and_merge_mode":CUT_AND_MERGE_MODE}
        
        #style sheet
        self.style()
        
        self.main_box = QtWidgets.QWidget(self)
        self.main_box.setGeometry(0,0,self.width_,self.height_)
        self.main_box.setStyleSheet(self.style_box)

        self.main_layout = QtWidgets.QFormLayout(self.main_box)

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
        self.chosse_osu_file_btn=QtWidgets.QPushButton(self)
        self.chosse_osu_file_btn.setText(f'{BUTTON_TEXT_1_SPACE}Choose .osu file{BUTTON_TEXT_1_SPACE}')
        self.chosse_osu_file_btn.setStyleSheet(self.style_btn)
        self.chosse_osu_file_btn.clicked.connect(self.open_osu_file)
        #
        self.automatic_btn=QtWidgets.QPushButton(self)
        self.automatic_btn.setText(f'{BUTTON_TEXT_1_SPACE*44}Automatic{BUTTON_TEXT_1_SPACE*43}')
        self.automatic_btn.setStyleSheet(self.style_btn)
        self.automatic_btn.clicked.connect(self.change_to_automatic)
        if len(self.osu_file_path)==0:
            self.automatic_btn.setEnabled(False)
        
        self.manual_btn=QtWidgets.QPushButton(self)
        self.manual_btn.setText(f'{BUTTON_TEXT_1_SPACE}Manual{BUTTON_TEXT_1_SPACE}')
        self.manual_btn.setStyleSheet(self.style_btn)
        self.manual_btn.clicked.connect(self.change_to_manual)
        if len(self.osu_file_path)==0:
            self.manual_btn.setEnabled(False)
        #

        #
        self.main_layout.addRow(self.osu_file_name_label)
        self.main_layout.addRow(self.chosse_osu_file_btn)
        self.main_layout.addRow(self.automatic_btn,self.manual_btn)

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
        self.output_setting_btn=QtWidgets.QPushButton(self)
        self.output_setting_btn.setText(f'{BUTTON_TEXT_1_SPACE}Output Setting{BUTTON_TEXT_1_SPACE}')
        self.output_setting_btn.setStyleSheet(self.style_btn)
        self.output_setting_btn.clicked.connect(self.change_setting_window)

        self.main_layout.addRow(self.output_setting_btn)
        #
        self.convert_btn=QtWidgets.QPushButton(self)
        self.convert_btn.setText(f'{BUTTON_TEXT_1_SPACE}Convert{BUTTON_TEXT_1_SPACE}')
        self.convert_btn.setStyleSheet(self.style_btn)
        self.convert_btn.clicked.connect(lambda:self.start_convert('auto'))

        self.main_layout.addRow(self.convert_btn)
        
        #
        self.back_to_menu_btn=QtWidgets.QPushButton(self)
        self.back_to_menu_btn.setText(f'{BUTTON_TEXT_1_SPACE}Back to menu{BUTTON_TEXT_1_SPACE}')
        self.back_to_menu_btn.setStyleSheet(self.style_btn)
        self.back_to_menu_btn.clicked.connect(self.start_ui)

        self.main_layout.addRow(self.back_to_menu_btn)

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
        self.add_bpm_btn=QtWidgets.QPushButton(self)
        self.add_bpm_btn.setText(f'{BUTTON_TEXT_1_SPACE}Add new bpm timing point{BUTTON_TEXT_1_SPACE}')
        self.add_bpm_btn.setStyleSheet(self.style_btn)
        self.add_bpm_btn.clicked.connect(self.add_bpm)

        self.main_layout.addRow(self.add_bpm_btn)
        #

        self.delete_bpm_btn=QtWidgets.QPushButton(self)
        self.delete_bpm_btn.setText(f'{BUTTON_TEXT_1_SPACE*33}Delete bpm timing point{BUTTON_TEXT_1_SPACE*33}')
        self.delete_bpm_btn.setStyleSheet(self.style_btn)
        self.delete_bpm_btn.clicked.connect(self.delete_bpm)

        self.current_del_timing_point_id_box=QtWidgets.QComboBox(self)
        self.current_del_timing_point_id_box.setStyleSheet(self.style_line_edit)
        self.main_layout.addRow(self.delete_bpm_btn,self.current_del_timing_point_id_box)
        #
        self.output_setting_btn=QtWidgets.QPushButton(self)
        self.output_setting_btn.setText(f'{BUTTON_TEXT_1_SPACE}Output Setting{BUTTON_TEXT_1_SPACE}')
        self.output_setting_btn.setStyleSheet(self.style_btn)
        self.output_setting_btn.clicked.connect(self.change_setting_window)

        self.main_layout.addRow(self.output_setting_btn)
        #
        self.convert_btn=QtWidgets.QPushButton(self)
        self.convert_btn.setText(f'{BUTTON_TEXT_1_SPACE}Convert{BUTTON_TEXT_1_SPACE}')
        self.convert_btn.setStyleSheet(self.style_btn)
        self.convert_btn.clicked.connect(lambda:self.start_convert('manual'))

        self.main_layout.addRow(self.convert_btn)
        #
        self.back_to_menu_btn=QtWidgets.QPushButton(self)
        self.back_to_menu_btn.setText(f'{BUTTON_TEXT_1_SPACE}Back to menu{BUTTON_TEXT_1_SPACE}')
        self.back_to_menu_btn.setStyleSheet(self.style_btn)
        self.back_to_menu_btn.clicked.connect(self.start_ui)

        self.main_layout.addRow(self.back_to_menu_btn)

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

        bpm_layout.addWidget(bpm_id_name_label)
        bpm_layout.addWidget(bpm_id_label)
        bpm_layout.addWidget(bpm_start_offset_label)
        bpm_layout.addWidget(bpm_start_offset_line_edit)
        bpm_layout.addWidget(bpm_bpm_label)
        bpm_layout.addWidget(bpm_bpm_line_edit)
        bpm_layout.addWidget(bpm_time_signature_label)
        bpm_layout.addWidget(bpm_time_signature_line_edit)

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
        if mode == "auto":
            main_func('auto',self.osu_file_folder_path,self.osu_file_name,setting_parameters=self.setting_parameters)
        elif mode == "manual" and self.check_timing_point_list_is_valid():
            self.get_tp_list()
            self.sort_tp_list_by_offset()
            main_func('manual',self.osu_file_folder_path,self.osu_file_name,tp_list=self.tp_list,setting_parameters=self.setting_parameters)

    def change_setting_window(self):
        self.ui_setting=QtWidgets.QWidget()
        self.ui_setting.setWindowTitle(f'Osu Taiko Beatmap Image Converter: Setting')
        self.ui_setting.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.ui_setting.setStyleSheet(self.style_box)
        self.ui_setting.setGeometry(self.x()+int(self.width()/2)-500,self.y()+int(self.height()/2)-75,1000,150)
        
        self.setting_layout = QtWidgets.QFormLayout(self.ui_setting)
        #
        self.setting_first_line_widget=QtWidgets.QWidget()
        self.setting_first_line_layout=QtWidgets.QHBoxLayout(self.setting_first_line_widget)

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

        self.setting_first_line_layout.addWidget(self.setting_one_bar_w_label)
        self.setting_first_line_layout.addWidget(self.setting_one_bar_w_line_edit)
        self.setting_first_line_layout.addWidget(self.setting_one_bar_h_label)
        self.setting_first_line_layout.addWidget(self.setting_one_bar_h_line_edit)

        #
        self.setting_second_line_widget=QtWidgets.QWidget()
        self.setting_second_line_layout=QtWidgets.QHBoxLayout(self.setting_second_line_widget)

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

        self.setting_second_line_layout.addWidget(self.setting_bar_num_in_one_cut_label)
        self.setting_second_line_layout.addWidget(self.setting_bar_num_in_one_cut_line_edit)
        self.setting_second_line_layout.addWidget(self.setting_merge_mode_label)
        self.setting_second_line_layout.addWidget(self.setting_merge_mode_box)
        #
        self.setting_cancel_btn=QtWidgets.QPushButton(self.ui_setting)
        self.setting_cancel_btn.setText(f'{BUTTON_TEXT_1_SPACE*34}Cancel{BUTTON_TEXT_1_SPACE*34}')
        self.setting_cancel_btn.setStyleSheet(self.style_btn)
        self.setting_cancel_btn.clicked.connect(lambda:self.destroy_and_update_setting_window('cancel'))

        self.setting_change_btn=QtWidgets.QPushButton(self.ui_setting)
        self.setting_change_btn.setText(f'Change')
        self.setting_change_btn.setStyleSheet(self.style_btn)
        self.setting_change_btn.clicked.connect(lambda:self.destroy_and_update_setting_window('change'))

        #
        self.setting_layout.addRow(self.setting_first_line_widget)
        self.setting_layout.addRow(self.setting_second_line_widget)
        self.setting_layout.addRow(self.setting_cancel_btn,self.setting_change_btn)
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

    def resizeEvent(self,event):
        width, height = event.size().width(), event.size().height()
        self.main_box.setGeometry(0,0,width,height)
        
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