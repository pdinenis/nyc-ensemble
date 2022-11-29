import numpy as np

sandy2 = np.loadtxt('sandy2.storm',skiprows = 3)

sandy5 = np.zeros((5,7))

for i in range(7):
    sandy5[:,i] = np.linspace(sandy2[0,i],sandy2[1,i],num = 5)

np.savetxt('sandy5.storm', sandy5, header = '5\n2012-10-30T00:00:00\n', comments = '')


