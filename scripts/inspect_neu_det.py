from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter
import csv

try:
    from PIL import Image
except ImportError:
    Image = None

# ===== 路径配置 =====
ROOT = Path("data/neu_det_raw")
IMAGE_DIR = ROOT / "images"
XML_DIR = ROOT / "annotations"
LOG_DIR = Path("logs/dataset_check")
LOG_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}

# 这里先用你当前统计出来的6类
KNOWN_CLASSES = {
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
}

def parse_xml(xml_path: Path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    filename = root.findtext("filename")
    size_node = root.find("size")
    xml_width = int(size_node.findtext("width")) if size_node is not None and size_node.findtext("width") else None
    xml_height = int(size_node.findtext("height")) if size_node is not None and size_node.findtext("height") else None

    objects = []
    for obj in root.findall("object"):
        name = obj.findtext("name")
        bndbox = obj.find("bndbox")

        bbox = None
        if bndbox is not None:
            try:
                bbox = {
                    "xmin": int(float(bndbox.findtext("xmin"))),
                    "ymin": int(float(bndbox.findtext("ymin"))),
                    "xmax": int(float(bndbox.findtext("xmax"))),
                    "ymax": int(float(bndbox.findtext("ymax"))),
                }
            except (TypeError, ValueError):
                bbox = None

        objects.append({
            "name": name,
            "bbox": bbox,
        })

    return {
        "filename": filename,
        "xml_width": xml_width,
        "xml_height": xml_height,
        "objects": objects,
    }

def find_image_by_stem(stem: str):
    for ext in IMAGE_SUFFIXES:
        candidate = IMAGE_DIR / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None

def get_real_image_size(img_path: Path):
    if Image is None:
        return None, None
    with Image.open(img_path) as img:
        return img.size  # (width, height)

def main():
    images = [p for p in IMAGE_DIR.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES] if IMAGE_DIR.exists() else []
    xmls = list(XML_DIR.glob("*.xml")) if XML_DIR.exists() else []

    image_stems = {p.stem for p in images}
    xml_stems = {p.stem for p in xmls}

    no_xml_images = sorted(image_stems - xml_stems)
    no_img_xmls = sorted(xml_stems - image_stems)

    class_counter = Counter()
    total_objects = 0

    anomalies = []

    for xml_path in xmls:
        try:
            info = parse_xml(xml_path)
        except Exception as e:
            anomalies.append({
                "xml_file": xml_path.name,
                "issue_type": "xml_parse_error",
                "detail": str(e),
            })
            continue

        stem = xml_path.stem
        img_path = find_image_by_stem(stem)

        # 空标注
        if len(info["objects"]) == 0:
            anomalies.append({
                "xml_file": xml_path.name,
                "issue_type": "empty_annotation",
                "detail": "XML中没有object节点",
            })

        # 尺寸检查：XML声明尺寸 vs 真实图片尺寸
        if img_path is not None and Image is not None:
            real_w, real_h = get_real_image_size(img_path)
            if info["xml_width"] != real_w or info["xml_height"] != real_h:
                anomalies.append({
                    "xml_file": xml_path.name,
                    "issue_type": "size_mismatch",
                    "detail": f"xml=({info['xml_width']},{info['xml_height']}), real=({real_w},{real_h})",
                })
        elif img_path is None:
            anomalies.append({
                "xml_file": xml_path.name,
                "issue_type": "missing_image",
                "detail": f"未找到与 {xml_path.name} 对应的图片",
            })

        # 遍历object
        for idx, obj in enumerate(info["objects"]):
            cls_name = obj["name"]
            bbox = obj["bbox"]

            if cls_name:
                class_counter[cls_name] += 1
                total_objects += 1

            # 类别未知
            if cls_name not in KNOWN_CLASSES:
                anomalies.append({
                    "xml_file": xml_path.name,
                    "issue_type": "unknown_class",
                    "detail": f"object[{idx}] class={cls_name}",
                })

            # bbox 为空
            if bbox is None:
                anomalies.append({
                    "xml_file": xml_path.name,
                    "issue_type": "invalid_bbox_format",
                    "detail": f"object[{idx}] bbox解析失败",
                })
                continue

            xmin, ymin, xmax, ymax = bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]

            # 零宽高 / 反向框
            if xmin >= xmax:
                anomalies.append({
                    "xml_file": xml_path.name,
                    "issue_type": "invalid_bbox_width",
                    "detail": f"object[{idx}] xmin={xmin}, xmax={xmax}",
                })
            if ymin >= ymax:
                anomalies.append({
                    "xml_file": xml_path.name,
                    "issue_type": "invalid_bbox_height",
                    "detail": f"object[{idx}] ymin={ymin}, ymax={ymax}",
                })

            # 越界检查（基于XML尺寸）
            xml_w, xml_h = info["xml_width"], info["xml_height"]
            if xml_w is not None and xml_h is not None:
                if xmin < 0 or ymin < 0 or xmax > xml_w or ymax > xml_h:
                    anomalies.append({
                        "xml_file": xml_path.name,
                        "issue_type": "bbox_out_of_range",
                        "detail": f"object[{idx}] bbox=({xmin},{ymin},{xmax},{ymax}), size=({xml_w},{xml_h})",
                    })

    # 把文件级配对异常也记进去
    for stem in no_xml_images:
        anomalies.append({
            "xml_file": f"{stem}.xml",
            "issue_type": "image_without_xml",
            "detail": f"图片 {stem} 存在，但缺少XML",
        })

    for stem in no_img_xmls:
        anomalies.append({
            "xml_file": f"{stem}.xml",
            "issue_type": "xml_without_image",
            "detail": f"XML {stem}.xml 存在，但缺少图片",
        })

    # 输出统计
    print("==== 数据源基础统计 ====")
    print(f"图片数量: {len(images)}")
    print(f"XML数量: {len(xmls)}")
    print(f"object总数: {total_objects}")
    print(f"类别集合: {sorted(class_counter.keys())}")
    print(f"每类数量: {dict(class_counter)}")

    print("\n==== 配对异常 ====")
    print(f"有图片但无XML: {len(no_xml_images)}")
    print(f"有XML但无图片: {len(no_img_xmls)}")

    print("\n==== 异常统计 ====")
    anomaly_counter = Counter(a["issue_type"] for a in anomalies)
    if anomaly_counter:
        for k, v in anomaly_counter.items():
            print(f"{k}: {v}")
    else:
        print("未发现异常")

    # 保存异常CSV
    csv_path = LOG_DIR / "dataset_anomalies.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["xml_file", "issue_type", "detail"])
        writer.writeheader()
        writer.writerows(anomalies)

    print(f"\n异常明细已保存: {csv_path}")

if __name__ == "__main__":
    main()