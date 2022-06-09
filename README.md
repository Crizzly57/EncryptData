# Encrypt Data [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Latest release](https://badgen.net/github/release/Naereen/Strapdown.js)](https://github.com/Naereen/Strapdown.js/releases) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
This program is useful to encrypt files and secure them. It is fully written in Python. 
## How it works
Add files or folders to the UI, and it will find all files.  
After the encryption, the filename then has the following suffix "_encrypted".   
If you want to delete the old files after the process, then you can select this in the settings.

The files will be encrypted with AES-128 Bit, this is done by the Fernet class from the Cryptography modul.  
If the file is an PDF, then the modul PikePDF will be used.  
After encrypting the PDF, it can then be opened with the correct password.  

## Features
- Drag 'n' Drop files and folders in the UI
- Encrypt and decrypt files with AES
- Encrypt and decrypt PDF's
- German & English language supported
- Maximize & minimize the window

## Screenshots
![Screenshot_overview](https://user-images.githubusercontent.com/81525848/172855337-80dd26c3-aef5-4650-90a7-16700a5a0d1e.png)
![Screenshot_settings](https://user-images.githubusercontent.com/81525848/172855377-975d54a6-4a3f-408b-9a57-708b9d92c2dc.png)

## Dependencies
- [Cryptography](https://cryptography.io/en/latest/)
- [PikePDF](https://pikepdf.readthedocs.io/en/latest/)
- [PyQt5](https://pypi.org/project/PyQt5/)
- Python 3.9

## License
Encrypt Data is available under the MIT license. See the [LICENSE](https://github.com/Crizzly57/EncryptData/blob/master/LICENSE.md) file for more info.