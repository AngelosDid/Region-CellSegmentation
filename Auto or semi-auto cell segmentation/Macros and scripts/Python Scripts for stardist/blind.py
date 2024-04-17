import random
import sys
import pickle 
from distutils.dir_util import copy_tree
from itertools import cycle, islice 
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from os import listdir, rename, chdir
from os.path import isfile, join, isdir


pythyblinders = [
    "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
    "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
    "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot", "Rattata",
    "Raticate", "Spearow", "Fearow", "Ekans", "Arbok", "Pikachu", "Raichu",
    "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina", "Nidoqueen", "Nidoran♂",
    "Nidorino", "Nidoking", "Clefairy", "Clefable", "Vulpix", "Ninetales",
    "Jigglypuff", "Wigglytuff", "Zubat", "Golbat", "Oddish", "Gloom", "Vileplume",
    "Paras", "Parasect", "Venonat", "Venomoth", "Diglett", "Dugtrio", "Meowth",
    "Persian", "Psyduck", "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine",
    "Poliwag", "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop",
    "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool",
    "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke",
    "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel",
    "Dewgong", "Grimer", "Muk", "Shellder", "Cloyster", "Gastly", "Haunter",
    "Gengar", "Onix", "Drowzee", "Hypno", "Krabby", "Kingler", "Voltorb", "Electrode",
    "Exeggcute", "Exeggutor", "Cubone", "Marowak", "Hitmonlee", "Hitmonchan",
    "Lickitung", "Koffing", "Weezing", "Rhyhorn", "Rhydon", "Chansey", "Tangela",
    "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking", "Staryu", "Starmie",
    "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar", "Pinsir", "Tauros",
    "Magikarp", "Gyarados", "Lapras", "Ditto", "Eevee", "Vaporeon", "Jolteon",
    "Flareon", "Porygon", "Omanyte", "Omastar", "Kabuto", "Kabutops", "Aerodactyl",
    "Snorlax", "Articuno", "Zapdos", "Moltres", "Dratini", "Dragonair", "Dragonite",
    "Mewtwo", "Mew", "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava",
    "Typhlosion", "Totodile", "Croconaw", "Feraligatr", "Sentret", "Furret", "Hoothoot",
    "Noctowl", "Ledyba", "Ledian", "Spinarak", "Ariados", "Crobat", "Chinchou",
    "Lanturn", "Pichu", "Cleffa", "Igglybuff", "Togepi", "Togetic", "Natu",
    "Xatu", "Mareep", "Flaaffy", "Ampharos", "Bellossom", "Marill", "Azumarill",
    "Sudowoodo", "Politoed", "Hoppip", "Skiploom", "Jumpluff", "Aipom", "Sunkern",
    "Sunflora", "Yanma", "Wooper", "Quagsire", "Espeon", "Umbreon", "Murkrow",
    "Slowking", "Misdreavus", "Unown", "Wobbuffet", "Girafarig", "Pineco", "Forretress",
    "Dunsparce", "Gligar", "Steelix", "Snubbull", "Granbull", "Qwilfish", "Scizor",
    "Shuckle", "Heracross", "Sneasel", "Teddiursa", "Ursaring", "Slugma", "Magcargo",
    "Swinub", "Piloswine", "Corsola", "Remoraid", "Octillery", "Delibird", "Mantine",
    "Skarmory", "Houndour", "Houndoom", "Kingdra", "Phanpy", "Donphan", "Porygon2",
    "Stantler", "Smeargle", "Tyrogue", "Hitmontop", "Smoochum", "Elekid", "Magby",
    "Miltank", "Blissey", "Raikou", "Entei", "Suicune", "Larvitar", "Pupitar",
    "Tyranitar", "Lugia", "Ho-Oh", "Celebi"
]

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

def Select_Directory ():                                                                                    
    def sel_dir():
        global chosen_input
        global final_paths
        chosen_input = filedialog.askdirectory(title='Select Directory to Blind')
        names_in_paths = [file for file in listdir(chosen_input) if isfile(join(chosen_input, file))]                  
        if len(names_in_paths) == 0 :
            Showmessages('error','Empty Input Directory','You need a directory that contains files')
        else :
            final_paths = names_in_paths
            aroot.destroy()
    aroot = Tk()
    aroot.title ('Select Directory to Blind')
    aroot.resizable(True,True)
    aroot.geometry('300x200')
    DirButton = Button(aroot,text='Locate Directory', command=sel_dir).place(x=75,y=80)
    aroot.mainloop()

def SelectCopyDirectoryPath():
    def sel_cp_dir():
        global copy_directory
        global safety_validation 
        copy_directory = filedialog.askdirectory(title='Select the output for renamed files')
        cppaths = [copy_directory+'/'+file for file in listdir(copy_directory) if isfile(join(copy_directory, file))]    # creates a list with all paths in str format
        dir_paths = [copy_directory+'/'+file for file in listdir(copy_directory) if isdir(join(copy_directory, file))] 
        if len(cppaths) != 0 or len(dir_paths) != 0 :
            Showmessages('error','Non-empty directory','The copy directory must be empty')
        else :
            safety_validation = True
            broot.destroy()
    broot = Tk()
    broot.title ('Select Output directory')
    broot.resizable(True,True)
    broot.geometry('300x200')
    DirButton = Button(broot,text='Locate Output', command=sel_cp_dir).place(x=75,y=80)
    broot.mainloop()


