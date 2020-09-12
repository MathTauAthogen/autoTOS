# Cleans up the data! See the Google Doc (https://docs.google.com/document/d/1Vjsw9VIRL8PDP4b7krbxwE0MRT4YMP06uGuQVYCLXdo/edit)
# Puts it in the "Model Data" format
#
#
# TODO list:
# 1. Loop over all sites

import pandas as pd
import json
import string

# Function removerange
# Inputs: a, the first index of the substring; b, the last index of the substring; lens, an array of the current indices of the tokens; labels, a current list of all of the info about the tokens.
# Output: A new lens and labels list, where lens has the combined token size and labels has all of the data about the token.
def removerange(a, b, lens, labels, (sub,sub2)):
    c = []
    inb = True
    for i in range(len(lens)):
        if(inb and lens[i]>a):
            inb = False
            c += [i]
        if((not inb) and lens[i]>b):
            c += [i]
            break
    return [lens[:c[0]]+lens[c[1]:], labels[:c[0] - 1]+[(sub,sub2,a,b)]+labels[c[1]:]]

###############################################################################################################

b = raw_input("Which TOS?")#TEMP: Test on one TOS at a time

#Initialize the Labelled Excerpts Data Table

df = pd.read_csv (r'labeled_excerpts.csv.bak')
sitedf = df[df['slug'] == b]

###############################################################################################################

tokenlist = {} # A list of all of the sentences, which are newline-separated in the input.
full = "" # The full text of the TOS of the site

with open("tos/"+b+".txt", "r") as g:
    full = g.read() #Get the full text
    printable = set(string.printable)
    full = filter(lambda x: x in printable, full)
    tokenlistb = full.splitlines() #Get a list of sentences
    lens = [sum(map(len,tokenlistb[:i]))+i+1 for i in range(len(tokenlistb) + 1)] #Find the starting index of each sentences

    full = " ".join(full.split('\n')) #Put the full text on only one line.

labels = [('','','','') for i in range(len(tokenlistb))] #Initialize something containing inner tuples that can be indexed to the same amount as the other values

#sub = label, iterate over all
#sub2 = its class_id

for i, row in sitedf.iterrows():
    sub = " ".join(row['excerpt'].split('\n'))
    sub2 = row['class_id']
    ind = full.index(sub)
    lens, labels = removerange(ind, ind + len(sub), lens, labels, (sub, sub2))

#And finish it off

c = [{"token":full[lens[i]-1:lens[i+1] - 2], "labels":[{"text":labels[i][0], "start":labels[i][2]-lens[i]+2, "end":labels[i][3]-lens[i]+1, "class_id":labels[i][1]} for j in range(i,i+1) if labels[j] != ('','','','')]} for i in range(len(labels))]

print(json.dumps(c))
