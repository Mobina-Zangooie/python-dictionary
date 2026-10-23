
import tkinter as tk
import json
import os
import requests
# Import the Image tool from the Pillow library (it opens and converts pictures)
# from PIL import Image
import sys

# # Open the png icon (the name is relative, so run this file from the project folder)
# image = Image.open('app_icon.png')
# # Save it in ICO format with several sizes so Windows can pick the right one
# image.save('app_icon.ico', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])

# ---------- Color constants ----------
# Defined once here so every widget uses the same palette
EVERGREEN = '#344C3D'   # window and frame background
MOSS = '#73BA6E'        # buttons
SAGE_HINT = '#BFCFBB'   # text cursor color inside the entry
SAGE = '#8EA58C'        # entry and result label background

# ---------- Path constants ----------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DICTIONARY_WORDS_PATH = os.path.join(BASE_DIR, 'dictionary_words.json')
# BROKEN_DICTIONARY_WORDS_PATH = os.path.join(BASE_DIR, 'broken_dictionary_words.json')
# ICON_PATH = os.path.join(BASE_DIR, 'app_icon.png')

# ---------- Path constants ----------
# get 'frozen' attribute from sys, if not exist return False
if getattr(sys, 'frozen', False) :
    # Running as an .exe made by PyInstaller
    RESOURCE_DIR = sys._MEIPASS                  # folder of the bundled files (icon)
    DATA_DIR = os.path.dirname(sys.executable)   # folder next to the .exe file
else :
    # Running normally (VS Code or terminal)
    RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = RESOURCE_DIR

ICON_PATH = os.path.join(RESOURCE_DIR, 'app_icon.png')
DICTIONARY_WORDS_PATH = os.path.join(DATA_DIR, 'dictionary_words.json')
BROKEN_DICTIONARY_WORDS_PATH = os.path.join(DATA_DIR, 'broken_dictionary_words.json')
URL = 'https://api.mymemory.translated.net/get'

# ---------- Text constants ----------
INTERNET_LABEL_TEXT ="از اینترنت، کلمه هنوز ذخیره نشده"                  

# ---------- Data ----------
# Initial dictionary, used when dictionary_words.json does not exist or is broken
# English word (key) -> Persian meaning (value)
default_words = {'book' : 'کتاب', 'horse' : 'اسب', 'stone' : 'سنگ',
         'banana' : 'موز', 'door' : 'در', 'yellow' : 'زرد',
         'red' : 'قرمز', 'sea' : 'دریا', 'window' : 'پنجره',
         'ant' : 'مورچه', 'lake' : 'دریاچه', 'wind' : 'باد',
         'grass' : 'چمن', 'tree' : 'درخت', 'cloud' : 'ابر',
         'green' : 'سبز', 'hill' : 'تپه', 'friend' : 'دوست',
         'grape' : 'انگور', 'meat' : 'گوشت', 'far' : 'دور',
         'cat' : 'گربه', 'mother' : 'مادر', 'near' : 'نزدیک',
         'car' : 'ماشین', 'father' : 'پدر', 'happy' : 'شاد',
         'dog' : 'سگ', 'fruit' : 'میوه', 'sad' : 'غمگین',
         'monkey' : 'میمون', 'ice' : 'یخ', 'girl' : 'دختر',
         }

# ---------- Logic ----------
def pre_processing(eng_word) :
    """Return the word without outer spaces and in lower case."""
    
    # word pre processing
    eng_word = eng_word.strip()   # remove spaces from both ends
    eng_word = eng_word.lower()   # make it lowercase so 'Cat' matches 'cat'
    
    return eng_word
    
def translate(eng_word) :
    """Return the Persian meaning of an English word using the dictionary or internet,
    otherwise None."""
    
    # word pre processing
    eng_word = pre_processing(eng_word)
    
    # get() returns the default message (here is None) if the word is not in the dictionary 
    persian_word = words.get(eng_word)
    
    # Search online if english word is not in the dictionary
    if eng_word not in words :
        persian_word = online_translate(eng_word)

    return persian_word

