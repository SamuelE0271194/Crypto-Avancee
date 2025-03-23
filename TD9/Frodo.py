#!/usr/bin/env python3
import sys
import random
import hashlib

def hex_to_bit(hex_string):
    out = "0" + hex_string #just to fix the problem if theres a missing 0, if there isint, it will round down anyways
    out = bin(int(out, 16))[2:].zfill((len(out) // 2) * 8) 
    return out

def bit_string_to_array(bit_string):
    out = [int(i) for i in bit_string]
    return out

def bit_array_to_string(bit_array):
    out = ""
    for i in bit_array:
        out += str(i)
    return out

def transpose_mat(matrix):
    out = [[None for i in range(len(matrix))] for j in range(len(matrix[0]))]
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            out[j][i] = matrix[i][j]
    return out

def add_mat(mat1, mat2):
    if (len(mat1) != len(mat2)):
        print("Not the no of rows!")
        return
    if (len(mat1[0]) != len(mat2[0])):
        print("Not the no of col!")
        return
    out = [[0 for i in range(len(mat1[0]))] for j in range(len(mat1))]
    for i in range(len(mat1)):
        for j in range(len(mat1[0])):
            out[i][j] = mat1[i][j] + mat2[i][j]
    return out

def mul_mat(mat1, mat2):
    if len(mat1[0]) != len(mat2):
        print("Cols do not match rows") 
        return
    out = [[0 for i in range(len(mat2[0]))] for j in range(len(mat1))]
    for i in range(len(mat1)):
        for j in range(len(mat2[0])):
            entry = 0
            for k in range(len(mat1[0])):
                entry += mat1[i][k] * mat2[k][j]
            out[i][j] = entry
    return out

def encode(bit_string, B = 2, m_bar = 8, n_bar = 8, q = 32768):
    l = B * m_bar * n_bar
    K = [[0 for i in range(n_bar)] for j in range(m_bar)]
    for i in range(m_bar):
        for j in range(n_bar):
            k = 0
            for l in range(B):
                k += bit_string[(i * n_bar + j) * B + l] * (2**l)
            K[i][j] = k * q // (2**B)
    return K

def decode(matrix, B = 2, m_bar = 8, n_bar = 8, q = 32768):
    l = B * m_bar * n_bar
    k_out = [0 for i in range(l)]
    for i in range(m_bar):
        for j in range(n_bar):
            k = round(matrix[i][j] * 2**B / q)
            k = k % (2 ** B)
            k_l = [0 for i in range(B)]
            for l in range(B):
                k_l[l] = k % 2
                k >>= 1

            for l in range(B):
                k_out[((i * n_bar) + j) * B + l] = k_l[l]
    return k_out

def pack(matrix, D = 15):
    n1 = len(matrix)
    n2 = len(matrix[0])
    b_out = [0 for i in range(D * n1 * n2)]
    for i in range(n1):
        for j in range(n2):
            temp = matrix[i][j]
            c_l = [0 for i in range(D)]
            for l in range(D):
                c_l[l] = temp % 2
                temp >>= 1
            for l in range(D): 
                b_out[((i * n2) + j) * D + l] = c_l[D - 1 - l]
    return b_out 

def unpack(bit_string, n1, n2, D = 15):
    mat_out = [[0 for i in range(n2)] for j in range(n1)]
    for i in range(n1):
        for j in range(n2):
            temp = 0
            for l in range(D):
                temp += bit_string[((i * n2) + j) * D + l] * (2 ** (D - 1- l))
            mat_out[i][j] = temp
    return mat_out
            

chi_freq = (9288, 8720, 7216, 5264, 3384, 1918, 958, 422, 164, 56, 17, 4, 1)

def gen_T(chi_table = chi_freq):
    T_chi = list(range(len(chi_freq)))
    T_chi[0] = int(chi_freq[0] / 2) - 1
    for z in range(1, len(chi_freq)):
        T_chi[z] = T_chi[0] + sum(chi_freq[1:z + 1])

    return T_chi
#
##input is a random bit string of length chi (based on table)
def sample_from_table(r, table = gen_T(chi_freq)):
    #print(r)
    len_chi = len(table)
    t = 0
    e = 0
    for i in range(1, len(r)):
        t += r[i] * 2**(i - 1)
    #print(t)
    for i in range(len(table) - 1):
        if t > table[i]:
            e += 1
    if (r[0] == 1):
        e = -e
    return e

#r should be a string of string of bits, n1 (row) * n2 (cols) in r
def sample_matrix(r, n1, n2):
    sample_mat = [[0 for i in range(n2)] for j in range(n1)]
    for i in range(n1):
        for j in range(n2):
            sample_mat[i][j] = sample_from_table(r[(i * n2) + j])
    return sample_mat


##seed should be a string of bits
def gen_matrix(seedA, n = 8, q = 32768):
    shake = hashlib.shake_128()
    seed_len = len(seedA)
    A = [[0 for i in range(n)] for j in range(n)]

    for i in range(n):
        b = bin(i)[2:].zfill(16) + seedA
        b = (int(b, 2)).to_bytes(16 + seed_len, byteorder = "big")
        #print(b)
        shake.update(b)
        c_row = shake.digest(16 * n)
        c_row = bin(int(c_row.hex(), 16))[2:].zfill(16 * n * 8)
        c_row = [c_row[16 * i : 16 * (i + 1)] for i in range(n)]
        for j in range(n):
            #print(int(c_row[j], 2))
            A[i][j] = int(c_row[j], 2) % q
    return A

def keygen(len_s = 128, len_se = 128, len_z  = 128, len_seedA = 128, n = 640, n_bar = 8, len_chi = 16, len_pkh = 128):
    s_se_z = [random.randint(0, 1) for i in range(len_s + len_se + len_z)]
    s = s_se_z[0: len_s]
    se = s_se_z[len_s: len_s + len_se]
    z = s_se_z[len_s + len_se:]

    s = "".join(str(bit) for bit in s)
    se = "".join(str(bit) for bit in se)
    z = "".join(str(bit) for bit in z)

    s = (int(s, 2).to_bytes(len_s // 8, byteorder = "big")) 
    se = (int(se, 2).to_bytes(len_se // 8, byteorder = "big")) 
    z = (int(z, 2).to_bytes(len_z // 8, byteorder = "big")) 
    #print(z)

    shake = hashlib.shake_128()
    
    shake.update(z)
    seed_a = shake.digest(len_seedA)
    seed_a_bit = hex_to_bit(seed_a.hex())
    A = gen_matrix(seed_a_bit, n = n)
    #print_mat(A)
    shake.update(bytes([0x5f]) + se)
    r_strings = shake.digest(2 * n * n_bar * len_chi //8)
    #print(r_strings)
    r_s = [r_strings[i * len_chi // 8: (i + 1) * len_chi // 8].hex() for i in range(2 * n * n_bar)]
    r_s_bits = [bit_string_to_array(hex_to_bit(i)) for i in r_s]
    #print(r_s_bits)
    S_t_error = sample_matrix(r_s_bits[0: n * n_bar], n_bar, n)
    S = transpose_mat(S_t_error)
    #print_mat(S_t)
    E = sample_matrix(r_s_bits[n * n_bar: ], n, n_bar)
    #print_mat(E_error)
    #print_mat(A)
    #print_mat(S)
    B = mul_mat(A, S)
    B = add_mat(B, E)
    #print_mat(B)

    b = pack(B)
    b = [str(i) for i in b]
    b = "".join(b)
    #print(hex(int(b, 2)))
    #print(seed_a.hex() + b)
    shake.update(seed_a)
    pkh = shake.digest(len_pkh//8)

    seed_a = (bin(int(seed_a.hex(), 16))[2:]).zfill(len_seedA)
    pk = seed_a + b

    s = bin(int(s.hex(), 16))[2:].zfill(len_s)
    
    sk = s + seed_a + b
    #print(sk)
    #print(bin(S_t_error[0][0])[2:].zfill(16))
    for i in range(n_bar):
        for j in range(n):
            sk += bin(S_t_error[i][j])[2:].split("b")[-1].zfill(16)
    #print(pk)
    print(sk)
    return (pk, sk)


def print_mat(matrix):
    for i in range(len(matrix)):
        print(matrix[i])

#info should be a hex string
def write_to_file(info, filename):
    file = open(filename, "w")
    for line in info:
        file.write(line + "\n")
    file.close()
    return

def main():
    #private keys are stored in lines, with \n splitting the (SK, s, PK, PKH)
    input_arg = list(sys.argv)[1:]

    random.seed(123)

    #encode decode, pack unpack
    #k_encode = [random.randint(0, 1) for j in range(128)]
    #k_encode_test = encode(k_encode)
    #print_mat(k_encode_test)
    #k_decode_test = decode(k_encode_test)
    #print(k_decode_test)
    #print(k_encode == k_decode_test)
    #print("HERERER")
    #k_pack_test = pack(k_encode_test)
    #print(k_pack_test)
    #k_unpack_test = unpack(k_pack_test, 8, 8)
    #print_mat(k_unpack_test)
    #print(gen_T())

    #checking that sample is realistic
    #for i in range(100000):
    #    r = [random.randint(0, 1) for j in range(16)]
    #    if (sample_from_table(r) < -10):
    #        print(i)
    #r = [] 
    #for i in range(64):
    #    r.append([random.randint(0, 1) for j in range(16)])
    #mat_sample = sample_matrix(r, 8, 8)
    #print_mat(mat_sample)

    #print_mat(gen_matrix("01"))

    pk, sk = keygen()
    print(hex(int(pk, 2)))
    sk = hex(int(sk, 2))
    write_to_file([sk], "output_keygen.sk")


if __name__ == "__main__":
    main()