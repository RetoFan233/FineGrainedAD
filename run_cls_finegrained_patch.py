# import os
# from datasets import dataset_classes
# from multiprocessing import Pool

# if __name__ == '__main__':

#     pool = Pool(processes=2)

#     datasets = ['mvtec']
#     # datasets = ['visa']
    
#     # datasets = ['mvtec', 'visa']
#     # shots = [4]
#     shots = [1, 2, 4]

#     # os.environ['CUDA_VISIBLE_DEVICES'] = "1"
#     for shot in shots:
#         for dataset in datasets:
#             classes = dataset_classes[dataset]
#             for cls in classes[:]:
#                 sh_method = f'python train_cls_finegrained_patch.py ' \
#                             f'--dataset {dataset} ' \
#                             f'--k-shot {shot} ' \
#                             f'--class_name {cls} ' \

#                 print(sh_method)
#                 pool.apply_async(os.system, (sh_method,))

#     pool.close()
#     pool.join()


import os
from datasets import dataset_classes
from multiprocessing import Pool

if __name__ == '__main__':
    
    # 使用8个进程对应8张GPU卡
    pool = Pool(processes=5)
    
    datasets = ['realiad']
    shots = [4, 2, 1]
    
    # 收集所有任务
    tasks = []
    for shot in shots:
        for dataset in datasets:
            classes = dataset_classes[dataset]
            for cls in classes[:]:
                tasks.append((dataset, shot, cls))
    
    print(f"Total tasks: {len(tasks)}")
    
    # 将任务分配到8张GPU卡上
    for i, (dataset, shot, cls) in enumerate(tasks):
        gpu_id = 0  # 循环分配GPU: 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, ...
        # gpu_id = i % 1  # 循环分配GPU: 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, ...
        
        sh_method = f'python train_cls_finegrained_patch.py ' \
                    f'--dataset {dataset} ' \
                    f'--k-shot {shot} ' \
                    f'--class_name {cls} ' \
        
        # print(f"GPU {gpu_id}: {cls}")
        pool.apply_async(os.system, (sh_method,))
    
    pool.close()
    pool.join()