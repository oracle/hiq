from hiq.cv_torch import *


def check_imagenette():
    dataset_train = get_cv_dataset(transform=None, name="full_size", split='train', return_type='pair')
    sampler_train = RandomSampler(dataset_train)
    data_loader_train = DataLoader(
        dataset_train, sampler=sampler_train,
        batch_size=4,  # Adjust batch size here
        num_workers=1,  # Adjust number of workers here
        pin_memory=True,  # Adjust pin memory here
        drop_last=True,
    )
    for i, (img, label) in enumerate(data_loader_train):
        print(i, img.shape, label)
        break


def check_imagenet1k():
    """
    Expect output:
    0 torch.Size([1, 3, 224, 224]) tensor([726])
    0 torch.Size([1, 3, 224, 224])
    0 dict_keys(['image', 'label'])
    """
    dataset_train = get_cv_dataset(path="imagenet-1k", return_type='pair')
    data_loader_train = DataLoader(dataset_train)
    for i, (img, label) in enumerate(data_loader_train):
        print(i, img.shape, label)
        break
    dataset_train = get_cv_dataset(path="imagenet-1k", return_type='image_only')
    data_loader_train = DataLoader(dataset_train)
    for i, (img) in enumerate(data_loader_train):
        print(i, img.shape)
        break
    dataset_train = get_cv_dataset(path="imagenet-1k", return_type='dict')
    data_loader_train = DataLoader(dataset_train)
    for i, (img) in enumerate(data_loader_train):
        print(i, img.keys())
        break


if __name__ == '__main__':
    check_imagenet1k()
    check_imagenette()
