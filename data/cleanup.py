import pandas as pd

df = pd.read_csv (r'labeled_excerpts.csv')

def removerange(a, b, lens, labels, (sub,sub2)):
    c = []
    inb = True
    for i in range(len(lens)):
        if(inb and lens[i]>a):
            inb = False
            c += [i]
        elif((not inb) and lens[i]>b):
            c += [i]
            break
    return [lens[:c[0]]+lens[c[1]:], labels[:c[0] - 1]+[(sub,sub2,a,b)]+labels[c[1]:]]

a = [] #All of model data; a list of lists which are each of the model data form.
b = raw_input("Which TOS?")#TEMP: Test on one TOS at a time
sitedf = df[df['slug'] == b]
tokenlist = {}
full = ""
with open(b+".txt", "r") as g:
    full = g.read()
    tokenlistb = full.splitlines()
    lens = [sum(map(len,tokenlistb[:i])) for i in range(len(tokenlistb) + 1)]
    tokenlist = [{"token":tokenlistb[i], "start":lens[i], "end":lens[i+1]-1} for i in range(len(tokenlistb))]
    full = "".join(full.split('\n'))

labels = [('','') for i in range(len(tokenlistb))]

#sub = label, iterate over all
#sub2 = its class_id

for i, row in sitedf.iterrows():
    sub = row['excerpt']
    sub2 = row['class_id']
    ind = full.index(sub)
    lens, labels = removerange(ind, ind + len(sub), lens, labels, (sub, sub2))


c = [{"token":full[lens[i]:lens[i+1] - 1], "labels":[{"text":labels[i][0], "start":labels[i][2], "end":labels[i][3], "class_id":labels[i][1]}]} for i in range(len(labels))]

print(c)
