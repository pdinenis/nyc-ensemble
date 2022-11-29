for i in range(4000,8000):
    try:
        with open('storm-surge/holland80-amr2/%04d_log.txt'%i, 'r') as f:
            last_line = f.readlines()[-1]
        if last_line[-22:-1]=="DUE TO TIME LIMIT ***":
            print(i)
    except:
        pass

