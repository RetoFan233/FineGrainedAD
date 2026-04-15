
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
import random
from tqdm import tqdm
from PromptAD import FineGrainedPatchAD
TASK = 'CLS'


def save_check_point(model, path):
    selected_keys = [
        'feature_gallery1',
        'feature_gallery2',
        'large_memory',
        'middle_memory',
        'patch_memory',
        'text_features',
        'background_features',
        'entity_features_list',
        'q_former'
    ]
    state_dict = model.state_dict()
    selected_state_dict = {k: v for k, v in state_dict.items() if k in selected_keys}

    torch.save(selected_state_dict, path)

def slice_images(images, slice_size=240):
    bs, c, h, w = images.shape
    assert h % slice_size == 0 and w % slice_size == 0, "Image dimensions must be divisible by slice size"
    
    # 切片数量
    num_slices_h = h // slice_size
    num_slices_w = w // slice_size
    
    # 切片
    slices = images.unfold(2, slice_size, slice_size).unfold(3, slice_size, slice_size)
    slices = slices.contiguous().view(bs, c, -1, slice_size, slice_size)
    slices = slices.permute(0, 2, 1, 3, 4).contiguous().view(-1, c, slice_size, slice_size)
    
    return slices, num_slices_h, num_slices_w


def cluster_tensor_preprocess(model, cluster_tensor):
    bs, c, h, w = cluster_tensor.shape #k 3 960 960
    
    # 切片
    slices, num_slices_h, num_slices_w = slice_images(cluster_tensor, slice_size=240)
    
    #对每个切片进行编码
    with torch.no_grad():
        _, slice_features, _, _ = model.encode_image(slices)
        # slice_features = model.encode_image(slices, patch_size=16)
        # _, _, slice_features, _, _, _ = model.encode_image(slices, patch_size=16)
        # slice_features = slice_features.squeeze(2) @ model.visual_proj
        
    # 将特征向量恢复成原始批次大小
    slice_features = slice_features.view(bs, num_slices_h * num_slices_w, 225, -1)  
    
    # 将每个切片的特征向量从 bs*225*640 变换为 bs*15*15*640
    slice_features = slice_features.view(bs, num_slices_h, num_slices_w, 15, 15, -1)
    slice_features = slice_features.permute(0, 1, 3, 2, 4, 5).contiguous()
    slice_features = slice_features.view(bs, num_slices_h * 15, num_slices_w * 15, -1)

    # 拉平成最终结果
    final_features = slice_features.view(bs, -1, slice_features.shape[-1])

    return final_features

# 通过 4*4 的窗口选择窗口内最多的类别
def max_pooling_with_argmax(input, kernel_size):
    input_unfold = F.unfold(input.unsqueeze(1), kernel_size=kernel_size, stride=kernel_size)
    input_unfold = input_unfold.view(input.size(0), input.size(1), -1, kernel_size * kernel_size)
    max_vals, max_indices = input_unfold.max(dim=-1)
    return max_vals, max_indices

# 通过 4*4 的窗口选择窗口内的平均值
def max_pooling_with_mode(input, kernel_size):
    bs, h, w = input.shape
    # input_unfold = F.unfold(input.unsqueeze(1).float(), kernel_size=(kernel_size, kernel_size), stride=(kernel_size, kernel_size))
    input_unfold = F.unfold(input.unsqueeze(1).float(), kernel_size=kernel_size, stride=kernel_size)
    input_unfold = input_unfold.view(bs, -1, kernel_size * kernel_size)
    mode_vals, _ = input_unfold.mode(dim=-1)
    return mode_vals

def average_pooling(input, kernel_size, stride):
    ne, bs, h, w = input.shape
    input_unfold = F.unfold(input, kernel_size=kernel_size, stride=stride)
    input_unfold = input_unfold.view(ne, bs, -1, kernel_size * kernel_size)
    avg_vals = input_unfold.mean(dim=-1)
    return avg_vals

