#!/usr/bin/env python3

#Some conversion tools
def hex_to_num(hex_val):
    return int(hex_val, 16)

def hexs_to_nums(hex_list):
    return list(map(lambda x: hex_to_num(x), hex_list))

class Point:
    #projective coords
    def __init__(self, x, z): 
        self.x = x
        self.z = z
    
    # not really correct, but its a place holder
    def __add__(self, other):
        return Point(self.x + other.x, self.z + other.z) 

    # other should be an int, not correct either but it does the job for swap
    # since mul by scalar is commutative i dont care
    def __mul__(self, other):
        return Point(self.x * other, self.z * other)
    __rmul__ = __mul__

    def __str__(self):
        return "(%d, %d)" % (self.x, self.z)

class Curve:
    #  BY^2Z = X(X^2 + AXZ + Z^2)
    def __init__(self, A = 486662, B = 1, prime = 2**255 - 19): #Defualt to curve 25519
        self.A = A
        inv_4 = pow(4, prime - 2, prime)
        self.Ap2o4 = ((A + 2) * inv_4) % prime #(a + 2) /4
        self.B = B
        self.zero = Point(0 ,0)
        self.prime = prime
    
    #need to convert to int cause python does some approximation for floats
    #floats are cause of ** and /
    def xADD(self, p, q, pq):
        #print("adding : ", p, q, pq)
        pdif = (p.x - p.z) % self.prime
        psum = (p.x + p.z) % self.prime 
        qdif = (q.x - q.z) % self.prime
        qsum = (q.x + q.z) % self.prime
        u = (pdif * qsum) % self.prime
        v = psum * qdif % self.prime
        uvp = pow(u+v, 2, self.prime)
        uvm = pow(u-v, 2, self.prime)
        new_x = (pq.z * uvp) % self.prime
        new_z = (pq.x * uvm) % self.prime
        return Point(new_x, new_z)

    def xDBL(self, p):
        pdif = (p.x - p.z) % self.prime
        psum = (p.x + p.z) % self.prime 
        q = pow(psum, 2, self.prime)
        r = pow(pdif, 2, self.prime)
        s = q - r % self.prime

        new_x = (q * r) % self.prime
        temp = (s * self.Ap2o4) % self.prime
        temp = r + temp
        new_z = (s * temp) % self.prime
        return Point(new_x, new_z)

    #if b == 1 then swap
    def swap(self, b, p, q):
        return (((1 - b) * p) + (b * q), (b * p) + ((1 - b) * q))

    #get x coordinates after making z = 1
    def normalise(self, point):
        if (point.z == 1):
            return point.x
        return (point.x * pow(point.z, self.prime - 2, self.prime)) % self.prime

def ladder(m, base_p, curve = Curve()):
    m_bin = bin(m)[2:] #this is biggest bit first
    u = Point(base_p.x, base_p.z)
    x0 = Point(1, 0)
    x1 = Point(base_p.x, base_p.z)
    for i in range(len(m_bin)):
        t0, t1 = curve.swap(int(m_bin[i]), x0, x1)
        t1 = curve.xADD(t0, t1, u)
        t0 = curve.xDBL(t0)
        x0, x1 = curve.swap(int(m_bin[i]), t0, t1) 
        '''
        if (m_bin[i] == "0"):
            x1 = curve.xADD(x0, x1, u)
            x0 = curve.xDBL(x0)
        else:
            x0 = curve.xADD(x0, x1, u)
            x1 = curve.xDBL(x1)
        '''

    return curve.normalise(x0)

