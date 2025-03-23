---
title: FrodoKEM128
author: Samuel Hon
---

Descirption of how the code works, and how to use it.
Only implemented a part of Keygen

# Usage
To use the code, firstly ensure that python is installed.
You might have to change the access permissions for the following files
keygen.py, encaps.py, decaps.py
The following command should work
```
$chmod +x filename
```
in order to run the file like an executable.

The following is an explination of the code and usage:

## keygen
keygen geneartes a private public key pair.

The code generates a file containing the in the following order, 
private key (sk), secret bits (s), public key(pk), public key hashed (pkh). 

Which is written into a file called output_keygen.sk. It also prints out the public key as a 32 bytes hex string.


Below is a template and example of how to run the code
```
$./Frodo.py
```

## Note
I only managed to implement the preliminary function for keygen. The outputs of keygen are probably not correct.
