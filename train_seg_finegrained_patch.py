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
from PromptAD import FineGrainedPatchAD
from collections import OrderedDict
from datasets.cluster_gt.visa import pcb2
TASK = 'SEG'

def save_check_point(model, path):
    selected_keys = [
        'feature_gallery1',
        'feature_gallery2',
        # 'large_memory',
        # 'middle_memory',
        # 'patch_memory',
        'text_features',
        'background_features',
        'entity_features_list',
        'q_former'
    ]
    state_dict = model.state_dict()
    selected_state_dict = {k: v for k, v in state_dict.items() if k in selected_keys}

    torch.save(selected_state_dict, path)


# def initialize_memory(obj_list):

#     mid = []
#     large = []
#     patch = []
#     for x in obj_list:
#         mid.append((x, []))
#         large.append((x, []))
#         patch.append((x, []))
#     mid_memory   = OrderedDict(mid)
#     large_memory = OrderedDict(large)
#     patch_memory = OrderedDict(patch)
#     return mid_memory, large_memory, patch_memory


@torch.no_grad()
def memory(model, normal_loader, class_name, device, precision):
    normal_features_ls = {}
    obj_list = []
    obj_list.append(class_name)
    mid_memory, large_memory, patch_memory = [], [], []
    # for i in range(len(obj_list)):
        # if dataset_name == 'mvtec':
        #     normal_data = MVTecDataset(root=dataset_dir, transform=preprocess, target_transform=transform,
        #                                aug_rate=-1, mode='train', k_shot=k_shot, save_dir=save_path,
        #                                obj_name=obj_list[i])
        # elif dataset_name == 'visa':
        #     normal_data = VisaDataset(root=dataset_dir, transform=preprocess, target_transform=transform,
        #                               mode='train', k_shot=k_shot, save_dir=save_path, obj_name=obj_list[i])

        # normal_dataloader = torch.utils.data.DataLoader(normal_data, batch_size=1, shuffle=False)
        # for index, items in enumerate(normal_loader):
    for (data, mask, label, name, img_type) in normal_loader:
        data = [model.transform(Image.fromarray(cv2.cvtColor(f.numpy(), cv2.COLOR_BGR2RGB))) for f in data]

        images = torch.stack(data, dim=0).to(device)
        # print("(Memory)images.shape:", images.shape) #torch.Size([k, 3, 240, 240])
        
        if precision == 'fp16':
            images = images.half()
        elif precision == 'bf16':
            images = images.to(torch.bfloat16)
        
        # images = items['img'].to(device)
        # cls_name = items['cls_name']
        # cls_id = items['cls_id']
        patch_size = 16
        # gt_mask = items['img_mask']
        # gt_mask[gt_mask > 0.5], gt_mask[gt_mask <= 0.5] = 1, 0
        # print("class_name", cls_name)
        large_scale_tokens, mid_scale_tokens, patch_tokens, class_tokens, large_scale, mid_scale = model.encode_image(images, patch_size)
        # print("shape in memory:", large_scale_tokens.shape, mid_scale_tokens.shape, patch_tokens.shape)
        
        # return
        # print("large_scale_tokens", large_scale_tokens.shape, mid_scale_tokens.shape, patch_tokens.shape)
        # for class_name, tokens in zip(cls_name, large_scale_tokens):
        #     large_memory[class_name].append(tokens)
        # for class_name, tokens in zip(cls_name, mid_scale_tokens):
        #     mid_memory[class_name].append(tokens)
        # for class_name, tokens in zip(cls_name, patch_tokens):
        #     patch_memory[class_name].append(tokens)
        for tokens in large_scale_tokens:
            large_memory.append(tokens)
        for tokens in mid_scale_tokens:
            mid_memory.append(tokens)
        for tokens in patch_tokens:
            patch_memory.append(tokens)
            #     print("lennnnnshape", tokens.shape)
            # print("large_memory", large_memory)
            # print("mid_memory", mid_memory)
            # print("large_memory", patch_memory)
    # for class_name in obj_list:
    large_memory = torch.cat(large_memory)
    mid_memory = torch.cat(mid_memory)
    patch_memory = torch.cat(patch_memory)
        # print("lennnnnshape", patch_memory[class_name].shape)


    return large_memory, mid_memory, patch_memory


