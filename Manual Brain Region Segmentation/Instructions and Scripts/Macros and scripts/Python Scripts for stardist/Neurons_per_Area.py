import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from os import listdir, mkdir
from os.path import isfile, join, isdir, exists
from collections import defaultdict
import csv

def Showmessages (msg_type, title, message):
    defroot = Tk()
    defroot.geometry('10x10')
    if msg_type == 'warning':
        messagebox.showwarning(title=title, message=message)
    if msg_type == 'error':
        messagebox.showerror(title=title, message=message)
    else :
        print(f'Wrong msg_type. Must be warning or error but it was {msg_type}')
        print(type(msg_type))
    defroot.destroy() 


def Select_Main_Roi_Directory ():                                                                                      # directory that has subdirectories (as many as the images) that contain the ROI files
    """Prompts the user to select a main directory where the very final ROIs are stored."""
    def select_directory():
        global chosen_path
        chosen_path = filedialog.askdirectory(title='Select Main Folder with final ROI folders (unzipped)')
        if SaveRoiPathsAndNumbers(chosen_path) == False :                                                               # this is not smartly designed because it runs the whole function first. But doens't matter computationally.
            message = 'Your selected Directory does not contain subdirectories. Please Try again'
            Showmessages(msg_type='error', title='Wrong Folder', message=message)
        else :                                                                                                          # in this case, a list_with_all_subdirs will have been created
            root.destroy()
    root = Tk()
    root.title ('Main Folder Selection')
    root.resizable(True,True)
    root.geometry('300x200')
    RoiDirButton = Button(root,text='Locate main ROI folder (unzipped)', command=select_directory).place(x=75,y=80)
    root.mainloop()



def SaveRoiPathsAndNumbers(chsn_path) :
    """ Input chsn_path : str indicating the path where the main ROI folder is.
        Output 1 -> list_with all_subdirs : str indicating the specific path for each subdirectory in the main ROI folder
        Output 2 (global) ->  Roinfo : dictionary with subdir names as keys and a list with 
        [number of neurons(int)] as value. Later on, more info will be added to the list. 
        
    """
    
    list_with_all_subdirs = [chsn_path+'/'+file for file in listdir(chsn_path) if isdir(join(chsn_path, file))]    # creates a list with all subdirectories paths in str format
    global Roinfo
    if len(list_with_all_subdirs) == 0 :
        return False 
    else :
        Roinfo = defaultdict(lambda: [None,None,None])                                           
        for path in list_with_all_subdirs :
            last_slash = path.rfind("/")
            roi_folder_name = path[last_slash+1:]
            path_length = len(listdir(path))
            Roinfo[roi_folder_name][0] = path_length 
        return list_with_all_subdirs 



def Select_Background_Measurement ():                                                                                      # directory that has subdirectories (as many as the images) that contain the ROI files
    """Prompts the user to select a main directory where the very final ROIs are stored."""
    def select_bg_directory():
        global chosen_bg_path
        chosen_bg_path = filedialog.askdirectory(title='Select Main Folder with csv background measurements')
        if VerifyCsvDetection(chosen_bg_path) == None :                                                               # this is not smartly designed because it runs the whole function first. But doens't matter computationally.
            message = 'Your selected Directory does not contain csv files. Please Try again'
            Showmessages(msg_type='error', title='Wrong Folder', message=message)
        else :                                                                                                          # in this case, a list_with_all_subdirs will have been created
            root.destroy()
    root = Tk()
    root.title ('Main CSV Folder with background measurements')
    root.resizable(True,True)
    root.geometry('300x200')
    BgDirButton = Button(root,text='Locate main csv folder', command=select_bg_directory).place(x=75,y=80)
    root.mainloop()


def VerifyCsvDetection(chsn_background_path):
    """Checks whether csv filse are included in the selected directory. Needs a minimum of one to return True"""
    for verifile in listdir(chsn_background_path):
        if verifile[-3:] == 'csv':
            return True
            

