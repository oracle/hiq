"""
+🔵
├── +conv1 (Conv2d) weight:[64, 3, 7, 7]
├── +bn1 (BatchNorm2d) weight:[64] bias:[64]
├── +layer1 (Sequential)
│   ├── +0 (Bottleneck)
│   │   ├── +conv1 (Conv2d) weight:[64, 64, 1, 1]
│   │   ├── bn1,bn2(BatchNorm2d) weight:[64] bias:[64]
│   │   ├── +conv2 (Conv2d) weight:[64, 64, 3, 3]
│   │   ├── +conv3 (Conv2d) weight:[256, 64, 1, 1]
│   │   ├── +bn3 (BatchNorm2d) weight:[256] bias:[256]
│   │   └── +downsample (Sequential)
│   │       ├── +0 (Conv2d) weight:[256, 64, 1, 1]
│   │       └── +1 (BatchNorm2d) weight:[256] bias:[256]
│   └── 1-2(Bottleneck)
│       ├── +conv1 (Conv2d) weight:[64, 256, 1, 1]
│       ├── bn1,bn2(BatchNorm2d) weight:[64] bias:[64]
│       ├── +conv2 (Conv2d) weight:[64, 64, 3, 3]
│       ├── +conv3 (Conv2d) weight:[256, 64, 1, 1]
│       └── +bn3 (BatchNorm2d) weight:[256] bias:[256]
├── +layer2 (Sequential)
│   ├── +0 (Bottleneck)
│   │   ├── +conv1 (Conv2d) weight:[128, 256, 1, 1]
│   │   ├── bn1,bn2(BatchNorm2d) weight:[128] bias:[128]
│   │   ├── +conv2 (Conv2d) weight:[128, 128, 3, 3]
│   │   ├── +conv3 (Conv2d) weight:[512, 128, 1, 1]
│   │   ├── +bn3 (BatchNorm2d) weight:[512] bias:[512]
│   │   └── +downsample (Sequential)
│   │       ├── +0 (Conv2d) weight:[512, 256, 1, 1]
│   │       └── +1 (BatchNorm2d) weight:[512] bias:[512]
│   └── 1-7(Bottleneck)
│       ├── +conv1 (Conv2d) weight:[128, 512, 1, 1]
│       ├── bn1,bn2(BatchNorm2d) weight:[128] bias:[128]
│       ├── +conv2 (Conv2d) weight:[128, 128, 3, 3]
│       ├── +conv3 (Conv2d) weight:[512, 128, 1, 1]
│       └── +bn3 (BatchNorm2d) weight:[512] bias:[512]
├── +layer3 (Sequential)
│   ├── +0 (Bottleneck)
│   │   ├── +conv1 (Conv2d) weight:[256, 512, 1, 1]
│   │   ├── bn1,bn2(BatchNorm2d) weight:[256] bias:[256]
│   │   ├── +conv2 (Conv2d) weight:[256, 256, 3, 3]
│   │   ├── +conv3 (Conv2d) weight:[1024, 256, 1, 1]
│   │   ├── +bn3 (BatchNorm2d) weight:[1024] bias:[1024]
│   │   └── +downsample (Sequential)
│   │       ├── +0 (Conv2d) weight:[1024, 512, 1, 1]
│   │       └── +1 (BatchNorm2d) weight:[1024] bias:[1024]
│   └── 1-35(Bottleneck)
│       ├── +conv1 (Conv2d) weight:[256, 1024, 1, 1]
│       ├── bn1,bn2(BatchNorm2d) weight:[256] bias:[256]
│       ├── +conv2 (Conv2d) weight:[256, 256, 3, 3]
│       ├── +conv3 (Conv2d) weight:[1024, 256, 1, 1]
│       └── +bn3 (BatchNorm2d) weight:[1024] bias:[1024]
├── +layer4 (Sequential)
│   ├── +0 (Bottleneck)
│   │   ├── +conv1 (Conv2d) weight:[512, 1024, 1, 1]
│   │   ├── bn1,bn2(BatchNorm2d) weight:[512] bias:[512]
│   │   ├── +conv2 (Conv2d) weight:[512, 512, 3, 3]
│   │   ├── +conv3 (Conv2d) weight:[2048, 512, 1, 1]
│   │   ├── +bn3 (BatchNorm2d) weight:[2048] bias:[2048]
│   │   └── +downsample (Sequential)
│   │       ├── +0 (Conv2d) weight:[2048, 1024, 1, 1]
│   │       └── +1 (BatchNorm2d) weight:[2048] bias:[2048]
│   └── 1-2(Bottleneck)
│       ├── +conv1 (Conv2d) weight:[512, 2048, 1, 1]
│       ├── bn1,bn2(BatchNorm2d) weight:[512] bias:[512]
│       ├── +conv2 (Conv2d) weight:[512, 512, 3, 3]
│       ├── +conv3 (Conv2d) weight:[2048, 512, 1, 1]
│       └── +bn3 (BatchNorm2d) weight:[2048] bias:[2048]
└── +fc (Linear) weight:[1000, 2048] bias:[1000]
"""
import torch
import torchvision
from hiq.vis import print_model


model = torchvision.models.resnet152()
model.conv1.weight.requires_grad = False
model.layer3[1].conv1.weight.requires_grad = False
model.layer4[0].bn3.bias.requires_grad = False
model = model.cuda()
with torch.no_grad():
    print(model.layer3[2].conv1.weight.requires_grad)
    print("*" * 80)
    print_model(model)
    #print_model(model, max_depth=3)
    #print_model(model, only_types=("Conv2d","Linear",'Bottleneck','Sequential'))
    #print_model(model, only_names=('layer1','0','bn3','conv1'))
