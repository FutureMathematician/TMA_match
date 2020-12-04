import pandas as pd
import re
import html
import json
import my_own_handy_functions as mf

data = pd.read_stata('trademark.dta')
data_nodup = data.drop_duplicates(['or_name'], keep='first', inplace=False) 
list_name = list(data_nodup['or_name'])
list_id = list(data_nodup['rf_id'])

#clean list_raworg_nodup and change to lower case
list_cleanorg = []
for i in range(0, len(list_name)):
    raw_name = list_name[i]
    # this unescape takes care most of the "&"
    clean_name = html.unescape(raw_name)
    # some exceptions below
    if '&Circlesolid;' not in clean_name and '&thgr;' not in clean_name and '&dgr;' not in clean_name:
        list_cleanorg.append(clean_name.lower())
    else:
        clean_name = clean_name.replace('&Circlesolid;', ' ')
        clean_name = clean_name.replace('&thgr;', 'o') #'\u03B8', actually should be 'o'
        clean_name = clean_name.replace('&dgr;', '-') # '\u03B4', actually should be '-'
        list_cleanorg.append(clean_name.lower())

# take care of char ";"
checkfmt = re.compile(r'\d+;') # at least one digit followed by a ";"
for i in range(0, len(list_cleanorg)):
    name = list_cleanorg[i]
    match = re.search(checkfmt, name, flags=0)
    if match:
        name = name.replace(match.group(0), '')
        list_cleanorg[i] = name

# These are stuff need to take care
err_fmt = ['f;vis', ';3m', ';bri', 'hô ;', 'sil;verbrook', 'el;ectronics', 'people;s', 's;p.a.', 'co;,']
crr_fmt = ['vis'  , '3m' , 'bri' , 'hô'  , 'silverbrook' , 'electronics' , 'people\'s','s.p.a.', 'co,' ]

for i in range(0, len(list_cleanorg)):
    name = list_cleanorg[i]
    for j in range(0, len(err_fmt)):
        err = err_fmt[j]
        crr = crr_fmt[j]
        if err in name:
            newname = name.replace(err, crr)
            list_cleanorg[i] = newname

post = r"( |\()a corp.*of.*$" # take care of "a corp... of..."
post_re = re.compile(post)
for i in range(0, len(list_cleanorg)):
    name = list_cleanorg[i]
    newname = post_re.sub('',name)
    list_cleanorg[i] = newname



# change ., to space
for i in range(0, len(list_cleanorg)):
    name = list_cleanorg[i]
    if '.,' in name:
        newname = name.replace('.,', ' ')
        list_cleanorg[i] = newname

##### below to find x.x.x.x.x.x.x from 10 x(s) to 3 x(s) #####################
def find_pattern(name):
    for i in range(10,1,-1):
        temp_re = re.compile('\\b(\\w)' + i*'\\.(\\w)\\b')
        m = re.search(temp_re, name)
        if m:
            print(name)
            print(m.group(0))
            return m.group(0)

def fix_pattern(name, i): # i from 10 to 1
    temp_re = re.compile('\\b(\\w)' + i*'\\.(\\w)\\b') # means x.x.x... (from 11x to 2x)
    m = re.search(temp_re, name)
    if m:
        new_re = ''.join(ele for ele in ['\\' + str(j) for j in range(1, i+1+1)])
        # for example, when i = 5, new_re = r"\1\2\3\4\5\6"
        newname = temp_re.sub(new_re, name)
        return newname
    else:
        return name

n = 0
for i in range(0, len(list_cleanorg)):
    name = list_cleanorg[i]
    newname = list_cleanorg[i]
    for n_x in range(10, 0, -1):
        newname = fix_pattern(newname, n_x)
    if newname != name:
        n+=1        
        list_cleanorg[i] = newname

#begin to take care of {} 

match_re = re.compile(r"{.*over.*\((.)\)}")

n = 0

for i in range(0, len(list_cleanorg)):
    name = list_cleanorg[i]
    m = re.search(match_re, name)
    if m:
        if m.group(1) == ' ':
            replace_char = ''
        else:
            replace_char = m.group(1)
        newname = re.sub(match_re, replace_char, name)
        list_cleanorg[i] = newname
        n+=1

#clean every char to correct ones   
list_cleanorg_afcharc=[]

garbage = []
for i in range(0, 33):
    garbage.append(chr(ord('\x80') + i))

garbage.append('\xad')

# dict_replace gives the correct char to replace the old one
with open('dict_char_replace.json', 'r') as f:
    dict_replace = json.load(f)

for i in range(0, len(list_cleanorg)):
    name = list_cleanorg[i]
    newchar_list = []
    if i in [466501, 494280, 664974]:
        continue;
    for char in name:
        if char == "\"":
            newchar_list.append("")
        elif char in garbage:
            newchar_list.append("")
        elif char != ' ':
            newchar_list.append(dict_replace[char])
        else:
            newchar_list.append(' ')
    newname = ''.join(newchar for newchar in newchar_list)
    list_cleanorg_afcharc.append(newname)

dot2replace_re = re.compile(r"(\. )|\.$|^\.") # dot space or dot at the end of the string or dot at beg
for i in range(0, len(list_cleanorg_afcharc)):
    name = list_cleanorg_afcharc[i]
    newname = dot2replace_re.sub(' ', name)
    list_cleanorg_afcharc[i] = newname 

white0 = r" +" # >=1 whitespace 
white0_re = re.compile(white0)
for i in range(0, len(list_cleanorg_afcharc)):
    name = list_cleanorg_afcharc[i]
    newname = white0_re.sub(' ', name)
    list_cleanorg_afcharc[i] = newname

white1 = r"^ | $" # begin or end with whitespace
white1_re = re.compile(white1)
for i in range(0, len(list_cleanorg_afcharc)):
    name = list_cleanorg_afcharc[i]
    newname = white1_re.sub('',name)
    list_cleanorg_afcharc[i] = newname

# take care of u s, u s a
usa_re = re.compile(r"\b(u) \b(s) \b(a)\b")
us_re = re.compile(r"\b(u) \b(s)\b")
for i in range(0, len(list_cleanorg_afcharc)):
    name = list_cleanorg_afcharc[i]
    newname = usa_re.sub('usa', name)
    newname = us_re.sub('us', newname)
    list_cleanorg_afcharc[i] = newname

# take care of "a l'energie"
temp_re = re.compile(r"\ba *l'* *energie")
for i in range(0, len(list_cleanorg_afcharc)):
    name = list_cleanorg_afcharc[i]
    newname = temp_re.sub("a l'energie", name)
    list_cleanorg_afcharc[i] = newname



###save pickle
dict_raw2new = {}
for i in range(0, len(list_name)):
    rawname = list_name[i]
    newname = list_cleanorg_afcharc[i]
    dict_raw2new.update({rawname: newname})

mf.pickle_dump(dict_raw2new, 'dict_pv_raw2new')

dict_new2raw = {}
for i in range(0, len(list_name)):
    rawname = list_name[i]
    newname = list_cleanorg_afcharc[i]
    if newname not in dict_new2raw:
        dict_new2raw[newname] = {rawname}
    else:
        dict_new2raw[newname].update({rawname})    

mf.pickle_dump(dict_new2raw, 'dict_pv_new2raw')
