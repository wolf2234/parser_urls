# URL parser

This is a program that parses files with the `dat` extension and pulls out all the URLs from there.

## Description:
This program generates two dictionaries, namely `dict_urls` and `dict_unshorten_urls`.
1. The first dictionary contains original links as keys and status codes as their values. There are 70 keys in this dictionary. 


2. The second dictionary contains original links as keys and unshortened links as their values. There are 57 keys in this dictionary.

The running time of the program is 2 minutes and 52 seconds.

Also in this program such a module as `multiprocessing` was used. This module was chosen to be used because it has a class like `Manager`. This class was very convenient to implement the required functionality. And also using this module the speed of the program was faster than when using the `threading` module.

## Libraries:
- pickle
- requests
- os
- time
- datetime
- loguru
- urlextract
- multiprocessing

