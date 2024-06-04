# REMIND THE USER THAT THERE SHOULD BE NO GAPS (SPACEBARS) IN THE NAMES OF THE IMAGES

# REMIND THE USER THAT THERE SHOULD BE NO GAPS (SPACEBARS) IN THE NAMES OF THE IMAGES

import pandas as pd 
from shutil import copy
from itertools import cycle, islice 
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from os import listdir, mkdir
from os.path import isfile, join, isdir, exists
from read_roi import read_roi_file                                              #in the StardistAll environment
from read_roi import read_roi_zip                                               #in the StardistAll environment
from shapely.geometry import Polygon
import roifile
import sys
import datetime




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

def Save_Zip_Paths_List(chsn_path) :
        """ Input chsn path : str indicating the path of a main directory
            Output          : list with all zip paths inside the main directory in string format.
            
            Will save subdirectories that each one contains a set of ROI files in zip format. Not the paths of the ROIs themselves."""
        
        list_with_all_subdirs = [chsn_path+'/'+file for file in listdir(chsn_path) if file[-3:]=='zip']    # creates a list with all subdirectories in str format
        if len(list_with_all_subdirs) == 0 :
            return False 
        else :
           return list_with_all_subdirs 

def Select_Roi_Directory (order):                                                                                      # directory that has subdirectories (as many as the images) that contain the ROI files
    """ Input row : int indicating if the function has been called for the selection of the first channel or the selection of the second
        Output    : The output is not in return form but as a change in the which_list dictionary value for a specific order key. 
                    This value is list with all zip paths in string format.
        Prompts the user to select a main directory and saves a list with all zip paths if the selection is right.
        These are the zip files that contain ROI files inside. Not the paths of the ROIs themselves"""
    which_time = {1:'First', 2:'Second'}
    def select_directory():
        chosen_path = filedialog.askdirectory(title=f'Select {which_time[order]} Main Folder with zip files containing ROIs')
        if Save_Zip_Paths_List(chosen_path) == False :
            message = 'Your selected directory does not contain zip files. Please Try again.'
            Showmessages(msg_type='error', title='Wrong Folder', message=message)
        else :
            rois_list = Save_Zip_Paths_List(chosen_path)                                                                                                         # in this case, a list_with_all_subdirs will have been created
            root.destroy()
            which_list[order] = rois_list
    root = Tk()
    root.title (f'{which_time[order]} Main Folder Selection')
    root.resizable(True,True)
    root.geometry('300x200')
    DirButton = Button(root,text=f'Locate {which_time[order]} main ROI folder', command=select_directory).place(x=75,y=80)
    root.mainloop()

def Match_Rois_From_Different_Channels (first_c,second_c,distinctnames) :
    """Input first_c       : List with paths for zip files containing rois
       Input second_c      : List with paths for zip files containing rois
       Input distinctnames : The part of the filename that the user has pointed out as disctinct between the two channels (see distinct_word->output of User_Input_Declare_Name_Difference)
       Output              : List with tuples. Each tuple has paths for zip files containing rois. These two paths correspond to the same image but another channel """
    
    nameone,nametwo = distinctnames                                        # distinct parts of the name for one channel and another (see distinct_word tuple)
    list_tuple_paths = []                                            
    for fpath in first_c :                                                 # iterate through all zip paths for one channel, let's say zchannel1
                                                                           # a try : can be added here in future. The problem is that the user might not see it. So I deliberately leave it
        lastslash = fpath.rfind('/') + 1                                   # The path of the two channels will never be the same because the zip files are in different directories. So we are looking only at the final directory, which follows the last slash in the path
        shortpath = fpath[lastslash:]                                      # i.e  the 'C:/Users/angdid/Desktop/BLAcfosRois/425538_20x-03-zchannel1-Bregma146.zip' has become '425538_20x-03-zchannel1-Bregma146.zip' 
        same_path_in_sechannel = shortpath.replace(nameone,nametwo)        # For instance, zchannel1 has 425568-zchannel1-bregmaX and we look for 425568-zchannel2-bregmaX in zchannel 2. We replace the 2 with 1 to test if they match
        for spath in second_c:                                               
            seclastslash = spath.rfind('/') + 1   
            secshortpath = spath[seclastslash:]
            if same_path_in_sechannel == secshortpath :
                list_tuple_paths.append((fpath,spath))
    return list_tuple_paths


    
