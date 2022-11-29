import numpy as np
import sys

NUM = sys.argv[1]

sandy2 = np.loadtxt('sandy2.storm',skiprows = 3)

sandy_new = np.zeros((NUM,7))

for i in range(7):
    sandy_new[:,i] = np.linspace(sandy2[0,i],sandy2[1,i],num = NUM)

np.savetxt('sandy'+str(NUM)+'.storm', sandy_new, header = str(NUM)+'\n2012-10-30T00:00:00\n', comments = '')


