import argparse

import torch.optim.lr_scheduler

from datasets import *
from datasets import dataset_classes
from utils.csv_utils import *
from utils.metrics import *
from utils.training_utils import *
from PromptAD import *
from utils.eval_utils import *
from torchvision import transforms
from tqdm import tqdm
# from PromptAD import FineGrainedAD, FineGrainedPatchAD, FineGrainedScaleAD
from PromptAD import FineGrainedPatchAD
from PIL import Image

TASK = 'SEG'

def test(model,
        args,
        dataloader: DataLoader,
        device: str,
        img_dir: str,
        check_path: str,
        ):

    # change the model into eval mode
    model.eval_mode()

    model.load_state_dict(torch.load(check_path), strict=False)

    score_maps = []
    test_imgs = []
    gt_mask_list = []
    names = []
    
    # 添加时间统计变量
    total_inference_time = 0.0
    total_samples = 0

    for (data, mask, label, name, img_type) in dataloader:

        data = [model.transform(Image.fromarray(f.numpy())) for f in data]
        data = torch.stack(data, dim=0)

        for d, n, l, m in zip(data, name, label, mask):
            test_imgs += [denormalization(d.cpu().numpy())]
            m = m.numpy()
            m[m > 0] = 1

            names += [n]
            gt_mask_list += [m]

        data = data.to(device)
        # 确保CUDA同步
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        
        # 统计推理时间
        start_time = time.time()
        with torch.no_grad():
            score_map = model(data, 'seg')
        
        # 确保CUDA同步以准确计时
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        
        end_time = time.time()
        inference_time = end_time - start_time
        total_inference_time += inference_time
        batch_size = data.size(0)
        total_samples += batch_size
        
        # 实时打印推理时间信息
        print(f"Batch inference time: {inference_time:.4f}s, Batch size: {batch_size}, Per image: {inference_time/batch_size:.4f}s")
        score_maps += score_map

    test_imgs, score_maps, gt_mask_list = specify_resolution(test_imgs, score_maps, gt_mask_list, resolution=(args.resolution, args.resolution))
    result_dict = metric_cal_pix_multiple_metrics(np.array(score_maps), gt_mask_list)
    # result_dict = metric_cal_pix(np.array(score_maps), gt_mask_list)

    # torch.save(model.state_dict(), check_path)
    if args.vis:
        plot_sample_compare(names, test_imgs, {'FineGrainedAD': score_maps}, gt_mask_list, save_folder=img_dir)
    
    # 打印总体推理时间统计
    if total_samples > 0:
        avg_time_per_image = total_inference_time / total_samples
        fps = 1.0 / avg_time_per_image
        print(f"\n========== 推理时间统计 ==========")
        print(f"总样本数: {total_samples}")
        print(f"总推理时间: {total_inference_time:.4f}s")
        print(f"平均每张图像推理时间: {avg_time_per_image:.4f}s")
        print(f"FPS: {fps:.2f}")
        print(f"==================================\n")

    return result_dict


def main(args):
    kwargs = vars(args)

    if kwargs['seed'] is None:
        kwargs['seed'] = 111
        # kwargs['seed'] = 222

    setup_seed(kwargs['seed'])

    if kwargs['use_cpu'] == 0:
        device = f"cuda:0"
    else:
        device = f"cpu"
    kwargs['device'] = device

    # prepare the experiment dir
    img_dir, csv_path, check_path = get_dir_from_args(TASK, **kwargs)

    # get the test dataloader
    test_dataloader, test_dataset_inst = get_dataloader_from_args(phase='test', perturbed=False, **kwargs)

    kwargs['out_size_h'] = kwargs['resolution']
    kwargs['out_size_w'] = kwargs['resolution']

    # get the model
    model = FineGrainedPatchAD(**kwargs)
    # model = FineGrainedScaleAD(**kwargs)
    model = model.to(device)

    # 统计模型参数量
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print("\n========== 模型参数量统计 ==========")
    print(f"总参数量: {total_params:,} ({total_params/1e6:.2f}M)")
    print(f"可训练参数量: {trainable_params:,} ({trainable_params/1e6:.2f}M)")
    print("=" * 36 + "\n")

    # as the pro metric calculation is costly, we only calculate it in the last evaluation
    metrics = test(model, args, test_dataloader, device, img_dir=img_dir, check_path=check_path)

    p_roc = round(metrics['p_roc'], 2)
    p_pro = round(metrics['p_pro'], 2)
    # pix_pro_auc = round(metrics['pix_pro_auc'], 2)
    # pix_max_f1 = round(metrics['pix_max_f1'], 2)
    object = kwargs['class_name']
    print(f'Object:{object} =========================== Pixel-AUROC:{p_roc} Pixel-Pro:{p_pro}\n')
    # print(f'Object:{object} =========================== Pixel-Pro-AUROC:{pix_pro_auc}\n')
    # print(f'Object:{object} =========================== Pixel-Max-F1:{pix_max_f1}\n')

    # save_metric(metrics, dataset_classes[kwargs['dataset']], kwargs['class_name'],
    #             kwargs['dataset'], csv_path)
    save_metric_mutiple(metrics, dataset_classes[kwargs['dataset']], kwargs['class_name'],
                kwargs['dataset'], csv_path)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def get_args():
    parser = argparse.ArgumentParser(description='Anomaly detection')
    parser.add_argument('--dataset', type=str, default='realiad', choices=['mvtec', 'visa', 'realiad'])
    parser.add_argument('--class_name', type=str, default='audiojack')

    parser.add_argument('--img-resize', type=int, default=240)
    parser.add_argument('--img-cropsize', type=int, default=240)
    parser.add_argument('--resolution', type=int, default=400)

    parser.add_argument('--batch-size', type=int, default=400)
    parser.add_argument('--vis', type=str2bool, choices=[True, False], default=False)
    parser.add_argument("--root-dir", type=str, default="./result_finegrained_0930_w15_fp32/")
    # parser.add_argument("--root-dir", type=str, default="./results/result_finegrained_0606_w15_fp32/")
    parser.add_argument("--load-memory", type=str2bool, default=True)
    parser.add_argument("--cal-pro", type=str2bool, default=False)
    parser.add_argument("--seed", type=int, default=111)
    parser.add_argument("--gpu_id", type=int, default=2)

    # pure test
    parser.add_argument("--pure-test", type=str2bool, default=False)

    # method related parameters
    parser.add_argument('--k-shot', type=int, default=4)
    parser.add_argument("--backbone", type=str, default="ViT-B-16-plus-240",
                        choices=['ViT-B-16-plus-240', 'ViT-B-16'])
    parser.add_argument("--pretrained_dataset", type=str, default="laion400m_e32")
    parser.add_argument("--version", type=str, default='')
    parser.add_argument("--precision", type=str, default='fp32')

    parser.add_argument("--use-cpu", type=int, default=0)

    # prompt tuning hyper-parameter
    parser.add_argument("--n_ctx", type=int, default=4)
    parser.add_argument("--n_ctx_ab", type=int, default=1)
    parser.add_argument("--n_pro", type=int, default=1)
    parser.add_argument("--n_pro_ab", type=int, default=4)

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    import os

    args = get_args()
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['CUDA_VISIBLE_DEVICES'] = f"{args.gpu_id}"
    main(args)