def few_shot(memory, token):
    retrive = []
    # for i in class_name:
    L, N, D = memory.shape
    retrive.append(memory.permute(2, 1, 0).reshape(D,-1)) # D NL
    retrive = torch.stack(retrive)# B D NL
     #B D L 
    M = 1/2 * torch.min(1.0 - torch.bmm(F.normalize(token.squeeze(2), dim = -1), F.normalize(retrive, dim = 1)), dim = -1)[0]
    return M



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
        img_dir: str,
        check_path: str,
        train_data: DataLoader,
        ):

    # change the model into eval mode
    model.eval_mode()
    
    # start_time = time.time()
    
    
    # large_memory, mid_memory, patch_memory = memory(model.to(device),train_data, args.class_name, device, args.precision)
    # model.build_image_feature_gallery_winclip(large_memory.squeeze(1), mid_memory.squeeze(1), patch_memory.squeeze(1))
    # memory_time = time.time() - start_time
    
    # print(f"Memory building time: {memory_time}")
    
    # print("memory.shape:", large_memory.shape, mid_memory.shape, patch_memory.shape)
    # return
    

    
    

    #old_visual_branch
    features1 = []
    features2 = []
    for (data, mask, label, name, img_type) in train_data:
        data = [model.transform(Image.fromarray(cv2.cvtColor(f.numpy(), cv2.COLOR_BGR2RGB))) for f in data]

        data = torch.stack(data, dim=0).to(device)
        _, _, feature_map1, feature_map2 = model.encode_image(data) #选择归一化四层特征(from VV-CLIP)的最后两层用作memorybank
        features1.append(feature_map1)
        features2.append(feature_map2)

    features1 = torch.cat(features1, dim=0)
    features2 = torch.cat(features2, dim=0)
    model.build_image_feature_gallery(features1, features2) # use training data to build memory bank(which can be interpreted as few-shot).

    # optimizer = torch.optim.SGD(model.prompt_learner.parameters(), lr=args.lr, momentum=args.momentum, weight_decay=args.weight_decay)
    # 修改为（同时训练prompt_learner和q_former）：
    trainable_params = list(model.prompt_learner.parameters()) + list(model.q_former.parameters())
    optimizer = torch.optim.SGD(trainable_params, lr=args.lr, momentum=args.momentum, weight_decay=args.weight_decay)
    
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.Epoch, eta_min=1e-5)
    criterion = nn.CrossEntropyLoss().to(device)
    criterion_tip = TripletLoss(margin=1.0)

    best_result_dict = None
    best_result_dict_pro = None
    gt_matches = None
    grouped_entity_features = None
    cluster_data = None
    token_dict_new = None
    rescale_matrix = None
    token_dict_new_960 = None
    #用tqdm包装dataloader，可以显示进度条
    # for epoch in range(args.Epoch):
    #     for (data, mask, label, name, img_type) in train_data:
    for epoch in tqdm(range(args.Epoch)):
        # for (data, mask, label, name, img_type) in train_data:
        for (data, mask, label, name, img_type) in tqdm(train_data, desc=f"Epoch {epoch+1}/{args.Epoch}", leave=False):
            
            if cluster_data is None:
                cluster_data = [model.cluster_transform(Image.fromarray(cv2.cvtColor(f.numpy(), cv2.COLOR_BGR2RGB))) for f in data] #240*4 pix
                cluster_data = torch.stack(cluster_data, dim=0).to(device) #k 3 960 960
            
            
            data = [model.transform(Image.fromarray(cv2.cvtColor(f.numpy(), cv2.COLOR_BGR2RGB))) for f in data]
            data = torch.stack(data, dim=0).to(device)

            data = data.to(device)
            # print("(Training)images.shape:", data.shape) #torch.Size([k, 3, 240, 240])
            # optimizer.zero_grad()
            # prompt_start_time = time.time()
            normal_text_prompt, abnormal_text_prompt_handle, abnormal_text_prompt_learned, normal_entity_prompts_list, abnormal_entity_prompts_handle_list, abnormal_entity_prompts_learned_list, normal_background_prompts, abnormal_background_prompts_handle, abnormal_background_prompts_learned = model.prompt_learner()

            optimizer.zero_grad()

            normal_text_features = model.encode_text_embedding(normal_text_prompt, model.tokenized_normal_prompts)
            normal_background_features = model.encode_text_embedding(normal_background_prompts, model.tokenized_normal_background_prompts)
            normal_entity_features_list = [model.encode_text_embedding(normal_entity_prompts, tokenized_normal_entity_prompts) for normal_entity_prompts, tokenized_normal_entity_prompts in zip(normal_entity_prompts_list, model.tokenized_normal_entity_prompts_list)]

            # normal_entity_features_list = normal_entity_features_list.append(normal_background_features)
            
            
            
            
            # print("normal_text_features.shape:", normal_text_features.shape)
            # print("normal_entity_features_list[0].shape:", normal_entity_features_list[0].shape)
            # print("normal_background_features.shape:", normal_background_features.shape)


            abnormal_text_features_handle = model.encode_text_embedding(abnormal_text_prompt_handle, model.tokenized_abnormal_prompts_handle)
            abnormal_text_features_learned = model.encode_text_embedding(abnormal_text_prompt_learned, model.tokenized_abnormal_prompts_learned)
            abnormal_text_features = torch.cat([abnormal_text_features_handle, abnormal_text_features_learned], dim=0)
            
            # print("abnormal_text_features_handle.shape:", abnormal_text_features_handle.shape)
            # print("abnormal_text_features_learned.shape:", abnormal_text_features_learned.shape)
            # print("abnormal_text_features.shape:", abnormal_text_features.shape)
            
            
            abnormal_background_features_handle = model.encode_text_embedding(abnormal_background_prompts_handle, model.tokenized_abnormal_background_prompts_handle)
            abnormal_background_features_learned = model.encode_text_embedding(abnormal_background_prompts_learned, model.tokenized_abnormal_background_prompts_learned)
            abnormal_background_features = torch.cat([abnormal_background_features_handle, abnormal_background_features_learned], dim=0)
            
            
            abnormal_entity_features_handle_list = [model.encode_text_embedding(abnormal_entity_prompts_handle, tokenized_abnormal_entity_prompts_handle) for abnormal_entity_prompts_handle, tokenized_abnormal_entity_prompts_handle in zip(abnormal_entity_prompts_handle_list, model.tokenized_abnormal_entity_prompts_handle_list)]
            abnormal_entity_features_learned_list = [model.encode_text_embedding(abnormal_entity_prompts_learned, tokenized_abnormal_entity_prompts_learned) for abnormal_entity_prompts_learned, tokenized_abnormal_entity_prompts_learned in zip(abnormal_entity_prompts_learned_list, model.tokenized_abnormal_entity_prompts_learned_list)]
            abnormal_entity_features_list = [torch.cat([abnormal_entity_features_handle, abnormal_entity_features_learned], dim=0) for abnormal_entity_features_handle, abnormal_entity_features_learned in zip(abnormal_entity_features_handle_list, abnormal_entity_features_learned_list)]
            
            # abnormal_entity_features_list = abnormal_entity_features_list.append(abnormal_background_features)
            
            
            # print("Number of abnormal_entity_features_handle_list:", len(abnormal_entity_features_handle_list))
            # print("abnormal_entity_features_handle_list[0].shape:", abnormal_entity_features_handle_list[0].shape)
            # print("abnormal_entity_features_learned_list[0].shape:", abnormal_entity_features_learned_list[0].shape)
            # print("abnormal_entity_features_list[0].shape:", abnormal_entity_features_list[0].shape)
            
            #把全图text_features和背景background_features添加进entity_features_list，提高代码可读性+并行性(方便调整)
            #先加text，再加background
            # normal_entity_features_list.append(normal_text_features)
            normal_entity_features_list.append(normal_background_features)
            
            
            #同理，把全图和背景异常特征加到列表最后面
            # abnormal_entity_features_list.append(abnormal_text_features)
            abnormal_entity_features_list.append(abnormal_background_features)
            
            #alignment loss:(让text_features - 所有entity_features - background_features == 0)
            # stacked_normal_entity_features = torch.stack(normal_entity_features_list)
            loss_normal_align = (torch.mean(F.normalize(normal_text_features, dim=-1), dim=0) - torch.mean(F.normalize(torch.sum(torch.stack(normal_entity_features_list), dim=0), dim=-1), dim=0)).norm(dim=0) ** 2.0
            # loss_normal_align = (torch.mean(F.normalize(normal_text_features, dim=-1), dim=0) - torch.mean(F.normalize(torch.sum(torch.stack(normal_entity_features_list), dim=0), dim=-1), dim=0) - torch.mean(F.normalize(normal_background_features, dim=-1), dim=0)).norm(dim=0) ** 2.0
            
            # print("abnormal_text_features.shape:", abnormal_text_features.shape)
            # print("abnormal_entity_features_list[0].shape:", abnormal_entity_features_list[0].shape)
            # print("abnormal_background_features.shape:", abnormal_background_features.shape)
            
            # Regularization loss (ℓ_reg): ‖(p_a_img - Σ p_a_ci) - p_b‖
            # Constrains that image-level abnormal features minus sum of component-level abnormal features equals background features
            loss_reg = ((torch.mean(F.normalize(abnormal_text_features_learned, dim=-1), dim=0) - torch.mean(F.normalize(torch.sum(torch.stack(abnormal_entity_features_learned_list), dim=0), dim=-1), dim=0)) - torch.mean(F.normalize(normal_background_features, dim=-1), dim=0)).norm(dim=0)
            # loss_abnormal_align = (abnormal_text_features - torch.sum(torch.stack(abnormal_entity_features_list), dim=0) - abnormal_background_features).norm(dim=0) ** 2.0
            
            
            
            
            # compute mean
            mean_ad_handle = torch.mean(F.normalize(abnormal_text_features_handle, dim=-1), dim=0)
            mean_ad_learned = torch.mean(F.normalize(abnormal_text_features_learned, dim=-1), dim=0)

            loss_match_abnormal = (mean_ad_handle - mean_ad_learned).norm(dim=0) ** 2.0
            
            # # compute mean background
            # mean_background_ad_handle = torch.mean(F.normalize(abnormal_background_features_handle, dim=-1), dim=0)
            # mean_background_ad_learned = torch.mean(F.normalize(abnormal_background_features_learned, dim=-1), dim=0)
            
            # loss_match_abnormal_background = (mean_background_ad_handle - mean_background_ad_learned).norm(dim=0) ** 2.0

            
            _, feature_map, _, _ = model.encode_image(data)
            # large_scale_tokens, mid_scale_tokens, patch_tokens, class_tokens, large_scale, mid_scale = model.encode_image(images, patch_size)
            # large_scale_tokens, mid_scale_tokens, feature_map, class_tokens, large_scale, mid_scale = model.encode_image(data, patch_size=16)
            # feature_map = feature_map.squeeze(2) @ model.visual_proj # K 225 640
            # print("encode shape:", large_scale_tokens.shape, mid_scale_tokens.shape, feature_map.shape, class_tokens.shape)
            
            
            
            
            #在训练text prompt时，需要先从图像token里找到对应的token，然后再计算loss(相当于图像的token和对应的text prompt之间进行对齐)
            #对于k-shot的输入图像，应当用经过Q-Former的实体级prompt(带有一部分定义好的文本信息，足够检索，不只是使用可学习，要不然没法找到真正的匹配)去feature_map中检索特征距离最接近的visual token.
            
            
            
            
            if token_dict_new_960 is None:
            # if token_dict_new is None:
                cluster_tensor = cluster_tensor_preprocess(model, cluster_data)
                # token_dict_new = model.language_guided_progressive_region_aggregation(feature_map, torch.stack(normal_entity_features_list, dim=0).squeeze(1))
                # print("token_dict_new", token_dict_new['idx_token'])
                # return
                token_dict_new_960 = model.language_guided_progressive_region_aggregation(cluster_tensor, torch.stack(normal_entity_features_list, dim=0).squeeze(1))
                # torch.set_printoptions(profile="full")
                # print("token_dict_new_960", token_dict_new_960['idx_token'])
                
                if args.class_name in ['pcb2']:
                    # print("im here")
                    token_dict_new_960['idx_token'] = pcb2.to(device).repeat(int(args.k_shot), 1)
                
                # return
                # return
                # token_dict_new_960['idx_token'] = scale_cluster_idx_to_standard_shape(token_dict_new_960['idx_token'])
                # print("token_dict_new_960", token_dict_new_960['idx_token'])
                
                # return

            # print("Return token_dict_new")
            # print("token_dict_idx_token_240 shape:", token_dict_new['idx_token'])
            # print("token_dict_idx_token_960 shape:", token_dict_new_960['idx_token'])
            
            # return
            #对idx_token进行下采样，还原到和图像对应的尺寸
            # token_dict_new['idx_token'] = scale_cluster_idx_to_standard_shape(token_dict_new['idx_token'])
            
            # print("shape before match:", torch.mean(feature_map, dim = 0, keepdim=True).shape, torch.stack(normal_entity_features_list).squeeze(1).shape)
            
                #得到聚类结果后，将每一类的特征进行平均，然后计算每一类的特征与文本特征的相似度，最后选择相似度最大的类别作为匹配结果，在训练时，文本特征只和自己最相似的类别进行对齐
                # avg_visual_token_representation = []
                # for i in range(token_dict_new['token_num']):
                #     #计算idx_token中值为i的索引
                #     indices = (token_dict_new['idx_token'][0] == i)
                #     # 取出索引对应的特征
                #     token_features = feature_map[0, indices, :] #i 640
                #     # 取平均值
                #     token_features = torch.mean(token_features, dim = 0, keepdim=True) #，1维度为token数量，2维度为特征维度 B 1 640
                #     avg_visual_token_representation.append(token_features)
                    
                # avg_visual_token_representation = torch.cat(avg_visual_token_representation, dim = 0) #token_num 640
                # # print("avg_visual_token_representation shape:", avg_visual_token_representation.shape)
                # #需要计算正常文本实体特征(N, C)和每个类别的visual token()的相似度，然后选择最大的那个对应的索引,即输出一个尺寸为token num
                # sim_e2v = torch.mm(F.normalize(torch.stack(normal_entity_features_list).squeeze(1), dim=-1), F.normalize(avg_visual_token_representation, dim=-1).transpose(0, 1)) #N K
                # matches_e2v = torch.argmax(sim_e2v, dim = -1) #N
                # print("matches_e2v", matches_e2v)
                
                avg_visual_token_representation_3600 = []
                for i in range(token_dict_new_960['token_num']):
                    #计算idx_token中值为i的索引
                    indices = (token_dict_new_960['idx_token'][0] == i)
                    # 取出索引对应的特征
                    token_features = cluster_tensor[0, indices, :] #i 640
                    # 取平均值
                    token_features = torch.mean(token_features, dim = 0, keepdim=True) #，1维度为token数量，2维度为特征维度 B 1 640
                    avg_visual_token_representation_3600.append(token_features)
                    
                avg_visual_token_representation_3600 = torch.cat(avg_visual_token_representation_3600, dim = 0) #token_num 640
                # print("avg_visual_token_representation shape:", avg_visual_token_representation.shape)
                #需要计算正常文本实体特征(N, C)和每个类别的visual token()的相似度，然后选择最大的那个对应的索引,即输出一个尺寸为token num
                sim_e2v_3600 = torch.mm(F.normalize(torch.stack(normal_entity_features_list).squeeze(1), dim=-1), F.normalize(avg_visual_token_representation_3600, dim=-1).transpose(0, 1)) #N K
                matches_e2v_3600 = torch.argmax(sim_e2v_3600, dim = -1) #N
                
                
                #生成每一个实体类别对应的feature map需要的rescale矩阵
                # rescale_matrix = torch.ones((len(normal_entity_features_list), feature_map.shape[0], 225)).cuda() #num_entity, k-shot, 225
                rescale_matrix_3600 = torch.ones((len(normal_entity_features_list), feature_map.shape[0], 3600)).cuda() #num_entity, k-shot, 3600
                # print("rescale_matrix_3600 shape:", rescale_matrix_3600.shape)
                # for e_idx in range(rescale_matrix.shape[0]):
                #     for v_idx in range(rescale_matrix.shape[1]):
                #         rescale_matrix[e_idx, v_idx, (token_dict_new['idx_token'][v_idx] == matches_e2v[e_idx])] += 0.3
                        
                for e_idx in range(rescale_matrix_3600.shape[0]):
                    for v_idx in range(rescale_matrix_3600.shape[1]):
                        rescale_matrix_3600[e_idx, v_idx, (token_dict_new_960['idx_token'][v_idx] == matches_e2v_3600[e_idx])] += 1.5
                
                #将rescale_matrix_3600从num_entity, k-shot, 3600 rescale到num_entity, k-shot, 225
                #用4*4的窗口，计算窗口内平均值来下采样
                rescale_matrix = scale_rescale_matrix_to_standard_shape(rescale_matrix_3600) #num_entity, k-shot, 225
                # print("rescale_matrix shape:", rescale_matrix.shape)
                if args.precision == 'fp16':
                    rescale_matrix = rescale_matrix.half()
                elif args.precision == 'bf16':
                    rescale_matrix = rescale_matrix.to(torch.bfloat16)
                
                
            # torch.set_printoptions(profile="full")
            # print("rescale_matrix shape:", rescale_matrix.shape)
            # print("rescale_matrix:", rescale_matrix)
            # torch.set_printoptions(profile="default")
            
            # return
            
            # intrinsic_entity_features_list = model.q_former(torch.stack(normal_entity_features_list), torch.stack(abnormal_entity_features_list))
            # if gt_matches is None and grouped_entity_features is None:
            #     # gt_matches = model.get_max_cosine_similarity_match(feature_map[0].unsqueeze(0), torch.stack(normal_entity_features_list).squeeze(1))[0]#(1, i(225), j(entity + 2))->(i(225), j(entity + 2))
            #     gt_matches = model.get_max_cosine_similarity_match(torch.mean(feature_map, dim = 0, keepdim=True), torch.stack(normal_entity_features_list).squeeze(1))[0]#(1, i(225), j(entity + 2))->(i(225), j(entity + 2))
            #     # print("shape of matches:", gt_matches)
            
            #     #定义一个dict用来保存不同实体对应的visual tokens
            #     grouped_entity_features = {k:[] for k in range(model.prompt_learner.num_entity + 1)}
                
            #     #遍历每个batch的实体特征，将其对应的visual token加入到对应的dict中
            #     # for k in range(model.prompt_learner.num_entity + 2):
            #         #使用索引从gt_matches中提取对应的visual tokens项
            #         # indices = (gt_matches == k)
            #     # print("shape of feature_map:", feature_map.shape)
            #     for inx in range(feature_map.shape[1]):
            #         grouped_entity_features[gt_matches[inx][1]].append(feature_map[:, inx, :])
            #     # print(feature_map[indices].shape)
                
            #     for k in range(model.prompt_learner.num_entity + 1):
            #         if len(grouped_entity_features[k]) == 0:
            #             # continue
            #             grouped_entity_features[k] = feature_map.clone().cuda().detach()
            #             continue
            #         else:
            #             grouped_entity_features[k] = torch.stack(grouped_entity_features[k], dim = 1).cuda().detach()
            #         # print(f"shape of {k} feature map:", grouped_entity_features[k].shape)
            
            
            # _, feature_map, _, _ = model.encode_image(data)
            
            # compute mean entity
            mean_entity_ad_handle_list = [torch.mean(F.normalize(abnormal_entity_features_handle, dim=-1), dim=0) for abnormal_entity_features_handle in abnormal_entity_features_handle_list]
            mean_entity_ad_learned_list = [torch.mean(F.normalize(abnormal_entity_features_learned, dim=-1), dim=0) for abnormal_entity_features_learned in abnormal_entity_features_learned_list]

            loss_match_entity_abnormal_list = [(mean_entity_ad_handle - mean_entity_ad_learned).norm(dim=0) ** 2.0 for mean_entity_ad_handle, mean_entity_ad_learned in zip(mean_entity_ad_handle_list, mean_entity_ad_learned_list)]

            
            # compute v2t loss and triplet loss
            normal_text_features_ahchor = normal_text_features.mean(dim=0).unsqueeze(0)
            normal_text_features_ahchor = normal_text_features_ahchor / normal_text_features_ahchor.norm(dim=-1, keepdim=True)
            
            # normal_background_features_ahchor = normal_background_features.mean(dim=0).unsqueeze(0)
            # normal_background_features_ahchor = normal_background_features_ahchor / normal_background_features_ahchor.norm(dim=-1, keepdim=True)
            
            normal_entity_features_ahchor_list = [normal_entity_features.mean(dim=0).unsqueeze(0) for normal_entity_features in normal_entity_features_list]
            normal_entity_features_ahchor_list = [normal_entity_features_ahchor / normal_entity_features_ahchor.norm(dim=-1, keepdim=True) for normal_entity_features_ahchor in normal_entity_features_ahchor_list]

            abnormal_text_features_ahchor = abnormal_text_features.mean(dim=0).unsqueeze(0)
            abnormal_text_features_ahchor = abnormal_text_features_ahchor / abnormal_text_features_ahchor.norm(dim=-1, keepdim=True)
            abnormal_text_features = abnormal_text_features / abnormal_text_features.norm(dim=-1, keepdim=True)
            
            # abnormal_background_features_ahchor = abnormal_background_features.mean(dim=0).unsqueeze(0)
            # abnormal_background_features_ahchor = abnormal_background_features_ahchor / abnormal_background_features_ahchor.norm(dim=-1, keepdim=True)
            # abnormal_background_features = abnormal_background_features / abnormal_background_features.norm(dim=-1, keepdim=True)
            
            abnormal_entity_features_ahchor_list = [abnormal_entity_features.mean(dim=0).unsqueeze(0) for abnormal_entity_features in abnormal_entity_features_list]
            abnormal_entity_features_ahchor_list = [abnormal_entity_features_ahchor / abnormal_entity_features_ahchor.norm(dim=-1, keepdim=True) for abnormal_entity_features_ahchor in abnormal_entity_features_ahchor_list]
            abnormal_entity_features_list = [abnormal_entity_features / abnormal_entity_features.norm(dim=-1, keepdim=True) for abnormal_entity_features in abnormal_entity_features_list]


            l_pos = torch.einsum('nic,cj->nij', feature_map, normal_text_features_ahchor.transpose(0, 1))
            l_neg_v2t = torch.einsum('nic,cj->nij', feature_map, abnormal_text_features.transpose(0, 1))
            
            # l_pos += torch.einsum('nic,cj->nij', class_tokens.unsqueeze(1), normal_text_features_ahchor.transpose(0, 1))
            # l_neg_v2t += torch.einsum('nic,cj->nij', class_tokens.unsqueeze(1), abnormal_text_features.transpose(0, 1))

            if model.precision == 'fp16':
                logit_scale = model.model.logit_scale.half()
            elif model.precision == 'bf16':
                logit_scale = model.model.logit_scale.to(torch.bfloat16)
            else:
                logit_scale = model.model.logit_scale
            
            
            #这里输入feature_map需要从原始feature_map中筛选背景区域的特征，而不是直接使用feature_map
            # l_background_pos = torch.einsum('nic,cj->nij', feature_map, normal_background_features_ahchor.transpose(0, 1))
            # l_background_neg_v2t = torch.einsum('nic,cj->nij', feature_map, abnormal_background_features.transpose(0, 1))
            
            # print("0shape:", feature_map[:,(token_dict_new['idx_token'][0] == matches_e2v[0]),:].shape)
            # print("1shape:", feature_map[:,(token_dict_new['idx_token'][0] == matches_e2v[1]),:].shape)
            
            # l_entity_pos_list = [torch.einsum('nic,cj->nij', feature_map, normal_entity_features_ahchor.transpose(0, 1)) for normal_entity_features_ahchor in normal_entity_features_ahchor_list]
            # l_entity_neg_v2t_list = [torch.einsum('nic,cj->nij', feature_map, abnormal_entity_features.transpose(0, 1)) for abnormal_entity_features in abnormal_entity_features_list]
            
            # l_entity_pos_list = [torch.einsum('nic,cj->nij', feature_map, normal_entity_features_ahchor.transpose(0, 1)) for normal_entity_features_ahchor in normal_entity_features_ahchor_list]
            # l_entity_neg_v2t_list = [torch.einsum('nic,cj->nij', feature_map, abnormal_entity_features.transpose(0, 1)) for abnormal_entity_features in abnormal_entity_features_list]
            
            l_entity_pos_list = [torch.einsum('nic,cj->nij', feature_map * rescale_matrix[i].unsqueeze(-1).expand_as(feature_map), normal_entity_features_ahchor.transpose(0, 1)) for i, normal_entity_features_ahchor in enumerate(normal_entity_features_ahchor_list)]
            l_entity_neg_v2t_list = [torch.einsum('nic,cj->nij', feature_map * rescale_matrix[i].unsqueeze(-1).expand_as(feature_map), abnormal_entity_features.transpose(0, 1)) for i, abnormal_entity_features in enumerate(abnormal_entity_features_list)]
            
            # l_entity_pos_list = [torch.einsum('nic,cj->nij', feature_map, normal_entity_features_ahchor.transpose(0, 1)) for normal_entity_features_ahchor in normal_entity_features_ahchor_list]
            # l_entity_neg_v2t_list = [torch.einsum('nic,cj->nij', feature_map, abnormal_entity_features.transpose(0, 1)) for abnormal_entity_features in abnormal_entity_features_list]
            
            
            # l_entity_pos_list = [torch.einsum('nic,cj->nij', grouped_entity_features[idx], normal_entity_features_ahchor.transpose(0, 1)) for idx, normal_entity_features_ahchor in enumerate(normal_entity_features_ahchor_list)]
            # l_entity_neg_v2t_list = [torch.einsum('nic,cj->nij', grouped_entity_features[idx], abnormal_entity_features.transpose(0, 1)) for idx, abnormal_entity_features in enumerate(abnormal_entity_features_list)]


            logits_v2t = torch.cat([l_pos, l_neg_v2t], dim=-1) * logit_scale

            target_v2t = torch.zeros([logits_v2t.shape[0], logits_v2t.shape[1]], dtype=torch.long).to(device)

            loss_v2t = criterion(logits_v2t.transpose(1, 2), target_v2t)

            # trip_loss = criterion_tip(class_tokens.unsqueeze(1), normal_text_features_ahchor, abnormal_text_features_ahchor)
            trip_loss = criterion_tip(feature_map, normal_text_features_ahchor, abnormal_text_features_ahchor)
            
            # logits_v2t_background = torch.cat([l_background_pos, l_background_neg_v2t], dim=-1) * logit_scale
            
            # target_v2t_background = torch.zeros([logits_v2t_background.shape[0], logits_v2t_background.shape[1]], dtype=torch.long).to(device)
            
            # loss_v2t_background = criterion(logits_v2t_background.transpose(1, 2), target_v2t_background)
            
            # trip_loss_background = criterion_tip(feature_map, normal_background_features_ahchor, abnormal_background_features_ahchor)
            
            
            logits_v2t_entity_list = [torch.cat([l_entity_pos, l_entity_neg_v2t], dim=-1) * logit_scale for l_entity_pos, l_entity_neg_v2t in zip(l_entity_pos_list, l_entity_neg_v2t_list)]
            
            target_v2t_entity_list = [torch.zeros([logits_v2t_entity.shape[0], logits_v2t_entity.shape[1]], dtype=torch.long).to(device) for logits_v2t_entity in logits_v2t_entity_list]
            
            loss_entity_v2t_list = [criterion(logits_v2t_entity.transpose(1, 2), target_v2t_entity) for logits_v2t_entity, target_v2t_entity in zip(logits_v2t_entity_list, target_v2t_entity_list)]
            
            # trip_entity_loss_list = [criterion_tip(feature_map, normal_entity_features_ahchor, abnormal_entity_features_ahchor) for normal_entity_features_ahchor, abnormal_entity_features_ahchor in zip(normal_entity_features_ahchor_list, abnormal_entity_features_ahchor_list)]
            trip_entity_loss_list = [criterion_tip(feature_map * rescale_matrix[idx].unsqueeze(-1).expand_as(feature_map), normal_entity_features_ahchor, abnormal_entity_features_ahchor) for idx, (normal_entity_features_ahchor, abnormal_entity_features_ahchor) in enumerate(zip(normal_entity_features_ahchor_list, abnormal_entity_features_ahchor_list))]
            # trip_entity_loss_list += [criterion_tip(feature_map[:,(token_dict_new['idx_token'][0] == matches_e2v[idx]),:], normal_entity_features_ahchor, abnormal_entity_features_ahchor) for idx, (normal_entity_features_ahchor, abnormal_entity_features_ahchor) in enumerate(zip(normal_entity_features_ahchor_list, abnormal_entity_features_ahchor_list))]
            # trip_entity_loss_list = [criterion_tip(grouped_entity_features[idx], normal_entity_features_ahchor, abnormal_entity_features_ahchor) for idx, (normal_entity_features_ahchor, abnormal_entity_features_ahchor) in enumerate(zip(normal_entity_features_ahchor_list, abnormal_entity_features_ahchor_list))]
            # trip_entity_loss_list = [criterion_tip(feature_map, normal_entity_features_ahchor, abnormal_entity_features_ahchor) for normal_entity_features_ahchor, abnormal_entity_features_ahchor in zip(normal_entity_features_ahchor_list, abnormal_entity_features_ahchor_list)]
            
            #
            loss = loss_v2t + trip_loss + loss_match_abnormal * args.lambda1 + sum(loss_entity_v2t_list) + sum(trip_entity_loss_list) + sum(loss_match_entity_abnormal_list) * args.lambda1 + loss_reg
            # loss = loss_v2t + trip_loss + loss_match_abnormal * args.lambda1 + sum(loss_entity_v2t_list) + sum(trip_entity_loss_list) + sum(loss_match_entity_abnormal_list) * args.lambda1  # without loss_reg 
            # loss = loss_v2t + trip_loss + loss_match_abnormal * args.lambda1 + sum(loss_entity_v2t_list) + sum(trip_entity_loss_list) + sum(loss_match_entity_abnormal_list) * args.lambda1 + loss_v2t_background + trip_loss_background + loss_match_abnormal_background * args.lambda1 + loss_normal_align + loss_abnormal_handle_align + loss_abnormal_learned_align
            # loss = loss_v2t + trip_loss + loss_match_abnormal * args.lambda1 + sum(loss_entity_v2t_list) + sum(trip_entity_loss_list) + sum(loss_match_entity_abnormal_list) * args.lambda1 + loss_v2t_background + trip_loss_background + loss_match_abnormal_background * args.lambda1
            # loss = loss_v2t + trip_loss + loss_match_abnormal * args.lambda1 + sum(loss_entity_v2t_list) + sum(trip_entity_loss_list) + sum(loss_match_entity_abnormal_list) * args.lambda1
            # loss = loss_v2t + trip_loss + loss_match_abnormal * args.lambda1

            loss.backward()
            optimizer.step()
            
            # prompt_end_time = time.time() 
            # print(f"Prompt training time: {prompt_end_time - prompt_start_time}")

        scheduler.step()
        # model.build_text_feature_gallery()
        model.build_text_feature_patch_gallery()
        # text_gallery_time = time.time()
        # print(f"Text gallery building time: {text_gallery_time - prompt_end_time}")
        # print("build text feature gallery done!!!")
        score_maps = []
        test_imgs = []
        gt_mask_list = []
        names = []

        test_start_time = time.time()
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
            score_map = model(data, 'seg')
            score_maps += score_map
        # test_end_time = time.time() - test_start_time
        # print(f"Test time: {test_end_time}")
        
        test_imgs, score_maps, gt_mask_list = specify_resolution(test_imgs, score_maps, gt_mask_list, resolution=(args.resolution, args.resolution))
        # result_dict = metric_cal_pix(np.array(score_maps), gt_mask_list)
        result_dict = metric_cal_pix_multiple_metrics(np.array(score_maps), gt_mask_list)


        if best_result_dict is None:
            best_result_dict = result_dict
            save_check_point(model, check_path)
            if args.vis:
                plot_sample_cv2(names, test_imgs, {'FineGrainedAD': score_maps}, gt_mask_list, save_folder=img_dir)

        elif best_result_dict['p_roc'] < result_dict['p_roc']:
            best_result_dict = result_dict
            save_check_point(model, check_path)
            if args.vis:
                plot_sample_cv2(names, test_imgs, {'FineGrainedAD': score_maps}, gt_mask_list, save_folder=img_dir)
        
        if best_result_dict_pro is None:
            best_result_dict_pro = result_dict
            save_check_point(model, check_path.replace('check_point', 'check_point_pro'))
        
        elif best_result_dict_pro['p_pro'] < result_dict['p_pro']:
            best_result_dict_pro = result_dict
            save_check_point(model, check_path.replace('check_point', 'check_point_pro'))
        

    return best_result_dict