#from little endian weird encoding
def split_hex(hex_string):
    if (len(hex_string) % 2 == 1):
        hex_string = "0" + hex_string
    m = [hex_string[i*2 : (i+1) * 2] for i in range(len(hex_string)//2)]
    return m

def split_to_numbers(hex_string):
    return hexs_to_nums(split_hex(hex_string))

def decodeLittleEndian(b, bits):
    return sum([b[i] << 8*i for i in range((bits+7)//8)])

def decodeUCoordinate(u_list, bits = 255):
    # Ignore any unused bits.
    if bits % 8:
        u_list[-1] &= (1<<(bits%8))-1
    return decodeLittleEndian(u_list, bits)

def encodeUCoordinate(u, bits = 255, p = 2**255 - 19):
    u = u % p
    return ''.join([hex((u >> 8*i) & 0xff)[2:].zfill(2) for i in range((bits+7)//8)])

def decodeScalar25519(k_list):
    k_list[0] &= 248
    k_list[31] &= 127
    k_list[31] |= 64
    return decodeLittleEndian(k_list, 255)

def main():

    #in little endian
    test_scalar_1 = "a546e36bf0527c9d3b16154b82465edd62144c0ac1fc5a18506a2244ba449ac4"
    test_scalar_2 = "4b66e9d4d1b4673c5ad22691957d6af5c11b6421e0ea01d42ca4169e7918ba0d"
    test_u_1 = "e6db6867583030db3594c1a424b15f7c726624ec26b3353b10a903a6d0ab1c4c"
    test_u_2 = "e5210f12786811d3f4b7959d0538ae2c31dbe7106fc03c3efc4cd549c715a493"
    test_scalar_1 = "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"

    a = split_to_numbers(test_scalar_1)
    b = split_to_numbers(test_scalar_2)
    c = split_to_numbers(test_u_1)
    d = split_to_numbers(test_u_2)

    s1 = decodeScalar25519(a)
    s2 = decodeScalar25519(b)
    u1 = decodeUCoordinate(c)
    u2 = decodeUCoordinate(d)

    u1x = ladder(s1, Point(9, 1))
    u2x = ladder(s2, Point(u2, 1))
    
    #print(encodeUCoordinate(u1x))
    #print(encodeUCoordinate(u2x))

    test_u_3 = "0900000000000000000000000000000000000000000000000000000000000000"
    test_scalar_3 = test_u_3

    k_test = test_scalar_3
    u_test = test_u_3
    loops = 1000000 #it works for 1000000 too but its very slow
    #for 1000000 loops 7c3911e0ab2586fd864497297e575e6f3bc601c0883c30df5f4dd2d24f665424
    for i in range(loops):
        k_num = decodeScalar25519(split_to_numbers(k_test))
        u_num = decodeUCoordinate(split_to_numbers(u_test))
        res = ladder(k_num, Point(u_num, 1))
        res = encodeUCoordinate(res)
        if (i == 0 or i == 999 or i == 99999 or i == 999999):
            print(res)
        #if (i % 50000 == 0):
        #    print("working, ", i)
        u_test = k_test
        k_test = res

    def otherTests():
        print(ladder(2, Point(2, 1), Curve(49, 1, 101)))
        print("~~~~~~~~~~~~~~")
        print(ladder(3, Point(2, 1), Curve(49, 1, 101)))
        print("~~~~~~~~~~~~~~")
        print(ladder(77, Point(2, 1), Curve(49, 1, 101)))
        print("--------------")
        print(ladder(2, Point(7, 1), Curve(682, 1, 1009)))
        print(ladder(3, Point(7, 1), Curve(682, 1, 1009)))
        print(ladder(5, Point(7, 1), Curve(682, 1, 1009)))
        print(ladder(34, Point(7, 1), Curve(682, 1, 1009)))
        print(ladder(104, Point(7, 1), Curve(682, 1, 1009)))
        print(ladder(947, Point(7, 1), Curve(682, 1, 1009)))
        print("--------------")
        print(ladder(2, Point(9, 1)))
        print(ladder(3, Point(9, 1)))
        print(ladder(4, Point(9, 1)))
        print(ladder(5, Point(9, 1)))
        print(ladder(7, Point(9, 1)))
        return
    
    return


if __name__ == "__main__":
    main()