def on_translate(event=None) :
    """Read the entry, translate the word and show the result.
    
    The event parameter lets this function work both as a button command
    (no argument) and as a key binding (tkinter passes an event object).
    """
    
    user_word = dic_entry.get()   # text currently typed in the entry
    
    from_internet = False 
    
    if pre_processing(user_word) not in words : # Not exists in the dictionary
        from_internet = True
    
    result = translate(user_word)
    
    # show the result in the label
    
    if result is None : # Searched online but couldn't find the translation
        hide_internet_widgets()
        result_label.config(text='ترجمه پیدا نشد')
        return  

    elif from_internet : # Show the online translation
        global online_translation
        online_translation = (pre_processing(user_word), result)
        show_internet_widgets()
        result_label.config(text=result)   
           
    else : # English word exists in the dictionary
        hide_internet_widgets()
        result_label.config(text=result)   
    
def  on_clear() :
    """Empty the entry and the result label and internet widgets"""
    
    dic_entry.delete(0, tk.END)        # delete from the first to the last character
    result_label.config(text='')
    hide_internet_widgets()

def other_persian_chars(persian_sentence) :
    """Return True if every character is a letter or a half space (U+200C)."""
    
    persian_words = persian_sentence.split() 
    
    for persian_word in persian_words :
        for char in persian_word :
            # Letters and the half space are allowed, anything else is not
            if not char.isalpha() and char != '\u200c' :
                return False
    
    return True

def other_eng_chars(eng_sentence) :
    """Return True if every character is a letter, an apostrophe or a hyphen."""
    
    eng_words = eng_sentence.split() 
    
    for eng_word in eng_words :
        for char in eng_word :
            # Letters, apostrophe and hyphen are allowed, anything else is not
            if not char.isalpha() and char not in ['\'', '-'] :
                return False
    
    return True   
     
def check_validity(sentence, chars_ok) :
    """Return True if all characters are allowed and the text has at least one letter."""
    
    # The sentence includes forbidden characters
    if not chars_ok :
        return False
    
    # An empty text is never valid
    if sentence == '' :
        return False 
    
    # A text with no letters at all (for example only '-') is not valid
    if not any(char.isalpha() for char in sentence) :
        return False
    
    return True 
   
def on_add() :
    """Validate the two entries and add the new word to the dictionary.
    
    Shows one of three messages: the word already exists, the word was
    added, or the input is invalid.
    """
    
    # Read english and persian entries
    eng_word = eng_entry.get()
    persian_word = persian_entry.get()
    
    # Pre process the inputs (lower case only for the English word)
    eng_word = pre_processing(eng_word)
    persian_word = persian_word.strip()
    
    # Check that each text only has allowed characters
    persian_chars_ok = other_persian_chars(persian_word)
    eng_chars_ok = other_eng_chars(eng_word)
    
    # Check both inputs with the same helper function
    persian_validity = check_validity(persian_word, persian_chars_ok)
    eng_validity = check_validity(eng_word, eng_chars_ok)
    
    clear_delay = 2000
    # Case 1: the English word is already in the dictionary
    if eng_word in words :
        add_result_label.config(text='این کلمه از قبل در دیکشنری وجود دارد')
    
    # Case 2: both inputs are valid, so add the word, save it and clear the entries
    elif persian_validity and eng_validity:
        words[eng_word] = persian_word
        saving_result = save_words()
        if saving_result :
            add_result_label.config(text='کلمه به دیکشنری شما اضافه شد')
        else :
            add_result_label.config(text='ذخیره در فایل ناموفق و در دیکشنری موفق')
            clear_delay = 3000
        eng_entry.delete(0, tk.END)  
        persian_entry.delete(0, tk.END)      
    
    # Case 3: invalid input (the entries are kept so the user can fix them)
    else :
        add_result_label.config(text='لطفا ورودی معتبر وارد کنید')
    
    # Clear the message after some seconds (some ms); no parentheses, so it runs later
    add_result_label.after(clear_delay, clear_add_result_label)  

def save_words() :
    """Write the words dictionary to dictionary_words.json.
    
    Return True if the file was saved, or False if saving failed
    (for example when the file is read-only or the disk is full).
    """
    
    try:
            with open(DICTIONARY_WORDS_PATH, 'w', encoding='utf-8') as f:
                # Here file is open
                # indent=2 writes the data on multiple lines
                json.dump(words, f, ensure_ascii=False, indent=2)
            # Here file is already closed  
            
    except OSError:
        return False
    return True    
    
