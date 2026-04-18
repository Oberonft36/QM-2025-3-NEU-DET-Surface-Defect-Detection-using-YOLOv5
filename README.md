好，我们从最稳的起点开始：先把**项目骨架**搭好，再进入**数据源核验**。这也符合你这道题的默认推进顺序：先明确交付物和目录结构，再做 XML 数据核验，然后才写转换脚本、搭环境、训练和写报告。题目的硬性要求也先记住：必须用 **NEU-DET 的 XML 标注版本**，必须自己做 **XML→YOLO 转换**，必须从 **GitHub 克隆 YOLO 源码**，**不能用预训练权重**，并且要交 `data_source.md`、`convert_xml_to_yolo.py`、`neu_det.yaml`、`env_report.md`、`training_report.md` 等材料。

## 本步要做什么

1. 建好整个项目目录
2. 明确每个文件将来放什么
3. 开始第一步：数据源核验

------

## 为什么要做

这题不是“跑通一次就算完”，而是要**按评分点完整交付**。如果一开始目录混乱，后面很容易出现这些问题：

- 代码能跑，但证据链不完整
- 训练结果有了，但报告材料散落
- 最后交作业时缺 `yaml`、缺日志、缺 10 张预测图
- 数据源有没有问题说不清

题目本身就把主线分成了：目录与交付物、数据核验、转换脚本、源码环境、从零训练、报告分析。

------

## 具体命令 / 目录结构

先在你的项目根目录下建这一套结构。

### 建议目录树

```text
yolo_neu_det_project/
├─ README.md
├─ data/
│  └─ neu_det_raw/                 # 原始 XML 版 NEU-DET 数据，先不要改动
│     ├─ images/                   # 原始图片
│     └─ annotations/              # 原始 XML 标注
│
├─ datasets/
│  └─ neu_det_yolo/                # 你转换后的 YOLO 数据集
│     ├─ images/
│     │  ├─ train/
│     │  ├─ val/
│     │  └─ test/
│     └─ labels/
│        ├─ train/
│        ├─ val/
│        └─ test/
│
├─ scripts/
│  ├─ inspect_neu_det.py           # 数据源核验脚本
│  └─ convert_xml_to_yolo.py       # XML -> YOLO 转换脚本
│
├─ configs/
│  └─ neu_det.yaml                 # 训练数据配置
│
├─ reports/
│  ├─ data_source.md               # 数据源说明与异常记录
│  ├─ env_report.md                # 环境与源码说明
│  └─ training_report.md           # 训练结果与失败分析
│
├─ logs/
│  ├─ dataset_check/               # 数据核验日志
│  └─ conversion/                  # 转换脚本日志、异常 CSV/JSON
│
├─ assets/
│  ├─ figures/                     # 报告里用的图
│  └─ predictions/                 # 至少 10 张预测可视化结果
│
├─ third_party/
│  └─ yolov5/                      # 后续 git clone 下来的 YOLO 源码
│
└─ runs/                           # 训练输出目录
   └─ train/
```

------

## 每个位置以后放什么

### `data/neu_det_raw/`

放**原始 XML 版 NEU-DET**，保持“原封不动”。
目的：证明你确实拿的是 XML 原始标注，而不是别人转好的 YOLO 版本。这个点是红线。

### `datasets/neu_det_yolo/`

放你自己转换后的标准 YOLO 目录结构：

- `images/train|val|test`
- `labels/train|val|test`

这也是后面 `neu_det.yaml` 要指向的位置。题目明确要求标准目录结构和数据划分。

### `scripts/inspect_neu_det.py`

专门做第一步数据核验：

- 图片总数
- XML 总数
- object 总数
- 类别集合
- 图片无 XML
- XML 无图片
- 类别拼写异常
- XML 尺寸与图片尺寸不一致

这些检查项正是你第一步要交代的。

### `scripts/convert_xml_to_yolo.py`

后面写 XML→YOLO 转换脚本。
题目要求它至少覆盖：VOC XML 解析、bbox 转换、归一化、划分 train/val/test、异常处理、日志记录。

### `configs/neu_det.yaml`

你必须自己写的数据配置文件，训练时显式指定。
后面如果训练命令没带这个文件，属于高风险扣分项。

### `reports/`

三个核心报告都放这里：

- `data_source.md`
- `env_report.md`
- `training_report.md`

这是明确要求的提交物。

### `third_party/yolov5/`

后面用 `git clone` 拉取 YOLO 源码。
这里先占位，提醒自己不能走 `pip install ultralytics` 黑盒路线。

### `assets/predictions/`

后面存至少 10 张预测可视化结果。这个也是明确要求。

------

## 你现在要做的最小动作

先执行下面这组命令。Linux / macOS / WSL 都能直接用；Windows PowerShell 我也给你一份。

### Linux / macOS / WSL