def User_Input_Declare_Name_Difference ():
    """ Global outputs 
        distinct word  : tuple with str indicating the part that differs between the names of rois of channel 1 and 2.

    Prompts the user to write the part that differs in the name between rois of channel 1 and rois of channel 2. Eg we have zchannel1 or zchannel2 in a larger name that is otherwise identical
"""
    
    def Entry_fields():
        global distinct_word
        distinct_word    = tuple(e1.get().strip().split(','))                                                                       # declares the word that differs
        master.destroy()

    master = Tk()
    textword = "Type the part of the name that distinguishes the two channels.For instance : '42-zchannel1-BregmaX' and '42-zchannel2-BregmaX' differ in 'zchannel1'.  " 
    textword2 = "Type both versions (i.e. zchannel1 and zchannel2) with a comma (no spacebars) :"
    Label(master, text=textword,font=("Arial", 11)).grid(row=0)
    Label(master, text=textword2,font=("Arial", 11)).grid(row=1)
    e1 = Entry(master)
    e1.insert(0,'zchannel1,zchannel2')
    e1.grid(row=0, column=1)
    Button(master,text='Ready!', command=Entry_fields).grid(row=3,column=1, sticky=W,pady=4)
    master.mainloop()


def User_Input_Declare_Intersection ():
    """ Global outputs 
        intersection: str indicating which channel (based on one element of the distinct word tuple) will be the 'smaller' one. For instance, we look how much of cfos is colocalising (is inside) NeuN and not vice versa.
        percentage  : int indicating minimum percentage of intersection between two channels in order to consider colocalization.

    For description read the global outputs description above
"""
    
    def Inter_fields():
        global intersection
        global percentage
        intersection = eone.get().strip()                                # strip to get rid of spacebars
        percentage = float(etwo.get().strip().replace('%',''))                                                                                              
        mastertwo.destroy()

    mastertwo = Tk()
    text = f'Type the name ({distinct_word[0]} or {distinct_word[1]}) of the channel that you want to locate inside another.'
    text2 = f"For instance, if {distinct_word[0]} is cfos (only nucleus) and {distinct_word[1]} is NeuN(all cytoplasm), then you should type {distinct_word[0]} "
    textpercentage = f"Type the minimum accepted percentage of intersection between {distinct_word[0]} and {distinct_word[0]} ∩ {distinct_word[1]}"
    textpercentage2 = f"for an overlap to be considered as colocalization"
    
    Label(mastertwo, text=text,font=("Arial", 11)).grid(row=0)
    Label(mastertwo, text=text2,font=("Arial", 11)).grid(row=1)
    Label(mastertwo, text=textpercentage,font=("Arial", 11)).grid(row=2)
    Label(mastertwo, text=textpercentage2,font=("Arial", 11)).grid(row=3)

    eone = Entry(mastertwo)
    eone.insert(0,f'{distinct_word[0]} OR {distinct_word[1]}')
    eone.grid(row=1, column=1)
    etwo = Entry(mastertwo)
    etwo.insert(0,'80%')
    etwo.grid(row=3, column=1)
    Button(mastertwo,text='Ready!', command=Inter_fields).grid(row=4,column=1, sticky=W,pady=4)
    mastertwo.mainloop()


def Select_Save_Directory ():                                                                                      # directory that has subdirectories (as many as the images) that contain the ROI files
    """Prompts the user to select a main directory where the excel file with overlap counts will be stored."""
    def select_excel_dir():
        global excel_path
        excel_path = filedialog.askdirectory(title='Select Folder to Save your results')
        if isdir(excel_path) :
            exroot.destroy()                                                             # this is not smartly designed because it runs the whole function first. But doens't matter computationally.
        else :                                                                                                          # in this case, a list_with_all_subdirs will have been created
            message = 'It seems that you have not selected a directory. Please Try again.'
            Showmessages(msg_type='error', title='Wrong Path', message=message)
    exroot = Tk()
    exroot.title ('Save Folder Selection')
    exroot.resizable(True,True)
    exroot.geometry('300x200')
    exDirButton = Button(exroot,text='Select where to save', command=select_excel_dir).place(x=75,y=80)
    exroot.mainloop()


