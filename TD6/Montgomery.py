#!/usr/bin/env python3

#Some conversion tools
def hex_to_num(hex_val):
    return int(hex_val, 16)

def hexs_to_nums(hex_list):
    return list(map(lambda x: hex_to_num(x), hex_list))

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

class Point:
    #projective coords
    def __init__(self, x, y, z): 
        self.x = x
        self.y = y
        self.z = z
    
    # not really correct, but its a place holder
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z) 

    # other should be an int, not correct either but it does the job for swap
    # since mul by scalar is commutative i dont care
    def __mul__(self, other):
        return Point(self.x * other, self.y * other, self.z * other)
    __rmul__ = __mul__

    def __str__(self):
        return "(%d, %d, %d)" % (self.x, self.y, self.z)

class Curve:
    #  BY^2Z = X(X^2 + AXZ + Z^2)
    def __init__(self, A = 486662, B = 1, prime = 2**255 - 19): #Defualt to curve 25519
        self.A = A
        inv_4 = pow(4, prime - 2, prime)
        self.Ap2o4 = ((A + 2) * inv_4) % prime #(a + 2) /4
        self.B = B
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
        return Point(new_x, 1, new_z) #y here doesn't matter

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
        return Point(new_x, 1, new_z) #y here doesn't matter

    #if b == 1 then swap
    def swap(self, b, p, q):
        return (((1 - b) * p) + (b * q), (b * p) + ((1 - b) * q))

    #get x coordinates after making z = 1
    def normalise(self, point):
        if (point.z == 1):
            return Point(point.x, point.y, 1)
        return Point((point.x * pow(point.z, self.prime - 2, self.prime)) % self.prime,
                     (point.y * pow(point.z, self.prime - 2, self.prime)) % self.prime,
                     1)

    #Using the algorithm in (4.4) "Montgomery curves and their arithmetic
    #                               The case of large characteristic fields
    #                               Craig Costello · Benjamin Smith"
    def recover(self, p, q, p_q): #p is (x:y:1), q is (x:z), p_q is p+q~ (x:z), in these cases, y = 1 is used as a place holder
        p = self.normalise(p)
        q = self.normalise(q)
        p_q = self.normalise(p_q)

        v1 = p.x * q.z % self.prime
        v2 = (q.x + v1) % self.prime
        v3 = (q.x - v1) % self.prime
        v3 = pow(v3, 2, self.prime)
        v3 = (v3 * p_q.x) % self.prime
        v1 = (2 * self.A * q.z) % self.prime
        v2 = (v2 + v1) % self.prime
        v4 = (p.x * q.x) % self.prime
        v4 = (v4 + q.z) % self.prime
        v2 = (v2 * v4) % self.prime
        v1 = (v1 * q.z) % self.prime
        v2 = (v2 - v1) % self.prime
        v2 = (v2 * p_q.z) % self.prime
        y = (v2 - v3) % self.prime
        v1 = (2 * self.B * p.y) % self.prime
        v1 = (v1 * q.z) % self.prime
        v1 = (v1 * p_q.z) % self.prime
        y = (y * pow(v1, self.prime - 2, self.prime)) % self.prime #normalize for z = 1

        return Point(q.x, y, q.z)

def ladder(m, base_p, curve = Curve()):

    m_bin = bin(m)[2:] #this is biggest bit first
    #y doesn't matter for the ladder operations
    u = Point(base_p.x, 1, base_p.z)
    x0 = Point(1, 1, 0) 
    x1 = Point(base_p.x, 1, base_p.z) 
    for i in range(len(m_bin)):
        t0, t1 = curve.swap(int(m_bin[i]), x0, x1)
        t1 = curve.xADD(t0, t1, u)
        t0 = curve.xDBL(t0)
        x0, x1 = curve.swap(int(m_bin[i]), t0, t1) 
    ##x1 is (m+1) * P
    return curve.recover(base_p, x0, x1)    

def main():

    def otherTests():
        print(ladder(2, Point(2, 2, 1), Curve(49, 1, 101)))
        print("~~~~~~~~~~~~~~")
        print(ladder(3, Point(2, 2, 1), Curve(49, 1, 101)))
        print("~~~~~~~~~~~~~~")
        print(ladder(77, Point(2, 2, 1), Curve(49, 1, 101)))
        print("--------------")
        print(ladder(2, Point(7, 207, 1), Curve(682, 1, 1009)))
        print(ladder(3, Point(7, 207, 1), Curve(682, 1, 1009)))
        print(ladder(5, Point(7, 207, 1), Curve(682, 1, 1009)))
        print(ladder(34, Point(7, 207, 1), Curve(682, 1, 1009)))
        print(ladder(104, Point(7, 207, 1), Curve(682, 1, 1009)))
        print(ladder(947, Point(7, 207, 1), Curve(682, 1, 1009)))
        print("--------------")
        y = 14781619447589544791020593568409986887264606134616475288964881837755586237401
        print(ladder(2, Point(9, y, 1)))
        print(ladder(3, Point(9, y, 1)))
        print(ladder(4, Point(9, y, 1)))
        print(ladder(5, Point(9, y, 1)))
        print(ladder(7, Point(9, y, 1)))
        return
    #print("~~~~~~~")
    otherTests()
    return

if __name__ == "__main__":
    main()