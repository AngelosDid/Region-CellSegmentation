# -*- coding: utf-8 -*-

# Note that this script treats Mean input different than the rest. It takes as Mean the information read by the dynamean.ijm macro. An empty input for all other values 
# means as a default - or + infinity. Whereas, for the minimum filed of Mean, it just means that we are not adding or subtracting anything.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QFont
from collections import defaultdict
import pandas as pd
import numpy as np
import copy
import shutil
import time


from os import listdir, mkdir
from os.path import isfile, join, isdir, exists
  


def RemoveRois():
    """Uses the global variables which are created in the SaveEntries() inside the class"""
    
    def Find_Background_Mean_Gray_Measurement ():
        """Will create a dictionary (background_mean) with the images filenames as keys and a value which will be a list containing the mean gray value and area of the isolated brain region of
        interest in each segmented image. These are values in the csv output of the dynamean.ijm macro. The mean gray value gives an 'inner' background measurement. Inner in a 
        sense that we are not taking into account the surrounding white region which is part of the image but not part of the isolated cropped brain region of interest. This
        mean gray value will be used later for filtering, either per se, or plus/minus a value that the user puts in the mean gray field. Mind that the mean gray value is rounded.
        This can be easily changed."""

        global background_mean
        background_mean = {}                                                            # dictionary with filenames as keys and mean gray and area of isolated cropped part of an image as value
        for file in listdir(dynameandir) :
            if file[-3:] == 'csv' : 
                first_tif_in_file = file.find('.tiff')                                   #Always mind if your data end with .tif or tiff. Keep the name up to the .tiff and not more. For instance, 425944.tiff.tiff.csv will be 425944.tif
                correct_name = file[:first_tif_in_file+5]
                df = pd.read_csv(f'{dynameandir}/{file}')
                meangray = round(df['Mean'][0])                                         # mind that we round the value
                meanarea = df['Area'][0]
                background_mean[correct_name] = [meangray,meanarea]
            else :
                print(f'Warning : a non-csv file was detected inside your directory for background measurements. Please inspect the file named {file} and remove it.')
                print('The program will shut down to avoid further complications')
                sys.exit()


    def Convert_to_int_or_Infinity():
        """The global values that are saved inside the class's method (see SaveEntries()) are in str format. This function converts them to float.
           Any '' values (that is, empty string) will be turned to minus or plus infinity (depending on whether they come from minimum or maximum entry fields)
           With respect to the exceptional case of Mean, a lack of input for the minimum would mean that the value is solely set based on the mean gray value 
           of the background_mean dictionary (mean gray is the first element of each value). """

        global area_double_threshold_condition                                          # if set to True, it means that the user has set a threshold for doubling cells based on area
        area_double_threshold_condition = False

        global_input_min_names    = ['Area', 'Mean', 'Mode', 'Median', 'Perim', 'Kurt', 'Round']
        global_input_max_names    = ['maxArea', 'maxMean', 'maxMode','maxMedian','maxPerim','maxKurt', 'maxRound']
        
        for variable_name in global_input_min_names :
            if variable_name in globals():
                if globals()[variable_name] == '':
                    if variable_name != 'Mean':
                        globals()[variable_name] = float('-inf')                        # Attribute minus infinity value if no input is inserted. 
                    else :                                                              # Except for the case of Mean, where lack of inputs means just take the info for the background and dont change it
                        globals()[variable_name] = 0                                    # Equals zero because that's the number that we will (later in another function) add to the mean gray value taken by the background_mean. Practically, we'll add nothing. 
                else :
                    globals()[variable_name] = float(globals()[variable_name])

        
        for var_name in global_input_max_names:
            if var_name in globals():
                if globals()[var_name] == '':
                    globals()[var_name] = float('inf')
                else :
                    globals()[var_name] = float(globals()[var_name])

        if 'Areadouble' in globals() :                                                  # This is specifically for converting the doubling threshold -which is based on the area- to float
            if globals()['Areadouble'] !='':
                globals()['Areadouble'] = float(globals()['Areadouble'])
                area_double_threshold_condition = True
            else:   
                globals()['Areadouble'] = float('inf')                                  #if nothing has been inserted to Areadouble then make it infinite so row_value (in FilterROIs()) is always smaller than it
                



    def Create_Included_Excluded_Subdirectories ():
        """Creates two subfolders inside the outputdir. One for the directories that will contain the filtered-in and one 
         for the directories that will contain the filtered-out ROIs for each file """
        final_rois_main_dir_path    = f'{outputdir}/Final_ROIs'
        excluded_rois_main_dir_path = f'{outputdir}/Excluded'
        mkdir(final_rois_main_dir_path)
        mkdir(excluded_rois_main_dir_path)
        return final_rois_main_dir_path, excluded_rois_main_dir_path
    
    def Initiate_Output_dictionaries ():
        """Will create dictionaries to :
           1) Later(!) transfer folders containing the Rejected ROIs :
           2) Later(!) Save the maximum(last) row of each csv file (in order to be able to iterate through this range in FilterROIs())
           3) Save the obsolete extension of those csv files ((in order to be able to find the csv paths in FilterROIs()))
           For 1) and 2), the key names will be based on the names of csv files. However, they will be devoid of the obsolete extension of the csv name (i.e '425944.tif instead' of '425944.tif.tiff.csv')
           For 3) an obsol_extension_csv_names dictionary is created (with the same keys as 1&2), where the obsolete name of a csv file (i.e 'tiff.csv' in 425944.tiff.tiff.csv)
           is saved.
           The reason the file names are corrected and don't include the obsolete path is because they have to match the stardist predictions' roi output."""
        
        global each_csv_max_row,rejected_dict,obsol_extension_csv_names
        each_csv_max_row = {}                                                          # every csv filename will be saved here as key (str) and the maximum (last) row of a respective csv file as a value
        rejected_dict = {}                                                             # every csv filename will be saved here as key (str) and the value is a list with ints corresponding to filtered out rows
        obsol_extension_csv_names = {}                                                 # the obsolete part of the csv name (which is taken out for each csv_max_row and rejected_dict) is saved as value here. Will be used to call the csv path in filterROIs

        for file in listdir(inputdir) :
            if file[-3:] == 'csv' : 
                first_tif_in_name = file.find('.tiff')                                  #keep the name up to the .tif5 and not more. For instance, 425944.tif.tiff.csv will be 425944.tif
                roifolder_correct_name = file[:first_tif_in_name+5]                    # + 5 to include the '.tiff' part. We want the name to stop at .tif so it matches the Roi folders later
                obsolete_extension = file[first_tif_in_name+5:]                        # the rest of the name will be saved in order to be able to retrieve the path when calling  df_file   = pd.read_csv(file_path) in filterROIs()
                each_csv_max_row[roifolder_correct_name] = float('inf')                #later on it will take the value of an int that represents the last row (number) of the csv file                                                  
                rejected_dict[roifolder_correct_name] = set()                          # we use set because we only want the excluded rows ones. If more columns in same row are surpassing criteria, doesn't matter because they are already excluded.
                obsol_extension_csv_names[roifolder_correct_name] = obsolete_extension # Key will be like 425944.tiff and value like 425944.tiff.tiff.csv if that's how the csv file is named. So, when calling from a key of rejected_dict or max_csv_row, we can add the obsolete name to track the file and call the right csv path

    def Create_Matching_Dictionary ():
        """ The role of this function is to compare expected input of columns with real input of columns and maintain only the overlapping cases, hence preventing keyerrors
            and controlling measurement inputs from the csv files.
        It create a cols_index_match dictionary which will contain only measurements that respond to the csv. The final result will be :
        {'Area':0, 'Mean':1, 'Mode':2 ...etc}. This means that the column of Area is the first one, of Mean the 2nd etc. Note that the values of these keys that signify the positions
        are obsolete, hence unecessary. In addition, the Perim. column of the csv is renamed to Perim before it's added to cols_index_match&
        Any addition of measurements to the GUI, would just require an insertion to the 
        a) cols_to_find 
        b) the GUI-related variables, 
        c) the global variable for the measurement [see SaveEntries() global variables]  
        d) the global_input_min/max_names [see Convert_to_int_or_Infinity]"""

        global cols_index_match
        cols_index_match = {}                                                       # Eventually will look like {'Area':0, 'Mean':1, 'Mode':2 ...etc} But if the developer adds or removes entry fields indexing will change. This is the purpose of that structure. To make it more flexible for additions/removals.         
        cols_to_find = ['Area', 'Mean', 'Mode', 'Perim.', 'Median', 'Kurt', 'Round']# Note that Perim. has a dot because that's how fiji names the measurement. We will get rid of it later in this function.
        all_names = [file for file in listdir(inputdir) if file[-3:] == 'csv']      # we create a list but we practically just need one file name
        single_csv_name = all_names[-1]                                             # Take the last filename as an example. We take from all_names because we know that these are csv files. This way we avoid erros due to unwanted non-csv files inside the input folder.
        csv_path = f'{inputdir}/{single_csv_name}'                                  
        df_csv      = pd.read_csv(csv_path)                                         # Open the last csv as dataframe. We assume that all results csv have the same measurements and same order.  
        
        for measurement_to_find in cols_to_find :
            user_input_list = list(df_csv.columns)                                  # list with the columns that the user has inserted. This is by default the variables from the entry fields of the software. They are sorted with a certain form, which can only change if the developer changes the input variables. 
            try :                                                                   
                right_index = user_input_list.index(measurement_to_find)            
            except :
                print(f'measuremnt {measurement_to_find} was not found')
            else :
                cols_index_match[measurement_to_find]= right_index                  # for instance 'Mean':1 or 'Mean':0 (if the area will be removed from entries in the future). The index value is obsolete. Can be removed from snippet in the future.
        
        # change Perim. to Perim                                                    This will help to associate its name directly with the global variables when we'll call it in filterRois(). The variables cannot have the dot.
        try :
            cols_index_match['Perim.']
        except :
            pass
        else : 
            perim_value = cols_index_match['Perim.']
            del cols_index_match['Perim.']
            cols_index_match['Perim'] = perim_value
    
    def FilterRois() :
        """Filters in or out ROIs based on the accepted ranges.
           For each file, it scans through columns and looks for criteria for exclusion. If such a criterion exists then the row will be discarded to a dictionary (rejected_dic)
           REGARDLESS the values in the rest of its columns. The accepted rows are not inserted in any dict. We can deduce which ones they are based on the rejected rows
           and the information of last(max) row in every file. 
           In addition, the last row of each file is saved in each_csv_max_row inside this function
           """
        
        extra_cell_counts = defaultdict(list)                                      # keys that correspond to filenames and empty list as value. Ints corresponding to row numbers will be appended here. These row numbers have an area big enough to signify that it's probably two neurons instead of one (see readoubled variable).             


        for excel_filename in rejected_dict.keys():                                    # 1) Iterate over filenames. The dictionary chosen is random. Anything containing all file names as keys is fine.
            removed_chunk = obsol_extension_csv_names[excel_filename]                  # we will place back the removed part of the csv name to be able to track the file
            file_path = f'{inputdir}/{excel_filename}{removed_chunk}' 
            df_file   = pd.read_csv(file_path)
            last_row=df_file.tail(1).index[0]                                      # save last row index to each_csv_max_row
            each_csv_max_row[excel_filename] = last_row                              

            if 'Perim.' in list(df_file.columns) : 
                df_file.rename(columns = {'Perim.':'Perim'}, inplace=True)         # Perim. changed already to Perim in Find_Measurement_Index_in_Colums(). Here we also change it for the csv file itself. 
            for column_name in cols_index_match.keys():                            # 2) Iterate over column names. Mind that we are iterating only over the columns that respond both in our input in the python code and the csv measurements
                for row_number,row_value in enumerate (df_file[column_name]):      # 3) Iterate over series 
                    row_number +=1                                                 # Because we don't want it to start from 0. Labels also don't start from 0
                    # define the minimum and maximum value
                    if column_name != 'Mean':
                        minimum_val = globals()[column_name]
                        max_val     = globals()[f'max{column_name}']              # This is why the maxnames are named after the min variables with  a max in front. So we call them easily
                    else :
                        minimum_val = globals()[column_name] + background_mean[excel_filename][0]                  # use the user input for minimum area and add it (or subtract if its minus) from the mean gray value of the cropped brain region of interest.
                        max_val     = globals()[f'max{column_name}']
                        print(f'for file {excel_filename} and row {row_number} minimum_val = {minimum_val} which is the sum of the background mean {background_mean[excel_filename][0]} and user input {globals()[column_name]}')
                        print(f'the row value is {row_value}')
                    
                    # apply the filtering
                    if minimum_val < row_value < max_val :
                        pass                                                        # we don't assign the accepted rows anywhere. Only the rejected
                        if column_name == 'Area':
                            if  Areadouble < row_value :
                                extra_cell_counts[excel_filename].append(row_number)    # the row where the big cell area (that will count as two) will be appended. This is informative but we actually care mostly about the number of elements appended.
                    else :
                        rejected_dict[excel_filename].add(row_number)                   # when a rejected row is added here, it means that all columns of the respective row will be rejected.
        










    def Paste_ROIS_To_Acccepted_OR_Rejected_Folder():
        """ Creates a folder with the name of each file in both Final_ROIs and excluded directories and pastes ROIs that pass or not the criteria, respectively"""
        for roifolder in listdir(roidir):
            mkdir(f'{outputdir}/Excluded/{roifolder}')                                                # make a folder with the file's name in the excluded directory
            mkdir(f'{outputdir}/Final_ROIs/{roifolder}')                                              # --//--   in the Final_ROIs directory
            roifolder_path = f'{roidir}/{roifolder}'
            subdir_path_inside_finalRois_folder= f'{outputdir}/Final_ROIs/{roifolder}'
            subdir_path_inside_excluded_folder = f'{outputdir}/Excluded/{roifolder}'
            try :                                                                                     # Just for validation that the names of the folders are found as keys in the names of the dictionaries that we'll use
                each_csv_max_row[roifolder]
                rejected_dict[roifolder]
            except :
                print(f'Error. {roifolder} not found in each_csv_max_row keys OR rejected_dict keys')
                print(f' printing each_csv_max_row keys for verification : {each_csv_max_row.keys()}')
                print(f' printing rejected_dict keys for verification : {rejected_dict.keys()}')

            else :
                n_of_rows = each_csv_max_row[roifolder] + 1 
                for row in range(1,n_of_rows) :                                                           # we iterate over the number of rows the csv file has (because the number of measurements done is of course the same with the number of ROIs). 
                    specific_roi_path = f'{roifolder_path}/{row}.roi'                                     # Each path corresponds to a .ROI file inside the roifolder_path. The ROIs will have been renamed to 1,2,3 etc after runing rename rois.py Therefore they should match with the numbers in the sets of accepted and rejected_dict because these numbers correspond to rows from the csv file (as defined in FilterRois())
                    specific_accepted_path = f'{subdir_path_inside_finalRois_folder}/{row}.roi'
                    specific_rejected_path = f'{subdir_path_inside_excluded_folder}/{row}.roi'
                    if row in rejected_dict[roifolder] :                                                  # This dict holds every row that has violated some criteria at least once
                        shutil.copy(specific_roi_path,specific_rejected_path)
                    else :
                        shutil.copy(specific_roi_path,specific_accepted_path)

    def Convert_Folder_to_Zip():
        """The files are so far saved as .rois inside respective folders. This function will also create zip files with the same filenames so they can be
        loaded directly in Fiji"""

        excluded_fold_path = f'{outputdir}\Excluded'
        for single_folder_name in listdir(excluded_fold_path):
            inside_folder_path  = join(excluded_fold_path, single_folder_name)                                  # This is the directory containing the rois. 
            zipfile = shutil.make_archive(f'{excluded_fold_path}\{single_folder_name}','zip',inside_folder_path)

        accepted_fol_path = f'{outputdir}\Final_ROIs'
        for single_fol_name in listdir(accepted_fol_path):
            inside_fol_path  = join(accepted_fol_path, single_fol_name)                                  # This is the directory containing the rois. 
            ziparch = shutil.make_archive(f'{accepted_fol_path}\{single_fol_name}','zip',inside_fol_path)




    def ShowFinalMessage():
        """Clears the message that tells the user to wait for the analysis before (s)he closes the main window. Gives a message saying that Analysis is finished"""
        ui.analysis_label.hide()
        ui.final_label.show()
        

    Find_Background_Mean_Gray_Measurement ()
    Convert_to_int_or_Infinity()
    Create_Included_Excluded_Subdirectories()
    Initiate_Output_dictionaries()
    Create_Matching_Dictionary()
    FilterRois()
    Paste_ROIS_To_Acccepted_OR_Rejected_Folder()
    Convert_Folder_to_Zip()
    ShowFinalMessage()
    

