import json
import re

import pandas as pd

data_nodup = pd.read_stata('tmc.dta')

list_id = list(data_nodup['own_id'])

list_old_conm = list(data_nodup['own_name'])
list_conm = []
for i in range(0, len(list_old_conm)):
    name = list_old_conm[i].lower()  # lower case
    list_conm.append(name)

post = r"( |\()a corp.*of.*$"  # "a corp... of..."
post_re = re.compile(post)
for i in range(0, len(list_conm)):
    name = list_conm[i]
    newname = post_re.sub('', name)
    list_conm[i] = newname

# change ., to space
for i in range(0, len(list_conm)):
    name = list_conm[i]
    if '.,' in name:
        newname = name.replace('.,', ' ')
        list_conm[i] = newname

# replacce x.y.z to xyz


def fix_pattern(name, i):  # i from 10 to 1
    temp_re = re.compile(r'\b(\w)' + i*r'\.(\w)\b')  # x.x.x
    m = re.search(temp_re, name)
    if m:
        new_re = ''.join(ele for ele in ['\\' + str(j)
                                         for j in range(1, i+1+1)])
        # reverse quoation, new_re = r"\1\2\3"
        newname = temp_re.sub(new_re, name)
        return newname
    else:
        return name


for i in range(0, len(list_conm)):
    name = list_conm[i]
    newname = list_conm[i]
    for n_x in range(10, 0, -1):
        newname = fix_pattern(newname, n_x)
    if newname != name:
        list_conm[i] = newname



# clean every char to correct ones
with open('dict_char_replace.json', 'r') as f:
    dict_replace = json.load(f)

list_conm_afcharc = []
for i in range(0, len(list_conm)):
    name = list_conm[i]
    newchar_list = []
    for char in name:
        if char != ' ' and char != '\x7f':
            newchar_list.append(dict_replace[char])
        else:
            newchar_list.append(' ')
    newname = ''.join(newchar for newchar in newchar_list)
    list_conm_afcharc.append(newname)

# dont replace . as space, keep dot, because for .com or .net keeping them has better results for search
# dot space or dot at the end of the string or dot at beg
dot2replace_re = re.compile(r"\. |\.$|^\.")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = dot2replace_re.sub(' ', name)
    list_conm_afcharc[i] = newname

#ltd inc co llc
for i in range(0, len(list_conm_afcharc)):
    name0 = list_conm_afcharc[i]
    name0 = name0.replace('.ltd.', ' ltd ')
    name0 = name0.replace('.ltd', ' ltd ')
    name0 = name0.replace('ltd.', ' ltd ')
    name0 = name0.replace('.limited', ' ltd ')
    name0 = name0.replace('.inc.', ' inc ')
    name0 = name0.replace('.inc', ' inc ')
    name0 = name0.replace('inc.', ' inc ')
    name0 = name0.replace('incorporated', ' inc ')
    name0 = name0.replace('incorporation', ' inc ')
    name0 = name0.replace('.co', ' co ')
    name0 = name0.replace('co.', ' co ')
    name0 = name0.replace('company', ' co ')
    name0 = name0.replace('.llc', ' llc ')
    name0 = name0.replace('llc.', ' llc ')
    name0 = name0.replace('corp.', ' corp ')
    name0 = name0.replace('.corp', ' corp ')
    name0 = name0.replace('.corporation', ' corp ')
    name0 = name0.replace('corporation', ' corp ')
    list_conm_afcharc[i] = name0

#limited
white0_re = re.compile(r" limited$")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = white0_re.sub(' ltd', name)
    list_conm_afcharc[i] = newname


# clean extra white space
white0_re = re.compile(r" +")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = white0_re.sub(' ', name)
    list_conm_afcharc[i] = newname

# begin or end with whitespace
white1_re = re.compile(r"^ | $")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = white1_re.sub('', name)
    list_conm_afcharc[i] = newname

# take care of u s, u s a
usa_re = re.compile(r"\b(u) \b(s) \b(a)\b")
us_re = re.compile(r"\b(u) \b(s)\b")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = usa_re.sub('usa', name)
    newname = us_re.sub('us', newname)
    list_conm_afcharc[i] = newname

with open('list_tmc_id.json', 'w') as handle:
    json.dump(list_id, handle, indent=2)

with open('list_tmc_conm.json', 'w') as handle:
    json.dump(list_old_conm, handle, indent=2)

with open('list_tmc_newname.json', 'w') as handle:
    json.dump(list_conm_afcharc, handle, indent=2)