def downsample_to_15x15_with_avg(tensor, kernel_size):
    # 假设 tensor 是形状为 bs*60*60 的张量
    ne, bs, h, w = tensor.shape
    assert h == 60 and w == 60, "输入张量的形状必须为 bs*60*60"

    # 通过 4x4 的窗口计算平均值
    pooled_tensor = average_pooling(tensor, kernel_size=kernel_size, stride=kernel_size)
    
    # 将结果拉平成 bs*15*15
    final_tensor = pooled_tensor.view(ne, bs, 15, 15)
    
    return final_tensor

#将60*60的tensor转为15*15的tensor导致区域精度下降严重(可视化结果展示)
#但是直接对240*240pixel特征进行聚类的效果又比较差
#有一种新策略，就是在60*60的聚类类别表征上算出每个位置的权重矩阵，然后在训练时再做平均，这样可以保留更多的区域权重信息
def scale_cluster_idx_to_standard_shape(category_tensor):
    # 假设 category_tensor 是形状为 bs*3600 的类别表征张量
    bs, num_tokens = category_tensor.shape
    assert num_tokens == 3600, "输入张量的第二维度必须为 3600"

    # 恢复空间形状
    spatial_categories = category_tensor.view(bs, 60, 60)
    
    # # 对类别张量进行 max pooling
    # pooled_categories, _ = max_pooling_with_argmax(spatial_categories, kernel_size=4)
    # 对类别张量进行 max pooling
    pooled_categories = max_pooling_with_mode(spatial_categories, kernel_size=4)

    print("before flatten shape:", pooled_categories.shape)
    
    print("pooled_categories:", pooled_categories)
    
    # 按行优先把225长度拉平成最终结果(15*15)
    final_pooled_categories = pooled_categories.view(bs, 15, 15).view(bs, -1).int()
    # final_pooled_categories = pooled_categories.view(bs, 15, 15).view(bs, -1).int()
    # final_pooled_categories = pooled_categories.view(bs, -1).int()
    print("after flatten shape:", final_pooled_categories.shape)
    
    print("final_pooled_categories:", final_pooled_categories)
    
    return final_pooled_categories


def scale_rescale_matrix_to_standard_shape(rescale_matrix):
    # 假设 category_tensor 是形状为 bs*3600 的类别表征张量
    num_entity, bs, num_tokens = rescale_matrix.shape
    assert num_tokens == 3600, "输入张量的第二维度必须为 3600"

    # 恢复空间形状
    spatial_categories = rescale_matrix.view(num_entity, bs, 60, 60)
    
    # # 对类别张量进行 max pooling
    # pooled_categories, _ = max_pooling_with_argmax(spatial_categories, kernel_size=4)
    # 对类别张量进行 max pooling
    pooled_categories = downsample_to_15x15_with_avg(spatial_categories, kernel_size=4)

    # print("before flatten shape:", pooled_categories.shape)
    
    # print("pooled_categories:", pooled_categories)
    
    # 按行优先把225长度拉平成最终结果(15*15)
    # final_pooled_categories = pooled_categories.view(num_entity, bs, 15, 15).view(bs, -1).int()
    # final_pooled_categories = pooled_categories.view(bs, 15, 15).view(bs, -1).int()
    final_pooled_categories = pooled_categories.view(num_entity, bs, -1)
    # print("after flatten shape:", final_pooled_categories.shape)
    
    # print("final_pooled_categories:", final_pooled_categories)
    
    return final_pooled_categories




