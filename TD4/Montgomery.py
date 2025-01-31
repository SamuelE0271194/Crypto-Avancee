#!/usr/bin/env python3
import sys

#Some conversion tools
def hex_to_byt(hex_val):
    byt_val = bin(int(hex_val, 16))[2:].zfill(8)
    return byt_val

def hexs_to_byts(hex_list):
    byt_list = list(map(lambda x: hex_to_byt(x), hex_list))
    return byt_list


P = 2**255 - 19

A = 486662

UP = 9
UV = 14781619447589544791020593568409986887264606134616475288964881837755586237401


def xADD(x1, x2, x_p):

    return (0, 0)

def xDBL(x1):

    return (0, 0)

#input values are integers, x and z are mod p
def ladder(m, x, z, p = P, a = A):
    m_bin = bin(m)[2:]
    m_len = len(m_bin)
    u = [x, 1]
    x0 = [1, 0]
    x1 = u
    for i in range(len(m_bin)):
        print(m_len - 1 - i) 
        if (m_bin[m_len - 1 -i] == 0):
            temp = xDBL(x1)
            x1 = xADD(x0, x1, u)
            x0 = temp
        else:
            x0 = xADD(x0, x1, u)
            x1 = xDBL(x1)

    return x0 ##need to fix this

ladder(100, 0, 0)