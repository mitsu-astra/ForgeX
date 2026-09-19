"""
Dataset module for Industrial Defect Visual Inspection
Handles image loading, stratified train/val/test splitting, and data augmentations.
"""

import os
import glob
from typing import Tuple, List, Dict, Optional
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.model_selection import train_test_split

CLASSES = ["crack", "hole", "normal", "rust", "scratch"]
CLASS_TO_IDX = {cls_name: i for i, cls_name in enumerate(CLASSES)}
IDX_TO_CLASS = {i: cls_name for i, cls_name in enumerate(CLASSES)}

# ImageNet statistics for normalization
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_transforms(img_size: int = 224) -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Returns train and validation/test torchvision transform pipelines.
    """
    train_transform = transforms.Compose([
        transforms.Resize((img_size + 32, img_size + 32)),
        transforms.RandomResizedCrop(img_size, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    return train_transform, val_transform


class DefectDataset(Dataset):
    """
    PyTorch Dataset for visual defect inspection images.
    """

    def __init__(self, samples: List[Tuple[str, int]], transform: Optional[transforms.Compose] = None):
        """
        Args:
            samples: List of (file_path, class_idx) tuples.
            transform: PyTorch image transformations.
        """
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, str]:
        path, label = self.samples[idx]
        try:
            with Image.open(path) as img:
                # Ensure 3-channel RGB representation
                img_rgb = img.convert("RGB")
        except Exception as e:
            raise RuntimeError(f"Error loading image {path}: {e}")

        if self.transform is not None:
            tensor = self.transform(img_rgb)
        else:
            tensor = transforms.ToTensor()(img_rgb)

        return tensor, label, path


def build_datasets(
    data_dir: str,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
    img_size: int = 224,
) -> Tuple[DefectDataset, DefectDataset, DefectDataset, Dict[str, int]]:
    """
    Scans data directory, splits into stratified train, val, and test sets.

    Returns:
        (train_dataset, val_dataset, test_dataset, class_counts)
    """
    all_samples: List[Tuple[str, int]] = []
    class_counts: Dict[str, int] = {}

    for cls_name in CLASSES:
        cls_dir = os.path.join(data_dir, cls_name)
        if not os.path.isdir(cls_dir):
            continue

        file_patterns = ["*.png", "*.jpg", "*.jpeg", "*.bmp"]
        files = []
        for pat in file_patterns:
            files.extend(glob.glob(os.path.join(cls_dir, pat)))
            files.extend(glob.glob(os.path.join(cls_dir, pat.upper())))

        files = sorted(list(set(files)))
        class_idx = CLASS_TO_IDX[cls_name]
        class_counts[cls_name] = len(files)

        for f in files:
            all_samples.append((f, class_idx))

    if not all_samples:
        raise ValueError(f"No valid images found in {data_dir} across classes {CLASSES}")

    paths = [s[0] for s in all_samples]
    labels = [s[1] for s in all_samples]

    # Stratified split: Train (70%) vs Rest (30%)
    train_paths, rest_paths, train_labels, rest_labels = train_test_split(
        paths, labels, test_size=(val_ratio + test_ratio), random_state=seed, stratify=labels
    )

    # Stratified split: Val (15%) vs Test (15%)
    val_prop = val_ratio / (val_ratio + test_ratio)
    val_paths, test_paths, val_labels, test_labels = train_test_split(
        rest_paths, rest_labels, test_size=(1.0 - val_prop), random_state=seed, stratify=rest_labels
    )

    train_samples = list(zip(train_paths, train_labels))
    val_samples = list(zip(val_paths, val_labels))
    test_samples = list(zip(test_paths, test_labels))

    train_tf, val_tf = get_transforms(img_size=img_size)

    train_dataset = DefectDataset(train_samples, transform=train_tf)
    val_dataset = DefectDataset(val_samples, transform=val_tf)
    test_dataset = DefectDataset(test_samples, transform=val_tf)

    return train_dataset, val_dataset, test_dataset, class_counts


def get_dataloaders(
    data_dir: str,
    batch_size: int = 32,
    num_workers: int = 4,
    img_size: int = 224,
    seed: int = 42,
) -> Tuple[DataLoader, DataLoader, DataLoader, Dict[str, int]]:
    """
    Helper function to get PyTorch DataLoaders for train, val, and test splits.
    """
    train_ds, val_ds, test_ds, counts = build_datasets(
        data_dir=data_dir,
        seed=seed,
        img_size=img_size,
    )

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=False,
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=False,
    )

    test_loader = DataLoader(
        test_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        drop_last=False,
    )

    return train_loader, val_loader, test_loader, counts
