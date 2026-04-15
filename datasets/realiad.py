import glob
import os
import random


"""
RealIAD数据集目录结构：
realiad/
├── audiojack/
│   ├── OK/
│   │   ├── S0001/
│   │   │   ├── XXXX.jpg (normal image)
│   │   ├── S0002/
│   │   │   ├── XXXX.jpg (normal image)
│   └── NG/
│       ├── AK/
│       │   ├── S0001/
│       │   │   ├── XXXX.jpg (defect image)
│       │   │   ├── XXXX.png (mask)
│       ├── BX/
│       ├── CH/
│       ├── HS/
│       ├── PS/
│       ├── QS/
│       ├── YW/
│       └── ZW/
├── bottle_cap/
│   ├── OK/
│   └── NG/
└── ...
"""

realiad_classes = ['audiojack', 'bottle_cap', 'button_battery', 'end_cap', 'eraser', 'fire_hood', 'mint', 'mounts', 'pcb', 'phone_battery', 'plastic_nut', 'plastic_plug', 'porcelain_doll', 'regulator', 'rolled_strip_base', 'sim_card_set', 'switch', 'tape', 'terminalblock', 'toothbrush', 'toy', 'toy_brick', 'transistor1', 'u_block', 'usb', 'usb_adaptor', 'vcpill', 'wooden_beads', 'woodstick', 'zipper']

REALIAD_DIR = 'datasets/anomaly_detection/realiad'