def CreateExcel (dict_with_rois) :
    """Input dict_with_rois : See output of Count_Overlaps ().
       Dict with filenames as keys and list with [overrois,total large neurons] as values.
       overrois itself is a dictionary that has filenames of single rois (usually numbers) as keys. It only has the keys that
       overlap significantly based on users cutoff criterion. Values of overrois are roi type information that can be translated back to roi.
        
       Creates an excel file with the overlaps """
    
    new_dict = {}
    for key, val in dict_with_rois.items():
        roirelated = val[0]                                                             # this is the overrois in the input
        totall     = val[1]                                                             # this is the total large neurons in the input
        new_dict[key] = [len(roirelated.keys()),totall]                                 # we are just isolating the keys of the overrois, which are practically the roi filenames that overlap significantly. We only take the number of them. Then we take the number of total       
    df = pd.DataFrame.from_dict(new_dict)  
    df.index =['Colocalized','Total of the other channel']
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M").replace(":","_")                               # i.e 2024-01-16 12_54     Meaning that it was created in 16th of January of 2024 at 12:54
    df.to_excel(f'{excel_path}/Colocalization of {intersection} ∩ to other channel--{now}.xlsx', header=True,
             sheet_name=f'At least {percentage}% colocalization')

def Recreate_Rois (coloca_rois):
    """Input dict_with_rois : See output of Count_Overlaps ().
       Dict with filenames as keys and list with [overrois,total large neurons] as values.
       overrois itself is a dictionary that has filenames of single rois (usually numbers) as keys. It only has the keys that
       overlap significantly based on users cutoff criterion. Values of overrois are roi type information that can be translated back to roi.
        
    Creates a directory with folders that contain the roi intersection of overlapping channels (only these that have surpassed the minimum cutoff percentage as set by the user) """

    mainfoldpath = f'{excel_path}/Intersections rois'
    mkdir(mainfoldpath)
    for SET_roikey,SET_roival in coloca_rois.items():
        imagepath = f'{mainfoldpath}/{SET_roikey}'
        mkdir(imagepath)                                                                              # create folder with the filename of the zip file (practically the image name)
        allroinfo = SET_roival [0]
        for polygroi in allroinfo.keys():
            if polygroi == "tuple":
                pass 
            else :
                allroinfo[polygroi].tofile(f'{imagepath}/{polygroi}.roi')
                

    
    
    




