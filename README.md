# testing 

1. install uv for fast pip installations
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
2. initialise the virual env 
```sh
uv venv
```
3. sourcing the virtual environment 
```sh 
source .venv/bin/activate
```
4. running the main app 
```sh 
python main.py #should initialise the models 
```
5. testing the websocket 
```sh 
 python3 -m websockets ws://localhost:8000/ws/debug
```


