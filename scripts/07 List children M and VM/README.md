# Listing children of communication path

Basic script providing list of meter and virtual meters under given communication path.

## How to run

All scripts reads authentication information from environment variables.

|Environment variable name|Value description|
|-|-|
|C4_USER|a username|
|C4_PASS|a password|

### Python

* Requires Python 3

The script allows to override environment variables for username and password by first two arguments.

> python ./main.py [username [password]]

### PowerShell

The script allows to override environment variables for username and password by first two arguments.

> pwsh main.ps1 [username [password]]

### VBScript

> cscript main.vbs