def Count_Overlaps () :
    """Output : Dict with filenames as keys and list with [overrois,total large neurons] as values.
       overrois itself is a dictionary that has filenames of single rois (usually numbers) as keys. It only has the keys that
       overlap significantly based on users cutoff criterion. Values of overrois are roi type information that can be translated back to roi -> https://pypi.org/project/roifile/#examples"""

    def ReadZip (mtchd_zpaths):
        """ Input: List with tuples that comprise paths for two zip files containing rois. Every two paths correspond to the same image but another channel.
            Output : Dictionary that has zip filenames as keys(for channels 1 & 2, separately). Value is an ordered dict with all information about ROIs + a new key called tuple.
                     This key has the names of the coupled rois (same image but different channels). This key is used later on, in EstimateOverlaPercentage().
            Reads the roi files that are inside a zip file"""
        all_roinfo_per_zip = {}
        for couple_of_zipaths in mtchd_zpaths :
            chnl1_slash_index = couple_of_zipaths[0].rfind('/') + 1                                  # we shorten the name from whole path to only what's following the last slash / of the path
            cnl1_nameonly    = couple_of_zipaths[0][chnl1_slash_index:]
            chnl2_slash_index = couple_of_zipaths[1].rfind('/') + 1 
            cnl2_nameonly    = couple_of_zipaths[1][chnl2_slash_index:]
            all_roinfo_per_zip[cnl1_nameonly] = read_roi_zip(couple_of_zipaths[0])
            all_roinfo_per_zip[cnl2_nameonly] = read_roi_zip(couple_of_zipaths[1])
            all_roinfo_per_zip[cnl1_nameonly]['tuple'] = (cnl1_nameonly,cnl2_nameonly)               # A 'tuple' key is created that has the names of the coupled rois (same image but different channels) 

        return all_roinfo_per_zip
    
    def FindUsersOption():
        """ Input : global variable intersection 
            Input2: global variable matched_zipaths
            Output: tuple (translated index corresponding to user's selection as first element, the other index as second)
            This is based on the global variable 'intersection' which is created in User_Input_Declare_Intersection.
            Locates if the user's selection (eg zchannel2) is in the first(index 0) or second (index 1) element of the tuples
            inside the matched_zipaths variable."""
    
        single_case = matched_zipaths[0]
        for idx, one_path in enumerate(single_case):
            if intersection in one_path :
                translated_user_selection = idx                                                          # index where the users word is located inside the tuple
                break
        
        if translated_user_selection == 0 :
            larger_channel = 1 
        elif translated_user_selection == 1 :
            larger_channel = 0 

        return (translated_user_selection,larger_channel)

    def CreateTupleWithAllinfo (name_of_file):
        """ Input name_of_file : str representing a zip filename.
            Global input       : zip_and_info
        Output : Tuple with all information (ordered dict) for the rois for both channels (each channel representing one element)"""
        try :
            bothnames = zip_and_info[filename]['tuple']                                                   # the tuple has the filenames of both matching zip files. It exists only in half of files (those from first channel)
        except KeyError:
            return False                                                                                  # False if there is no key tuple is inside the information. (It only exists in half of the files)
        else :
            infone_chanel     = zip_and_info [bothnames[0]]                                               # all information that we get reading a roi file (orderedict), including the x and z coordinates for channel 1  
            inftwo_chanel     = zip_and_info [bothnames[1]]                                               # all information that we get reading a roi file (orderedict), including the x and z coordinates for channel 2  
            tupledinformation = (infone_chanel,inftwo_chanel)
            print(bothnames)
            return tupledinformation


    def EstimateOverlaPercentage (rois,user_intersection_selection,larger_channel):
        """Input rois           : tuple with two orderded dicts with all information about a roi. 
                                  Keys of these dicts are the names of each roi file inside a zip file (usually just numbers)
                                  Each one of these keys includes (among other things) also two dicts.
                                  One dict is called 'x' and has coordinates for x as values. Same for the dict called 'y'
           Input intersection   : int. The translated user's input as to which channel we overlay on top of the other 
           Input larger_channel : int. The translated user's input of the channel that has larger ROIs (i.e. NeuN instead of cfos)
           
           Output 1 (already_overlapped) : Dictionary that has filenames of single rois (usually numbers) as keys. It only has the keys that
                                           overlap significantly. Values are roi type information that can be translated back to roi -> https://pypi.org/project/roifile/#examples                
           Output 2: total larger       : The total number of rois of the channel with the 'larger' objects """

        smaller_chinfo = rois[user_intersection_selection]                                                 # by smaller we just mean the rois of the channel with the smaller object
        larger_chinfo  = rois[larger_channel]
        already_overlapped= {}

        for roinumber in smaller_chinfo.keys():
            if roinumber == 'tuple':                                                                       # the tuple was inserted along with the keys (filenames of single rois). We want to skip this.
                continue
            if smaller_chinfo [roinumber]['type'] != 'polygon' :
                print(f'WARNING: The roi {roinumber} in  {filename}  could not be analyzed because it is not a polygon')
                continue              
            smallX_coords = smaller_chinfo [roinumber]['x']
            smallY_coords = smaller_chinfo [roinumber]['y']
            small_neuron = Polygon(list(zip(smallX_coords,smallY_coords)))
            small_neuron_area = small_neuron.area
            for big_roinumber in larger_chinfo:                                                           
                if big_roinumber in already_overlapped.keys():                                             # THIS CAN BE altered if the user allows overlap of many small objects inside one. Here though, if the bigger neuron has successfuly overlapped with another, it's not tested for a second time.
                    continue
                if big_roinumber == 'tuple':
                    continue                                                                               # the tuple was inserted along with the keys (filenames of single rois). We want to skip this.
                bigX_coords = larger_chinfo [big_roinumber] ['x']
                bigY_coords = larger_chinfo [big_roinumber] ['y']
                big_neuron = Polygon(list(zip(bigX_coords,bigY_coords)))
                try :
                    overlapolygon = small_neuron.intersection(big_neuron)
                except  :                                                                                  # This is explained in the stardist training steps word file. If the polygon is not drawn correctly this error might occur. Normally, the except name is GEOSException but it yields error and it is complicated to import it. Keep an eye on that. Error could be anything.
                    print(f' WARNING : The roi {roinumber} is probably a polygon drawn improperly. It cannot be analyzed')
                else :
                    overlapolygon_area = overlapolygon.area
                    if overlapolygon_area == 0 :
                        continue
                    else :
                        colocalization_percentage = (overlapolygon_area/small_neuron_area) * 100 
                        if colocalization_percentage >= percentage:                                                 # percentage is a global variable defined by the user 
                            intersect_roiformat = roifile.ImagejRoi.frompoints(list(zip(bigX_coords,bigY_coords)))  # the colocalized part will be saved as a new roi format type
                            already_overlapped[big_roinumber] = intersect_roiformat 
        
        total_larger = len([key for key in larger_chinfo.keys() if key != 'tuple'])                       # Total number of roi files/objects/neurons in the channel with the larger objects
        return already_overlapped,total_larger 

         
    # - - - - - -  main Count_Overlaps () code - - - - - -
    
    original_stdout = sys.stdout
    with open(f'{excel_path}/colocalization_log(inspect_for_WARNINGS).txt', 'w') as log_file:
        sys.stdout = log_file
        final_overlaprois = {}                                                                            # short filename as key and each value the output ofestimateoverlapeercentage ()
        zip_and_info = ReadZip(matched_zipaths)                                                           # Each zipath as key, all its info as ordered dict
        smaller_channel_idx,bigger_channel_dix = FindUsersOption()                                        # By smaller channel we mean the channel that the user chose that has the 'smaller' object. For instance, cfos instead of tdTomato or NeuN
        for filename in zip_and_info.keys():                                                              # We are practically iterating through the filenames
            if CreateTupleWithAllinfo(filename):                                                          # yields a tuple with all roinfo that we use as argument for the estimateoverlapercentage
                overrois,total_large = EstimateOverlaPercentage(CreateTupleWithAllinfo(filename),smaller_channel_idx,bigger_channel_dix)
                final_overlaprois[filename]= [overrois,total_large]                                       # this will be used for the creation of the excel file. Dict with filename as key and list with [number of overlaps,total small neurons]
                 
    sys.stdout = original_stdout
    return final_overlaprois





# -   -   -   -   -   -   M a i n    C o d e   -   -   -   -   -   -



which_list = {1:None,2:None}                                                                      # dictionary with int as key indicating which channel dataset is chosen. Value is a list with strings indicating subdirectories containing rois
Select_Roi_Directory (1)
Select_Roi_Directory (2)                
User_Input_Declare_Name_Difference()                                                              # the which list directory has now been enriched with lists containing subfolders in str format for both channels 1 and 2. The distinct word is also added as global variable.
User_Input_Declare_Intersection ()
matched_zipaths = Match_Rois_From_Different_Channels(which_list[1],which_list[2],distinct_word)   # List with the complete paths for every couple of zip files that have ROIs of the same image, yet for a different channel 
Select_Save_Directory ()
coloc_rois = Count_Overlaps ()
CreateExcel(coloc_rois)                                                                           # will save the file with a timestamp in the filename                                                                                              
Recreate_Rois(coloc_rois)

None;
