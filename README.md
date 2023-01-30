<div align="center">
<h1 align="center">Unreal Remote Render Farm</h1>

  <p align="center">
    Unreal Engine 5 remote render farm, a prototype for managing remote render
requests and distribute render jobs over the network with REST API.
Utilizes Unreal's Python
and Movie Render Queue plugins.
    <br />
    <a href="https://youtu.be/4pGhaMQACy8">Demo</a>
  </p>
</div>


## About The Project

<div align="center">
<img src="https://i.imgur.com/nk6CKQY.png" alt="preview"/>
</div>

The Unreal Render Farm is a side project of mine starting from 12/23/2022.
I broke down the topics that involves developing this project into each self-contained blog. 

- [Automate Unreal Rendering Using Python](https://www.xingyulei.com/post/ue-rendering-basic/)
- [Building HTTP Server with REST API in Python](https://www.xingyulei.com/post/py-http-server/)
- [Unreal Movie Render Queue (MRQ) Custom Executor](https://www.xingyulei.com/post/ue-rendering-custom-executor/)

And finally a complete break-down of the components and walk-through of the project:
- [Unreal Distributed Rendering Server Guide (Render Farm Implementation)](https://www.xingyulei.com/post/ue-rendering-remote-farm)

## Getting Started

### Prerequisites


- [Flask](https://pypi.org/project/Flask/): a micro web framework for creating APIs in Python
    ```
    pip install -U Flask
    ```
  the path to `flask.exe` needs to be specified in `requestManager.py`


- An Unreal Project with Movie Render Queue plugin enabled and at least one sequencer properly set up. 
The render farm needs at least
on render job to run, which requires a map/level, a level sequence and a master config.
  - the unreal executable and project path needs to be specified in `requestWorker.py`
  - the test job needs to be specified in `requestSubmitter.py`

### Launch

1. Run the `requestManager.py` first, which launches the server on `http://localhost:5000/`
2. Submit render jobs using `requestSubmitter.py`
3. (Optional) Browse render jobs statues in browser at server url
4. Render jobs by running `requestWorker.py`

