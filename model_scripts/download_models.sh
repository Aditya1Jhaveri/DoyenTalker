mkdir ./checkpoints  


#### Model links from google drive.
gdown --id 1x5EW6kIhgC72Jj0yod3hUPQYPF6ARxvq -O ./checkpoints/doyenTalker_V0.0.2_256.safetensors
gdown --id 1C-Bp2O-YvlDZKZHbVwDHTYslpGLvml0Q -O ./checkpoints/mapping_00229-model.pth
gdown --id 1nYFblibZUZ9jZDl5n0vI0AMnhK8-i9Nq -O  ./checkpoints/mapping_00109-model.pth.tar

### enhancer 
mkdir -p ./gfpgan/weights
wget -nc https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth -O ./gfpgan/weights/alignment_WFLW_4HG.pth 
wget -nc https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth -O ./gfpgan/weights/detection_Resnet50_Final.pth 
wget -nc https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth -O ./gfpgan/weights/GFPGANv1.4.pth 
wget -nc https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth -O ./gfpgan/weights/parsing_parsenet.pth 

