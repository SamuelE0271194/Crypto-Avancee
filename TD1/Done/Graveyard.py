#converts hex list into binary list
def hex_to_bin(hex_list):  
    bin_list = []
    for x in hex_list:
        #print(bin(int(x, 16)))
        bin_list.append(bin(int(x, 16))[2:].zfill(8))
    out = []
    for x in bin_list:
        for bit in x[::-1]:
            if (bit == "0"):
                out.append(0)
            else:
                out.append(1) 
    return out

#converts binary to hex
def bin_to_hex(bin_list):
    hex_list = []
    byt = ""
    for x in bin_list:
        if (len(byt) != 8):
            byt = str(x) + byt
            continue
        #print(byt)
        hex_store = hex(int(byt,2)).split("x")[-1]
        if (len(hex_store) < 2):
            hex_store = "0" + hex_store
        hex_list.append(hex_store)
        byt = str(x)
    if (byt != ""):
        #print(byt)
        hex_store = hex(int(byt,2)).split("x")[-1]
        if (len(hex_store) < 2):
            hex_store = "0" + hex_store
        hex_list.append(hex_store)
    return hex_list


#reads a file (returns binary) and returns in binary
def read_file_bin(filename, in_hex = False):
    fn = filename.rsplit(".")
    out = []
    if (fn[-1] == "txt"): #txt input
        f = open(filename)
        content = f.read()
        f.close()
        
        if in_hex: #hex values seperated by a space not including 0x
            out = content.split(" ")
            if (out[-1] == ""):
                out.remove("") 
            out = hex_to_bin(out) #inversion is done here

        else: 
            for x in content:
                out.append(int(x))

    elif (fn[-1] == "bin"): #binary input
        f = open(filename, mode = "rb")
        content = f.read()
        f.close()
        for x in content:
            binval = format(x, "b")
            temp = [int(i) for i in binval]
            out += temp[::-1]
    
    else :
        return out #No support for input file type

    return out 

#test_file = "test1.txt"
#test_file = "short-binary.bin"
#test1 = read_file_bin(test_file)
#print(test1)

#padding operation input should be in binary
def pad_bits(message): #Welp i can throw this away
    out = message
    str_out = ""
    if (len(out) % 1343 != 0):
        out += [1, 1, 1, 1]
    while (len(out)%1343 != 0):
        out.append(0)
    out.append(1)
    for x in out:
        str_out += str(x)
    #print(str_out)
    return out

