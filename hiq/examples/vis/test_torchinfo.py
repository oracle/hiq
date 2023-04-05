from torchinfo import summary
import torchvision

model = torchvision.models.resnet152()
summary(model)
