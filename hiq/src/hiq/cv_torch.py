from io import BytesIO

import PIL
import numpy as np
import torch
from datasets import load_dataset, DatasetDict
# ------------ Data -----------------
from hiq.cv_torch_data import IN_CAT, IN_MEAN, IN_STD
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms

DS_PATH_IMAGENET_TINY64_100K = "zh-plus/tiny-imagenet"
DS_PATH_IMAGENET1K = "imagenet-1k"
DS_PATH_IMAGENET100 = "clane9/imagenet-100"
DS_PATH_IMAGENETTE = "frgfm/imagenette"
DS_PATH_PLANTS_600 = "swueste/plants"
DS_PATH_PLANTS_300K = "mikehemberger/plantnet300K"
DS_PATH_HUMAN512_5K = "jlbaker361/flickr_humans_5k"
DS_PATH_HUMAN512_50K = "jlbaker361/flickr_humans_50k"
DS_PATH_COCO30K = "UCSC-VLAA/Recap-COCO-30K"
DS_PATH_COCOPERSON_40K = "Hamdy20002/COCO_Person"
DS_PATH_COCOCAP2017_5K = "lmms-lab/COCO-Caption2017"
DS_PATH_STDDOGS_15K = "amaye15/stanford-dogs"  # 14.4K
DS_PATH_OCRVQA = "howard-hou/OCR-VQA"
DS_PATH_OCRINVREC = "mychen76/invoices-and-receipts_ocr_v1"
DS_PATH_FASHION4_42K = "detection-datasets/fashionpedia_4_categories"
DS_PATH_CELEBA178_203K = "goodfellowliu/CelebA"
DS_PATH_CELEBA256_30K = "korexyz/celeba-hq-256x256"
DS_PATH_CELEBA1024_15K = "PhilSad/celeba-hq-15k"
DS_PATH_COCO122_117K = "detection-datasets/coco"  # 117K
DS_PATH_PHOTOCHAT_HQ_120 = "friedrichor/PhotoChat_120_square_HQ"
DS_PATH_LFW = "vilsonrodrigues/lfw"
DS_PATH_FASHION_MNIST = "fashion_mnist"  # 60K, 10K
DS_PATH_MNIST = "mnist"
DS_PATH_CIFAR10 = "uoft-cs/cifar10"
DS_PATH_HF_TEST = "hf-internal-testing/dummy_image_text_data"
DS_PATH_DOGFOOD_3K = "sasha/dog-food"  # train, test
DS_PATH_OXFLOWER_7K = "nelorth/oxford-flowers"  # 8k
DS_PATH_OXPET_3K = "timm/oxford-iiit-pet"
DS_PATH_BEANS_1K = "AI-Lab-Makerere/beans"
DS_PATH_APPLE_500 = "Francesco/apples-fvpl5"
DS_PATH_FFHQ256_70K = "merkol/ffhq-256"
DS_PATH_FFHQ512_30K = "cld07/captioned_ffhq_512"
DS_PATH_FFHQ128_20K = "AyoubChLin/FFHQ"
DS_PATH_FFHQ32_70K = "idning/ffhq32-caption"
DS_PATH_FFHQ64_70K = "Dmini/FFHQ-64x64"
DS_PATH_FFHQ128_70K = "nuwandaa/ffhq128"
DS_PATH_FFHQ_VINTAGE_1K = "Norod78/Vintage-Faces-FFHQAligned"
DS_PATH_FFHQ1024_4K = "pravsels/FFHQ_1024"
DS_PATH_LSUN_CHURCH120K = "tglcourse/lsun_church_train"
DS_PATH_OPENIMAGES = "dalle-mini/open-images"  # this has all the urls of the images