def load_realiad(category, k_shot):
    def load_normal_phase(root_path):
        """加载正常图像 (OK目录下的子目录)"""
        img_tot_paths = []
        gt_tot_paths = []
        tot_labels = []
        tot_types = []
        
        # 遍历OK目录下的所有子目录（如S0001, S0002等）
        if os.path.exists(root_path):
            subdirs = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
            subdirs.sort()  # 确保顺序一致
            for subdir in subdirs:
                subdir_path = os.path.join(root_path, subdir)
                # 查找图像文件，支持jpg和png格式
                img_paths = glob.glob(os.path.join(subdir_path, "*.jpg"))
                # 只保留文件名中包含"C1"的图像
                img_paths = [p for p in img_paths if "C1" in os.path.basename(p)]
                img_paths.sort()  # 确保顺序一致
                
                img_tot_paths.extend(img_paths)
                gt_tot_paths.extend([0] * len(img_paths))  # 正常图像没有mask
                tot_labels.extend([0] * len(img_paths))    # 标签为0（正常）
                tot_types.extend(['good'] * len(img_paths))
        
        return img_tot_paths, gt_tot_paths, tot_labels, tot_types
    
    def load_defect_phase(root_path):
        """加载缺陷图像 (NG目录下的子目录)"""
        img_tot_paths = []
        gt_tot_paths = []
        tot_labels = []
        tot_types = []
        
        if os.path.exists(root_path):
            # 遍历NG目录下的所有缺陷类型目录（如AK, BX等）
            defect_types = [d for d in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, d))]
            defect_types.sort()  # 确保顺序一致
            
            for defect_type in defect_types:
                defect_type_path = os.path.join(root_path, defect_type)
                
                # 遍历缺陷类型目录下的所有子目录（如S0001等）
                subdirs = [d for d in os.listdir(defect_type_path) if os.path.isdir(os.path.join(defect_type_path, d))]
                subdirs.sort()  # 确保顺序一致
                
                for subdir in subdirs:
                    subdir_path = os.path.join(defect_type_path, subdir)
                    
                    # 查找图像文件，支持jpg和png格式
                    img_paths = glob.glob(os.path.join(subdir_path, "*.jpg"))
                    # 只保留文件名中包含"C1"的图像
                    img_paths = [p for p in img_paths if "C1" in os.path.basename(p)]
                    img_paths.sort()  # 确保顺序一致
                    
                    # 为每个图像找到对应的mask文件
                    gt_paths = []
                    for img_path in img_paths:
                        base_name = os.path.splitext(os.path.basename(img_path))[0]
                        mask_path = os.path.join(subdir_path, f"{base_name}.png")
                        if not os.path.exists(mask_path):
                            # 如果没有找到对应的mask，尝试寻找_mask后缀的文件
                            # mask_path = os.path.join(subdir_path, f"{base_name}_mask.png")
                            #删除img_path
                            img_paths.remove(img_path)
                            continue #没找到就跳过
                        gt_paths.append(mask_path)
                    
                    img_tot_paths.extend(img_paths)
                    gt_tot_paths.extend(gt_paths)
                    tot_labels.extend([1] * len(img_paths))  # 标签为1（异常）
                    tot_types.extend([defect_type] * len(img_paths))
        
        return img_tot_paths, gt_tot_paths, tot_labels, tot_types

    def load_selected_images_from_kshot_file(category, k_shot, train_img_tot_paths, train_gt_tot_paths, train_tot_labels, train_tot_types):
        """根据k-shot文件选择训练图像"""
        
        # 首先检查输入数据的一致性
        input_lengths = [len(train_img_tot_paths), len(train_gt_tot_paths), len(train_tot_labels), len(train_tot_types)]
        if not all(length == input_lengths[0] for length in input_lengths):
            raise ValueError(f"Input data lists have inconsistent lengths: {input_lengths}")
        
        # 构建k-shot文件路径
        kshot_file = os.path.join('./datasets/seeds_realiad', f'{k_shot}_shot.txt')
        
        if not os.path.exists(kshot_file):
            print(f"Warning: K-shot file {kshot_file} not found, using random selection")
            if k_shot > 0 and len(train_img_tot_paths) >= k_shot:
                random.seed(42)
                indices = random.sample(range(len(train_img_tot_paths)), k_shot)
                return ([train_img_tot_paths[k] for k in indices],
                       [train_gt_tot_paths[k] for k in indices], 
                       [train_tot_labels[k] for k in indices],
                       [train_tot_types[k] for k in indices])
            else:
                return train_img_tot_paths, train_gt_tot_paths, train_tot_labels, train_tot_types
        
        # 读取k-shot文件
        with open(kshot_file, 'r') as f:
            lines = f.readlines()
        
        # 过滤出包含当前category和C1的图像路径
        selected_relative_paths = []
        for line in lines:
            line = line.strip()
            if line and category in line and 'C1' in line:
                selected_relative_paths.append(line)
        
        print(f"Found {len(selected_relative_paths)} selected paths for {category} from {kshot_file}")
        
        # 从训练图像列表中找到对应的图像
        selected_train_img_tot_paths = []
        selected_train_gt_tot_paths = []
        selected_train_tot_labels = []
        selected_train_tot_types = []
        
        for relative_path in selected_relative_paths:
            # 提取文件名
            filename = os.path.basename(relative_path)
            
            # 在训练图像列表中找到匹配的图像
            for i, img_path in enumerate(train_img_tot_paths):
                if filename == os.path.basename(img_path):
                    selected_train_img_tot_paths.append(train_img_tot_paths[i])
                    selected_train_gt_tot_paths.append(train_gt_tot_paths[i])
                    selected_train_tot_labels.append(train_tot_labels[i])
                    selected_train_tot_types.append(train_tot_types[i])
                    break
        
        print(f"Successfully matched {len(selected_train_img_tot_paths)} images for {category}")
        
        if len(selected_train_img_tot_paths) == 0:
            print(f"Warning: No images matched for {category}, using random selection")
            if k_shot > 0 and len(train_img_tot_paths) >= k_shot:
                random.seed(42)
                indices = random.sample(range(len(train_img_tot_paths)), k_shot)
                return ([train_img_tot_paths[k] for k in indices],
                       [train_gt_tot_paths[k] for k in indices], 
                       [train_tot_labels[k] for k in indices],
                       [train_tot_types[k] for k in indices])
        
        return selected_train_img_tot_paths[:k_shot], selected_train_gt_tot_paths[:k_shot], selected_train_tot_labels[:k_shot], selected_train_tot_types[:k_shot]

    assert category in realiad_classes

    # 定义路径
    train_img_path = os.path.join(REALIAD_DIR, category, 'OK')  # 训练用正常图像
    test_normal_path = os.path.join(REALIAD_DIR, category, 'OK')  # 测试用正常图像  
    test_defect_path = os.path.join(REALIAD_DIR, category, 'NG')  # 测试用缺陷图像

    # 加载训练数据（正常图像）
    train_img_tot_paths, train_gt_tot_paths, train_tot_labels, train_tot_types = load_normal_phase(train_img_path)

    # 加载测试数据（正常图像 + 缺陷图像）
    test_normal_img_paths, test_normal_gt_paths, test_normal_labels, test_normal_types = load_normal_phase(test_normal_path)
    test_defect_img_paths, test_defect_gt_paths, test_defect_labels, test_defect_types = load_defect_phase(test_defect_path)
    
    # 合并测试数据
    test_img_tot_paths = test_normal_img_paths + test_defect_img_paths
    test_gt_tot_paths = test_normal_gt_paths + test_defect_gt_paths
    test_tot_labels = test_normal_labels + test_defect_labels
    test_tot_types = test_normal_types + test_defect_types

    # 检查数据一致性
    # assert len(test_img_tot_paths) == len(test_gt_tot_paths), "Something wrong with test and ground truth pair!"
    # assert len(train_img_tot_paths) == len(train_gt_tot_paths), "Something wrong with train and ground truth pair!"

    # 使用新的k-shot选择方法
    selected_train_img_tot_paths, selected_train_gt_tot_paths, selected_train_tot_labels, selected_train_tot_types = \
        load_selected_images_from_kshot_file(category, k_shot, train_img_tot_paths, train_gt_tot_paths, train_tot_labels, train_tot_types)

    return (selected_train_img_tot_paths, selected_train_gt_tot_paths, selected_train_tot_labels, selected_train_tot_types), \
           (test_img_tot_paths, test_gt_tot_paths, test_tot_labels, test_tot_types)


