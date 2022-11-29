import numpy as np

maxes = []
for i in range(81):
    gaugemaxes = []
    for j in range(1,2):
        address = 'storm-surge/holland80-amr2/'+format(i,'04d')+'_output/gauge'+format(j,'05d')+'.txt'
        print(address)
        try:     
            q = np.loadtxt(address,skiprows =3, usecols = [0,5])
            gaugemaxes.append(np.max(q[q[:,0]>4.5,1]))
        except:
            gaugemaxes.append(-1.0)
            print('i=',i,'   j=',j)
    maxes.append(gaugemaxes)

maxes = np.array(maxes)
            
with open('surge_maxes_bing.npy', 'wb') as f:
    np.save(f, maxes)
print(maxes)
print(np.max(maxes))
print(np.min(maxes))
#print(np.argmax(maxes))