def fit(model,
        args,
        dataloader: DataLoader,
        device: str,
        check_path: str,
        train_data: DataLoader,
        ):

    # change the model into eval mode
    model.eval_mode()

    features1 = []
    features2 = []
    for (data, mask, label, name, img_type) in train_data:

        data = [model.transform(Image.fromarray(cv2.cvtColor(f.numpy(), cv2.COLOR_BGR2RGB))) for f in data]
        data = torch.stack(data, dim=0).to(device)
        _, _, feature_map1, feature_map2 = model.encode_image(data)
        features1.append(feature_map1)
        features2.append(feature_map2)

    features1 = torch.cat(features1, dim=0)
    features2 = torch.cat(features2, dim=0)
    model.build_image_feature_gallery(features1, features2)

    optimizer = torch.optim.SGD(model.prompt_learner.parameters(), lr=args.lr, momentum=args.momentum, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.Epoch, eta_min=1e-5)
    criterion = nn.CrossEntropyLoss().to(device)
    criterion_tip = TripletLoss(margin=1.0)

    best_result_dict = None
    gt_matches = None
    grouped_entity_features = None
    cluster_data = None
    token_dict_new = None
    rescale_matrix = None
    token_dict_new_960 = None
    for epoch in range(args.Epoch):
        for (data, mask, label, name, img_type) in train_data:
            
            if cluster_data is None:
                cluster_data = [model.cluster_transform(Image.fromarray(cv2.cvtColor(f.numpy(), cv2.COLOR_BGR2RGB))) for f in data] #240*4 pix
                cluster_data = torch.stack(cluster_data, dim=0).to(device) #k 3 960 960
            
            
            data = [model.transform(Image.fromarray(cv2.cvtColor(f.numpy(), cv2.COLOR_BGR2RGB))) for f in data]
            data = torch.stack(data, dim=0).to(device)

            # data = data[0:1, :, :, :].to(device)
            data = data.to(device)

            # normal_text_prompt, abnormal_text_prompt_handle, abnormal_text_prompt_learned, normal_entity_prompts_list, abnormal_entity_prompts_handle_list, abnormal_entity_prompts_learned_list = model.prompt_learner()

            normal_text_prompt, abnormal_text_prompt_handle, abnormal_text_prompt_learned, normal_entity_prompts_list, abnormal_entity_prompts_handle_list, abnormal_entity_prompts_learned_list, normal_background_prompts, abnormal_background_prompts_handle, abnormal_background_prompts_learned = model.prompt_learner()
            
            optimizer.zero_grad()

            normal_text_features = model.encode_text_embedding(normal_text_prompt, model.tokenized_normal_prompts)
            normal_background_features = model.encode_text_embedding(normal_background_prompts, model.tokenized_normal_background_prompts)
            normal_entity_features_list = [model.encode_text_embedding(normal_entity_prompts, tokenized_normal_entity_prompts) for normal_entity_prompts, tokenized_normal_entity_prompts in zip(normal_entity_prompts_list, model.tokenized_normal_entity_prompts_list)]
            
            
            abnormal_text_features_handle = model.encode_text_embedding(abnormal_text_prompt_handle, model.tokenized_abnormal_prompts_handle)
            abnormal_text_features_learned = model.encode_text_embedding(abnormal_text_prompt_learned, model.tokenized_abnormal_prompts_learned)
            abnormal_text_features = torch.cat([abnormal_text_features_handle, abnormal_text_features_learned], dim=0)

            abnormal_background_features_handle = model.encode_text_embedding(abnormal_background_prompts_handle, model.tokenized_abnormal_background_prompts_handle)
            abnormal_background_features_learned = model.encode_text_embedding(abnormal_background_prompts_learned, model.tokenized_abnormal_background_prompts_learned)
            abnormal_background_features = torch.cat([abnormal_background_features_handle, abnormal_background_features_learned], dim=0)
            
            
            abnormal_entity_features_handle_list = [model.encode_text_embedding(abnormal_entity_prompts_handle, tokenized_abnormal_entity_prompts_handle) for abnormal_entity_prompts_handle, tokenized_abnormal_entity_prompts_handle in zip(abnormal_entity_prompts_handle_list, model.tokenized_abnormal_entity_prompts_handle_list)]
            abnormal_entity_features_learned_list = [model.encode_text_embedding(abnormal_entity_prompts_learned, tokenized_abnormal_entity_prompts_learned) for abnormal_entity_prompts_learned, tokenized_abnormal_entity_prompts_learned in zip(abnormal_entity_prompts_learned_list, model.tokenized_abnormal_entity_prompts_learned_list)]
            abnormal_entity_features_list = [torch.cat([abnormal_entity_features_handle, abnormal_entity_features_learned], dim=0) for abnormal_entity_features_handle, abnormal_entity_features_learned in zip(abnormal_entity_features_handle_list, abnormal_entity_features_learned_list)]
            
            #把全图text_features和背景background_features添加进entity_features_list，提高代码可读性+并行性(方便调整)
            #先加text，再加background
            # normal_entity_features_list.append(normal_text_features)
            normal_entity_features_list.append(normal_background_features)
            
            
            #同理，把全图和背景异常特征加到列表最后面
            # abnormal_entity_features_list.append(abnormal_text_features)
            abnormal_entity_features_list.append(abnormal_background_features)
            
            
            
            # compute mean
            mean_ad_handle = torch.mean(F.normalize(abnormal_text_features_handle, dim=-1), dim=0)
            mean_ad_learned = torch.mean(F.normalize(abnormal_text_features_learned, dim=-1), dim=0)

            loss_match_abnormal = (mean_ad_handle - mean_ad_learned).norm(dim=0) ** 2.0

            cls_feature, _, _, _ = model.encode_image(data)

            # compute mean entity
            mean_entity_ad_handle_list = [torch.mean(F.normalize(abnormal_entity_features_handle, dim=-1), dim=0) for abnormal_entity_features_handle in abnormal_entity_features_handle_list]
            mean_entity_ad_learned_list = [torch.mean(F.normalize(abnormal_entity_features_learned, dim=-1), dim=0) for abnormal_entity_features_learned in abnormal_entity_features_learned_list]

            loss_match_entity_abnormal_list = [(mean_entity_ad_handle - mean_entity_ad_learned).norm(dim=0) ** 2.0 for mean_entity_ad_handle, mean_entity_ad_learned in zip(mean_entity_ad_handle_list, mean_entity_ad_learned_list)]
            
            
            # compute v2t loss and triplet loss
            normal_text_features_ahchor = normal_text_features.mean(dim=0).unsqueeze(0)
            normal_text_features_ahchor = normal_text_features_ahchor / normal_text_features_ahchor.norm(dim=-1, keepdim=True)

            normal_entity_features_ahchor_list = [normal_entity_features.mean(dim=0).unsqueeze(0) for normal_entity_features in normal_entity_features_list]
            normal_entity_features_ahchor_list = [normal_entity_features_ahchor / normal_entity_features_ahchor.norm(dim=-1, keepdim=True) for normal_entity_features_ahchor in normal_entity_features_ahchor_list]
            
            
            abnormal_text_features_ahchor = abnormal_text_features.mean(dim=0).unsqueeze(0)
            abnormal_text_features_ahchor = abnormal_text_features_ahchor / abnormal_text_features_ahchor.norm(dim=-1, keepdim=True)
            abnormal_text_features = abnormal_text_features / abnormal_text_features.norm(dim=-1, keepdim=True)

            abnormal_entity_features_ahchor_list = [abnormal_entity_features.mean(dim=0).unsqueeze(0) for abnormal_entity_features in abnormal_entity_features_list]
            abnormal_entity_features_ahchor_list = [abnormal_entity_features_ahchor / abnormal_entity_features_ahchor.norm(dim=-1, keepdim=True) for abnormal_entity_features_ahchor in abnormal_entity_features_ahchor_list]
            abnormal_entity_features_list = [abnormal_entity_features / abnormal_entity_features.norm(dim=-1, keepdim=True) for abnormal_entity_features in abnormal_entity_features_list]
            
            
            
            l_pos = torch.einsum('nc,cm->nm', cls_feature, normal_text_features_ahchor.transpose(0, 1))
            l_neg_v2t = torch.einsum('nc,cm->nm', cls_feature, abnormal_text_features.transpose(0, 1))

            if model.precision == 'fp16':
                logit_scale = model.model.logit_scale.half()
            else:
                logit_scale = model.model.logit_scale

            l_entity_pos_list = [torch.einsum('nc,cm->nm', cls_feature, normal_entity_features_ahchor.transpose(0, 1)) for normal_entity_features_ahchor in normal_entity_features_ahchor_list]
            l_entity_neg_v2t_list = [torch.einsum('nc,cm->nm', cls_feature, abnormal_entity_features.transpose(0, 1)) for abnormal_entity_features in abnormal_entity_features_list]
            
            
            logits_v2t = torch.cat([l_pos, l_neg_v2t], dim=-1) * logit_scale

            target_v2t = torch.zeros([logits_v2t.shape[0]], dtype=torch.long).to(device)

            loss_v2t = criterion(logits_v2t, target_v2t)

            trip_loss = criterion_tip(cls_feature, normal_text_features_ahchor, abnormal_text_features_ahchor)
            
            
            logits_v2t_entity_list = [torch.cat([l_entity_pos, l_entity_neg_v2t], dim=-1) * logit_scale for l_entity_pos, l_entity_neg_v2t in zip(l_entity_pos_list, l_entity_neg_v2t_list)]
            
            target_v2t_entity_list = [torch.zeros([logits_v2t_entity.shape[0]], dtype=torch.long).to(device) for logits_v2t_entity in logits_v2t_entity_list]
            
            loss_entity_v2t_list = [criterion(logits_v2t_entity, target_v2t_entity) for logits_v2t_entity, target_v2t_entity in zip(logits_v2t_entity_list, target_v2t_entity_list)]
            
            trip_entity_loss_list = [criterion_tip(cls_feature, normal_entity_features_ahchor, abnormal_entity_features_ahchor) for normal_entity_features_ahchor, abnormal_entity_features_ahchor in zip(normal_entity_features_ahchor_list, abnormal_entity_features_ahchor_list)]
            
            
            loss = loss_v2t + trip_loss + loss_match_abnormal * args.lambda1 + sum(loss_entity_v2t_list) + sum(trip_entity_loss_list) + sum(loss_match_entity_abnormal_list) * args.lambda1
            # loss = loss_v2t + trip_loss + loss_match_abnormal * args.lambda1

            loss.backward()
            optimizer.step()
        scheduler.step()
        # model.build_text_feature_gallery()
        model.build_text_feature_patch_gallery()

        scores_img = []
        score_maps = []
        test_imgs = []
        gt_list = []
        gt_mask_list = []
        names = []

        for (data, mask, label, name, img_type) in dataloader:

            data = [model.transform(Image.fromarray(f.numpy())) for f in data]
            data = torch.stack(data, dim=0)

            for d, n, l, m in zip(data, name, label, mask):
                test_imgs += [denormalization(d.cpu().numpy())]
                l = l.numpy()
                m = m.numpy()
                m[m > 0] = 1

                names += [n]
                gt_list += [l]
                gt_mask_list += [m]

            data = data.to(device)
            score_img, score_map = model(data, 'cls')
            score_maps += score_map
            scores_img += score_img

        test_imgs, score_maps, gt_mask_list = specify_resolution(test_imgs, score_maps, gt_mask_list, resolution=(args.resolution, args.resolution))
        result_dict = metric_cal_img(np.array(scores_img), gt_list, np.array(score_maps))

        if best_result_dict is None:
            save_check_point(model, check_path)
            best_result_dict = result_dict

        elif best_result_dict['i_roc'] < result_dict['i_roc']:
            save_check_point(model, check_path)
            best_result_dict = result_dict

    return best_result_dict


