---
title: Ed25519 Signature scheme
author: Samuel Hon
---

Descirption of how the code works, and how to use it.

# Usage
To use the code, firstly ensure that python is installed.
You might have to change the access permissions for the following files
keygen.py, signEd25519.py, verifyEd25519.py, batch.py
The following command should work
```
$chmod +x filename
```
in order to run the file like an executable.

The following code is working in the context of the Ed25519 curve as specified in the RFC documentation.

The following is an explination of the code and usage:

## keygen
keygen geneartes a private public key pair.

The code generates a file containing the public and private(secret) key, as a binary file.

The inputs to keygen.py are
- PrivateKey, the private key of the user (in hex). If this is not provided, it will generate a random private key.
- fileName, the name which the key pair will be saved (without postfixes). If no name is provided, this will save the file as prefix.sk and prefix.pk (sk = secret/private key, pk = public key)

Below is a template and example of how to run the code
```
$./keygen.py privateKey(Optional) fileName(Optional)
$./keygen.py f5e5767cf153319517630f226876b86c8160cc583bc013744c6bf255f5cc0ee5 test4
```

## sign
signEd25519 signs a message with a given private key.

The code generates a file containing the signature (as a binary file). The output file is saves as a combination of the filenames. So we need the input file names to not contain /. 

Basically, ensure the files you are using are in the current directory.

The inputs to signEd25519.py are
- messagefile, the filename or message you'd like to encrypt. Note that this fil is read as a binary text (Not that it should matter, just ensure that when you verify, you are using the same message file)
- private.sk, the *filename* of the file containing the private key of the signer in a binary file.
- public.pk, the *filename* corresponding public key to the private key. This is optional, and if not provided, will be computed on the spot. If you are unsure of the matching public key, ommit this.

Below is a template and example of how to run the code
```
$./signEd25519.py messageToSign privateKey.sk publicKey.sk(optional)
$./signEd25519.py ed25519-20110926.pdf prefix.sk
```

## verify
verifyEd25519 verifies a signature, with a message and public key.

The code takes in a signature, message and public key, and prints ACCEPT of REJECT depending on the validity of the signature in the context of the message and public key

The inputs to verifyEd25519.py are
- signature file, the *filename* of the file containing the signature. The file should be a binary file.
- public key file, the *filename* of the file containing the public key of the signer in a binary file.
- message file, the filename of the file containing the message which is has been signed. The content type of the file doesn't matter, but make sure that it is the exact same file which was used when signing

Below is a template and example of how to run the code
```
$./verifyEd25519.py signatureFile publickeyfile message
$./verifyEd25519.py sign_ed25519-20110926_prefix.bin prefix.pk ed25519-20110926.pdf 
```

## batch
batch verifies a batch of signatures, it takes in an input text file containg the *filenames* to be verified in plaintext.

Each line in thie input file should be the *filenames* of the signature, corresponding public key, corresponding message.

The corresponding files (eg the signature file in line 1) are the binary files of the siganture and public key, while the message can be of any type (but will be verified as a binary file, so should have been signed using the binary of the file)

batch takes this text file and returns ACCEPT if all the signatures are correct, and REJECT otherwise.

*Check* that all the files being accessed are in the current directory.

Below is an example of running the code
```
$./batch.py batchVerify.txt 
```
Note batch verifies the signatures by calculating a random linear combination of each signature to verify.

This is done using multiexponentiation, by checking ${\Sigma z_i R_i - \Sigma (z_i * s_i) P + \Sigma (z_i * (-h_i)) Q_i = 0}$, where 
- z_i is a random 128 bit integer 
- R_i is the point which is encoded in the signature, with s_i the corresponding scalar
- P the base point used in the signing (Defined in RFC)
- Q_i the point which is encoded in the public key
- h_i the hash (SHA512) of the (R_i || Q || m_i), where m_i is the corresponding messagea

Contrary to the method used in the 2-d scalar multiplication case, instead of computing the linear combination of the various points first and using them later to avoid computation. 
I decided to sum them on the go as the number of (binary) linear combinations here is $2^{n+1}$ where $n$ is the number of signatures to verify. (There are n $R$, n $Q$, and 1 $P$)

Whereas, since the scalars have at most 128 bits, we expect at most $3 \times bits(max 128) \times n$ additions, used in the computation.

## Some other stuff
In case you want to convert a hex string into a binary file. 
There is a code msg_to_bin.py, which converts a hex string in a plaintext file into a binary file.
It takes in a file conating a hex string in plain text, and returns the binary file of the hex string.

Below is an example of running the code
```
$./msg_to_bin.py msg1.txt
```

## Organisation of the files here. 
The test files here are all in the Tests folder, but since we need the files to be in the working directory, if you want to test using these files, you should be in the Tests directory instead, and call the codes.
Eg
```
../Tests$ ../../batch.py batchVerify.txt 
```
The signature files here correspond to the test.pk/sk and msg.bin files