def load_words() :
    """Return the dictionary saved in dictionary_words.json.
    
    If the file does not exist, return a copy of default_words.
    If the file is broken, store the broken file and return a copy of default_words.
    """
    
    try :
        with open(DICTIONARY_WORDS_PATH, 'r', encoding='utf-8') as f:
            # Here file is open
            saved_words = json.load(f)
        # Here file is already closed 
           
    except FileNotFoundError :
        return default_words.copy()   # copy, so default_words never changes
    
    except json.JSONDecodeError:
        os.replace(DICTIONARY_WORDS_PATH, BROKEN_DICTIONARY_WORDS_PATH)
        return default_words.copy()
    
    return saved_words
  
def clear_add_result_label() :
    """Empty the message label under the add button."""
    
    add_result_label.config(text='')

def online_translate(eng_word) :
    '''Return the persian meaning of the english word using the internet
    Other wise return None.'''

    # pre processing the english word
    eng_word = pre_processing(eng_word)
    
    # Check the validity of the english word
    eng_chars_ok = other_eng_chars(eng_word)
    eng_validity = check_validity(sentence=eng_word, chars_ok=eng_chars_ok)
    
    if eng_validity :
        
        parameters = {'q' : eng_word, 'langpair' : 'en|fa'}
    
        try : 
          response = requests.get(URL, params=parameters, timeout=5)
    
        # ConnectionError and Timeout   
        except requests.exceptions.RequestException : 
            return None
    
        if response.status_code == 200 : # Successful
        
            # The translation of the english word
            try :
                translated = response.json()['responseData']['translatedText']
                translated = translated.strip()
        
            # response.json() => JSONDecodeError => ValueError
            # ResponseData has a None or not a dictionary value  
            except (ValueError, KeyError, TypeError) :
                return None
        
            # checking the validity of the translation
            chars_ok = other_persian_chars(translated)
            validity = check_validity(translated, chars_ok)
        
            if validity and translated != eng_word and translated != '' :
                return translated
                
    return None

def show_internet_widgets() :
    '''Shows the internet label(with its original text) and the save button.'''
    
    internet_label.config(text=INTERNET_LABEL_TEXT, bg=SAGE_HINT, fg=EVERGREEN)
    save_button.pack(side='left', pady=10, padx=(5,0))

def hide_internet_widgets() :
    '''Hides the internet label and the save button.'''   
    
    internet_label.config(bg=EVERGREEN, fg=EVERGREEN)
    save_button.pack_forget()
    global online_translation
    online_translation = None

def on_save() :
    '''Saves the online translation into the dictionary and the JSON file.'''
    
    if online_translation is None :
        return
    
    eng_word, persian_word = online_translation # Unpack the tuple
    
    # The word was added meanwhile(for example from the add section),
    # So don't overwrite its meaning
    if eng_word in words : 
        internet_label.config(text='این کلمه از قبل در دیکشنری وجود دارد')
        
    else :
        # Add to the dictionary
        words[eng_word] = persian_word
        
        # Save to the JSON file
        if save_words() :
            internet_label.config(text='کلمه به دیکشنری شما اضافه شد')
        
        else :
            internet_label.config(text='ذخیره در فایل ناموفق و در دیکشنری موفق')
    
    # Reset the state
    dic_entry.delete(0, tk.END)
    result_label.config(text='')   
    save_button.pack_forget()

# Global variable
online_translation = None
  
# Load the saved words once, when the program starts
words = load_words()
                    
# ---------- Window setup ----------
window = tk.Tk()

window.title('دیکشنری')

window.geometry('400x600')

# Set the window icon
icon = tk.PhotoImage(file=ICON_PATH)
window.iconphoto(True, icon)

window.config(bg=EVERGREEN)   # window background color

# ---------- Labels ----------
# Title label at the top of the window
welcome_label = tk.Label(window,
                         text="دیکشنری انگلیسی به فارسی من",
                         fg='white', bg=EVERGREEN,
                         font=('vazir', 16, 'bold'),
                         )
welcome_label.pack(pady=(20, 0))

# Instruction label right below the title
label = tk.Label(window,
                 text="یک کلمه انگلیسی بنویسید",
                 fg='white', bg=EVERGREEN,
                 font=('vazir', 12))
label.pack()

# ---------- Entry and translate button ----------
# Create and place a frame for the entry and translate button
frame1 = tk.Frame(window, bg=EVERGREEN)
frame1.pack()

# Entry where the user types the English word
dic_entry = tk.Entry(frame1,
                     width=15,
                     bg=SAGE, fg='white',
                     insertbackground=SAGE_HINT,   # color of the blinking cursor
                     font=('vazir', 14),
                     justify='center')
