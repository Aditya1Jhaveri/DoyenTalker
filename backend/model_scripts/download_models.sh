mkdir ./checkpoints  


#### Model links from google drive.
gdown 12MmoyH-UUQTQr3WOZXSXD3HV10iwUoba -O ./checkpoints/doyenTalker_V0.0.2_256.safetensors
gdown 1_IaiMJ3q3noEWqJmjXemHFx77byymZMh -O ./checkpoints/mapping_00229-model.pth
gdown 1gR4l5leM5mfKKeSOWtY6wplFikxGehgX -O ./checkpoints/mapping_00109-model.pth.tar

### enhancer 
mkdir -p ./gfpgan/weights
wget -nc https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth -O ./gfpgan/weights/alignment_WFLW_4HG.pth 
wget -nc https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth -O ./gfpgan/weights/detection_Resnet50_Final.pth 
wget -nc https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth -O ./gfpgan/weights/GFPGANv1.4.pth 
wget -nc https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth -O ./gfpgan/weights/parsing_parsenet.pth 