class ImageLabelDataSet(Dataset):
    """A builtin Dataset class to meet most common needs, and feel free to inherit it."""

    def __init__(self, dataset, transform=None, return_type='dict', split='train', image_size=224, convert_rgb=True,
                 img_key=None, norm=(IN_MEAN, IN_STD), max_num=int(1e100)):
        if isinstance(dataset, DatasetDict) and (split is None or split in dataset):
            split = split or "train"
            self.dataset = dataset[split]
        else:
            self.dataset = dataset
        self.transform = transform
        self.max_num = max_num
        self.return_type = return_type
        self.image_size_pair = (image_size, image_size) if isinstance(image_size, int) else image_size
        if img_key is None:
            self.img_key = 'image' if 'image' in self.dataset.column_names else 'img'
        else:
            self.img_key = img_key
        self.label_key = 'label' if 'label' in self.dataset.column_names else 'lbl'
        self.convert_rgb = convert_rgb
        self.to_tensor_transform = transforms.ToTensor()
        if self.image_size_pair is not None:
            self.resize_transform = transforms.Resize(self.image_size_pair)
        if self.label_key not in self.dataset.column_names:
            self.label_key = None
        if transform is None:
            self.normalize_transform = transforms.Normalize(mean=norm[0], std=norm[1])
        else:
            # Check if self.transform contains a resize operation
            contains_resize = False
            if self.transform:
                for t in self.transform.transforms:
                    if isinstance(t, transforms.Resize) or isinstance(t, transforms.RandomResizedCrop):
                        contains_resize = True
                        break
            if not contains_resize and self.image_size_pair is not None:
                # Check the size of the first image in the dataset
                first_image = self.dataset[self.img_key][0]
                if isinstance(first_image, torch.Tensor):
                    first_image = transforms.ToPILImage()(first_image)
                first_image_size = first_image.size  # (width, height)

                # Add a resize transform if image size does not match
                if first_image_size != self.image_size_pair:
                    resize_transform = transforms.Resize(self.image_size_pair)
                    if self.transform:
                        # Insert the resize transform at the beginning
                        self.transform.transforms.append(resize_transform)
                    else:
                        self.resize_transform = transforms.Resize(self.image_size_pair)

    def __len__(self):
        l = len(self.dataset)
        return min(l, self.max_num)

    def handle_pil_image(self, pil_img):
        if isinstance(pil_img, PIL.JpegImagePlugin.JpegImageFile):
            return pil_img
        with BytesIO() as output:
            pil_img.save(output, format='JPEG')
            img_bytes = output.getvalue()
        img = PIL.Image.open(BytesIO(img_bytes))
        return img

    def __getitem__(self, idx):
        item = self.dataset[idx]
        # if self.img_key not in item:
        #    print(item.keys())
        img = item[self.img_key]
        if self.convert_rgb and img.mode != 'RGB':
            img = img.convert('RGB')
        img = self.handle_pil_image(img)
        if self.transform is None:
            if isinstance(self.image_size_pair, tuple):
                img = self.resize_transform(img)
            img = self.to_tensor_transform(img)
            img_ = self.normalize_transform(img)
        else:
            img_ = self.transform(img)

        if self.return_type == 'image_only':
            return img_
        elif self.return_type == 'pair':
            return img_, item[self.label_key] if self.label_key else ''
        else:
            del item[self.img_key]
            item['image'] = img_
            return item