def main(args):
    
    kwargs = vars(args)

    if kwargs['seed'] is None:
        kwargs['seed'] = 111

    setup_seed(kwargs['seed'])

    if kwargs['use_gpu'] == -1:
        device = "cpu"
    elif 0 <= kwargs['use_gpu'] <= 7:
        device = f"cuda:{kwargs['use_gpu']}"
    else:
        raise ValueError(f"use_gpu must be between -1 and 7, got {kwargs['use_gpu']}")
    kwargs['device'] = device

    # prepare the experiment dir
    img_dir, csv_path, check_path = get_dir_from_args(TASK, **kwargs)
    
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
    # model = FineGrainedScaleAD(**kwargs)
    model = FineGrainedPatchAD(**kwargs)
    # model = FineGrainedAD(**kwargs)
    # model = PromptAD(**kwargs)
    model = model.to(device)
    
    # model.build_text_feature_patch_gallery()
    # model.calculate_textual_patch_anomaly_score()
    
    # return

    # as the pro metric calculation is costly, we only calculate it in the last evaluation
    metrics = fit(model, args, test_dataloader, device, img_dir=img_dir, check_path=check_path, train_data=train_dataloader)

    p_roc = round(metrics['p_roc'], 2)
    object = kwargs['class_name']
    print(f'Object:{object} =========================== Pixel-AUROC:{p_roc}\n')

    save_metric(metrics, dataset_classes[kwargs['dataset']], kwargs['class_name'],
                kwargs['dataset'], csv_path)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def get_args():
    parser = argparse.ArgumentParser(description='Anomaly detection')
    parser.add_argument('--dataset', type=str, default='realiad', choices=['mvtec', 'visa', 'realiad'])
    parser.add_argument('--class_name', type=str, default='audiojack')

    parser.add_argument('--img-resize', type=int, default=240)
    parser.add_argument('--img-cropsize', type=int, default=240)
    # parser.add_argument('--img-resize', type=int, default=224)
    # parser.add_argument('--img-cropsize', type=int, default=224)
    parser.add_argument('--resolution', type=int, default=400)

    parser.add_argument('--batch-size', type=int, default=100)
    parser.add_argument('--vis', type=str2bool, choices=[True, False], default=False)
    parser.add_argument("--root-dir", type=str, default="./result_finegrained_0930_w15_fp32")
    # parser.add_argument("--root-dir", type=str, default="./result_finegrained_0606_w15_fp32")
    parser.add_argument("--load-memory", type=str2bool, default=True)
    parser.add_argument("--cal-pro", type=str2bool, default=False)
    parser.add_argument("--seed", type=int, default=111)
    parser.add_argument("--gpu-id", type=int, default=0)

    # pure test
    parser.add_argument("--pure-test", type=str2bool, default=False)

    # method related parameters
    parser.add_argument('--k-shot', type=int, default=4)
    # parser.add_argument("--backbone", type=str, default="ViT-B-16-plus-240",
    #                     choices=['ViT-B-16-plus-240', 'ViT-B-16'])
    parser.add_argument("--backbone", type=str, default="ViT-B-16-plus-240",
                        choices=['ViT-B-16-plus-240', 'ViT-B-16', 'ViT-B-16-plus', 'ViT-B-32', 'ViT-L-14', 'ViT-L-14-280', 'ViT-L-14-336', 'ViT-H-14'])
    # parser.add_argument("--pretrained_dataset", type=str, default="laion400m")
    parser.add_argument("--pretrained_dataset", type=str, default="laion400m_e32")
    parser.add_argument("--version", type=str, default='')
    parser.add_argument("--precision", type=str, default='bf16')

    parser.add_argument("--use-gpu", type=int, default=0)

    # prompt tuning hyper-parameter
    parser.add_argument("--n_ctx", type=int, default=4)
    parser.add_argument("--n_ctx_ab", type=int, default=1)
    parser.add_argument("--n_pro", type=int, default=1)
    parser.add_argument("--n_pro_ab", type=int, default=4)
    parser.add_argument("--Epoch", type=int, default=100)

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
