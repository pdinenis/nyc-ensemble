import numpy as np
peak_t_list = []
for i in range(5000):
    try:
        address = "storm-surge/holland80-amr2/"+str(i+4000).zfill(4)+"_output/gauge00013.txt"
        q = np.loadtxt(address, skiprows = 10, usecols = [0,1,5])
        j_max = np.argmax(q[:,2])
        peak_t_list.append(q[j_max,1])
        if q[j_max,0] != 3:
            print(str(i+4000).zfill(4)+":    "+str(q[j_max,0]))
    except:
        peak_t_list.append(-1.0)
        print(str(i+4000)+":    fail")
peak_t_list = np.array(peak_t_list)
np.savetxt("peak_times.txt",peak_t_list)
