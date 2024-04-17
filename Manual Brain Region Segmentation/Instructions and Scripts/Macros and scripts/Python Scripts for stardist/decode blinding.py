import pickle 
import pandas as pd
import pickle 
from shutil import copy
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from os import listdir, rename, chdir
from os.path import isfile, join, isdir

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

def Select_File ():                                                                                    
    root = Tk()
    root.resizable(True,True)
    root.geometry('300x200')
    root.title ('Select the encrypted pickle file ')
    chosen_input = filedialog.askopenfilename(title='Locate the encrypted pickle file')                 
    root.destroy()
    return chosen_input

def DirectoryToUnblind ():                                                                                    
    def sel_dir():
        global final_names
        global chosen_unblindinput
        chosen_unblindinput = filedialog.askdirectory(title='Select Directory to Unblind')
        names_in_paths = [file for file in listdir(chosen_unblindinput) if isfile(join(chosen_unblindinput, file))]                  
        if len(names_in_paths) == 0 :
            Showmessages('error','Empty Directory','You need a directory that contains files')
        else :
            final_names = names_in_paths
            aroot.destroy()
    aroot = Tk()
    aroot.title ('Select Directory to Unblind')
    aroot.resizable(True,True)
    aroot.geometry('300x200')
    DirButton = Button(aroot,text='Directory to unblind', command=sel_dir).place(x=100,y=80)
    aroot.mainloop()


def SelectOutputDirectory ():                                                                                    
    def sel_outdir ():
        global chosen_output
        chosen_output = filedialog.askdirectory(title='Select Directory to copy Unblinded Results')
        names_in_paths = [file for file in listdir(chosen_output) if isfile(join(chosen_output, file))]                  
        if len(names_in_paths) != 0 :
            Showmessages('error','Non-Empty Directory','You need an output directory that is empty')
        else :
            broot.destroy()
    broot = Tk()
    broot.title ('Select Directory to copy Unblinded Results')
    broot.resizable(True,True)
    broot.geometry('300x200')
    secDirButton = Button(broot,text='New unblinded directory', command=sel_outdir).place(x=100,y=80)
    broot.mainloop()




def CreateUnblindedFiles (unblind_dict):
    """Input unblind_dict : Dictionary that has real filenames as keys and a pokemon str as values

       Creates new unblinded files in a new directory that has been previously selected.
      """

    file_extension_start_index = final_names[0].rfind('.')
    file_extension = final_names[0][file_extension_start_index:]
    for realname,pokemon in unblind_dict.items():
        pokemon+=file_extension
        for pokname in final_names :
            if pokemon == pokname :
                src_path = f'{chosen_unblindinput}/{pokemon}'      #this is the path of the blinded image
                paste_path= f'{chosen_output}/{realname}'          # this is where the unblinded will be created
                copy (src_path, paste_path)
                break


pickle_with_info = Select_File()
DirectoryToUnblind()
SelectOutputDirectory()
with open(pickle_with_info, 'rb') as file:
    loaded_dict = pickle.load(file)
    informativedf = pd.DataFrame([loaded_dict])
    informativedf.to_csv('decrypted.csv')
    CreateUnblindedFiles(loaded_dict)




None;