```bash
mkdir -p yolo_neu_det_project/{data/neu_det_raw,datasets/neu_det_yolo/images/{train,val,test},datasets/neu_det_yolo/labels/{train,val,test},scripts,configs,reports,logs/dataset_check,logs/conversion,assets/figures,assets/predictions,third_party,runs/train}

cd yolo_neu_det_project

touch README.md
touch scripts/inspect_neu_det.py
touch scripts/convert_xml_to_yolo.py
touch configs/neu_det.yaml
touch reports/data_source.md
touch reports/env_report.md
touch reports/training_report.md
```

### Windows PowerShell

```powershell
mkdir yolo_neu_det_project
cd yolo_neu_det_project

mkdir data
mkdir data\neu_det_raw

mkdir datasets
mkdir datasets\neu_det_yolo
mkdir datasets\neu_det_yolo\images
mkdir datasets\neu_det_yolo\images\train
mkdir datasets\neu_det_yolo\images\val
mkdir datasets\neu_det_yolo\images\test
mkdir datasets\neu_det_yolo\labels
mkdir datasets\neu_det_yolo\labels\train
mkdir datasets\neu_det_yolo\labels\val
mkdir datasets\neu_det_yolo\labels\test

mkdir scripts
mkdir configs
mkdir reports
mkdir logs
mkdir logs\dataset_check
mkdir logs\conversion
mkdir assets
mkdir assets\figures
mkdir assets\predictions
mkdir third_party
mkdir runs
mkdir runs\train

ni README.md -ItemType File
ni scripts\inspect_neu_det.py -ItemType File
ni scripts\convert_xml_to_yolo.py -ItemType File
ni configs\neu_det.yaml -ItemType File
ni reports\data_source.md -ItemType File
ni reports\env_report.md -ItemType File
ni reports\training_report.md -ItemType File
```

------

## 你执行后应该看到什么

你应该能看到类似这样的目录：

```text
yolo_neu_det_project/
├─ data/
├─ datasets/
├─ scripts/
├─ configs/
├─ reports/
├─ logs/
├─ assets/
├─ third_party/
└─ runs/
```

并且以下文件已经存在：

```text
scripts/inspect_neu_det.py
scripts/convert_xml_to_yolo.py
configs/neu_det.yaml
reports/data_source.md
reports/env_report.md
reports/training_report.md
```

------

## 如果报错，先查哪里

### 1. `mkdir -p` 报错

大概率是你在 Windows 的 CMD 里执行了 Linux 命令。
修复：改用 PowerShell 版本。

### 2. `touch` 报错

Windows 一般没有 `touch`。
修复：用 `ni xxx -ItemType File`。

### 3. 目录已经存在

这不是问题。
只要最终结构对，就继续。

------

## 完成后怎么自检

你现在可以自查这 4 件事：

1. 是否有 **原始数据目录** 和 **转换后数据目录** 的分离
   有就对。这样后面能证明你没直接改原始数据。
2. 是否有 **核验脚本** 和 **转换脚本** 分离
   有就对。这样报告和证据链清晰。
3. 是否有 **configs / reports / runs / assets**
   有就对。这样训练、报告、图片证据都能落位。
4. 是否已经预留 **YOLO 源码目录**
   有就对。后面直接 `git clone`，不容易走偏到黑盒安装。

------

## 这一步影响哪些评分点

这一小步虽然还没得出模型结果，但会直接影响后续多个评分点：

- 提交物是否完整
- 过程是否可复现
- 数据来源和转换过程是否可审计
- 是否能保留训练日志、曲线、预测图等证据
- 是否符合源码训练而非黑盒路线

这和题目的“完整交付、可复现、可解释、可提交”目标是一致的。

------

## 接着进入第一步：数据源核验

下面是你下一步要做的内容，我先直接给你，不让你卡在“下一步写什么”。

### 本步要做什么

核验你手里的 **NEU-DET XML 原始数据** 是否真的可用于后续转换和训练。

### 为什么要做

因为后面很多报错，不是训练本身的问题，而是：

- 图片和 XML 对不上
- XML 里类别名拼写混乱
- 标注框越界
- XML 写的尺寸和图片真实尺寸不一致
- 原始数据目录不规范

如果不先核验，后面写转换脚本时会混进一堆假错误。

### 你现在要做的最小动作

把你的原始数据放进这里：

```text
yolo_neu_det_project/data/neu_det_raw/
```

理想情况是类似：

```text
data/neu_det_raw/
├─ images/
└─ annotations/
```

如果你的原始目录名字不是这个，也没关系，先放进去，后面我们在核验脚本里适配。

------

## 第一版 `inspect_neu_det.py`

先给你一个可直接跑的最小版本，用来统计基础信息。

