---
title: chacha20 implementation in python
author: Samuel Hon
---

Descirption of how the code works, and how to use it.

# Usage
To use the code, firstly ensure that python is installed.
You might have to change the access permissions for the following files
chacha20.py, aead_wrap.py, aead_unwrap.py, poly1305_gen.py, poly1305_check.py.
The following command should work
```
$chmod +x filename
```
in order to run the file like an executable.

The following is an example of the usage
```
$./chacha20.py keyfile 000000000000004a00000000 sunscreen.txt out.bin
$./aead_wrap.py key_aead.bin 070000004041424344454647 ad_aead.bin sunscreen.txt test_wrap.bin
$./aead_unwrap.py key_aead.bin 070000004041424344454647 ad_aead.bin test_wrap.bin 1ae10b594f09e26a7e902ecbd0600691
```
The inputs to chacha20.py are 
    - keyfile: a binary file contaning the key
    - nonce: a 96 bit (12 byte/ 12 hex characters)
    - plaintext: text to encrypt (or decrypt)
    - output file: file to output encrypted (or decrypted) text to
The chacha implementation works both ways as an encryptor and decryptor

The inputs to aead_wrap.py are
    - keyfile: a binary file containing the key
    - nonce: a 96 bit (12 byte/ 12 hex characters)
    - ad_aead: the additional authenticated data (in a binary file)
    - plaintext: the text to encrypt
    - output file: the file to output the encrypted text
In addition, the tag for authenticity of the output will be printed in the standard output

The inputs to aead_unwrap.py are
    - keyfile: a binary file containing the key
    - nonce: a 96 bit (12 byte/ 12 hex characters)
    - ad_aead: the additional authenticated data (in a binary file)
    - cipherfile: the cipher text to decrypt (in binary, this file also contains the aad and some trailing information)
    - tag: the tag to check the authenticity of the ciphertext

## Some other stuff
You can instead run the file by using python/python3 at the front of the command
```
$python aead_unwrap.py key_aead.bin 070000004041424344454647 ad_aead.bin test_wrap.bin 1ae10b594f09e26a7e902ecbd0600691
```

You will also need the files poly1305_gen.py and poly1305_check.py in the same working directory