def get_cv_dataset(path=DS_PATH_IMAGENETTE,
                   name=None,
                   batch_size=1,
                   image_size=None,
                   split=None,
                   shuffle=True,
                   num_workers=4,
                   transform=None,
                   return_loader=False,
                   return_type='pair',
                   convert_rgb=True,
                   img_key=None,
                   datasetclass=ImageLabelDataSet,
                   max_num=int(1e100),
                   # explicit distributed training
                   rank=None,
                   world_size=None,
                   **loader_params):
    """
    image_size: None - no resize, otherwise resize to image_sizeximage_size
    In PyTorch Lightning, you do not need to manually use DistributedSampler for your dataset or data loader.
    PyTorch Lightning automatically handles distributed training under the hood, including setting up the appropriate
    data sampling strategies.
    """
    if return_type not in ['image_only', 'pair', 'dict']:
        raise ValueError("return_type must be 'image_only' or 'pair' or 'dict'")

    if path == DS_PATH_IMAGENETTE:
        if name is None:
            name = "full_size"
        assert name in ('160px', '320px', 'full_size')
    elif path == DS_PATH_IMAGENET1K:
        name = None
    elif path == DS_PATH_OPENIMAGES:
        img_key = 'url'
        name = "default"
    elif path == DS_PATH_STDDOGS_15K:
        img_key = 'pixel_values'
    elif path == DS_PATH_FFHQ512_30K:
        img_key = 'source_image'
    elif path == DS_PATH_MNIST:
        name = 'mnist'
    elif path == DS_PATH_FASHION_MNIST:
        name = 'fashion_mnist'
    try:
        dataset = load_dataset(path, name, trust_remote_code=True, split=split)
    except ValueError as e:
        print("☠", e)
        dataset = load_dataset(path, name, trust_remote_code=True, split='train')

    if isinstance(split, str):
        custom_dataset = datasetclass(dataset,
                                      transform=transform,
                                      return_type=return_type,
                                      split=split,
                                      image_size=image_size,
                                      convert_rgb=convert_rgb,
                                      img_key=img_key,
                                      max_num=max_num)
        if return_loader:
            if rank is None or world_size is None or world_size == 1:
                return DataLoader(custom_dataset,
                                  batch_size=batch_size,
                                  shuffle=shuffle,
                                  num_workers=num_workers,
                                  **loader_params)
            else:
                sampler = torch.utils.data.DistributedSampler(
                    custom_dataset, num_replicas=world_size, rank=rank, shuffle=shuffle
                )
                return DataLoader(dataset=custom_dataset,
                                  batch_size=batch_size,
                                  sampler=sampler,
                                  num_workers=num_workers,
                                  **loader_params)
        else:
            return custom_dataset
    else:
        datasets_or_loader = {}
        for split_name in dataset.keys():
            datasets_or_loader[split_name] = datasetclass(dataset,
                                                          transform=transform,
                                                          return_type=return_type,
                                                          split=split_name,
                                                          image_size=image_size,
                                                          convert_rgb=convert_rgb,
                                                          img_key=img_key,
                                                          max_num=max_num)
        if return_loader:
            for split_name in datasets_or_loader:
                if rank is None or world_size is None or world_size == 1:
                    datasets_or_loader[split_name] = DataLoader(dataset=datasets_or_loader[split_name],
                                                                batch_size=batch_size,
                                                                shuffle=shuffle,
                                                                num_workers=num_workers,
                                                                **loader_params)
                else:
                    sampler = torch.utils.data.DistributedSampler(
                        datasets_or_loader[split_name], num_replicas=world_size, rank=rank, shuffle=shuffle
                    )
                    datasets_or_loader[split_name] = DataLoader(dataset=datasets_or_loader[split_name],
                                                                batch_size=batch_size,
                                                                sampler=sampler,
                                                                num_workers=num_workers,
                                                                **loader_params)
        return datasets_or_loader


def get_datasplit(d, s):
    if isinstance(d, dict):
        if s in ("validation", 'val'):
            if 'val' in d:
                return d['val']
            if 'validation' in d:
                return d['validation']
            if 'test' in d:
                print(f"🔥 Warning: no validation set, use test set instead.")
                return d['test']
        if s in d:
            return d[s]
        else:
            if s == 'test' and s not in d:
                return get_datasplit(d, 'validation')
            err_msg = f"☠ error: no split:{s} in dataset:{d}!"
            print(err_msg)
            return d['train']
    return d


def ensure_split(d, train_ratio=0.9, val_key='test'):
    assert train_ratio < 1.0
    if isinstance(d, dict):
        if 'train' in d and ('val' in d) or ('test' in d) or ('validation' in d):
            return d
        if 'train' in d and len(d.keys()) == 1:
            r = d['train']
        train_size = int(train_ratio * len(r))
        val_size = len(r) - train_size
        train_dataset, val_dataset = random_split(r, [train_size, val_size])
        d['train'], d[val_key] = train_dataset, val_dataset
    else:
        train_size = int(train_ratio * len(d))
        val_size = len(d) - train_size
        train_dataset, val_dataset = random_split(d, [train_size, val_size])
        d = {}
        d['train'], d[val_key] = train_dataset, val_dataset
    return d


