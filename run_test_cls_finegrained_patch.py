import os
from datasets import dataset_classes
from multiprocessing import Pool

if __name__ == '__main__':

    pool = Pool(processes=4)

    # datasets = ['visa']
    # datasets = ['mvtec']
    datasets = ['visa']
    # shots = [4]
    # shots = [4]
    # shots = [4]
    shots = [1, 2, 4]
    # shots = [1]
    # shots = [2]

    for shot in shots:
        for dataset in datasets:
            classes = dataset_classes[dataset]
            for cls in classes[:]:
                sh_method = f'python test_cls_finegrained_patch.py ' \
                            f'--dataset {dataset} ' \
                            f'--k-shot {shot} ' \
                            f'--class_name {cls} ' \

                print(sh_method)
                pool.apply_async(os.system, (sh_method,))

    pool.close()
    pool.join()




