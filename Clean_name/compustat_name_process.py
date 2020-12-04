import my_own_handy_functions as mf
import re
import pandas as pd 
import time
import json


data = pd.read_stata('compustat.dta')

data_nodup = data.drop_duplicates(['conml'], keep='first', inplace=False) 
list_gvkey = list(data_nodup['gvkey'])

#company name经常返回空值，要用Company Legal Name
# if use conm, often get null result from bing searc 
# note, have to use legal name hereh

#转化为小写字母~~~~~
list_old_conm = list(data_nodup['conml']) 

list_conm = [] #此列表存储小写公司名称
for i in range(0, len(list_old_conm)):
    name = list_old_conm[i].lower()
    list_conm.append(name)
#转化为小写字母~~~~~完毕


#### get all characters in the company names, to check abnormal cases#########
dict_clean_char = {}
for i in range(0,len(list_gvkey)): #遍历所有公司
    name = list_conm[i]  
    for char in name: #遍历公司名称的全部字母
        if char != " ":
            gvkey = list_gvkey[i]
            if char not in dict_clean_char:
                dict_clean_char[char] = [(gvkey, name)] #把新字符加入库中
            else:
                dict_clean_char[char].append((gvkey, name))
    if 1 % 5000 == 0:
        print(i)

list_char = list(dict_clean_char.keys())
list_char.sort() # 所有公司名含有的字符集
################################################################################

# dict_replace gives the correct char to replace the old one
# 将字符改成易于bing搜索的字符串
with open('dict_char_replace.json', 'r') as f:
    dict_replace = json.load(f) 

##########################################################
# 将.,改为空格
for i in range(0, len(list_conm)):
    name = list_conm[i]
    if '.,' in name:
        newname = name.replace('.,', ' ')
        list_conm[i] = newname
        
#############################################################
# below to find x.x.x.x.x.x.x from 10 x(s) to 3 x(s)
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

for i in range(0, len(list_conm)):
    name = list_conm[i]
    newname = list_conm[i]
    for n_x in range(10, 0, -1):
        newname = fix_pattern(newname, n_x)
    if newname != name:
        n+=1        
        list_conm[i] = newname

################################################################
# use dict_replace to clean every char
list_conm_afcharc = []
for i in range(0, len(list_conm)):
    name = list_conm[i]
    newchar_list = []
    for char in name:
        if char != ' ':
            newchar_list.append(dict_replace[char])
        else:
            newchar_list.append(' ')
    newname = ''.join(newchar for newchar in newchar_list)
    list_conm_afcharc.append(newname)    

# dont replace . as space, keep dot, because for .com or .net keeping them has better results for search
dot2replace_re = re.compile(r"(\. )|\.$|^\.") # dot space or dot at the end of the string or dot at beg
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = dot2replace_re.sub(' ', name)
    list_conm_afcharc[i] = newname 

white0 = r" +" # >=1 whitespace 
white0_re = re.compile(white0)
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = white0_re.sub(' ', name)
    list_conm_afcharc[i] = newname

white1 = r"^ | $" # begin or end with whitespace
white1_re = re.compile(white1)
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = white1_re.sub('',name)
    list_conm_afcharc[i] = newname

# take care of u s, u s a
usa_re = re.compile(r"\b(u) \b(s) \b(a)\b")
us_re = re.compile(r"\b(u) \b(s)\b")
for i in range(0, len(list_conm_afcharc)):
    name = list_conm_afcharc[i]
    newname = usa_re.sub('usa', name)
    newname = us_re.sub('us', newname)
    list_conm_afcharc[i] = newname

mf.pickle_dump(list_gvkey, 'list_compustat_gvkey')
mf.pickle_dump(list_old_conm, 'list_compustat_conml')
mf.pickle_dump(list_conm_afcharc, 'list_compustat_newname')

