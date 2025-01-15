#For reading the files (only binary and txt)
def read_file(filename):
    fn = filename.rsplit(".")
    out = []
    if (fn[-1] == "txt"): #txt input
        f = open(filename)
        content = f.read()
        f.close()
        for x in content:
            hexval = format(ord(x), "x")
            if (len(hexval) < 2):
                hexval = "0" + hexval
            out.append(hexval)
    elif (fn[-1] == "bin"): #binary input
        f = open(filename, mode = "rb")
        content = f.read()
        f.close()
        for x in content:
            hexval = format(x, "x")
            if (len(hexval) < 2):
                hexval = "0" + hexval
            out.append(hexval)
    else :
        return out#No support for input file type
    #print(out)
    return out

#print(read_file("short.txt"))
#print(read_file("short-binary.bin"))

'''
Shake algorithm, here input should be the message as a list of 
hex values (excluding the 0x at the start, see format from read_file)
'''
def shake128(message): 
    out = pad(message)
    return out

#padding operation 
def pad(message):
    out = message
    to_add = 168 - (len(out) % 168)
    if (to_add == 1): #check length of message
        out.append("9F")
    else: 
        to_add -= 1
        out.append("1F")
        while (to_add != 0):
            if (to_add == 1):
                out.append("80")
            else:
                out.append("00")
            to_add -= 1
    return out

#print(pad(read_file("short.txt")))
print(pad(read_file("short-binary.bin")))
