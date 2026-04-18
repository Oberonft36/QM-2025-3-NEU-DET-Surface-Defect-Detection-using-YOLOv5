from pathlib import Path
import xml.etree.ElementTree as ET
import random
import shutil
import csv

# ===== 路径配置 =====
ROOT = Path("data/neu_det_raw")
IMAGE_DIR = ROOT / "images"
XML_DIR = ROOT / "annotations"

OUT_ROOT = Path("datasets/neu_det_yolo")
OUT_IMAGE_DIR = OUT_ROOT / "images"
OUT_LABEL_DIR = OUT_ROOT / "labels"

LOG_DIR = Path("logs/conversion")
LOG_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_SUFFIXES = [".jpg", ".jpeg", ".png", ".bmp"]

# ===== 类别映射：后续 neu_det.yaml 必须保持同顺序 =====
CLASS_NAMES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]
CLASS_TO_ID = {name: i for i, name in enumerate(CLASS_NAMES)}

# ===== 划分比例 =====
TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1
SEED = 42

def find_image_by_stem(stem: str):
    for ext in IMAGE_SUFFIXES:
        img_path = IMAGE_DIR / f"{stem}{ext}"
        if img_path.exists():
            return img_path
    return None

def parse_xml(xml_path: Path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    size = root.find("size")
    img_w = int(size.findtext("width"))
    img_h = int(size.findtext("height"))

    objects = []
    for obj in root.findall("object"):
        cls_name = obj.findtext("name")
        bndbox = obj.find("bndbox")

        xmin = int(float(bndbox.findtext("xmin")))
        ymin = int(float(bndbox.findtext("ymin")))
        xmax = int(float(bndbox.findtext("xmax")))
        ymax = int(float(bndbox.findtext("ymax")))

        objects.append({
            "class_name": cls_name,
            "bbox": (xmin, ymin, xmax, ymax)
        })

    return img_w, img_h, objects

def convert_bbox(img_w, img_h, bbox):
    xmin, ymin, xmax, ymax = bbox

    box_w = xmax - xmin
    box_h = ymax - ymin
    x_center = xmin + box_w / 2
    y_center = ymin + box_h / 2

    # 归一化
    x_center /= img_w
    y_center /= img_h
    box_w /= img_w
    box_h /= img_h

    return x_center, y_center, box_w, box_h

def split_dataset(xml_files, seed=42, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-8, "划分比例之和必须为1"

    xml_files = sorted(xml_files)
    random.seed(seed)
    random.shuffle(xml_files)

    n = len(xml_files)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    n_test = n - n_train - n_val

    train_files = xml_files[:n_train]
    val_files = xml_files[n_train:n_train + n_val]
    test_files = xml_files[n_train + n_val:]

    return {
        "train": train_files,
        "val": val_files,
        "test": test_files
    }

def save_label_file(label_path: Path, lines):
    label_path.parent.mkdir(parents=True, exist_ok=True)
    with open(label_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def copy_image(src_img: Path, dst_img: Path):
    dst_img.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_img, dst_img)

def prepare_output_dirs():
    for split in ["train", "val", "test"]:
        (OUT_IMAGE_DIR / split).mkdir(parents=True, exist_ok=True)
        (OUT_LABEL_DIR / split).mkdir(parents=True, exist_ok=True)

def convert_one_xml(xml_path: Path, split: str, anomalies: list):
    try:
        img_w, img_h, objects = parse_xml(xml_path)
    except Exception as e:
        anomalies.append({
            "xml_file": xml_path.name,
            "issue_type": "xml_parse_error",
            "detail": str(e),
        })
        return False

    img_path = find_image_by_stem(xml_path.stem)
    if img_path is None:
        anomalies.append({
            "xml_file": xml_path.name,
            "issue_type": "missing_image",
            "detail": f"未找到与 {xml_path.stem} 对应的图片",
        })
        return False

    lines = []
    for idx, obj in enumerate(objects):
        cls_name = obj["class_name"]
        xmin, ymin, xmax, ymax = obj["bbox"]

        if cls_name not in CLASS_TO_ID:
            anomalies.append({
                "xml_file": xml_path.name,
                "issue_type": "unknown_class",
                "detail": f"object[{idx}] class={cls_name}",
            })
            continue

        if xmin >= xmax:
            anomalies.append({
                "xml_file": xml_path.name,
                "issue_type": "invalid_bbox_width",
                "detail": f"object[{idx}] xmin={xmin}, xmax={xmax}",
            })
            continue

        if ymin >= ymax:
            anomalies.append({
                "xml_file": xml_path.name,
                "issue_type": "invalid_bbox_height",
                "detail": f"object[{idx}] ymin={ymin}, ymax={ymax}",
            })
            continue

        if xmin < 0 or ymin < 0 or xmax > img_w or ymax > img_h:
            anomalies.append({
                "xml_file": xml_path.name,
                "issue_type": "bbox_out_of_range",
                "detail": f"object[{idx}] bbox=({xmin},{ymin},{xmax},{ymax}), size=({img_w},{img_h})",
            })
            continue

        class_id = CLASS_TO_ID[cls_name]
        x_center, y_center, box_w, box_h = convert_bbox(img_w, img_h, (xmin, ymin, xmax, ymax))

        line = f"{class_id} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}"
        lines.append(line)

    # 即便某个文件没有有效框，也保留空txt，便于追踪
    out_label_path = OUT_LABEL_DIR / split / f"{xml_path.stem}.txt"
    save_label_file(out_label_path, lines)

    # 复制图片
    out_img_path = OUT_IMAGE_DIR / split / img_path.name
    copy_image(img_path, out_img_path)

    return True

def save_split_summary(split_result):
    summary_path = LOG_DIR / "split_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        for split, files in split_result.items():
            f.write(f"{split}: {len(files)}\n")
    print(f"划分统计已保存: {summary_path}")

def save_anomalies(anomalies):
    csv_path = LOG_DIR / "conversion_anomalies.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["xml_file", "issue_type", "detail"])
        writer.writeheader()
        writer.writerows(anomalies)
    print(f"异常日志已保存: {csv_path}")

def main():
    prepare_output_dirs()

    xml_files = sorted(XML_DIR.glob("*.xml"))
    print(f"原始 XML 数量: {len(xml_files)}")

    split_result = split_dataset(
        xml_files,
        seed=SEED,
        train_ratio=TRAIN_RATIO,
        val_ratio=VAL_RATIO,
        test_ratio=TEST_RATIO
    )

    print("数据集划分结果:")
    for split, files in split_result.items():
        print(f"  {split}: {len(files)}")

    anomalies = []
    success_count = 0

    for split, files in split_result.items():
        for xml_path in files:
            ok = convert_one_xml(xml_path, split, anomalies)
            if ok:
                success_count += 1

    print(f"\n成功处理 XML 数量: {success_count}")
    print(f"异常数量: {len(anomalies)}")

    save_split_summary(split_result)
    save_anomalies(anomalies)

    print("\n转换完成，输出目录结构如下：")
    print(OUT_ROOT)

if __name__ == "__main__":
    main()