# Redpitaya-IO-Sync
Library for Synchronous and Deterministic Control of Redpitaya Digital and Analog IOs



### Virtual Environment (optional)
* Create virtual environment 
    ```
    sudo apt update
    sudo apt install python3-venv
    python3 -m venv .venv
    
    ```
* Activate virtual environment
    ```
    source .venv/bin/activate     # Linux / macOS
    # .venv\Scripts\activate      # Windows
    ```


### Local Installation
* Navigate to python lib and install via pip3 (-e for editable install):
    ```
    cd redpitaya-io-sync
    python3 -m pip install --upgrade pip setuptools wheel
    pip3 install -e .
    ```