def LocateAreaFromBackgroundMeasurements(chsn_dir):
    """ Input chsn_dir : str indicating the path of the folder with the background csv measurements of a region (not cell)
        Input Roinfo (global) : dictionary with file name as key and a list with [number of neurons(int),None,None] as value.
        Output         : dictionary with file name as key and a list with [number of neurons(int), area of region(int),None] as value
    
        Reads the Area column from background measurements for each image and appends it as an element to the list of Roinfo
        To achieve so, it looks for a key in the Roinfo with the same name as the csv file, without the csv extension.
        """
    
    for bgfile in listdir(chsn_dir):
        if bgfile[-3:] == 'csv':
            respective_in_Roinfo = bgfile[:-4]                      # Replaces the csv filename to make it match with the folder name that has been used for key in the Roinfo(Roinfo). 
            complete_path = chsn_dir +"/"+ bgfile
            try :
                bgdf= pd.read_csv(complete_path)
            except FileNotFoundError:
                print(f'WARNING : The path {complete_path} doesnt exist or isnt a csv file. Check your folders extensions and whether they end to .tif or .tiff ')
            else : 
                areasize = bgdf['Area'][0]
                try :
                    Roinfo[respective_in_Roinfo][1] = areasize
                except KeyError:                                   #if the match between the Roinfo keys and the csv filename cannot be done. 
                    print("WARNING : The converted name of csv to tiff does not match with any of the Roinfo keys")
                    

def SelectNucleiMeasurementsDirectory ():                                                                                      # directory that has subdirectories (as many as the images) that contain the ROI files
    """Output (global) : str indicating a directory where nuclei/cell measurements are stored
    Prompts the user to select a main directory where the fiji measurements (e.g area, mean gray valeu) are stored."""
    def select_measure_directory():
        global measurement_path
        measurement_path = filedialog.askdirectory(title='Select Folder with nuclei/cell csv measurements')
        if VerifyCsvDetection(measurement_path) == False :                                                               # this is not smartly designed because it runs the whole function first. But doens't matter computationally.
            message = 'Your selected Directory does not contain csv files. Please Try again'
            Showmessages(msg_type='error', title='Wrong Folder', message=message)
        else :                                                                                                          # in this case, a list_with_all_subdirs will have been created
            root.destroy()
    root = Tk()
    root.title ('CSV measurements Folder')
    root.resizable(True,True)
    root.geometry('300x200')
    MeasureDirButton = Button(root,text='Locate folder with Fiji measurements', command=select_measure_directory).place(x=75,y=80)
    root.mainloop()   


def GetAverageIntensity(mpath):
    """ Input mpath            : str indicating the path of the folder with the nuclei/cell csv measurements of stardist predictions
        Input Roinfo (global)  : dictionary with file name as key and a list with [number of neurons(int), area of region(int),None] as value
        Output                 : dictionary with file name as key and a list with [number of neurons(int), area of region(int),mean gray value(float)] as value
    Looks through all nuclei/cell measurement csv file and gets the average mean gray value of the cells.
    It is crucial to run a last nuclei measurement AFTER you run the manual.ijm and have manually corrected your ROIs"""          
    
    for mfile in listdir(mpath):
        if mfile[-3:] == 'csv':
            same_as_Roinfo = mfile[:-4]                      # Replaces the csv filename to make it match with the folder name that has been used for key in the Roinfo(Roinfo). 
            full_path = mpath +"/"+ mfile
            try :
                dfmeasures= pd.read_csv(full_path)
            except FileNotFoundError:
                print(f'WARNING : The path {full_path} doesnt exist or isnt a csv file. Check your folders extensions and whether they end to .tif or .tiff ')     
            else :
                average_intensity = dfmeasures['Mean'].mean()
                try :
                    Roinfo[same_as_Roinfo][2] = average_intensity
                except KeyError:                                   #if the match between the Roinfo keys and the csv filename cannot be done. 
                    print("WARNING : The converted name of csv to tiff does not match with any of the Roinfo keys")




Select_Main_Roi_Directory()
subdir_paths = SaveRoiPathsAndNumbers(chosen_path)                 # Roinfo is also created here. It has by default 3 None values inside a list. The Number of detected cells/nuclei replaces the first None value.
Select_Background_Measurement()
LocateAreaFromBackgroundMeasurements(chosen_bg_path)               # Roinfo is updated with background mean gray value here (2nd element)
# SelectNucleiMeasurementsDirectory ()
# GetAverageIntensity(measurement_path)

                                                                   # save as xlsx
finaldf = pd.DataFrame.from_dict(Roinfo)
finaldf.index =['N of objects','Area', 'Intensity']
path_final = 'C:/Users/anacfil/Desktop'
finaldf.to_excel(r'C:/Users/anacfil/Desktop/20240307_Sophie.xlsx', header=True,
             sheet_name='Animals IDs & measurements') 





