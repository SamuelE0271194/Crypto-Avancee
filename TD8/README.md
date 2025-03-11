---
title: Ed25519 Signature scheme
author: Samuel Hon
---

Descirption of how the code works, and how to use it.

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

The inputs to keygen.py are
- PrivateKey file, the private key of the user (32 byte hex string) in the first line of the file. If this is not provided, it will generate a random private key.

Below is a template and example of how to run the code
```
$./keygen.py privateKeyFile(Optional)
$./keygen.py test_keygen.sk
```

## encaps
encaps generates a random message, which is then hashed with a given public key (of the receiver) (as in the FO transform) to generate a "r" and "k". 
The "r" is the used to encrypt the message along with the public key of the receiver, to produce a ciphertext. 
While "k" hashed with the cipher text to produce a K.
A cipher text and K is returned.

In this case the encryption takes a message M, (recievers) public key PK, and an r.
It then uses the r as as the senders private key and generates a shared secret, r * PK.
The shared secret is then just xor-ed onto the message to generate the cipher text

The inputs to encaps.py are
- public key, a 32 byte hex string

Below is a template and example of how to run the code
```
$./encaps.py public_key
$./encaps.py a28d6dd77eb4e12f9347071f7f369fa14a91ebf01368e59364983492e10a6729
```

## decaps
decaps decapsulates a given ciphertext using the corresponding private key. 
The ciphertext is decrpyted with the users private key to recover the message.
The message is the encapsulate as the sender would have done, to check if the K derived is the same as the K which was sent along with the ciphertext. 

The inputs to decaps.py are
- private_key_file, the file generated using keygen
- ciphertext, a hex string of the ciphertext

Below is a template and example of how to run the code
```
$./decaps.py Private_key(file) ciphertext(hex string)
$./decaps.py output_keygen.sk 7b4f9fc5b04753cea9b0f8b1c28dbc7804700f8cf8560454fcfca4ebd3b49b5600e15f5fbf1053abb9f77fb20cb5ec2f2009e59cfb5edc06993a6cb6495bbb3e
```

## Notes
The hash functions used here are sha3 based, with the addition of concatinating "01", "02", "03" to the front based on which hash function is being used.

When encapsulating a message, the random r generated is treated as a private key for a standard diffe-hellman exchange. 
A public key is then generated based on this r, and placed at the start of the cipher text returned. 
The encapsulator then geneartes the shared secret using the public key, and xor this into the random message it has generated.

The decapsulator after receiving the cipher text, takes the public key at the start, and generates the shared secret. Which it can the use to decrypt the ciphertext.
Which is simply just xoring the shared secret.