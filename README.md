# FineGrainedAD: Towards Fine-Grained Vision-Language Alignment for Few-Shot Anomaly Detection

Official implementation of **FineGrainedAD** (Accepted by *Pattern Recognition 2026*).

[[Paper (Elsevier)]](https://doi.org/10.1016/j.patcog.2026.113316) [[arXiv]](https://arxiv.org/pdf/2510.26464)

## Overview

FineGrainedAD proposes Multi-Level Fine-Grained Semantic Caption (MFSC) and a novel framework consisting of Multi-Level Learnable Prompt (MLLP) and Multi-Level Semantic Alignment (MLSA) to achieve component-level few-shot anomaly detection.

## Install

**Environment**: Python 3.9, CUDA 11.8, PyTorch 2.1

```bash
bash install.sh
```

## Data

We support three anomaly detection datasets: **MVTec-AD**, **VisA**, and **RealIAD**.

Set up soft links in `datasets/anomaly_detection/`:
```bash
mkdir -p datasets/anomaly_detection
ln -s /path/to/mvtec_anomaly_detection datasets/anomaly_detection/mvtec_anomaly_detection
ln -s /path/to/VisA datasets/anomaly_detection/VisA
ln -s /path/to/realiad datasets/anomaly_detection/realiad
```

## Run

### Pixel-level anomaly segmentation (training + evaluation)
```bash
python run_seg_finegrained_patch.py
```

### Image-level anomaly classification (training + evaluation)
```bash
python run_cls_finegrained_patch.py
```

### Test only (with pre-trained checkpoints)
```bash
python run_test_seg_finegrained_patch.py
python run_test_cls_finegrained_patch.py
```

### Single class training/testing
```bash
# Train segmentation for a single class
python train_seg_finegrained_patch.py --dataset mvtec --class_name bottle --k-shot 4

# Test segmentation for a single class
python test_seg_finegrained_patch.py --dataset mvtec --class_name bottle --k-shot 4
```

## Code Structure
```
├── PromptAD/
│   ├── CLIPAD/                        # Modified OpenCLIP framework
│   │   ├── transformer.py             # Contains QueryFormer
│   │   └── model_configs/             # ViT model configurations
│   ├── model.py                       # Core model (FineGrainedPatchAD)
│   ├── ad_prompts.py                  # Anomaly detection prompt templates
│   ├── fine_grained_prompts.py        # MFSC for MVTec-AD, VisA, RealIAD
│   └── clusters.py                    # DPC-KNN clustering (CTM, TCBlock)
├── datasets/
│   ├── mvtec.py, visa.py, realiad.py  # Dataset loaders
│   ├── dataset.py                     # CLIPDataset base class
│   ├── seeds_mvtec/                   # Few-shot sample seeds
│   ├── seeds_visa/
│   ├── seeds_realiad/
│   └── cluster_gt/                    # Pre-defined clustering GT
├── utils/                             # Metrics, visualization, etc.
├── train_seg_finegrained_patch.py     # Pixel-level training
├── test_seg_finegrained_patch.py      # Pixel-level testing
├── train_cls_finegrained_patch.py     # Image-level training
├── test_cls_finegrained_patch.py      # Image-level testing
├── run_seg_finegrained_patch.py       # Multi-process seg training
├── run_test_seg_finegrained_patch.py  # Multi-process seg testing
├── run_cls_finegrained_patch.py       # Multi-process cls training
└── run_test_cls_finegrained_patch.py  # Multi-process cls testing
```

## Citation
```
@article{fan2026finegrainedad,
title = {Towards Fine-Grained Vision-Language Alignment for Few-Shot Anomaly Detection},
journal = {Pattern Recognition},
volume = {178},
pages = {113316},
year = {2026},
issn = {0031-3203},
doi = {https://doi.org/10.1016/j.patcog.2026.113316},
url = {https://www.sciencedirect.com/science/article/pii/S0031320326002815},
author = {Yuanting Fan and Jun Liu and Xiaochen Chen and Bin-Bin Gao and Jian Li and Yong Liu and Jinlong Peng and Chengjie Wang}
}
```

## Acknowledgement

We thank the great works [WinCLIP](https://github.com/zqhang/Accurate-WinCLIP-pytorch.git), [CoOp](https://github.com/KaiyangZhou/CoOp.git), and [PromptAD](https://github.com/FuNz-0/PromptAD.git) for assisting with our work.
