# DozukiPDFBackup
A Python program for making PDF backups of Dozuki guides while retaining perceived file structure.
Dozuki API is missing several functions that I wanted, mainly to export .pdf for offline viewing.
My solution is to use webdriver to crawl through all the directories and export the guides.
It ignores wikis (because those guides already exist elsewhere) and embedded documents (usually kept separate from build guides, like MSDS for my case), but you can add those yourself if you want.

To use it, just put in your Dozuki URL where you want it to start and login information, and the directory where you want the files to be saved.
