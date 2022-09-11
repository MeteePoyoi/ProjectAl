# Installation

#### 1. Install Linux development packages

**For Debian and Ubuntu**

```
sudo apt install build-essential
```

**For Redhat**

```
sudo yum groupinstall "Development Tools"
```

#### 2. Install miniforge from https://github.com/conda-forge/miniforge

-   Answer Yes when prompt to activate (base) environment at login
-   Should see **_(base)_** at beginning of command prompt. If not logout and login again

<span style="color:#F78181">_(base) root@localhost: ~$_</span>

#### 3. Setup and Activate virtual environment for python

```
conda create -n autobot python=3.9
conda activate autobot
```

Should see **_(autobot)_** at beginning of command prompt

<span style="color:#F78181">_(autobot) root@localhost: ~$_</span>

#### 4. Install required packages for python

Cautions:

-   must be in **_(autobot)_** environment
-   must be in your installation directory

For Linux

```
conda install icu
conda install pytorch torchvision
pip install -r requirements.txt
```

For OSX

```
conda install -c apple tensorflow-deps=2.9.0
conda install icu
conda install pytorch torchvision

pip install -r requirements-osx.txt
```

---

# Training Model

### _Prepare data file_

Data file must be in CSV format with the following rules

-   2 Field names: `intent_id` and `keyword` on the first line
-   No space after comma
-   No comma(s) within text
-   `intent_id` is an index to response text and can be number or text

```
intent_id,keyword
f7716d57-1666-423a-be1d-7be24010889b,สวัสดี
f7716d57-1666-423a-be1d-7be24010889b,สวัสดีครับ
f7716d57-1666-423a-be1d-7be24010889b,สวัสดีค่ะ
```

### _Train new model_

```
cd training
python training.py --data=PATH/TO/DATAFILE  --save-model=PATH/TO/SAVEMODEL
```

### _Continue Training from previous train_

```
cd training
python training.py --data=PATH/TO/DATAFILE  --save-model=PATH/TO/SAVEMODEL --load-model=PATH/TO/PREVIOUS_MODEL
```

### _After Finish the Training_

-   Folder `SAVEMODEL` and file`SAVEMODEL_labels.pickle` will be created in `PATH/TO`
-   Both folder and file are needed when uses model.

For example

python training.py --data=dataset/v1/q_data.csv --save-mode=model/simple_v1

folder `simple_v1` and file `simple_v1_labels.pickle` will be created in `dataset/v1`

---

# Start API Server

_Note:_ all commands must be executed from _autobot_ folder

#### - Activate autobot environment using conda (assume environment is autobot)

```
conda activate autobot
```

#### - Activate autobot environement using venv (assume venv call autobot)

```
source autobot/bin/activate
```

#### - Run the server using uvicorn

```
export AUTOBOT_CONFIG=config/config.json
uvicorn main:app --reload
```

#### - Run the server using guvicorn

```
export AUTOBOT_CONFIG=config/config.json
server/bin/start.sh
```

### _URLs_

-   API Server: http://localhost:8000
-   OpenAPI: http://localhost:8000/docs
-   Redocs: http://localhost:8000/redoc
