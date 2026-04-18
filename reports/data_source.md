# data_source.md

## 1. 数据集来源

本实验使用 [NEU-DET](http://faculty.neu.edu.cn/songkechen/zh_CN/zdylm/263270/list/index.htm) 工业缺陷数据集，该数据集包含钢材表面缺陷图像及对应标注信息，常用于目标检测任务研究。

数据集包含 6 类典型缺陷：

- crazing
- inclusion
- patches
- pitted_surface
- rolled-in_scale
- scratches



## 2. 数据格式说明

原始数据采用 VOC（Pascal VOC）格式：

- 图像文件：`.jpg`
- 标注文件：`.xml`

每个 XML 文件包含：

- 图像尺寸（width, height）
- 目标类别（name）
- 边界框坐标（xmin, ymin, xmax, ymax）



## 3. 数据集规模统计

数据集统计如下：

- 图像数量：1800
- 标注文件数量：1800
- 总目标数量：4189

各类别分布如下：

| 类别            | 数量     |
| --------------- | -------- |
| crazing         | 689      |
| inclusion       | 1011     |
| patches         | 881      |
| pitted_surface  | 432      |
| rolled-in_scale | 628      |
| scratches       | 548      |
| **总计**        | **4189** |



## 4. 数据一致性检查

在数据预处理阶段，通过在终端运行

```
scripts/inspect_neu_det.py
```

脚本，对数据进行了完整性检查：

- 有图片但无 XML：0
- 有 XML 但无图片：0
- 异常标注：未发现

综上：数据集结构完整，无缺失或损坏样本。



## 5. 数据格式转换

为适配 YOLOv5 训练流程，使用脚本：

```text
scripts/convert_xml_to_yolo.py