def main(args):
    kwargs = vars(args)

    if kwargs['seed'] is None:
        kwargs['seed'] = 111

    setup_seed(kwargs['seed'])

    if kwargs['use_cpu'] == 0:
        device = f"cuda:0"
    else:
        device = f"cpu"
    kwargs['device'] = device

    # prepare the experiment dir
    _, csv_path, check_path = get_dir_from_args(TASK, **kwargs)

    #如果ckpt已经存在，就不训练了，直接返回
    if os.path.exists(check_path):
        return
    
    # get the train dataloader
    train_dataloader, train_dataset_inst = get_dataloader_from_args(phase='train', perturbed=False, **kwargs)

    # get the test dataloader
    test_dataloader, test_dataset_inst = get_dataloader_from_args(phase='test', perturbed=False, **kwargs)

    kwargs['out_size_h'] = kwargs['resolution']
    kwargs['out_size_w'] = kwargs['resolution']

    # get the model
    model = FineGrainedPatchAD(**kwargs)
    model = model.to(device)

    # as the pro metric calculation is costly, we only calculate it in the last evaluation
    metrics = fit(model, args, test_dataloader, device, check_path=check_path, train_data=train_dataloader)

    i_roc = round(metrics['i_roc'], 2)
    object = kwargs['class_name']
    print(f'Object:{object} =========================== Image-AUROC:{i_roc}\n')

    save_metric(metrics, dataset_classes[kwargs['dataset']], kwargs['class_name'],
                kwargs['dataset'], csv_path)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def get_args():
    parser = argparse.ArgumentParser(description='Anomaly detection')
    parser.add_argument('--dataset', type=str, default='mvtec', choices=['mvtec', 'visa', 'realiad'])
    parser.add_argument('--class_name', type=str, default='carpet')

    parser.add_argument('--img-resize', type=int, default=240)
    parser.add_argument('--img-cropsize', type=int, default=240)
    parser.add_argument('--resolution', type=int, default=400)

    parser.add_argument('--batch-size', type=int, default=400)
    parser.add_argument('--vis', type=str2bool, choices=[True, False], default=False)
    parser.add_argument("--root-dir", type=str, default="./result_finegrained_0930_w15_fp32")
    parser.add_argument("--load-memory", type=str2bool, default=True)
    parser.add_argument("--cal-pro", type=str2bool, default=False)
    parser.add_argument("--seed", type=int, default=111)
    parser.add_argument("--gpu-id", type=int, default=0)

    # pure test
    parser.add_argument("--pure-test", type=str2bool, default=False)

    # method related parameters
    parser.add_argument('--k-shot', type=int, default=4)
    parser.add_argument("--backbone", type=str, default="ViT-B-16-plus-240",
                        choices=['ViT-B-16-plus-240', 'ViT-B-16'])
    parser.add_argument("--pretrained_dataset", type=str, default="laion400m_e32")
    parser.add_argument("--precision", type=str, default='fp32')
    parser.add_argument("--use-cpu", type=int, default=0)

    # prompt tuning hyper-parameter
    parser.add_argument("--n_ctx", type=int, default=4)
    parser.add_argument("--n_ctx_ab", type=int, default=1)
    parser.add_argument("--n_pro", type=int, default=3)
    parser.add_argument("--n_pro_ab", type=int, default=4)
    parser.add_argument("--Epoch", type=int, default=50)

    # optimizer
    parser.add_argument("--lr", type=float, default=0.002)
    parser.add_argument("--momentum", type=float, default=0.9)
    parser.add_argument("--weight_decay", type=float, default=0.0005)

    # loss hyper parameter
    parser.add_argument("--lambda1", type=float, default=0.001)

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    import os

    args = get_args()
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['CUDA_VISIBLE_DEVICES'] = f"{args.gpu_id}"
    main(args)
