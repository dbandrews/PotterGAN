PotterGAN
==============================

A GAN for generating novel pottery designs.

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          
    ├── data               <- Data for a variety of ceramic items separated into subfolders. 
    │   ├── mugs            

    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │


## Setup 

* To run image scraping/processing scripts - follow the steps on Alexey B's fork of darknet: https://github.com/AlexeyAB/darknet#how-to-use-yolo-as-dll-and-so-libraries. 
Note that installing Visual Studio first, then CUDA+CUDNN is required to get it to build with CUDA support. Build darknet.exe, and yolo_cpp_dll.dll. 
(https://github.com/AlexeyAB/darknet#how-to-use-yolo-as-dll-and-so-libraries )

    + Place pthreadVC2.dll, yolo_cpp_dll.dll in scripts folder.
    + Place yolov4.weights in scripts/cfg folder (links to download in Darknet repo)

