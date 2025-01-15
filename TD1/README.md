---
title: Shake128 implementation in python
author: Samuel Hon
---

Descirption of how the code works, and how to use it.

# Usage
To use the code, firstly ensure that python is installed.
You might have to change the access permissions with
```
$chmod +x shake128.py
```
in order to run the file like an executable.

As for usage, use the following line
```
$./shake128.py N < byte_stream
```
Where byte_stream is the name of the file containing the text or binary you'd like to hash, and N is the number of bytes to output.
The input will be read as binary, so texts in the txt for example are fine.
By default, if N is not provided, the output will be 32 bytes.

The following line is an example using the "short-binary.bin" file in the sample_input folder, with a 32 byte output
```
$./shake128.py 32 < ../sample_input/short-binary.bin
```

## Must have file
Along with the code, the round_constants.txt file should be in the same working directory as the program.
This file just contains the constants used in the iota portion of the code