import os
file = ''
ar = []
arInMes = []
f = open(os.path.abspath('./unit1/task' + file), 'rb')
for line in f:
    ar.append(line)
for number in range((min(len(ar), len(arInMes)))):
    if ar != arInMes:
        print(ar[])