def CopyToSelectedDirectory():
    if chosen_input != copy_directory:                                                                                   # one more safety valve here to ensure that the input path differs from the path to past. Update : this safety can probably be removed now. It's obsolete.
        copy_tree(chosen_input,copy_directory)
    else:
        Showmessages('error','Same input and output directory','You have to select different folders for input and output!')


def HideTheTruth():
    """Output : a dictionary that has the name of an image as key and a name of a pokemon as value"""
    mysterious_knower = {}
    if len(pythyblinders) >= len(final_paths):
        for img_name in final_paths :
            mysterious_knower[img_name] = pythyblinders.pop()
        return mysterious_knower
    else : 
        Showmessages('error','inadequate list for blinding','Your list has to be at least as large as the number of your files')

def TransformToPokemon(blinded_dict):
    for eikoname,pokemon in blinded_dict.items():
        spcfic_pth = f"{copy_directory}/{eikoname}"
        converted_path = f"{copy_directory}/{pokemon}.tiff"
        rename(spcfic_pth, converted_path)

def AskForExtraFolder (number=0):
    ''' Input number : int representing how many times this function has been called in the past. 
    
       Asks for path that we can use to renames the files of a folder based on the names that the first files acquired following renaming. 
       This is useful in case that we have ROIs that have the same name as the images that we renamed.
       For instance : 455955.tiff was previously renamed to nidorino. The 495595.tiff.zip will be renamed to nidorino.zip
       In order to do this, we have to ask for a second folder. This is what this function does. Renaming per se will be done in another function
       '''

    verbal = {0:'Second', 1:'Third'}
    moreverbal = {0:'any', 1:'one more folder'} 
    croot = Tk()
    croot.geometry("100x100")
    choice = messagebox.askquestion(f"{verbal[number]} Blinding Based on First",f"Do you want to rename {moreverbal[number]} zip files based on your new blinded names ?") 
    croot.destroy()
    croot.mainloop()
    return choice      
    

def SelectZipDir ():                                                                                    
    droot = Tk()
    droot.title ('Blind a zip directory')
    droot.resizable(True,True)
    droot.geometry('300x200')
    zipath = filedialog.askdirectory(title='Locate zip folder to blind with same names')
    zipnames = [file[:-4] for file in listdir(zipath) if isfile(join(zipath, file))]           # test to see if there are files
    if len(zipnames) == 0  :                                                                          # If there are no files in the input, raise an error
        Showmessages('error','Empty directory','The copy directory must contain zip files. \
                     Run the program again and make sure that you empty the folder with the blinded images first \
                     to avoid comlications')
    else :
        messagebox.showwarning('Dont mess it up','You are going to rename all zip files in your selected folder. Make sure you maintain a copy of your original files before you proceed !')
        droot.destroy()
        return zipath,zipnames

    droot.mainloop()

def RenameZipsBasedOnBlinding (roispath,roisnames):
    """Based on the blinding that has already taken place, this function detects zip files with identical names as the images 
       (after ignoring the .zip extension in the name) and renames in respect to the pokemon that was used for blinding of each image.
       """
    for realname,pokemon in blinded_files.items():
        for roiName in roisnames :
            if realname == roiName :
                path_of_zip = f'{roispath}/{realname}.zip' 
                pokemon_path= f'{roispath}/{pokemon}.zip'
                rename (path_of_zip, pokemon_path)
                break




    




safety_validation = False                                                               # Because there is risk of overwriting important files, the code will stop unless safety validation turns to True.


Select_Directory()                                                                      # the list containing all paths in str format will also be created here
SelectCopyDirectoryPath()                                                               # here the user selects the path to paste the files from the select_directory 
if safety_validation == True :
    CopyToSelectedDirectory()
else : 
    Showmessages ('error', 'Safety Validation for Copy Violated',
                   'The procedure was stopped because something went wrong')
    sys.exit()
random.shuffle(pythyblinders)                                                           # we shuffle the list for randomization
blinded_files = HideTheTruth()                                                          # dictionary with blinded names as values
TransformToPokemon(blinded_files)                                                       # renames the files in the copy directory based on these values
chdir (copy_directory)                                                                  # save the pkl inside the copy directory
pickle.dump(blinded_files, open("encrypted", "wb"))                                       # will be saved in the users name
if AskForExtraFolder () == 'yes':                                                       # if the user wants to insert a second folder with zip files this time for blinding
    pathforzips,namesofzips = SelectZipDir ()                                           # then selects this folder
    RenameZipsBasedOnBlinding (pathforzips,namesofzips)
if AskForExtraFolder (1) == 'yes':                                                      # if the user wants to insert a third folder with zip files this time for blinding (because we have excluded and included zips in our pipeline)
    secpathforzips,secnamesofzips = SelectZipDir ()                                     # then selects this folder
    RenameZipsBasedOnBlinding (secpathforzips,secnamesofzips)