# ipady adds extra internal space to the top and bottom of the box 
dic_entry.pack(side='left', pady=(20,10), padx=(0,15), ipady=4) 

# Pressing Enter inside the entry does the same as clicking the translate button
dic_entry.bind('<Return>', on_translate)

# Put the cursor in the entry as soon as the program starts
dic_entry.focus()

translate_button = tk.Button(frame1,
                             width=10,
                             text='ترجمه',
                             bg=MOSS, fg='white',
                             font=('vazir', 14),
                             command=on_translate)   # no parentheses: call it on click, not now
translate_button.pack(side='left', pady=(20,10), padx=(15,0))

# ---------- Result Label ----------
# Label that displays the Persian meaning
result_label = tk.Label(window,
                        width=28,
                        text="",
                        fg='white', bg=SAGE,
                        font=('vazir', 14),
                         )
result_label.pack(pady=10, ipady=4)

# ---------- Clear and Save to dictionary button ----------
# Create and place a frame for the buttons
button_frame = tk.Frame(window, bg=EVERGREEN)
button_frame.pack()

# Button that clears the entry and the result
clear_button = tk.Button(button_frame,
                             width=8,
                             text='پاک کن',
                             bg=MOSS, fg='white',
                             font=('vazir', 14),
                             command=on_clear)
clear_button.pack(side='left', pady=10, padx=(0,25))

# Button that saves the translated word into dictionary
save_button = tk.Button(button_frame,
                        width=16,
                        text='ذخیره در دیکشنری',
                        bg=MOSS, fg='white',
                        font=('vazir', 14),
                        command=on_save)

# ---------- Internet Label ----------
# Label that indicates we searched into internet
internet_label = tk.Label(window,
                         text=INTERNET_LABEL_TEXT,
                         fg=EVERGREEN, bg=EVERGREEN,
                         font=('vazir', 12, 'bold'),
                         )
internet_label.pack(pady=10, ipady=4, ipadx=4)

# ---------- Add section ----------
# Title of the add-word section, aligned to the right (east) side
add_label = tk.Label(window,
                     text="افزودن کلمه جدید",
                     fg='white', bg=EVERGREEN,
                     font=('vazir', 12),
                     justify='right')
add_label.pack(anchor= 'e', pady=10, padx=40)

# ---------- English to Persian entries ----------
# Create and place a frame for the labels of entries
frame2 = tk.Frame(window, bg=EVERGREEN)
frame2.pack()

# Small hint above the English entry
eng_label = tk.Label(frame2,
                     text='کلمه انگلیسی را وارد کنید',
                     fg='white', bg=EVERGREEN,
                     font=('vazir', 10))
eng_label.pack(side='left', anchor='w', padx=(0,25))

# Small hint above the Persian entry
persian_label = tk.Label(frame2,
                     text='کلمه فارسی را وارد کنید',
                     fg='white', bg=EVERGREEN,
                     font=('vazir', 10))
persian_label.pack(side='left', anchor='e')

# Create and place a frame for the entries
frame3 = tk.Frame(window, bg=EVERGREEN)
frame3.pack()

# Entry for the new English word
eng_entry = tk.Entry(frame3,
                     width=13,
                     bg=SAGE, fg='white',
                     insertbackground=SAGE_HINT,   # color of the blinking cursor
                     font=('vazir', 14),
                     justify='center')
eng_entry.pack(side='left', pady=(0,10), padx=(0,6), ipady=4) 

# Entry for its Persian meaning
persian_entry = tk.Entry(frame3,
                     width=13,
                     bg=SAGE, fg='white',
                     insertbackground=SAGE_HINT,   # color of the blinking cursor
                     font=('vazir', 14),
                     justify='center')
persian_entry.pack(side='left',pady=(0,10), padx=(6,0), ipady=4)

# Button that adds user's input to the dictionary
add_button = tk.Button(window,
                       width=15,
                       text='افزودن به دیکشنری +',
                       bg=MOSS, fg='white',
                       font=('vazir', 12),
                       command=on_add)
add_button.pack(pady=10)

# Label that shows the result of adding to the dictionary
add_result_label = tk.Label(window,
                        width=28,
                         text="",
                         fg='white', bg=EVERGREEN,
                         font=('vazir', 14))
add_result_label.pack(ipady=4)

# Keep the window open and listen for events (clicks, key presses, ...)
window.mainloop()