if __name__ == '__main__':
    # 测试数据集读取效果
    import sys
    import os
    
    print("=" * 80)
    print("RealIAD Dataset Loading Test")
    print("=" * 80)
    
    # 测试参数
    test_category = 'audiojack'  # 可以修改为其他类别
    test_k_shot = 4
    
    print(f"Testing category: {test_category}")
    print(f"K-shot value: {test_k_shot}")
    print("-" * 80)
    
    try:
        # 加载数据集
        (train_img_paths, train_gt_paths, train_labels, train_types), \
        (test_img_paths, test_gt_paths, test_labels, test_types) = load_realiad(test_category, test_k_shot)
        
        print("✓ Dataset loading successful!")
        print()
        
        # 打印训练集信息
        print("TRAINING SET:")
        print(f"  Total training samples: {len(train_img_paths)}")
        print(f"  K-shot selected samples: {test_k_shot}")
        print(f"  Normal samples: {sum(1 for label in train_labels if label == 0)}")
        print(f"  Anomaly samples: {sum(1 for label in train_labels if label == 1)}")
        
        if train_img_paths:
            print("  Sample training images:")
            for i, (img_path, gt_path, label, img_type) in enumerate(zip(train_img_paths[:5], train_gt_paths[:5], train_labels[:5], train_types[:5])):
                print(f"    [{i+1}] {os.path.basename(img_path)} | Label: {label} | Type: {img_type}")
                print(f"        Full path: {img_path}")
                print(f"        GT path: {gt_path}")
                print(f"        File exists: {os.path.exists(img_path)}")
                if gt_path != 0:
                    print(f"        GT exists: {os.path.exists(gt_path)}")
                print()
        
        print("-" * 80)
        
        # 打印测试集信息
        print("TEST SET:")
        print(f"  Total test samples: {len(test_img_paths)}")
        print(f"  Normal samples: {sum(1 for label in test_labels if label == 0)}")
        print(f"  Anomaly samples: {sum(1 for label in test_labels if label == 1)}")
        
        # 统计缺陷类型
        defect_types = {}
        for img_type in test_types:
            if img_type != 'good':
                defect_types[img_type] = defect_types.get(img_type, 0) + 1
        
        if defect_types:
            print(f"  Defect types distribution:")
            for defect_type, count in sorted(defect_types.items()):
                print(f"    {defect_type}: {count} samples")
        
        if test_img_paths:
            print("  Sample test images:")
            # 显示前3个正常样本
            normal_samples = [(i, img_path, gt_path, label, img_type) for i, (img_path, gt_path, label, img_type) 
                            in enumerate(zip(test_img_paths, test_gt_paths, test_labels, test_types)) if label == 0]
            if normal_samples:
                print("    Normal samples:")
                for i, (idx, img_path, gt_path, label, img_type) in enumerate(normal_samples[:3]):
                    print(f"      [{idx+1}] {os.path.basename(img_path)} | Label: {label} | Type: {img_type}")
                    print(f"          File exists: {os.path.exists(img_path)}")
            
            # 显示前3个异常样本
            anomaly_samples = [(i, img_path, gt_path, label, img_type) for i, (img_path, gt_path, label, img_type) 
                             in enumerate(zip(test_img_paths, test_gt_paths, test_labels, test_types)) if label == 1]
            if anomaly_samples:
                print("    Anomaly samples:")
                for i, (idx, img_path, gt_path, label, img_type) in enumerate(anomaly_samples[:3]):
                    print(f"      [{idx+1}] {os.path.basename(img_path)} | Label: {label} | Type: {img_type}")
                    print(f"          File exists: {os.path.exists(img_path)}")
                    if gt_path != 0:
                        print(f"          GT exists: {os.path.exists(gt_path)}")
        
        print("-" * 80)
        
        # 验证数据一致性
        print("DATA CONSISTENCY CHECK:")
        print(f"  ✓ Train images count: {len(train_img_paths)}")
        print(f"  ✓ Train GT count: {len(train_gt_paths)}")
        print(f"  ✓ Train labels count: {len(train_labels)}")
        print(f"  ✓ Train types count: {len(train_types)}")
        print(f"  ✓ Test images count: {len(test_img_paths)}")
        print(f"  ✓ Test GT count: {len(test_gt_paths)}")
        print(f"  ✓ Test labels count: {len(test_labels)}")
        print(f"  ✓ Test types count: {len(test_types)}")
        
        # 检查文件路径中是否都包含C1
        c1_train_count = sum(1 for path in train_img_paths if "C1" in os.path.basename(path))
        c1_test_count = sum(1 for path in test_img_paths if "C1" in os.path.basename(path))
        print(f"  ✓ Train images with C1: {c1_train_count}/{len(train_img_paths)}")
        print(f"  ✓ Test images with C1: {c1_test_count}/{len(test_img_paths)}")
        
        # 检查文件存在性
        missing_train_files = [path for path in train_img_paths if not os.path.exists(path)]
        missing_test_files = [path for path in test_img_paths if not os.path.exists(path)]
        
        if missing_train_files:
            print(f"  ⚠ Missing train files: {len(missing_train_files)}")
            for file in missing_train_files[:3]:  # 只显示前3个
                print(f"    - {file}")
        else:
            print(f"  ✓ All training files exist")
            
        if missing_test_files:
            print(f"  ⚠ Missing test files: {len(missing_test_files)}")
            for file in missing_test_files[:3]:  # 只显示前3个
                print(f"    - {file}")
        else:
            print(f"  ✓ All test files exist")
        
        print()
        print("=" * 80)
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error loading dataset: {str(e)}")
        import traceback
        traceback.print_exc()