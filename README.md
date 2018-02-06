# Curseforge Changelog Compiler
This script scrapes changelogs from curseforge for any jars that are different in the new mod directory. The changelogs are then dumped in the file changelog.html

### Step 1: Creating a Google CSE
1. Before starting anything, you **MUST** create a custom search engine.
   You can do this [here](https://cse.google.com/). The 'Sites to search' **MUST** be https://minecraft.curseforge.com/
2. Your **cse_id** is found in the URL https://cse.google.com/cse/setup/basic?cx={CSE_ID_STRING}

### Step 2: Getting a Google Python API Key
1. Follow the instructions [on this page](https://developers.google.com/api-client-library/python/guide/aaa_apikeys) to get your google python api key

### Step 3: Configuring the Script
There are 5 parameters to be configured in 'config.txt'.

**api_key** = the API key you retrieved in step 2

**cse_id** = the CSE ID you retrieved in step 1

**path_old** = the path to the directory containing the old modpack version mods.

Eg: *C:\USER\NAME\documents\Curse\Minecraft\Instances\MODPACK_NAME\mods*

**path_new** = the path to the directory containing the new modpack version mods.

**modpack_name** = The modpack name and current (new) version.

Eg: *FTB Revelations 1.4.0*

### Once all steps are complete, start run.bat.

#### The changelog will appear as changelog.html. I will add tag stripping options in the future. 