```python
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter

# ===== 1. 改成你自己的原始数据路径 =====
ROOT = Path("data/neu_det_raw")
IMAGE_DIR = ROOT / "images"
XML_DIR = ROOT / "annotations"

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}

def parse_xml(xml_path: Path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    filename = root.findtext("filename")
    size_node = root.find("size")
    width = int(size_node.findtext("width")) if size_node is not None else None
    height = int(size_node.findtext("height")) if size_node is not None else None

    objects = []
    for obj in root.findall("object"):
        name = obj.findtext("name")
        bndbox = obj.find("bndbox")
        if bndbox is None:
            continue
        xmin = bndbox.findtext("xmin")
        ymin = bndbox.findtext("ymin")
        xmax = bndbox.findtext("xmax")
        ymax = bndbox.findtext("ymax")
        objects.append({
            "name": name,
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
        })

    return {
        "filename": filename,
        "width": width,
        "height": height,
        "objects": objects,
    }

def main():
    images = [p for p in IMAGE_DIR.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES] if IMAGE_DIR.exists() else []
    xmls = list(XML_DIR.glob("*.xml")) if XML_DIR.exists() else []

    image_stems = {p.stem for p in images}
    xml_stems = {p.stem for p in xmls}

    no_xml_images = sorted(image_stems - xml_stems)
    no_img_xmls = sorted(xml_stems - image_stems)

    class_counter = Counter()
    total_objects = 0

    for xml_path in xmls:
        info = parse_xml(xml_path)
        for obj in info["objects"]:
            class_counter[obj["name"]] += 1
            total_objects += 1

    print("==== 数据源基础统计 ====")
    print(f"图片数量: {len(images)}")
    print(f"XML数量: {len(xmls)}")
    print(f"object总数: {total_objects}")
    print(f"类别集合: {sorted(class_counter.keys())}")
    print(f"每类数量: {dict(class_counter)}")

    print("\n==== 配对异常 ====")
    print(f"有图片但无XML: {len(no_xml_images)}")
    print(f"有XML但无图片: {len(no_img_xmls)}")

    if no_xml_images[:10]:
        print("示例-有图片无XML:", no_xml_images[:10])
    if no_img_xmls[:10]:
        print("示例-有XML无图片:", no_img_xmls[:10])

if __name__ == "__main__":
    main()
```

------

## 你执行后应该看到什么

运行：

```bash
python scripts/inspect_neu_det.py
```

你应该得到类似：

```text
==== 数据源基础统计 ====
图片数量: xxx
XML数量: xxx
object总数: xxx
类别集合: ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
每类数量: {...}

==== 配对异常 ====
有图片但无XML: x
有XML但无图片: x
```

------

## 这一步怎么验收

这一轮先只验 3 件事：

1. 脚本能跑
2. 能统计出图片数、XML 数、类别集合
3. 能查出“图片/XML 是否一一配对”

只要这三件过了，我们下一步就升级脚本，继续加：

- XML 尺寸 vs 真实图片尺寸检查
- 类别拼写一致性检查
- bbox 越界检查
- 空标注检查
- 异常日志导出

这些正是题目要求你在 `data_source.md` 里说明的内容。

------

## 现在你做完后，把这两样发给我

1. 你的项目目录树截图或文本
2. `python scripts/inspect_neu_det.py` 的输出结果

你一发，我就继续带你做下一步：把核验脚本升级成“可写入异常清单 + 可直接支撑 `data_source.md`”的版本。









==== 数据源基础统计 ====
图片数量: 1800
XML数量: 1800
object总数: 4189
类别集合: ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
每类数量: {'crazing': 689, 'patches': 881, 'inclusion': 1011, 'pitted_surface': 432, 'rolled-in_scale': 628, 'scratches': 548}

==== 配对异常 ====
有图片但无XML: 0
有XML但无图片: 0

## 1. 原始数据基础统计

对原始 XML 版 NEU-DET 数据进行初步核验，结果如下：

- 图片数量：1800
- XML 标注文件数量：1800
- XML 中 object 总数：4189
- 类别集合：crazing, inclusion, patches, pitted_surface, rolled-in_scale, scratches

各类别目标数量如下：

- crazing: 689
- inclusion: 1011
- patches: 881
- pitted_surface: 432
- rolled-in_scale: 628
- scratches: 548

初步配对检查结果：

- 有图片但无 XML：0
- 有 XML 但无图片：0

说明当前数据集在文件级别上是一一对应的，未发现明显缺失。

质量检查通过：未发现空标注、未知类别、越界框、零宽高框、尺寸不一致等问题

\yolo_neu_det_project\logs\dataset_check

.
└─neu_det_raw
    ├─ANNOTATIONS
    └─IMAGES

(dl2026) PS D:\yolo_neu_det_project>  python scripts/convert_xml_to_yolo.py
原始 XML 数量: 1800
数据集划分结果:（7：2：1）
  train: 1260
  val: 360
  test: 180

成功处理 XML 数量: 1800
异常数量: 0
划分统计已保存: logs\conversion\split_summary.txt
异常日志已保存: logs\conversion\conversion_anomalies.csv

转换完成，输出目录结构如下：
datasets\neu_det_yolo