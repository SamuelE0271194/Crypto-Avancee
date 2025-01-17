#!/usr/bin/env python3
import sys

def byt_to_hex(byt_list):
    hex_list = []
    for x in byt_list:
        hex_store = hex(int(x,2)).split("x")[-1]
        if (len(hex_store) < 2):
            hex_store = "0" + hex_store
        hex_list.append(hex_store)
    return hex_list

def hex_to_byt(hex_list):
    byt_list = []
    for x in hex_list:
        byt_store = bin(int(x, 16))[2:].zfill(8)
        byt_list.append(byt_store)
    byt_list = byt_list[::-1]
    return byt_list

def combine_hex_list(hex_list):
    out = "".join(hex_list)
    return out

def byt_to_bits(byt_list):
    bin_list = []
    for byte in byt_list:
        temp = [] 
        for bit in byte:
            temp.append(int(bit))
        bin_list += temp[::-1]
    return bin_list

def bits_to_byt(bin_list): #for single bytes
    temp = [str(x) for x in bin_list]
    temp = temp[::-1]
    byte = "".join(temp)
    return byte

def read_file_byt_byt(filename, in_hex = False, asBinary = True):
    fn = filename.rsplit(".")
    out = []
    if (fn[-1] == "txt"): #txt input
        
        f = open(filename)
        content = f.read()
        f.close()
        
        if asBinary:
            out = [bin(x)[2:].zfill(8) for x in bytearray(content, 'utf-8')]
            #print(out)
            return out
        
        elif in_hex: #hex values seperated by a space not including 0x
            temp = content.split(" ")
            if (temp[-1] == ""):
                temp.remove("") 
            out = hex_to_byt(temp)
            out = out[::-1] ##its because the hex_to_byt is a bit convoluted, but either case this fixes the input
        
        else: #this here is for binary input in txt
            count = 0
            byt = ""
            for x in content:
                if (count == 8):
                    count = 0
                    out.append(byt)
                    byt = ""
                    continue
                byt = str(x) + byt
                count += 1
            if (count != 0): #this should not happen if we are getting bytes
                while (count % 8 != 0): 
                    count += 1
                    byt = "0" + byt
                out.append(byt)

    elif (fn[-1] == "bin"): #binary input
        f = open(filename, mode = "rb")
        content = f.read()
        f.close()
        for x in content:
            binval = format(x, "b")
            while (len(binval) < 8):
                binval = "0" + binval
            #print(binval)
            out.append(binval)
    
    else :
        return out #No support for input file type
    return out 

def print_state(block, visual = True, form = "binary"):
    #print("Note that its printing down then left")
    #print("a1 b1 c1 d1 e1")
    #print("a2 b2 c2 d2 e2")
    #print("etc ...")
    magic_x = [3, 4, 0, 1, 2]
    magic_y = [2, 1, 0, 4, 3]
    out_block = [[[] for j in range(5)] for i in range(5)]
    for i in range(5):
        for j in range(5):
            if visual: 
                out_block[i][j] = block[magic_x[i]][magic_y[j]]
            else:
                out_block[i][j] = block[i][j]

    for i in range(5):
        for j in range(5):
            if form == "binary":
                print(out_block[i][j]) #lane
            elif form == "bytes":
                temp = [out_block[i][j][k*8 : (k+1)*8] for k in range(8)] #just subdividing the lane into 8
                temp = [bits_to_byt(line) for line in temp]
                temp = temp[::-1]
                print(temp) #lane
            elif form == "hex":
                temp = [out_block[i][j][k*8 : (k+1)*8] for k in range(8)] #just subdividing the lane into 8
                temp = [bits_to_byt(line) for line in temp]
                temp = byt_to_hex(temp)
                temp = temp[::-1]
                print(combine_hex_list(temp)) #lane

        print("-----") #new sheet
    #With respect to the visual representation
    
'''
Shake algorithm, here input should be the message as a list of 
hex values (excluding the 0x at the start, see format from read_file_hex)
'''
#input here should be a byte list
def pad_byts(message):
    out = [i for i in message]
    if (len(out) % 168 == 167):
        out.append("10011111")
        return out

    out.append("00011111")
    while (len(out) % 168 != 167):
        out.append("00000000")
    out.append("10000000")
    return out

#input here should have 168 bytes this fills up the c part
def padding_c(message): 
    out = [i for i in message]
    while (len(out) % 200 != 0):
        out.append ("00000000")
    return out

#input block should be the 5x5x64 array the values are bits here
def theta(block):
    column_values = [[0 for i in range(64)] for j in range(5)]
    new_block = [[[0 for k in range(64)] for j in range(5)] for i in range(5)]
    for i in range(5):
        for k in range(64):
            col_val = 0
            for j in range(5):
                col_val += block[i][j][k]
            col_val %= 2
            column_values[i][k] = col_val

    for i in range(5):
        for j in range(5):
            for k in range(64):
                #k-1 will just wrap so its fine
                #i out of index can be troublesome
                i_col_plus1 = i + 1 
                if i_col_plus1 == 5:
                    i_col_plus1 = 0

                new_block[i][j][k] = block[i][j][k] + column_values[i-1][k] + column_values[i_col_plus1][k-1]
                new_block[i][j][k] %= 2
    return new_block 

