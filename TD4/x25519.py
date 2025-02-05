#!/usr/bin/env python3
import sys
import Montgomery


def main():
    args = list(sys.argv)[1:]
    #first argument = m, second argument = u

    m = args[0]
    print(m)
    m = Montgomery.split_to_numbers(m)
    m = Montgomery.decodeScalar25519(m)
    
    u = 9
    if (len(args) > 1):
        u = args[1]
        print(u)
        u = Montgomery.split_to_numbers(u)
        u = Montgomery.decodeUCoordinate(u)
    print("~~~~~~~~")
    out = Montgomery.ladder(m, Montgomery.Point(u, 1))
    print(out)
    print(Montgomery.encodeUCoordinate(out))

    return

if __name__ == "__main__":
    main()