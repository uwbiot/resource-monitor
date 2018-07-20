import os

df = os.popen("df -h /")
i = 0
data = {}

while i<3:
    i = i + 1
    line = df.readline()
    if i==1:
        desc = line.split()[0:6]
    if i==2:
        info = line.split()[0:6]

print desc
print info
for i in range(0, 5):
    print 'Disk_{0} :'.format(desc[i]) + info[i]
info = {}
