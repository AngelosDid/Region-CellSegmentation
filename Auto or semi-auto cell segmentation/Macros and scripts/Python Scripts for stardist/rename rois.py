
## This code Finds and Renames (in a separate folder) ROI files based on an ascending order. The names of ROIS given by the Stardist are not sorted hence they must
## be changed. The input has to be a folder which contains all other folders, each one containing all ROIS of the respective image.
## Hierarchy -> Main Directory -> Subdirectories -> .ROI files in each subdirectory.

from shutil import copy
from itertools import cycle, islice 
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from os import listdir, mkdir
from os.path import isfile, join, isdir, exists

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

def Save_Subdirectories_Paths_List(chsn_path) :
        global subfolders_in_dir
        list_with_all_subdirs = [chsn_path+'/'+file for file in listdir(chsn_path) if isdir(join(chsn_path, file))]    # creates a list with all subdirectories in str format
        if len(list_with_all_subdirs) == 0 :
            return False 
        else :
           subfolders_in_dir = list_with_all_subdirs                                                                   # in this case, a list_with_all_subdirs will be created


def Select_Main_Roi_Directory ():                                                                                      # directory that has subdirectories (as many as the images) that contain the ROI files
    """Prompts the user to select a main directory and saves a list with all subdirectories' paths if the correction is right"""
    def select_directory():
        global chosen_path
        chosen_path = filedialog.askdirectory(title='Select Main Folder with ROI folders')
        if Save_Subdirectories_Paths_List(chosen_path) == False :
            message = 'Your selected Directory does not contain subdirectories. Please Try again'
            Showmessages(msg_type='error', title='Wrong Folder', message=message)
        else :                                                                                                          # in this case, a list_with_all_subdirs will have been created
            root.destroy()
    root = Tk()
    root.title ('Main Folder Selection')
    root.resizable(True,True)
    root.geometry('300x200')
    DirButton = Button(root,text='Locate main ROI folder', command=select_directory).place(x=75,y=80)
    root.mainloop()

def Select_Output_Roi_Directory ():                                                                                     # directory that has subdirectories (as many as the images) that contain the ROI files
    """Prompts the user to select an output directory where the ROIS will be saved"""
    def select_out_directory():
        global chosen_output
        chosen_output = filedialog.askdirectory(title='Select Output Folder')
        if chosen_output == chosen_path :  
            message = 'The input and output folders are the same. Please try again.'                                                             # if the input selection is same as the output :
            Showmessages(msg_type='error',title='Wrong Selection', message=message)
        else :
            root.destroy()
    root = Tk()
    root.title ('Main Output Folder Selection')
    root.resizable(True,True)
    root.geometry('300x200')
    DirButton = Button(root,text='Locate Output Folder', command=select_out_directory).place(x=75,y=80)
    root.mainloop()


def Create_Output_Subdirectories (subdirs) :
    """Will create empty subdirectories with the names of the subdirectories of the main input directory"""
    for subdir_pth in subdirs:
        start_index = subdir_pth.rfind('/')
        folder_name = subdir_pth[start_index:]
        mkdir(chosen_output+'/'+folder_name)
        

def Rename_ROI_files_Ascending_Order (subdirs):
    """Input subdirs : list with paths of subdirectories as strings"""
    for subdirectory_path in subdirs:
        strt_indx = subdirectory_path.rfind('/')
        subdirname = subdirectory_path[strt_indx:]

        for number_name, roifile in enumerate (listdir(subdirectory_path)) :
            if roifile[-3:] == 'roi' :
                copy_path = subdirectory_path+'/'+roifile 
                paste_path = chosen_output+'/'+subdirname+'/'+str(number_name+1)+'.roi'                      # +1 to avoid starting from 0 , because measurements also dont start from 0 in csv files created by fiji
                copy(copy_path,paste_path)
            else :
                message = 'A file that was not .roi was detected. This will affect the naming'
                Showmessages(msg_type='warning', title='Non-.roi file', message=message)

        # all_rois_inside_subdir = [file for file in listdir(subdirectory_path) if file[-3:]=='roi']
    return 

  


Select_Main_Roi_Directory()
Select_Output_Roi_Directory()
Create_Output_Subdirectories(subfolders_in_dir)                                                                        # Creates empty folders within the main output folder
Rename_ROI_files_Ascending_Order(subfolders_in_dir)



None 


