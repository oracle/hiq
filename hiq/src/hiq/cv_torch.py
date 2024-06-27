import numpy as np
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from datasets import load_dataset, DatasetDict
from PIL import Image
from io import BytesIO

IN_MEAN = np.array([0.485, 0.456, 0.406])
IN_STD = np.array([0.229, 0.224, 0.225])

DS_PATH_IMAGENET = "imagenet-1k"
DS_PATH_IMAGENETTE = "frgfm/imagenette"


class ImageLabelDataSet(Dataset):
    def __init__(self, dataset, transform=None, return_type='dict', split='train', image_size=224):
        if isinstance(dataset, DatasetDict) and (split is None or split in dataset):
            split = split or "train"
            self.dataset = dataset[split]
        else:
            self.dataset = dataset
        self.transform = transform
        self.return_type = return_type
        self.image_size = image_size
        if transform is None:
            if isinstance(self.image_size, int):
                self.resize_transform = transforms.Resize((image_size, image_size))
            self.to_tensor_transform = transforms.ToTensor()
            self.normalize_transform = transforms.Normalize(mean=IN_MEAN, std=IN_STD)

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        img = item['image']
        label = item['label']

        if img.mode != 'RGB':
            img = img.convert('RGB')
        with BytesIO() as output:
            img.save(output, format='JPEG')
            img_bytes = output.getvalue()
        img = Image.open(BytesIO(img_bytes))
        if self.transform is None:
            if isinstance(self.image_size, int):
                img = self.resize_transform(img)
            img = self.to_tensor_transform(img)
            img = self.normalize_transform(img)
        else:
            img = self.transform(img)

        if self.return_type == 'image_only':
            return img
        elif self.return_type == 'pair':
            return img, label
        else:
            item['image'] = img
            return item


def get_cv_dataset(path=DS_PATH_IMAGENETTE,
                   name=None,  # "full_size"
                   batch_size=1,
                   image_size=224,
                   split=None,  # 'train'
                   shuffle=True,
                   num_workers=1,
                   transform=None,
                   return_loader=False,
                   return_type='pair'):
    if return_type not in ['image_only', 'pair', 'dict']:
        raise ValueError("return_type must be 'image_only' or 'pair' or 'dict'")
    dataset = load_dataset(path, name, split=split, trust_remote_code=True)
    custom_dataset = ImageLabelDataSet(dataset, transform=transform, return_type=return_type, split=split,
                                       image_size=image_size)

    if return_loader:
        return DataLoader(custom_dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
    else:
        return custom_dataset
