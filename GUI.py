from app import main_func
import os
from PyQt5 import QtGui, QtWidgets, QtCore
import sys
from os import startfile


#global variable
WIDTH=1000
HEIGHT=180
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

        #style sheet
        self.style()
        
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
            background:#1f1f1f;
            border:1px solid #000;
            font-size:18px;
            color:#ffffff;
            font-family:Verdana;
            border-color:#1f1f1f;
            margin:1px
        '''
        
    def start_ui(self):
        self.main_box = QtWidgets.QWidget(self)
        self.main_box.setGeometry(0,0,self.width_,self.height_)
        self.main_box.setStyleSheet(self.style_box)

        self.main_layout = QtWidgets.QFormLayout(self.main_box)
        #

        self.chosse_osu_file_btn=QtWidgets.QPushButton(self)
        self.chosse_osu_file_btn.setText(f'{BUTTON_TEXT_1_SPACE}Choose .osu file{BUTTON_TEXT_1_SPACE}')
        self.chosse_osu_file_btn.setStyleSheet(self.style_btn)
        self.chosse_osu_file_btn.clicked.connect(self.open_osu_file)

        self.osu_file_name_label = ScrollLabel(self)
        self.osu_file_name_label.setStyleSheet(self.style_box)
        
        #

        self.output_setting_btn=QtWidgets.QPushButton(self)
        self.output_setting_btn.setText(f'{BUTTON_TEXT_1_SPACE}Output Setting{BUTTON_TEXT_1_SPACE}')
        self.output_setting_btn.setStyleSheet(self.style_btn)
        self.output_setting_btn.clicked.connect(self.open_setting_window)
        #
        self.convert_btn=QtWidgets.QPushButton(self)
        self.convert_btn.setText(f'{BUTTON_TEXT_1_SPACE}Convert{BUTTON_TEXT_1_SPACE}')
        self.convert_btn.setStyleSheet(self.style_btn)
        self.convert_btn.clicked.connect(self.start_convert)
        self.convert_btn.setEnabled(False)

        #
        self.main_layout.addRow(self.chosse_osu_file_btn,self.osu_file_name_label)
        self.main_layout.addRow(self.output_setting_btn)
        self.main_layout.addRow(self.convert_btn)

    def open_osu_file(self):
        osu_file_path , filterType = QtWidgets.QFileDialog.getOpenFileName(filter='OSU (*.osu)')
        s=osu_file_path.split('/')
        self.osu_file_folder_path=""
        i=0
        while i<len(s)-1:
            self.osu_file_folder_path+=s[i]
            self.osu_file_folder_path+='/'
            i+=1
        self.osu_file_name=s[i]
        if osu_file_path !="":
            self.osu_file_name_label.setText(osu_file_path)
            self.convert_btn.setEnabled(True)

    def start_convert(self):
        main_func(self.osu_file_folder_path,self.osu_file_name)

    def open_setting_window(self):
        pass
        
# class for scrollable label
class ScrollLabel(QtWidgets.QScrollArea):
 
    # constructor
    def __init__(self, *args, **kwargs):
        QtWidgets.QScrollArea.__init__(self, *args, **kwargs)
 
        # making widget resizable
        self.setWidgetResizable(True)
 
        # making qwidget object
        content = QtWidgets.QWidget(self)
        self.setWidget(content)
 
        # h box layout
        lay = QtWidgets.QFormLayout(content)
 
        # creating label
        self.label = QtWidgets.QLabel(content)
 
        # setting alignment to the text
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
 
        # making label multi-line
        #self.label.setWordWrap(True)
 
        # adding label to the layout
        lay.addRow(self.label)
 
    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Form = MyWidget()
    Form.show()
    sys.exit(app.exec_())