def rho(block):
    new_block = [[[0 for k in range(64)] for j in range(5)] for i in range(5)]
    for k in range(64):
        new_block[0][0][k] = block[0][0][k]
    i = 1
    j = 0
    for t in range(24):
        offset = int(((t+1) * (t+2))/2)
        for k in range(64):
            shift = (k - offset) % 64 #modulo length of word
            new_block[i][j][k] = block[i][j][shift]
        temp = j
        j = (2 * i + 3 * j) % 5
        i = temp
    return new_block

def pi(block):
    new_block = [[[0 for k in range(64)] for j in range(5)] for i in range(5)]
    for i in range(5):
        for j in range(5):
            for k in range(64):
                new_block[i][j][k] = block[(i + 3*j) % 5][i][k]
    return new_block

def chi(block):
    new_block = [[[0 for k in range(64)] for j in range(5)] for i in range(5)]
    for i in range(5):
        for j in range(5):
            for k in range(64):
                #to prevent out of range
                i_plus1 = (i+1) % 5
                i_plus2 = (i+2) % 5
                temp1 = (block[i_plus1][j][k] + 1) % 2
                temp2 = (block[i_plus2][j][k])
                and_temp = 0
                if (temp1 == 1 and temp2 == 1):
                    and_temp = 1
                new_block[i][j][k] = (block[i][j][k] + and_temp) % 2
    return new_block

#the input round_counstant should be a 64 bit list
def iota(block, round_constant):
    new_block = [[[0 for k in range(64)] for j in range(5)] for i in range(5)]
    central = [0 for k in range(64)]
    for k in range(64):
        central[k] = (block[0][0][k] + round_constant[k]) % 2

    for i in range(5):
        for j in range(5):
            for k in range(64):
                if (i == 0) and (j == 0):
                    new_block[i][j][k] = central[k]
                else:
                    new_block[i][j][k] = block[i][j][k]
    return new_block

def round_constants_to_bits(constant_file):
    f = open(constant_file)
    content = f.read()
    f.close()
    content = content.split("\n")
    content = [byt_to_bits(hex_to_byt(line.split(" "))) for line in content]
    return content
#print(round_constants_to_bits("round_constants.txt"))

#in state here should be a list of bits, it outputs a list of bits
def shakef(in_string):
    bit_count = 0
    state = [[[0 for k in range(64)] for j in range(5)] for i in range(5)]
    for j in range(5):
        for i in range(5):
            for k in range(64): 
                state[i][j][k] = in_string[bit_count]
                bit_count += 1
    
    iota_constants = round_constants_to_bits("round_constants.txt")

    for i in range(24):
        #print("~~~~~~~~~~~Round ", i)
        #need to xor message somewhere here
        state = theta(state)
        state = rho(state)
        state = pi(state)
        state = chi(state)
        state = iota(state, iota_constants[i])
        #print_state(state, False, "hex")

    out = []
    for j in range(5):
        for i in range(5):
            for k in range(64):
                out.append(state[i][j][k])

    return out

def shake128(message, output_bytes = 32): 
    to_shake = [0 for i in range(1600)] #initial value

    padded_msg = padding_c(pad_byts(message))
    msg_bits = byt_to_bits(padded_msg) #should be a multiple of 1600, this is handelled in the padding
    chunks = [msg_bits[i*1344: (i+1)*1344] for i in range(int(len(msg_bits)/1344))]
    
    for chunk in chunks: #this is the absorbtion bit of the msg
        #print("chunk absorbed")
        #print(bit_list_hex(chunk))
        #print(len(chunk))
        for i in range(1344):
            to_shake[i] = (to_shake[i] + chunk[i])%2
        to_shake = shakef(to_shake)
    
    #just need to squeeze 
    temp = []
    loops = (output_bytes // 168) + 1
    for round in range(loops):
        squeeze = to_shake[:1344]
        #print("squeezed")
        #print(bit_list_hex(squeeze))
        temp.append(squeeze)
        #print(len(squeeze))
        to_shake = shakef(to_shake)

    out = []
    count1 = 0 
    count2 = 0
    while (len(out) < output_bytes * 8):
        if count1 == 1344:
            count2 += 1
            count1 = 0
        out.append(temp[count2][count1])
        count1 += 1

    out = "".join(bit_list_hex(out))
    return out

#input should be a list of bits, length multiple of 8
def bit_list_hex(in_string):
    out = [in_string[(i*8): (i+1)*8] for i in range(int(len(in_string)/8))]
    out = [bits_to_byt(x) for x in out]
    out = byt_to_hex(out)
    return out

def main2():
    args = list(sys.argv)
    N = 32
    if (len(args) > 1):
        N = int(args[1])
    store = []
    for line in sys.stdin.buffer.readlines():
        for value in line:
            byte = bin(value)[2:].zfill(8)
            store.append(byte)
    hashed = shake128(store, N)
    print(hashed)
    return

def main():   #usage ./shake128.py filename bytes out
    #args = input().split(" ")
    args = list(sys.argv)[1:]
    #print(args)
    if (len(args) == 0):
        print("Missing input file")
        return 
    filename = args[0]
    if len(args) == 1:
        hashed = shake128(read_file_byt_byt(filename, False, True))
    else: 
        bytesout = int(args[1])
        hashed = shake128(read_file_byt_byt(filename, True, False), bytesout)
    print(hashed)

if __name__ == "__main__":
    main2()