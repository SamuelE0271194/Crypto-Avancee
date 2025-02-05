---
title: x25519 key exchange in python
author: Samuel Hon
---

Descirption of how the code works, and how to use it.

# Usage
To use the code, firstly ensure that python is installed.
You might have to change the access permissions for the following files
Montgomery.py x25519.py
The following command should work
```
$chmod +x filename
```
in order to run the file like an executable.

The following is an example of the usage
```
$./x25519.py 77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a
$./x25519.py 77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f
```
The inputs to x25519.py are 
    - m: a 32 byte hex string which acts as a private key in the diffie-hellman protocol
    - u (optional): a 32 byte hex string, which acts as the (x-coordinates) of the base point (By default, if no argument is provided, this point will be 9)

x25519.py acts as a key generator, which is used for both public key generation as well as for key exchange.

## Some other stuff
You can instead run the file by using python/python3 at the front of the command
```
$python x25519.py m u
```

Montgomery.py is where most of the functions (such as xADD xDBL) are stored. Running it just runs a check on the set of test vectors.
Just a note when repeatly reusing values. The decoding of the scalar (m) and the base point (u) are different. 
As such when resuing values, its better to pass in their respective hex strings, and let the code decode them accordingly.

## More stuff
Montgomery actually is able to support other curves. 
In the ladder function, you can modify the value of curve, which by default is set to curve25519, with A = 486662.
But you can input different curves but creating a new curve object, and setting the values of A, B, of the weierstrass normal form, and the prime for the underlying field.