class Ui_MainWindow(object):
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 750)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        

        # -- set buttons -- 

        self.roi_button = QtWidgets.QPushButton(self.centralwidget)     #input for the directory with all rois
        self.roi_button.setGeometry(QtCore.QRect(570, 209, 150, 30))
        self.roi_button.setObjectName("roi_button")
        self.roi_button.clicked.connect(self.RoiDialog)

        self.input = QtWidgets.QPushButton(self.centralwidget)           #input for the measurements (csv files)
        self.input.setGeometry(QtCore.QRect(570, 259, 150, 30))
        self.input.setObjectName("input_button")
        self.input.clicked.connect(self.InputDialog)

        self.dynamean = QtWidgets.QPushButton(self.centralwidget)          # input for the measurements of the whole area of interest (csv files). Mean gray value will be later taken for each
        self.dynamean.setGeometry(QtCore.QRect(570, 309, 150, 30))
        self.dynamean.setObjectName("dynamic_mean_input_button")
        self.dynamean.clicked.connect(self.DynameanDialog)
        
        self.output = QtWidgets.QPushButton(self.centralwidget)
        self.output.setGeometry(QtCore.QRect(570, 359, 150, 30))
        self.output.setObjectName("output_button")
        self.output.clicked.connect(self.OutputDialog)

        self.ready_button = QtWidgets.QPushButton(self.centralwidget)
        self.ready_button.setGeometry(QtCore.QRect(700, 570, 155, 56))
        self.ready_button.setFont(QFont('Arial', 15))
        self.ready_button.setObjectName("ready_button")
        self.ready_button.clicked.connect(self.AfterInput)

        # -- set hidden labels  --

        #analysis_label will be initially hidden and shown only in NextDisplay()
        self.analysis_label = QtWidgets.QLabel(self.centralwidget)
        self.analysis_label.setGeometry(QtCore.QRect(60, 100, 600, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.analysis_label.setFont(font)
        self.analysis_label.setObjectName("analysis_label")
        self.analysis_label.hide()
        # analysis_label has been hidden

        # Final message will be initially hidden and shown only after all processing is completed.
        self.final_label = QtWidgets.QLabel(self.centralwidget)
        self.final_label.setGeometry(QtCore.QRect(60, 100, 600, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.final_label.setFont(font)
        self.final_label.setObjectName("final_label")
        self.final_label.hide()

        
        # -- set labels --

        self.minimum_label = QtWidgets.QLabel(self.centralwidget)
        self.minimum_label.setGeometry(QtCore.QRect(263, 20, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.minimum_label.setFont(font)
        self.minimum_label.setObjectName("minimum_label")

        self.maximum_label = QtWidgets.QLabel(self.centralwidget)
        self.maximum_label.setGeometry(QtCore.QRect(382, 20, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.maximum_label.setFont(font)
        self.maximum_label.setObjectName("maximum_label")

        self.Areadouble_label = QtWidgets.QLabel(self.centralwidget)
        self.Areadouble_label.setGeometry(QtCore.QRect(480, 20, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.Areadouble_label.setFont(font)
        self.Areadouble_label.setObjectName("minimum_label")

        self.doublexplain_label = QtWidgets.QLabel(self.centralwidget)
        self.doublexplain_label.setGeometry(QtCore.QRect(560, 55, 500, 70))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.doublexplain_label.setFont(font)
        self.doublexplain_label.setObjectName("explain_label")

        self.doublexplain2_label = QtWidgets.QLabel(self.centralwidget)
        self.doublexplain2_label.setGeometry(QtCore.QRect(560, 70, 500, 70))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.doublexplain2_label.setFont(font)
        self.doublexplain2_label.setObjectName("explain2_label")
        
        self.area_label = QtWidgets.QLabel(self.centralwidget)
        self.area_label.setGeometry(QtCore.QRect(20, 75, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.area_label.setFont(font)
        self.area_label.setObjectName("area_label")
        
        self.mean_label = QtWidgets.QLabel(self.centralwidget)
        self.mean_label.setGeometry(QtCore.QRect(20, 150, 190, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.mean_label.setFont(font)
        self.mean_label.setObjectName("mean_label")
        
        self.modal_label = QtWidgets.QLabel(self.centralwidget)
        self.modal_label.setGeometry(QtCore.QRect(20, 235, 190, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.modal_label.setFont(font)
        self.modal_label.setObjectName("modal_label")
        
        self.median_label = QtWidgets.QLabel(self.centralwidget)
        self.median_label.setGeometry(QtCore.QRect(20, 315, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.median_label.setFont(font)
        self.median_label.setObjectName("median_label")
        
        self.perim_label = QtWidgets.QLabel(self.centralwidget)
        self.perim_label.setGeometry(QtCore.QRect(20, 395, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.perim_label.setFont(font)
        self.perim_label.setObjectName("perim_label")
        
        self.kurtosis_label = QtWidgets.QLabel(self.centralwidget)
        self.kurtosis_label.setGeometry(QtCore.QRect(20, 475, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.kurtosis_label.setFont(font)
        self.kurtosis_label.setObjectName("kurtosis_label")

        self.round_label = QtWidgets.QLabel(self.centralwidget)
        self.round_label.setGeometry(QtCore.QRect(20, 555, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.round_label.setFont(font)
        self.round_label.setObjectName("round_label")
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(265, 650, 260, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        # Settings for minimum thresholds

        self.area_field = QtWidgets.QTextEdit(self.centralwidget)
        self.area_field.setGeometry(QtCore.QRect(250, 80, 61, 41))
        self.area_field.setObjectName("area_field")
        self.mean_field = QtWidgets.QTextEdit(self.centralwidget)
        self.mean_field.setGeometry(QtCore.QRect(250, 160, 61, 41))
        self.mean_field.setObjectName("mean_field")
        self.modal_field = QtWidgets.QTextEdit(self.centralwidget)
        self.modal_field.setGeometry(QtCore.QRect(250, 240, 61, 41))
        self.modal_field.setObjectName("modal_field")
        self.median_field = QtWidgets.QTextEdit(self.centralwidget)
        self.median_field.setGeometry(QtCore.QRect(250, 320, 61, 41))
        self.median_field.setObjectName("median_field")
        self.perim_field = QtWidgets.QTextEdit(self.centralwidget)
        self.perim_field.setGeometry(QtCore.QRect(250, 400, 61, 41))
        self.perim_field.setObjectName("perim_field")
        self.kurtosis_field = QtWidgets.QTextEdit(self.centralwidget)
        self.kurtosis_field.setGeometry(QtCore.QRect(250, 480, 61, 41))
        self.kurtosis_field.setObjectName("kurtosis_field")
        self.round_field = QtWidgets.QTextEdit(self.centralwidget)
        self.round_field.setGeometry(QtCore.QRect(250, 560, 61, 41))
        self.round_field.setObjectName("round_field")

        # Settings for maximum values 

        self.max_area_field = QtWidgets.QTextEdit(self.centralwidget)
        self.max_area_field.setGeometry(QtCore.QRect(370, 80, 61, 41))
        self.max_area_field.setObjectName("maxarea_field")
        self.max_mean_field = QtWidgets.QTextEdit(self.centralwidget)
        self.max_mean_field.setGeometry(QtCore.QRect(370, 160, 61, 41))
        self.max_mean_field.setObjectName("maxmean_field")
        self.max_modal_field = QtWidgets.QTextEdit(self.centralwidget)
        self.max_modal_field.setGeometry(QtCore.QRect(370, 240, 61, 41))
        self.max_modal_field.setObjectName("maxmodal_field")
        self.max_median_field = QtWidgets.QTextEdit(self.centralwidget)
        self.max_median_field.setGeometry(QtCore.QRect(370, 320, 61, 41))
        self.max_median_field.setObjectName("maxmedian_field")
        self.max_perim_field = QtWidgets.QTextEdit(self.centralwidget)
        self.max_perim_field.setGeometry(QtCore.QRect(370, 400, 61, 41))
        self.max_perim_field.setObjectName("maxperim_field")
        self.max_kurtosis_field = QtWidgets.QTextEdit(self.centralwidget)
        self.max_kurtosis_field.setGeometry(QtCore.QRect(370, 480, 61, 41))
        self.max_kurtosis_field.setObjectName("maxkurtosis_field")
        self.max_round_field = QtWidgets.QTextEdit(self.centralwidget)
        self.max_round_field.setGeometry(QtCore.QRect(370, 560, 61, 41))
        self.max_round_field.setObjectName("maxround_field")
        self.Areadouble_field = QtWidgets.QTextEdit(self.centralwidget)
        self.Areadouble_field.setGeometry(QtCore.QRect(480, 80, 61, 41))
        self.Areadouble_field.setObjectName("Areadouble_field")
        
        # Rest settings 

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 792, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def AfterInput(self): 
        """After the Ready button is pressed, this calls functions for saving the entries, clearing the main window
        as well as showing new messages while processing files. RemoveRois-which includes all subfunctions for analysis- is also called at this stage"""
        self.SaveEntries()
        self.ClearAll()
        self.NewDisplay()
        RemoveRois()


    def SaveEntries(self):
        """Saves the user's entries as global variables that will be used outside this class. 
        Note that the entries for minimum thresholds have EXACTLY the same names as the -contingent- columns of the results.csv files.
        These csv columns are the columns as named by default by ImageJ. The maximum cut-off criteria are EXACTLY the same names with a 'max' first. There are two exceptions :
        First : the Perim variable (in contrast to Perim. as imageJ names it) Second : the Areadouble that doesn't exist as a measurement in Imagej. 
        The names of these global variables help us to easilly call them while iterating over the associated column(that is, measurement). 
        For instance, when iterating over a column that has the value 'Mean', we can do  
        globals()[column_name] < some_value < globals()[f'max{column_name}'] to see if some_value is between Mean and maxMean's values. This is why the variables
        must be named exactly like the columns of csv and why variables with max must be followed by exactly the same name afterwards.
        """
        global Area, Mean, Mode, Median, Perim, Kurt, Round, maxArea, maxMean, maxMode,maxMedian,maxPerim,maxKurt, maxRound, Areadouble
        Area       = self.area_field.toPlainText().strip()
        Mean       = self.mean_field.toPlainText().strip()
        Mode       = self.modal_field.toPlainText().strip()
        Median     = self.median_field.toPlainText().strip()
        Perim      = self.perim_field.toPlainText().strip()
        Kurt       = self.kurtosis_field.toPlainText().strip()
        Round      = self.round_field.toPlainText().strip()
        maxArea    = self.max_area_field.toPlainText().strip()
        maxMean    = self.max_mean_field.toPlainText().strip()
        maxMode    = self.max_modal_field.toPlainText().strip()
        maxMedian  = self.max_median_field.toPlainText().strip()
        maxPerim   = self.max_perim_field.toPlainText().strip()
        maxKurt    = self.max_kurtosis_field.toPlainText().strip()
        maxRound   = self.max_round_field.toPlainText().strip()
        Areadouble = self.Areadouble_field.toPlainText().strip()


    def ClearAll (self):
        """Clears the mainwindow"""
        # Clear widgets 
        self.area_field.deleteLater()
        self.mean_field.deleteLater()
        self.modal_field.deleteLater()
        self.median_field.deleteLater()
        self.perim_field.deleteLater()
        self.kurtosis_field.deleteLater()
        self.round_field.deleteLater()
        self.max_area_field.deleteLater()
        self.max_mean_field.deleteLater()
        self.max_modal_field.deleteLater()
        self.max_median_field.deleteLater()
        self.max_perim_field.deleteLater()
        self.max_kurtosis_field.deleteLater()
        self.max_round_field.deleteLater()
        self.Areadouble_field.deleteLater()
        # Clear labels
        self.minimum_label.deleteLater()
        self.maximum_label.deleteLater()
        self.area_label.deleteLater()
        self.mean_label.deleteLater()
        self.modal_label.deleteLater()
        self.median_label.deleteLater()
        self.perim_label.deleteLater()
        self.kurtosis_label.deleteLater()
        self.round_label.deleteLater()
        self.Areadouble_label.deleteLater()
        self.label.deleteLater()
        self.doublexplain_label.deleteLater()
        self.doublexplain2_label.deleteLater()
        # Hide buttons
        self.roi_button.deleteLater()
        self.input.deleteLater()
        self.output.deleteLater()
        self.ready_button.deleteLater()
        self.dynamean.deleteLater()
      
    def RoiDialog(self):
        global roidir
        roidir = QFileDialog.getExistingDirectory(None, "Select main ROI directory")

    def InputDialog(self):
        global inputdir
        inputdir = QFileDialog.getExistingDirectory(None, "Select Directory with csv files")

    def DynameanDialog(self):
        global dynameandir
        dynameandir = QFileDialog.getExistingDirectory(None, "Select an output Directory")
    
    def OutputDialog(self):
        global outputdir
        outputdir = QFileDialog.getExistingDirectory(None, "Select an output Directory")

        
    
    def NewDisplay(self) :
        """New display on main window after input has been inserted. Tells the user to not close the main window."""
        self.analysis_label.show()
        

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Filter ROIs"))
        
        self.roi_button.setText(_translate("MainWindow", "Roi Folder"))
        self.input.setText(_translate("MainWindow", "Nuclei Measurements"))
        self.dynamean.setText(_translate("MainWindow", "Background Measurements"))
        self.output.setText(_translate("MainWindow", "Output Folder"))
        self.ready_button.setText(_translate("MainWindow", " R e a d y ! "))
        self.area_label.setText(_translate("MainWindow", "Area"))
        self.mean_label.setText(_translate("MainWindow", "Mean gray value"))
        self.modal_label.setText(_translate("MainWindow", "Modal gray value"))
        self.median_label.setText(_translate("MainWindow", "Median "))
        self.perim_label.setText(_translate("MainWindow", "Perimeter"))
        self.kurtosis_label.setText(_translate("MainWindow", "Kurtosis"))
        self.round_label.setText(_translate("MainWindow", "Round"))
        self.label.setText(_translate("MainWindow", "If a field is irrelevant leave blank"))
        self.analysis_label.setText(_translate("MainWindow", "Analyzing... Don't close this window!"))
        self.final_label.setText(_translate("MainWindow", "Analysis Completed! You may close this window now"))
        self.minimum_label.setText(_translate("MainWindow", "Min"))
        self.maximum_label.setText(_translate("MainWindow", "Max"))
        self.Areadouble_label.setText(_translate("MainWindow", "Double"))
        self.doublexplain_label.setText(_translate("MainWindow", "min < double < max "))
        self.doublexplain2_label.setText(_translate("MainWindow", "cells between double and max will be counted as 2 instead of 1"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

