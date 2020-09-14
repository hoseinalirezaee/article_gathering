## How to use
> Recommended python version is `3.8`

> The app is tested on `Linux`. But should be run without any problem on `Windows` too.
###### 1. Create a python virtual environment <br>
Use the following command to create a virtual environment:
```shell script
python -m venv <virtual environment name>
ex: python -m venv .venv
```

###### 2. Activate the virtual environment <br>
To activate virtual environment on `Linux`, use the following command:
```shell script
source <virtual environment path>/bin/activate
ex: source .venv/bin/activate
```
###### 3. Install required packages using `pip`: <br>
 There is a file called `requirements.txt` in project files.
 you can use it to install required packages:
 ```shell script
pip install -r requirements.txt
```

###### 4. Update articles info <br>
Use the following command to update the articles info. 
This info is about article summary, keywords, download link etc.
```
python articles.py update
```

###### 5. Download articles <br>
To actually download the articles file, use the following command.
```shell script
python articles.py download
```

###### Notes
* You can cancel downloading at any time. All downloaded files are stored and 
wont be downloaded again. 
* You can also use the `update` command periodically to see if a new article in available.
* All downloaded content will be stored in `data` directory.