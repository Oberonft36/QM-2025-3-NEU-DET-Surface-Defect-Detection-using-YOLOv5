# env_report.md

## 0. 从零训练说明

本项目严格按照要求从零训练，未加载任何 `.pt` 预训练权重。



## 1. YOLOv5 获取方式

本项目未使用 `pip install ultralytics` 或 `conda install ultralytics` 作为黑盒训练入口，而是通过 GitHub 克隆 YOLOv5 源码仓库完成环境搭建与训练流程分析。

获取命令：

```bash
git clone https://github.com/ultralytics/yolov5.git
```

存放路径：

```
third_party/yolov5
```



## 2. YOLOv5 目录结构

克隆后 YOLOv5 项目的主要目录结构如下：

```
yolov5/
├── models/       
├── data/         
├── utils/         
├── train.py       
├── val.py       
├── detect.py     
├── requirements.txt
└── README.md
```



## 3. 训练入口分析

本项目使用 YOLOv5 源码中的训练脚本：

```
third_party/yolov5/train.py
```

通过直接调用该脚本实现“从零训练”。



## 4. Python 与依赖环境

- Conda 环境名：`dl2026`
- Python 版本：`3.10.20`
- PyTorch 版本：`2.11.0 + cu130`
- CUDA：可用（GPU 加速训练）
- 依赖安装方式：

```
pip install -r requirements.txt
```



## 5. 数据集配置文件（neu_det.yaml）

数据集配置文件路径：

```
configs/neu_det.yaml
```

内容如下：

```
train: datasets/neu_det_yolo/images/train
val: datasets/neu_det_yolo/images/val
test: datasets/neu_det_yolo/images/test

nc: 6

names:
  0: crazing
  1: inclusion
  2: patches
  3: pitted_surface
  4: rolled-in_scale
  5: scratches
```



## 6. 训练参数说明

本实验采用从零训练（未加载任何预训练权重），关键参数如下：

- 模型结构：YOLOv5n
- epoch：100
- batch size：16
- 输入尺寸：640
- 设备：GPU（device=0）



## 7. 训练过程问题与解决

配图

在训练过程中，Windows 环境下出现 DataLoader worker 异常退出问题：

```
RuntimeError: DataLoader worker exited unexpectedly
```

解决方法：

```
--workers 0
```

通过关闭多进程数据加载解决