try:
    import lightning
    from torch.utils.data.dataloader import default_collate


    class DataModuleFromConfig(lightning.LightningDataModule):
        def __init__(
                self,
                dataset_name="frgfm/imagenette",
                batch_size=1,
                image_size=None,
                num_workers=1,
                config_name="full_size",
                split=None,
                shuffle=True,
                convert_rgb=True,
        ):
            super().__init__()
            self.dataset_name = dataset_name
            self.batch_size = batch_size
            self.image_size = image_size
            self.dataset_configs = dict()
            self.num_workers = num_workers
            self.config_name = config_name
            self.split = split
            self.shuffle = shuffle
            self.convert_rgb = convert_rgb

            self.train_dataloader = self._train_dataloader
            self.val_dataloader = self._val_dataloader

        def setup(self, stage=None):
            self.datasets = get_cv_dataset(
                path=self.dataset_name,
                name=self.config_name,
                image_size=self.image_size,
                split=self.split,
                batch_size=self.batch_size,
                num_workers=self.num_workers,
                return_type="dict",
                convert_rgb=self.convert_rgb,
            )

        def _train_dataloader(self):
            return DataLoader(
                get_datasplit(self.datasets, "train"),
                batch_size=self.batch_size,
                num_workers=self.num_workers,
                shuffle=self.shuffle,
                collate_fn=default_collate,
                pin_memory=True,
            )

        def _val_dataloader(self):
            return DataLoader(
                get_datasplit(self.datasets, "validation"),
                batch_size=self.batch_size,
                num_workers=self.num_workers,
                collate_fn=default_collate,
                shuffle=False,
                pin_memory=True,
            )

        def _test_dataloader(self):
            return DataLoader(
                get_datasplit(self.datasets, "test"),
                batch_size=self.batch_size,
                num_workers=self.num_workers,
                collate_fn=default_collate,
                shuffle=False,
                pin_memory=True,
            )

except:
    pass


def imshow(img):
    from matplotlib import pyplot as plt
    img = img / 2 + 0.5  # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


def verify_datasets(dataset_names=('fashion_mnist',), sz=128, batch_size=2):  # "cifar10", 'mnist', DS_PATH_CELEBA
    from tqdm import tqdm

    transform = transforms.Compose(
        [
            transforms.RandomHorizontalFlip(p=0.3),
            # transforms.RandomResizedCrop(sz, scale=(0.5, 0.95), ratio=(1.3, 2.0)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
        ]
    )
    loader_params = dict(
        shuffle=False,
        drop_last=True,
        pin_memory=True,
    )
    for n in dataset_names:
        dataloader = get_cv_dataset(path=n,
                                    image_size=sz,
                                    split='validation',
                                    batch_size=batch_size,
                                    num_workers=2,
                                    transform=transform,
                                    return_type="pair",
                                    return_loader=True,
                                    convert_rgb=True,
                                    **loader_params
                                    )
        with tqdm(dataloader, dynamic_ncols=True, colour="#ff924a") as data:
            for images, label in data:
                print(images.shape)
                if n == 'mnist':
                    assert (images.shape == torch.Size([batch_size, 3, sz, sz]))
                else:
                    assert (images.shape == torch.Size([batch_size, 3, sz, sz]))
                imshow(images[0])
                if n == DS_PATH_IMAGENET1K:
                    print(IN_CAT[label[0].item()])
                imshow(images[1])
                if n == DS_PATH_IMAGENET1K:
                    print(IN_CAT[label[1].item()])
                break


if __name__ == "__main__":
    verify_datasets((DS_PATH_IMAGENET1K,), sz=128)
    '''
    datasets = get_cv_dataset(path=DS_PATH_IMAGENETTE,
                              image_size=256,
                              split=None,
                              batch_size=2,
                              num_workers=2,
                              return_type="dict")
    validation_dataset = datasets["validation"]
    print(validation_dataset)

    datasets = get_cv_dataset(path=DS_PATH_IMAGENETTE, return_loader=False, name='full_size', split=None)
    validation_dataset = datasets["validation"]
    print(validation_dataset)'''
