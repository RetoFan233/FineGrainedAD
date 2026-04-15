import sys
import time
sys.path.append('..')
sys.path.append('.')

import torch
import random
import torch.nn as nn
from PromptAD import CLIPAD
from torch.nn import functional as F
from PromptAD.ad_prompts import *
from PIL import Image
from scipy.ndimage import gaussian_filter
from PromptAD.fine_grained_prompts import fine_grained_normal_prompts_v3, total_classes2id, class_state_abnormal_refined, fine_grained_color_list, fine_grained_texture_list, fine_grained_shape_list, fine_grained_location_list, fine_grained_number_list

from PromptAD.CLIPAD import SimpleTokenizer as _Tokenizer
from PromptAD.CLIPAD.transformer import QueryFormer
from PromptAD.clusters import CTM, TCBlock
from torchvision import transforms

valid_backbones = ['ViT-B-16-plus-240', 'ViT-B-16', 'ViT-B-16-plus', 'ViT-B-32', 'ViT-L-14', 'ViT-L-14-280', 'ViT-L-14-336', 'ViT-H-14']
valid_pretrained_datasets = ['laion400m_e32', 'laion2b', 'laion400m', 'laion2b_s32b_b79k', 'openai']

mean_train = [0.48145466, 0.4578275, 0.40821073]
std_train = [0.26862954, 0.26130258, 0.27577711]


def _convert_to_rgb(image):
    return image.convert('RGB')


class FineGrainedPatchPromptLearner(nn.Module):
    def __init__(self, n_ctx, n_pro, n_ctx_ab, n_pro_ab, classname, clip_model, pre):
        super().__init__()

        if pre == 'fp16':
            dtype = torch.float16
        elif pre == 'bf16':
            dtype = torch.bfloat16
        else:
            dtype = torch.float32

        # state_anomaly1 = state_anomaly + class_state_abnormal[classname] # ('damaged {}') + ('{} with large breakage', '{} with small breakage', '{} with contamination') #通用的异常state+特定类别的异常state

        # if classname in class_mapping:
        #     classname = class_mapping[classname]

        #First, we get the fine_grained normal prompts for the class
        normal_class_fine_grained_prompts_dict = fine_grained_normal_prompts_v3[total_classes2id[classname]]
        # normal_class_fine_grained_prompts_dict = fine_grained_normal_prompts_v2[total_classes2id[classname]]
        
        #str
        # normal_class_fine_grained_caption: str = normal_class_fine_grained_prompts_dict["summary"]
        normal_class_fine_grained_caption: str = normal_class_fine_grained_prompts_dict["caption"]
        
        # print("normal_class_fine_grained_caption: ", normal_class_fine_grained_caption)
        
        #dict
        normal_class_fine_grained_level_1: dict = normal_class_fine_grained_prompts_dict["Level_1"][0]
        normal_class_fine_grained_level_2: dict = normal_class_fine_grained_prompts_dict["Level_2"][0]
        normal_class_fine_grained_level_3: dict = normal_class_fine_grained_prompts_dict["Level_3"][0]
        
        # print("normal_class_fine_grained_level_1: ", normal_class_fine_grained_level_1)
        
        #首先在level_1的foreground上加一个{}用来替换异常状态词，这个就follow固定模板走
        #然后在level_3的texture上引入可学习的prompt，这个本质上就是一个tensor，可以通过模型学习得到
        #最终在最后的描述里，将对应单词替换为上述的prompt
        
        #Level_1: foreground
        normal_foreground_level_1 = normal_class_fine_grained_level_1["foreground"]
        # print("normal_foreground_level_1:", normal_foreground_level_1)
        #level_1: background
        normal_background_level_1 = normal_class_fine_grained_level_1["background"] + " background"
        
        abnormal_foreground_level_1 = [anomaly.replace("{}", normal_foreground_level_1) for anomaly in class_state_abnormal_refined[classname]]
        # abnormal_foreground_level_1 = [anomaly.replace("{}", normal_foreground_level_1) for anomaly in class_state_abnormal_refined[classname]]
        # print("abnormal_foreground_level_1: ", abnormal_foreground_level_1)
        
        #Level_2: entity, relation
        # normal_entity_level_2: str = normal_class_fine_grained_level_2["entity"] #e.g., bristle clusters toothbrush handle
        # normal_entity_level_2: str = " and ".join(normal_class_fine_grained_level_2["entity"]) #e.g., bristle clusters and toothbrush handle
        entity_list = normal_class_fine_grained_level_2["entity"]
        num_entity = len(entity_list)
        self.num_entity = num_entity
        # normal_entity_caption_list = normal_class_fine_grained_level_2["caption"]
        normal_entity_caption_list = normal_class_fine_grained_level_3["entity_caption"]
        normal_location_list = normal_class_fine_grained_level_2["location"]
        normal_number_list = normal_class_fine_grained_level_2["number"]
        abnormal_entity_caption_list = []
        
        for index in range(num_entity):
            abnormal_entity_caption = normal_entity_caption_list[index].lower()
            #首先替换实体名称为原始名称+异常状态词
            #分情况讨论:
            #1. 如果实体名称中最后一位不为s，那需要先从normal_entity_caption中找复数形态，然后替换为异常状态词，如果找不到，再替换原始名称为原始名称+异常状态词
            random_abnormal_state = random.choice(class_state_abnormal_refined[classname]).replace('{}', '')
            if entity_list[index][-1] != 's':
                if entity_list[index] + 's' in abnormal_entity_caption:
                    abnormal_entity_caption = abnormal_entity_caption.replace(entity_list[index] + 's', entity_list[index] + 's' + random_abnormal_state)
                else:
                    abnormal_entity_caption = abnormal_entity_caption.replace(entity_list[index], entity_list[index] + random_abnormal_state)
            else:
                abnormal_entity_caption = abnormal_entity_caption.replace(entity_list[index], entity_list[index] + random_abnormal_state)
            
            #然后考虑替换实体数量
            #如果实体数量为1，则在abnormal_entity_caption替换A Single, The Single, A, One, Single为其他数量？
            #这个先不加了？
            # random_entity_number = random.choice(fine_grained_number_list.remove(normal_number_list[index]))
            
            # if normal_number_list[index] == '1':
            #     abnormal_entity_caption = abnormal_entity_caption.replace('Single')
            
            #然后考虑替换位置信息
            #对于实体位置为center的，可能需要替换center或者centrally为其他位置，对于其他不为center的，直接替换即可
            random_entity_location = random.choice([normal_location for normal_location in fine_grained_location_list if normal_location != normal_location_list[index]])
            # random_entity_location = random.choice(fine_grained_location_list.remove(normal_location_list[index]))
            if normal_location_list[index] == 'center':
                abnormal_entity_caption = abnormal_entity_caption.replace("center", random_entity_location)
                abnormal_entity_caption = abnormal_entity_caption.replace("centrally", random_entity_location)
            else:
                abnormal_entity_caption = abnormal_entity_caption.replace(normal_location_list[index], random_entity_location)
            
            abnormal_entity_caption_list.append(abnormal_entity_caption)
        # abnormal_entity_level_2 = ".".join([anomaly.replace("{}", normal_entity_level_2)  for anomaly in class_state_abnormal_refined[classname]]) #e.g., bristle clusters and toothbrush handle with xxx.
        # abnormal_entity_level_2 = ".".join([anomaly.replace("{}", normal_entity_level_2)  for anomaly in class_state_abnormal_refined[classname]]) #e.g., bristle clusters and toothbrush handle with xxx.
        # print("abnormal_entity_level_2: ", abnormal_entity_level_2)
        
        # normal_relation_level_2: str = normal_class_fine_grained_level_2["logical relation"]
        normal_relation_level_2: str = normal_class_fine_grained_level_2["relation"]
        
        #将normal relation中的所有entity(可能有多个)替换为abnormal entity(也是多个)
        abnormal_relation_level_2 = []
        for single_abnormal in class_state_abnormal_refined[classname]:
        # for single_abnormal in class_state_abnormal_refined[classname]:
            abnormal_relation_level_2_tmp = normal_relation_level_2
            for i in normal_class_fine_grained_level_2["entity"]:
                abnormal_relation_level_2_tmp = abnormal_relation_level_2_tmp.replace(i, single_abnormal.replace('{}', i))
            abnormal_relation_level_2.append(abnormal_relation_level_2_tmp)
        # abnormal_relation_level_2 = [normal_relation_level_2.replace(normal_entity_level_2, anomaly.replace("{}", normal_entity_level_2)) for anomaly in class_state_abnormal_refined[classname]]
        # print("abnormal_relation_level_2: ", abnormal_relation_level_2)
        
        #Level_3: color, texture, shape(这里有一个粗略的想法：我们已知所有数据中的color, texture, shape存在很多种，对于明显不一样的，可以作为人工设计的负样本)
        normal_color_level_3 = ".".join(normal_class_fine_grained_level_3["color"])
        # normal_color_level_3 = normal_class_fine_grained_level_3["color"]
        abnormal_color_level_3 = [color for color in fine_grained_color_list if color not in normal_class_fine_grained_level_3["color"]]
        # abnormal_color_level_3 = ".".join([color for color in fine_grained_color_list if color not in normal_class_fine_grained_level_3["color"]])
        # print("abnormal_color_level_3: ", abnormal_color_level_3)
        
        normal_texture_level_3 = ".".join(normal_class_fine_grained_level_3["texture"])
        # normal_texture_level_3 = normal_class_fine_grained_level_3["texture"]
        abnormal_texture_level_3 = [texture for texture in fine_grained_texture_list if texture not in normal_class_fine_grained_level_3["texture"]]
        # abnormal_texture_level_3 = ".".join([texture for texture in fine_grained_texture_list if texture not in normal_class_fine_grained_level_3["texture"]])
        # print("abnormal_texture_level_3: ", abnormal_texture_level_3)
        
        normal_shape_level_3 = ".".join(normal_class_fine_grained_level_3["shape"])
        # normal_shape_level_3 = normal_class_fine_grained_level_3["shape"]
        abnormal_shape_level_3 = [shape for shape in fine_grained_shape_list if shape not in normal_class_fine_grained_level_3["shape"]]
        # abnormal_shape_level_3 = ".".join([shape for shape in fine_grained_shape_list if shape not in normal_class_fine_grained_level_3["shape"]])
        # print("abnormal_shape_level_3: ", abnormal_shape_level_3)
        
        abnormal_background_level_1 = [normal_background_level_1 + anomaly.replace('{}', '') for anomaly in class_state_abnormal_refined[classname]]
        
        
        # #entity_caption list构建
        # entity_caption_list = normal_class_fine_grained_level_2["entity_caption"]
        # #加入background信息
        # entity_caption_list.append(normal_class_fine_grained_level_1["background"] + " background")
        # #加入foreground信息
        # entity_caption_list.append(normal_foreground_level_1 + " foreground")
        
        # tokenized_entity_caption = torch.cat([CLIPAD.tokenize(p) for p in entity_caption_list]) #[N, 77]
        
        # with torch.no_grad():
        #     entity_caption_embedding = clip_model.token_embedding(tokenized_entity_caption).type(dtype) #[N, 77, 640]
        
        #entity_caption_embedding用于后续逐image_feature_token计算最终的local text feature
        # print("Shape of entity_caption_embedding: ", entity_caption_embedding.shape)
        # abnormal_foreground_level_1 = [normal_foreground_level_1 + anomaly for anomaly in class_state_abnormal_refined[classname]]
        
        # normal_texture_level_3 = normal_class_fine_grained_level_3["texture"]
        
        # abnormal_texture_level_3 = [normal_texture_level_3 + anomaly for anomaly in class_state_abnormal_refined[classname]]
        
        
        
        
        
        ctx_dim = clip_model.ln_final.weight.shape[0]

        # random initialization
        normal_ctx_vectors = torch.empty(n_pro, n_ctx, ctx_dim, dtype=dtype) # 3, 4, dim
        abnormal_ctx_vectors = torch.empty(n_pro_ab, n_ctx_ab, ctx_dim, dtype=dtype) # 4, 1, dim

        nn.init.normal_(normal_ctx_vectors, std=0.02)
        nn.init.normal_(abnormal_ctx_vectors, std=0.02)

        normal_prompt_prefix = " ".join(["N"] * n_ctx) # N N N N n_ctx=4
        abnormal_prompt_prefix = " ".join(["A"] * n_ctx_ab) # A n_ctx_ab=1

        self.normal_ctx = nn.Parameter(normal_ctx_vectors)  # to be optimized
        self.abnormal_ctx = nn.Parameter(abnormal_ctx_vectors)  # to be optimized

        # normal prompt
        normal_prompts = [normal_prompt_prefix + " " + normal_class_fine_grained_caption + "." for _ in range(n_pro)] # [(N N N N classname .) * 3]. . . 
        # print("normal_prompts: ", normal_prompts)
        
        #暂时先把这四个属性绑定到模型训练中
        normal_relation_prompts = [normal_prompt_prefix + " " + normal_relation_level_2 + "." for _ in range(n_pro)]
        normal_color_prompts = [normal_prompt_prefix + " " + normal_color_level_3 + "." for _ in range(n_pro)]
        normal_texture_prompts = [normal_prompt_prefix + " " + normal_texture_level_3 + "." for _ in range(n_pro)]
        normal_shape_prompts = [normal_prompt_prefix + " " + normal_shape_level_3 + "." for _ in range(n_pro)]
        
        #再加一个背景的Prompt
        normal_background_prompts = [normal_prompt_prefix + " " + normal_background_level_1 + "." for _ in range(n_pro)]
        
        #normal entities prompt
        normal_entity_prompt_list = [[normal_prompt_prefix + " " + normal_entity_caption + "." for _ in range(n_pro)] for normal_entity_caption in normal_entity_caption_list]
        
        # normal_prompts = [normal_prompt_prefix + " " + classname + "." for _ in range(n_pro)] # [(N N N N classname .) * 3]. . . 

        # abnormal prompt
        self.n_ab_handle = len(class_state_abnormal_refined[classname])
        self.n_ab_relation_handle = len(abnormal_relation_level_2)
        self.n_ab_color_handle = len(abnormal_color_level_3)
        self.n_ab_texture_handle = len(abnormal_texture_level_3)
        self.n_ab_shape_handle = len(abnormal_shape_level_3)
        self.n_ab_background_handle = len(abnormal_background_level_1)
        # self.n_ab_handle = len(state_anomaly1)
        # abnormal_prompts_handle = [normal_prompt_prefix + " " + state.format(classname) + "." for state in state_anomaly1 for _ in range(n_pro)]
        # abnormal_prompts_learned = [normal_prompt_prefix + " " + abnormal_prompt_prefix + " " + classname + "." for _ in range(n_pro_ab) for _ in range(n_pro)]
        
        #这里要将修改后的anomaly_caption嵌入(对应Caption)
        abnormal_prompts_handle = [normal_prompt_prefix + " " + normal_class_fine_grained_caption.replace(normal_foreground_level_1, abnormal_foreground) + "." for abnormal_foreground in abnormal_foreground_level_1 for _ in range(n_pro)]
        abnormal_prompts_learned = [normal_prompt_prefix + " " + abnormal_prompt_prefix + " " + normal_class_fine_grained_caption + "." for _ in range(n_pro_ab) for _ in range(n_pro)]
        
        abnormal_entity_prompts_handle_list = [[normal_prompt_prefix + " " + abnormal_entity_caption + "." for _ in range(n_pro)] for abnormal_entity_caption in abnormal_entity_caption_list]

        print("abnormal_prompts_handle: ", abnormal_prompts_handle)
        print("abnormal_prompts_learned: ", abnormal_prompts_learned)
        
        #background
        abnormal_background_prompts_handle = [normal_prompt_prefix + " " + abnormal_background + "." for abnormal_background in abnormal_background_level_1 for _ in range(n_pro)]
        abnormal_background_prompts_learned = [normal_prompt_prefix + " " + abnormal_prompt_prefix + " " + normal_background_level_1 + "." for _ in range(n_pro_ab) for _ in range(n_pro)]
        
        abnormal_relation_prompts_handle = [normal_prompt_prefix + " " + single_abnormal_relation + "." for single_abnormal_relation in abnormal_relation_level_2 for _ in range(n_pro)]
        abnormal_color_prompts_handle = [normal_prompt_prefix + " " + single_abnormal_color + "." for single_abnormal_color in abnormal_color_level_3  for _ in range(n_pro)]
        abnormal_texture_prompts_handle = [normal_prompt_prefix + " " + single_abnormal_texture + "." for single_abnormal_texture in abnormal_texture_level_3 for _ in range(n_pro)]
        abnormal_shape_prompts_handle = [normal_prompt_prefix + " " + single_abnormal_shape + "." for single_abnormal_shape in abnormal_shape_level_3  for _ in range(n_pro)]
        
        abnormal_relation_prompts_learned = [normal_prompt_prefix + " " + abnormal_prompt_prefix + " " + normal_relation_level_2 + "." for _ in range(n_pro_ab) for _ in range(n_pro)]
        abnormal_color_prompts_learned = [normal_prompt_prefix + " " + abnormal_prompt_prefix + " " + normal_color_level_3 + "." for _ in range(n_pro_ab) for _ in range(n_pro)]
        abnormal_texture_prompts_learned = [normal_prompt_prefix + " " + abnormal_prompt_prefix + " " + normal_texture_level_3 + "." for _ in range(n_pro_ab) for _ in range(n_pro)]
        abnormal_shape_prompts_learned = [normal_prompt_prefix + " " + abnormal_prompt_prefix + " " + normal_shape_level_3 + "." for _ in range(n_pro_ab) for _ in range(n_pro)]
        # abnormal_prompts = abnormal_prompts_learned + abnormal_prompts_handle
        
        abnormal_entity_prompts_learned_list = [[normal_prompt_prefix + " " + abnormal_prompt_prefix + " " + normal_entity_caption + "." for _ in range(n_pro_ab) for _ in range(n_pro)] for normal_entity_caption in normal_entity_caption_list]

        tokenized_normal_prompts = CLIPAD.tokenize(normal_prompts)
        tokenized_abnormal_prompts_handle = torch.cat([CLIPAD.tokenize(p) for p in abnormal_prompts_handle])
        tokenized_abnormal_prompts_learned = torch.cat([CLIPAD.tokenize(p) for p in abnormal_prompts_learned])
        
        print("shape of tokenized_normal_prompts:", tokenized_normal_prompts.shape)
        print("shape of tokenized_abnormal_prompts_handle:", tokenized_abnormal_prompts_handle.shape)
        print("shape of tokenized_abnormal_prompts_learned:", tokenized_abnormal_prompts_learned.shape)
        
        #entity:
        tokenized_normal_entity_prompts_list = [CLIPAD.tokenize(normal_entity_prompt) for normal_entity_prompt in normal_entity_prompt_list]
        tokenized_abnormal_entity_prompts_handle_list = [torch.cat([CLIPAD.tokenize(p) for p in abnormal_entity_prompt_handle]) for abnormal_entity_prompt_handle in abnormal_entity_prompts_handle_list]
        tokenized_abnormal_entity_prompts_learned_list = [torch.cat([CLIPAD.tokenize(p) for p in abnromal_entity_prompt_learned]) for abnromal_entity_prompt_learned in abnormal_entity_prompts_learned_list]
        
        print("Num Entity:", len(tokenized_normal_entity_prompts_list))
        print("shape of single entity tokenized_normal_entity_prompt:", tokenized_normal_entity_prompts_list[0].shape)
        print("shape of single entity tokenized_abnormal_entity_prompt_handle:", tokenized_abnormal_entity_prompts_handle_list[0].shape)
        print("shape of single entity tokenized_abnormal_entity_prompt_learned:", tokenized_abnormal_entity_prompts_learned_list[0].shape)
        
        
        
        #这些就是细粒度属性级别的normal, abnormal(handle + learned)
        tokenized_normal_relation_prompts = CLIPAD.tokenize(normal_relation_prompts)
        tokenized_abnormal_relation_prompts_handle = torch.cat([CLIPAD.tokenize(p) for p in abnormal_relation_prompts_handle])
        tokenized_abnormal_relation_prompts_learned = torch.cat([CLIPAD.tokenize(p) for p in abnormal_relation_prompts_learned])
        
        print("shape of tokenized_normal_relation_prompts:", tokenized_normal_relation_prompts.shape)
        print("shape of tokenized_abnormal_relation_prompts_handle:", tokenized_abnormal_relation_prompts_handle.shape)
        print("shape of tokenized_abnormal_relation_prompts_learned:", tokenized_abnormal_relation_prompts_learned.shape)
        
        tokenized_normal_color_prompts = CLIPAD.tokenize(normal_color_prompts)
        tokenized_abnormal_color_prompts_handle = torch.cat([CLIPAD.tokenize(p) for p in abnormal_color_prompts_handle])
        tokenized_abnormal_color_prompts_learned = torch.cat([CLIPAD.tokenize(p) for p in abnormal_color_prompts_learned])
        
        print("shape of tokenized_normal_color_prompts:", tokenized_normal_color_prompts.shape)
        print("shape of tokenized_abnormal_color_prompts_handle:", tokenized_abnormal_color_prompts_handle.shape)
        print("shape of tokenized_abnormal_color_prompts_learned:", tokenized_abnormal_color_prompts_learned.shape)
        
        
        tokenized_normal_texture_prompts = CLIPAD.tokenize(normal_texture_prompts)
        tokenized_abnormal_texture_prompts_handle = torch.cat([CLIPAD.tokenize(p) for p in abnormal_texture_prompts_handle])
        tokenized_abnormal_texture_prompts_learned = torch.cat([CLIPAD.tokenize(p) for p in abnormal_texture_prompts_learned])
        
        print("shape of tokenized_normal_texture_prompts:", tokenized_normal_texture_prompts.shape)
        print("shape of tokenized_abnormal_texture_prompts_handle:", tokenized_abnormal_texture_prompts_handle.shape)
        print("shape of tokenized_abnormal_texture_prompts_learned:", tokenized_abnormal_texture_prompts_learned.shape)
        
        
        tokenized_normal_shape_prompts = CLIPAD.tokenize(normal_shape_prompts)
        tokenized_abnormal_shape_prompts_handle = torch.cat([CLIPAD.tokenize(p) for p in abnormal_shape_prompts_handle])
        tokenized_abnormal_shape_prompts_learned = torch.cat([CLIPAD.tokenize(p) for p in abnormal_shape_prompts_learned])
        
        print("shape of tokenized_normal_shape_prompts:", tokenized_normal_shape_prompts.shape)
        print("shape of tokenized_abnormal_shape_prompts_handle:", tokenized_abnormal_shape_prompts_handle.shape)
        print("shape of tokenized_abnormal_shape_prompts_learned:", tokenized_abnormal_shape_prompts_learned.shape)
        
        
        #加一个background的tokenized
        tokenized_normal_background_prompts = CLIPAD.tokenize(normal_background_prompts)
        tokenized_abnormal_background_prompts_handle = torch.cat([CLIPAD.tokenize(p) for p in abnormal_background_prompts_handle])
        tokenized_abnormal_background_prompts_learned = torch.cat([CLIPAD.tokenize(p) for p in abnormal_background_prompts_learned])
        

        with torch.no_grad():
            normal_embedding = clip_model.token_embedding(tokenized_normal_prompts).type(dtype)
            abnormal_embedding_handle = clip_model.token_embedding(tokenized_abnormal_prompts_handle).type(dtype)
            abnormal_embedding_learned = clip_model.token_embedding(tokenized_abnormal_prompts_learned).type(dtype)
            
            normal_entity_embedding_list = [clip_model.token_embedding(tokenized_normal_entity_prompts).type(dtype) for tokenized_normal_entity_prompts in tokenized_normal_entity_prompts_list]
            abnormal_entity_embedding_handle_list = [clip_model.token_embedding(tokenized_abnormal_entity_prompts_handle).type(dtype) for tokenized_abnormal_entity_prompts_handle in tokenized_abnormal_entity_prompts_handle_list]
            abnormal_entity_embedding_learned_list = [clip_model.token_embedding(tokenized_abnormal_entity_prompts_learned).type(dtype) for tokenized_abnormal_entity_prompts_learned in tokenized_abnormal_entity_prompts_learned_list]
            
            normal_relation_embedding = clip_model.token_embedding(tokenized_normal_relation_prompts).type(dtype)
            abnormal_relation_embedding_handle = clip_model.token_embedding(tokenized_abnormal_relation_prompts_handle).type(dtype)
            abnormal_relation_embedding_learned = clip_model.token_embedding(tokenized_abnormal_relation_prompts_learned).type(dtype)
            
            normal_color_embedding = clip_model.token_embedding(tokenized_normal_color_prompts).type(dtype)
            abnormal_color_embedding_handle = clip_model.token_embedding(tokenized_abnormal_color_prompts_handle).type(dtype)
            abnormal_color_embedding_learned = clip_model.token_embedding(tokenized_abnormal_color_prompts_learned).type(dtype)
            
            normal_texture_embedding = clip_model.token_embedding(tokenized_normal_texture_prompts).type(dtype)
            abnormal_texture_embedding_handle = clip_model.token_embedding(tokenized_abnormal_texture_prompts_handle).type(dtype)
            abnormal_texture_embedding_learned = clip_model.token_embedding(tokenized_abnormal_texture_prompts_learned).type(dtype)
            
            normal_shape_embedding = clip_model.token_embedding(tokenized_normal_shape_prompts).type(dtype)
            abnormal_shape_embedding_handle = clip_model.token_embedding(tokenized_abnormal_shape_prompts_handle).type(dtype)
            abnormal_shape_embedding_learned = clip_model.token_embedding(tokenized_abnormal_shape_prompts_learned).type(dtype)
            
            normal_background_embedding = clip_model.token_embedding(tokenized_normal_background_prompts).type(dtype)
            abnormal_background_embedding_handle = clip_model.token_embedding(tokenized_abnormal_background_prompts_handle).type(dtype)
            abnormal_background_embedding_learned = clip_model.token_embedding(tokenized_abnormal_background_prompts_learned).type(dtype)
            
        
        print("shape of normal_embedding:", normal_embedding.shape)
        print("shape of abnormal_embedding_handle:", abnormal_embedding_handle.shape)
        print("shape of abnormal_embedding_learned", abnormal_embedding_learned.shape)
        
        print("shape of single normal_entity_embedding:", normal_entity_embedding_list[0].shape)
        print("shape of single abnormal_entity_embedding_handle:", abnormal_entity_embedding_handle_list[0].shape)
        print("shape of single abnormal_entity_embedding_learned:", abnormal_entity_embedding_learned_list[0].shape)
        
        print("shape of relation embedding", normal_relation_embedding.shape, abnormal_relation_embedding_handle.shape, abnormal_relation_embedding_learned.shape)
        print("shape of color embedding", normal_color_embedding.shape, abnormal_color_embedding_handle.shape, abnormal_color_embedding_learned.shape)
        print("shape of texture embedding", normal_texture_embedding.shape, abnormal_texture_embedding_handle.shape, abnormal_texture_embedding_learned.shape)
        print("shape of shape embedding", normal_shape_embedding.shape, abnormal_shape_embedding_handle.shape, abnormal_shape_embedding_learned.shape)
        # These token vectors will be saved when in save_model(),
        # but they should be ignored in load_model() as we want to use
        # those computed using the current class names
        self.register_buffer("normal_token_prefix", normal_embedding[:, :1, :])  # SOS
        self.register_buffer("normal_token_suffix", normal_embedding[:, 1 + n_ctx:, :])  # CLS, EOS

        self.register_buffer("abnormal_token_prefix_handle", abnormal_embedding_handle[:, :1, :])  # SOS
        self.register_buffer("abnormal_token_suffix_handle", abnormal_embedding_handle[:, 1 + n_ctx:, :])  # CLS, EOS

        self.register_buffer("abnormal_token_prefix_learned", abnormal_embedding_learned[:, :1, :])  # SOS
        self.register_buffer("abnormal_token_suffix_learned", abnormal_embedding_learned[:, 1 + n_ctx + n_ctx_ab:, :])  # CLS, EOS

        #entity
        self.register_buffer("normal_token_entity_prefix_list", torch.cat([normal_entity_embedding[:, :1, :].unsqueeze(0) for normal_entity_embedding in normal_entity_embedding_list]))
        self.register_buffer("normal_token_entity_suffix_list", torch.cat([normal_entity_embedding[:, 1 + n_ctx:, :].unsqueeze(0) for normal_entity_embedding in normal_entity_embedding_list]))

        self.register_buffer("abnormal_token_entity_prefix_handle_list", torch.cat([abnormal_entity_embedding_handle[:, :1, :].unsqueeze(0) for abnormal_entity_embedding_handle in abnormal_entity_embedding_handle_list]))
        self.register_buffer("abnormal_token_entity_suffix_handle_list", torch.cat([abnormal_entity_embedding_handle[:, 1 + n_ctx:, :].unsqueeze(0) for abnormal_entity_embedding_handle in abnormal_entity_embedding_handle_list]))

        self.register_buffer("abnormal_token_entity_prefix_learned_list", torch.cat([abnormal_entity_embedding_learned[:, :1, :].unsqueeze(0) for abnormal_entity_embedding_learned in abnormal_entity_embedding_learned_list]))
        self.register_buffer("abnormal_token_entity_suffix_learned_list", torch.cat([abnormal_entity_embedding_learned[:, 1 + n_ctx + n_ctx_ab:, :].unsqueeze(0) for abnormal_entity_embedding_learned in abnormal_entity_embedding_learned_list]))

        print("shape of normal_token_entity_prefix_list:", self.normal_token_entity_prefix_list.shape)
        print("shape of normal_token_entity_suffix_list:", self.normal_token_entity_suffix_list.shape)
        print("shape of abnormal_token_entity_prefix_handle:", self.abnormal_token_entity_prefix_handle_list.shape)
        print("shape of abnormal_token_entity_suffix_handle:", self.abnormal_token_entity_suffix_handle_list.shape)
        print("shape of abnormal_token_entity_prefix_learned:", self.abnormal_token_entity_prefix_learned_list.shape)
        print("shape of abnormal_token_entity_suffix_learned:", self.abnormal_token_entity_suffix_learned_list.shape)

        #relation:
        self.register_buffer("normal_token_relation_prefix", normal_relation_embedding[:, :1, :])  # SOS
        self.register_buffer("normal_token_relation_suffix", normal_relation_embedding[:, 1 + n_ctx:, :])  # CLS, EOS
        
        self.register_buffer("abnormal_token_relation_prefix_handle", abnormal_relation_embedding_handle[:, :1, :])  # SOS
        self.register_buffer("abnormal_token_relation_suffix_handle", abnormal_relation_embedding_handle[:, 1 + n_ctx:, :])  # CLS, EOS
        
        self.register_buffer("abnormal_token_relation_prefix_learned", abnormal_relation_embedding_learned[:, :1, :])  # SOS
        self.register_buffer("abnormal_token_relation_suffix_learned", abnormal_relation_embedding_learned[:, 1 + n_ctx + n_ctx_ab:, :])
        
        #color:
        self.register_buffer("normal_token_color_prefix", normal_color_embedding[:, :1, :])  # SOS
        self.register_buffer("normal_token_color_suffix", normal_color_embedding[:, 1 + n_ctx:, :])
        
        self.register_buffer("abnormal_token_color_prefix_handle", abnormal_color_embedding_handle[:, :1, :])  # SOS
        self.register_buffer("abnormal_token_color_suffix_handle", abnormal_color_embedding_handle[:, 1 + n_ctx:, :])
        
        self.register_buffer("abnormal_token_color_prefix_learned", abnormal_color_embedding_learned[:, :1, :])  # SOS
        self.register_buffer("abnormal_token_color_suffix_learned", abnormal_color_embedding_learned[:, 1 + n_ctx + n_ctx_ab:, :])
        
        #texture:
        self.register_buffer("normal_token_texture_prefix", normal_texture_embedding[:, :1, :])
        self.register_buffer("normal_token_texture_suffix", normal_texture_embedding[:, 1 + n_ctx:, :])
        
        self.register_buffer("abnormal_token_texture_prefix_handle", abnormal_texture_embedding_handle[:, :1, :])
        self.register_buffer("abnormal_token_texture_suffix_handle", abnormal_texture_embedding_handle[:, 1 + n_ctx:, :])
        
        self.register_buffer("abnormal_token_texture_prefix_learned", abnormal_texture_embedding_learned[:, :1, :])
        self.register_buffer("abnormal_token_texture_suffix_learned", abnormal_texture_embedding_learned[:, 1 + n_ctx + n_ctx_ab:, :])
        
        #shape:
        self.register_buffer("normal_token_shape_prefix", normal_shape_embedding[:, :1, :])
        self.register_buffer("normal_token_shape_suffix", normal_shape_embedding[:, 1 + n_ctx:, :])
        
        self.register_buffer("abnormal_token_shape_prefix_handle", abnormal_shape_embedding_handle[:, :1, :])
        self.register_buffer("abnormal_token_shape_suffix_handle", abnormal_shape_embedding_handle[:, 1 + n_ctx:, :])
        
        self.register_buffer("abnormal_token_shape_prefix_learned", abnormal_shape_embedding_learned[:, :1, :])
        self.register_buffer("abnormal_token_shape_suffix_learned", abnormal_shape_embedding_learned[:, 1 + n_ctx + n_ctx_ab:, :])
        
        #background:
        self.register_buffer("normal_token_background_prefix", normal_background_embedding[:, :1, :])
        self.register_buffer("normal_token_background_suffix", normal_background_embedding[:, 1 + n_ctx:, :])
        
        self.register_buffer("abnormal_token_background_prefix_handle", abnormal_background_embedding_handle[:, :1, :])
        self.register_buffer("abnormal_token_background_suffix_handle", abnormal_background_embedding_handle[:, 1 + n_ctx:, :])
        
        self.register_buffer("abnormal_token_background_prefix_learned", abnormal_background_embedding_learned[:, :1, :])
        self.register_buffer("abnormal_token_background_suffix_learned", abnormal_background_embedding_learned[:, 1 + n_ctx + n_ctx_ab:, :])
        
        
        #entity caption
        # self.register_buffer("entity_caption_embedding", entity_caption_embedding)
        
        
        self.n_pro = n_pro
        self.n_ctx = n_ctx
        self.n_pro_ab = n_pro_ab
        self.n_ctx_ab = n_ctx_ab
        self.tokenized_normal_prompts = tokenized_normal_prompts  # torch.Tensor
        self.tokenized_abnormal_prompts_handle = tokenized_abnormal_prompts_handle  # torch.Tensor
        self.tokenized_abnormal_prompts_learned = tokenized_abnormal_prompts_learned  # torch.Tensor
        
        self.tokenized_normal_background_prompts = tokenized_normal_background_prompts
        self.tokenized_abnormal_background_prompts_handle = tokenized_abnormal_background_prompts_handle
        self.tokenized_abnormal_background_prompts_learned = tokenized_abnormal_background_prompts_learned
        
        
        # self.tokenized_abnormal_prompts = torch.cat([tokenized_abnormal_prompts_handle, tokenized_abnormal_prompts_learned], dim=0)
        # self.tokenized_abnormal_prompts = tokenized_abnormal_prompts_handle
        # self.name_lens = name_lens
        self.tokenized_normal_entity_prompts_list = tokenized_normal_entity_prompts_list
        self.tokenized_abnormal_entity_prompts_handle_list = tokenized_abnormal_entity_prompts_handle_list
        self.tokenized_abnormal_entity_prompts_learned_list = tokenized_abnormal_entity_prompts_learned_list
        
        # self.tokenized_entity_caption = tokenized_entity_caption
        
        #各个属性的加权系数，值在0-1之间，训练时可以更新
        self.normal_relation_w = nn.Parameter(torch.randn(1, dtype=dtype))
        self.normal_color_w = nn.Parameter(torch.randn(1, dtype=dtype))
        self.normal_texture_w = nn.Parameter(torch.randn(1, dtype=dtype))
        self.normal_shape_w = nn.Parameter(torch.randn(1, dtype=dtype))
        
        self.abnormal_relation_w = nn.Parameter(torch.randn(1, dtype=dtype))
        self.abnormal_color_w = nn.Parameter(torch.randn(1, dtype=dtype))
        self.abnormal_texture_w = nn.Parameter(torch.randn(1, dtype=dtype))
        self.abnormal_shape_w = nn.Parameter(torch.randn(1, dtype=dtype))
        
        self.weight_sigmoid = nn.Sigmoid()

    def forward(self):

        # learned normal prompt
        normal_ctx = self.normal_ctx

        normal_prefix = self.normal_token_prefix
        normal_suffix = self.normal_token_suffix

        normal_prompts = torch.cat(
            [
                normal_prefix,  # (n_pro, 1, dim)
                normal_ctx,     # (n_pro, n_ctx, dim)
                normal_suffix,  # (n_pro, *, dim)
            ],
            dim=1,
        )
        
        #background
        normal_background_prefix = self.normal_token_background_prefix
        normal_background_suffix = self.normal_token_background_suffix
        
        normal_background_prompts = torch.cat(
            [
                normal_background_prefix,  # (n_pro, 1, dim)
                normal_ctx,     # (n_pro, n_ctx, dim)
                normal_background_suffix,  # (n_pro, *, dim)
            ],
            dim=1,
        )
        
        
        
        
        #entity
        #首先沿着第0维度将entity相关的normal, abnormal_handle, abnormal_learned均还原为list
        num_entity = len(self.tokenized_normal_entity_prompts_list)
        # 使用 torch.chunk 将张量沿着第0维度拆分为 N 个张量
        normal_entity_prefix_list = torch.chunk(self.normal_token_entity_prefix_list, chunks=num_entity, dim=0)
        normal_entity_suffix_list = torch.chunk(self.normal_token_entity_suffix_list, chunks=num_entity, dim=0)

        abnormal_entity_prefix_handle_list = torch.chunk(self.abnormal_token_entity_prefix_handle_list, chunks=num_entity, dim=0)
        abnormal_entity_suffix_handle_list = torch.chunk(self.abnormal_token_entity_suffix_handle_list, chunks=num_entity, dim=0)

        abnormal_entity_prefix_learned_list = torch.chunk(self.abnormal_token_entity_prefix_learned_list, chunks=num_entity, dim=0)
        abnormal_entity_suffix_learned_list = torch.chunk(self.abnormal_token_entity_suffix_learned_list, chunks=num_entity, dim=0)
        # print("shape of normal_entity_prefix", normal_entity_prefix_list[0].shape)
        # print("shape of normal_ctx", normal_ctx.shape)
        # print("shape of normal_entity_suffix", normal_entity_suffix_list[0].shape)
        
        normal_entity_prompts_list = [
            torch.cat([normal_entity_prefix.squeeze(0), normal_ctx, normal_entity_suffix.squeeze(0)], dim=1) for normal_entity_prefix, normal_entity_suffix in zip(normal_entity_prefix_list, normal_entity_suffix_list)
        ]
        
        
        #relation
        normal_relation_prefix = self.normal_token_relation_prefix
        normal_relation_suffix = self.normal_token_relation_suffix
        
        normal_relation_prompts = torch.cat(
            [
                normal_relation_prefix,  # (n_pro, 1, dim)
                normal_ctx,     # (n_pro, n_ctx, dim)
                normal_relation_suffix,  # (n_pro, *, dim)
            ],
            dim=1,
        )
        
        #color
        normal_color_prefix = self.normal_token_color_prefix
        normal_color_suffix = self.normal_token_color_suffix
        
        normal_color_prompts = torch.cat(
            [
                normal_color_prefix,  # (n_pro, 1, dim)
                normal_ctx,     # (n_pro, n_ctx, dim)
                normal_color_suffix,  # (n_pro, *, dim)
            ],
            dim=1,
        )
        
        #texture
        normal_texture_prefix = self.normal_token_texture_prefix
        normal_texture_suffix = self.normal_token_texture_suffix
        
        normal_texture_prompts = torch.cat(
            [
                normal_texture_prefix,  # (n_pro, 1, dim)
                normal_ctx,     # (n_pro, n_ctx, dim)
                normal_texture_suffix,  # (n_pro, *, dim)
            ],
            dim=1,
        )
        
        #shape
        normal_shape_prefix = self.normal_token_shape_prefix
        normal_shape_suffix = self.normal_token_shape_suffix
        
        normal_shape_prompts = torch.cat(
            [
                normal_shape_prefix,  # (n_pro, 1, dim)
                normal_ctx,     # (n_pro, n_ctx, dim)
                normal_shape_suffix,  # (n_pro, *, dim)
            ],
            dim=1,
        )
        
        #用sigmoid将权重归一化
        weight_sigmoid = self.weight_sigmoid
        normal_relation_w = weight_sigmoid(self.normal_relation_w)
        normal_color_w = weight_sigmoid(self.normal_color_w)
        normal_texture_w = weight_sigmoid(self.normal_texture_w)
        normal_shape_w = weight_sigmoid(self.normal_shape_w)
        
        # print("value of normal_weights:", normal_relation_w, normal_color_w, normal_texture_w, normal_shape_w)
        
        #将normal的多个属性特征加权相加到normal_prompts中
        normal_prompts = normal_prompts + normal_relation_w * normal_relation_prompts + normal_color_w * normal_color_prompts + normal_texture_w * normal_texture_prompts + normal_shape_w * normal_shape_prompts

        # print("shape of normal_prompts:", normal_prompts.shape)
        

        # handle abnormal prompt
        n_ab_handle = self.n_ab_handle
        
        n_ab_relation_handle = self.n_ab_relation_handle
        n_ab_color_handle = self.n_ab_color_handle
        n_ab_texture_handle = self.n_ab_texture_handle
        n_ab_shape_handle = self.n_ab_shape_handle
        n_ab_background_handle = self.n_ab_background_handle

        n_pro, n_ctx, dim = normal_ctx.shape # 3, 4, dim
        normal_ctx1 = normal_ctx.unsqueeze(0).expand(n_ab_handle, -1, -1, -1).reshape(-1, n_ctx, dim) # n_ab_handle * n_pro, n_ctx, dim

        abnormal_prefix_handle = self.abnormal_token_prefix_handle
        abnormal_suffix_handle = self.abnormal_token_suffix_handle

        abnormal_prompts_handle = torch.cat(
            [
                abnormal_prefix_handle,     # (n_pro * n_ab_handle, 1, dim)
                normal_ctx1,                # (n_pro * n_ab_handle, n_ctx, dim)
                abnormal_suffix_handle,     # (n_pro * n_ab_handle, *, dim)
            ],
            dim=1,
        )
        # print("shape of abnormal_prompts_handle:", abnormal_prompts_handle.shape)
        
        #background
        normal_background_ctx1 = normal_ctx.unsqueeze(0).expand(n_ab_background_handle, -1, -1, -1).reshape(-1, n_ctx, dim)
        
        abnormal_background_prefix_handle = self.abnormal_token_background_prefix_handle
        abnormal_background_suffix_handle = self.abnormal_token_background_suffix_handle
        
        abnormal_background_prompts_handle = torch.cat(
            [
                abnormal_background_prefix_handle,     # (n_pro * n_ab_background_handle, 1, dim)
                normal_background_ctx1,                # (n_pro * n_ab_background_handle, n_ctx, dim)
                abnormal_background_suffix_handle,     # (n_pro * n_ab_background_handle, *, dim)
            ],
            dim=1,
        )
        
        
        
        
        #entity
        normal_entity_ctx1 = normal_ctx.unsqueeze(0).expand(1, -1, -1, -1).reshape(-1, n_ctx, dim) #1 * n_pro, n_ctx, dim
        
        abnormal_entity_prompts_handle_list = [torch.cat(
            [
                abnormal_entity_prefix_handle.squeeze(0),     # (n_pro * 1, 1, dim)
                normal_entity_ctx1,                # (n_pro * 1, n_ctx, dim)
                abnormal_entity_suffix_handle.squeeze(0),     # (n_pro * 1, *, dim)
            ],
            dim=1,
        ) for abnormal_entity_prefix_handle, abnormal_entity_suffix_handle in zip(abnormal_entity_prefix_handle_list, abnormal_entity_suffix_handle_list)]
        
        
        #relation
        normal_relation_ctx1 = normal_ctx.unsqueeze(0).expand(n_ab_relation_handle, -1, -1, -1).reshape(-1, n_ctx, dim) #n_ab_relation_handle * n_pro, n_ctx, dim
        
        abnormal_relation_prefix_handle = self.abnormal_token_relation_prefix_handle
        abnormal_relation_suffix_handle = self.abnormal_token_relation_suffix_handle
        
        abnormal_relation_prompts_handle = torch.cat(
            [
                abnormal_relation_prefix_handle,     # (n_pro * n_ab_relation_handle, 1, dim)
                normal_relation_ctx1,                # (n_pro * n_ab_relation_handle, n_ctx, dim)
                abnormal_relation_suffix_handle,     # (n_pro * n_ab_relation_handle, *, dim)
            ],
            dim=1,
        )
        
        #从abnormal_relation_prompts_handle的第0维度(n_pro * n_ab_relation_handle)中选出激活值最大的topk个,k为n_pro * n_ab_handle
        # print("shape of abnormal_relation_prompts_handle(Before Top-K):", abnormal_relation_prompts_handle.shape)
        mean_abnormal_relation_prompts_handle = abnormal_relation_prompts_handle.mean(dim=(1,2), keepdim=True)
        _, indices = torch.topk(mean_abnormal_relation_prompts_handle.float(), n_pro * n_ab_handle, dim=0)
        # print("shape of indices:", indices.shape)
        abnormal_relation_prompts_handle = abnormal_relation_prompts_handle[indices.squeeze()]
        # print("shape of abnormal_relation_prompts_handle(After Top-K):", abnormal_relation_prompts_handle.shape)
        #color
        normal_color_ctx1 = normal_ctx.unsqueeze(0).expand(n_ab_color_handle, -1, -1, -1).reshape(-1, n_ctx, dim) #n_ab_color_handle * n_pro, n_ctx, dim
        
        abnormal_color_prefix_handle = self.abnormal_token_color_prefix_handle
        abnormal_color_suffix_handle = self.abnormal_token_color_suffix_handle
        
        abnormal_color_prompts_handle = torch.cat(
            [
                abnormal_color_prefix_handle,     # (n_pro * n_ab_color_handle, 1, dim)
                normal_color_ctx1,                # (n_pro * n_ab_color_handle, n_ctx, dim)
                abnormal_color_suffix_handle,     # (n_pro * n_ab_color_handle, *, dim)
            ],
            dim=1,
        )
        
        # print("shape of abnormal_color_prompts_handle(Before Top-K):", abnormal_color_prompts_handle.shape)
        mean_abnormal_color_prompts_handle = abnormal_color_prompts_handle.mean(dim=(1,2), keepdim=True)
        _, indices = torch.topk(mean_abnormal_color_prompts_handle.float(), n_pro * n_ab_handle, dim=0)

        abnormal_color_prompts_handle = abnormal_color_prompts_handle[indices.squeeze()]
        # print("shape of abnormal_color_prompts_handle(After Top-K):", abnormal_color_prompts_handle.shape)
        #texture
        normal_texture_ctx1 = normal_ctx.unsqueeze(0).expand(n_ab_texture_handle, -1, -1, -1).reshape(-1, n_ctx, dim) #n_ab_texture_handle * n_pro, n_ctx, dim
        
        abnormal_texture_prefix_handle = self.abnormal_token_texture_prefix_handle
        abnormal_texture_suffix_handle = self.abnormal_token_texture_suffix_handle
        
        abnormal_texture_prompts_handle = torch.cat(
            [
                abnormal_texture_prefix_handle,     # (n_pro * n_ab_texture_handle, 1, dim)
                normal_texture_ctx1,                # (n_pro * n_ab_texture_handle, n_ctx, dim)
                abnormal_texture_suffix_handle,     # (n_pro * n_ab_texture_handle, *, dim)
            ],
            dim=1,
        )
        # print("shape of abnormal_texture_prompts_handle(Before Top-K):", abnormal_texture_prompts_handle.shape)
        mean_abnormal_texture_prompts_handle = abnormal_texture_prompts_handle.mean(dim=(1,2), keepdim=True)
        _, indices = torch.topk(mean_abnormal_texture_prompts_handle.float(), n_pro * n_ab_handle, dim=0)
        # print("shape of indices:", indices.shape)

        abnormal_texture_prompts_handle = abnormal_texture_prompts_handle[indices.squeeze()]
        # print("shape of abnormal_texture_prompts_handle(After Top-K):", abnormal_texture_prompts_handle.shape)
        #shape
        normal_shape_ctx1 = normal_ctx.unsqueeze(0).expand(n_ab_shape_handle, -1, -1, -1).reshape(-1, n_ctx, dim) #n_ab_shape_handle * n_pro, n_ctx, dim
        
        abnormal_shape_prefix_handle = self.abnormal_token_shape_prefix_handle
        abnormal_shape_suffix_handle = self.abnormal_token_shape_suffix_handle
        
        abnormal_shape_prompts_handle = torch.cat(
            [
                abnormal_shape_prefix_handle,     # (n_pro * n_ab_shape_handle, 1, dim)
                normal_shape_ctx1,                # (n_pro * n_ab_shape_handle, n_ctx, dim)
                abnormal_shape_suffix_handle,     # (n_pro * n_ab_shape_handle, *, dim)
            ],
            dim=1,
        )
        
        # print("shape of abnormal_shape_prompts_handle(Before Top-K):", abnormal_shape_prompts_handle.shape)
        mean_abnormal_shape_prompts_handle = abnormal_shape_prompts_handle.mean(dim=(1,2), keepdim=True)
        _, indices = torch.topk(mean_abnormal_shape_prompts_handle.float(), n_pro * n_ab_handle, dim=0)

        abnormal_shape_prompts_handle = abnormal_shape_prompts_handle[indices.squeeze()]
        # print("shape of abnormal_shape_prompts_handle(After Top-K):", abnormal_shape_prompts_handle.shape)
        #将abnormal_handle的多个属性特征加权相加到abnormal_prompts_handle中
        #先将异常权重归一化
        abnormal_relation_w = weight_sigmoid(self.abnormal_relation_w)
        abnormal_color_w = weight_sigmoid(self.abnormal_color_w)
        abnormal_texture_w = weight_sigmoid(self.abnormal_texture_w)
        abnormal_shape_w = weight_sigmoid(self.abnormal_shape_w)
        
        abnormal_prompts_handle = abnormal_prompts_handle + abnormal_relation_w * abnormal_relation_prompts_handle + abnormal_color_w * abnormal_color_prompts_handle + abnormal_texture_w * abnormal_texture_prompts_handle + abnormal_shape_w * abnormal_shape_prompts_handle
        
        # learned abnormal prompt
        abnormal_prefix_learned = self.abnormal_token_prefix_learned
        abnormal_suffix_learned = self.abnormal_token_suffix_learned
        abnormal_ctx = self.abnormal_ctx
        n_pro_ad, n_ctx_ad, dim_ad = abnormal_ctx.shape
        normal_ctx2 = normal_ctx.unsqueeze(0).expand(self.n_pro_ab, -1, -1, -1).reshape(-1, n_ctx, dim)
        abnormal_ctx = abnormal_ctx.unsqueeze(0).expand(self.n_pro, -1, -1, -1).reshape(-1, n_ctx_ad, dim_ad)

        abnormal_prompts_learned = torch.cat(
            [
                abnormal_prefix_learned,        # (n_pro * n_pro_ab, 1, dim)
                normal_ctx2,                    # (n_pro * n_pro_ab, n_ctx, dim)
                abnormal_ctx,                   # (n_pro * n_pro_ab, n_ctx_ab, dim)
                abnormal_suffix_learned,        # (n_pro * n_pro_ab, *, dim)
            ],
            dim=1,
        )
        
        
        #background
        normal_background_ctx2 = normal_ctx.unsqueeze(0).expand(self.n_pro_ab, -1, -1, -1).reshape(-1, n_ctx, dim)
        
        abnormal_background_prefix_learned = self.abnormal_token_background_prefix_learned
        abnormal_background_suffix_learned = self.abnormal_token_background_suffix_learned
        
        abnormal_background_prompts_learned = torch.cat(
            [
                abnormal_background_prefix_learned,        # (n_pro * n_pro_ab, 1, dim)
                normal_ctx2,                             # (n_pro * n_pro_ab, n_ctx, dim)
                abnormal_ctx,                            # (n_pro * n_pro_ab, n_ctx_ab, dim)
                abnormal_background_suffix_learned,        # (n_pro * n_pro_ab, *, dim)
            ],
            dim=1,
        )
        
        #entity
        # print("shape of abnormal_entity_prefix_learned_list:", abnormal_entity_prefix_learned_list[0].shape)
        # print("shape of normal_ctx2:", normal_ctx2.shape)
        # print("shape of abnormal_ctx:", abnormal_ctx.shape)
        # print("shape of abnormal_entity_suffix_learned_list:", abnormal_entity_suffix_learned_list[0].shape)
        abnormal_entity_prompts_learned_list = [torch.cat(
            [
                abnormal_entity_prefix_learned.squeeze(0),        # (n_pro * n_pro_ab, 1, dim)
                normal_ctx2,                          # (n_pro * n_pro_ab, n_ctx, dim)
                abnormal_ctx,                         # (n_pro * n_pro_ab, n_ctx_ab, dim)
                abnormal_entity_suffix_learned.squeeze(0),        # (n_pro * n_pro_ab, *, dim)
            ],
            dim=1,
        ) for abnormal_entity_prefix_learned, abnormal_entity_suffix_learned in zip(abnormal_entity_prefix_learned_list, abnormal_entity_suffix_learned_list)]
        
        
        #relation
        abnormal_relation_prefix_learned = self.abnormal_token_relation_prefix_learned
        abnormal_relation_suffix_learned = self.abnormal_token_relation_suffix_learned
        # abnormal_relation_ctx = self.abnormal_ctx
        # normal_relation_ctx2 = normal_ctx.unsqueeze(0).expand(self.n_pro_ab, -1, -1, -1).reshape(-1, n_ctx, dim)
        # abnormal_relation_ctx = abnormal_relation_ctx.unsqueeze(0).expand(self.n_pro, -1, -1, -1).reshape(-1, n_ctx_ad, dim_ad)
        
        abnormal_relation_prompts_learned = torch.cat(
            [
                abnormal_relation_prefix_learned,        # (n_pro * n_pro_ab, 1, dim)
                normal_ctx2,                             # (n_pro * n_pro_ab, n_ctx, dim)
                abnormal_ctx,                            # (n_pro * n_pro_ab, n_ctx_ab, dim)
                abnormal_relation_suffix_learned,        # (n_pro * n_pro_ab, *, dim)
            ],
            dim=1,
        )
        
        #color
        abnormal_color_prefix_learned = self.abnormal_token_color_prefix_learned
        abnormal_color_suffix_learned = self.abnormal_token_color_suffix_learned
        
        abnormal_color_prompts_learned = torch.cat(
            [
                abnormal_color_prefix_learned,        # (n_pro * n_pro_ab, 1, dim)
                normal_ctx2,                          # (n_pro * n_pro_ab, n_ctx, dim)
                abnormal_ctx,                         # (n_pro * n_pro_ab, n_ctx_ab, dim)
                abnormal_color_suffix_learned,        # (n_pro * n_pro_ab, *, dim)
            ],
            dim=1,
        )
        
        #texture
        abnormal_texture_prefix_learned = self.abnormal_token_texture_prefix_learned
        abnormal_texture_suffix_learned = self.abnormal_token_texture_suffix_learned
        
        abnormal_texture_prompts_learned = torch.cat(
            [
                abnormal_texture_prefix_learned,        # (n_pro * n_pro_ab, 1, dim)
                normal_ctx2,                           # (n_pro * n_pro_ab, n_ctx, dim)
                abnormal_ctx,                          # (n_pro * n_pro_ab, n_ctx_ab, dim)
                abnormal_texture_suffix_learned,        # (n_pro * n_pro_ab, *, dim)
            ],
            dim=1,
        )
        
        #shape
        abnormal_shape_prefix_learned = self.abnormal_token_shape_prefix_learned
        abnormal_shape_suffix_learned = self.abnormal_token_shape_suffix_learned
        
        abnormal_shape_prompts_learned = torch.cat(
            [
                abnormal_shape_prefix_learned,        # (n_pro * n_pro_ab, 1, dim)
                normal_ctx2,                         # (n_pro * n_pro_ab, n_ctx, dim)
                abnormal_ctx,                        # (n_pro * n_pro_ab, n_ctx_ab, dim)
                abnormal_shape_suffix_learned,        # (n_pro * n_pro_ab, *, dim)
            ],
            dim=1,
        )
        
        #将abnormal_learned的多个属性特征加权相加到abnormal_prompts_learned中
        
        abnormal_prompts_learned = abnormal_prompts_learned + abnormal_relation_w * abnormal_relation_prompts_learned + abnormal_color_w * abnormal_color_prompts_learned + abnormal_texture_w * abnormal_texture_prompts_learned + abnormal_shape_w * abnormal_shape_prompts_learned

        # abnormal_prompts = torch.cat([abnormal_prompts_handle, abnormal_prompts_learned], dim=0)
        # abnormal_prompts = abnormal_prompts_handle

        return normal_prompts, abnormal_prompts_handle, abnormal_prompts_learned, normal_entity_prompts_list, abnormal_entity_prompts_handle_list, abnormal_entity_prompts_learned_list, normal_background_prompts, abnormal_background_prompts_handle, abnormal_background_prompts_learned


#这个类相比于FineGrainedAD，是将text_feature转化为了patch级别的text_feature，而不是整体的text_feature(即通过多个该类别的entity描述来计算出一个text_feature list, 然后根据image_feature逐token计算相似度最高的text_feature，用这个来代替原始全局的text_feature)
class FineGrainedPatchAD(torch.nn.Module):
    def __init__(self, out_size_h, out_size_w, device, backbone, pretrained_dataset, n_ctx, n_pro, n_ctx_ab, n_pro_ab, class_name, precision='fp16',k_shot=4, **kwargs):
        '''

        :param out_size_h:
        :param out_size_w:
        :param device:
        :param backbone:
        :param pretrained_dataset:
        '''
        super(FineGrainedPatchAD, self).__init__()

        self.shot = k_shot

        self.out_size_h = out_size_h
        self.out_size_w = out_size_w
        # self.precision = 'fp16' #precision  -40% GPU memory (2.8G->1.6G) with slight performance drop
        self.precision = precision
        
        
        self.device = device
        self.get_model(n_ctx, n_pro, n_ctx_ab, n_pro_ab, class_name, backbone, pretrained_dataset)
        self.phrase_form = '{}'
        self.device = device
        # self.entity_features_list = []

        # version v1: no norm for each of linguistic embedding
        # version v1:    norm for each of linguistic embedding
        self.version = 'V1' # V1:
        # visual textual, textual_visual

        self.transform = transforms.Compose([
            transforms.Resize((kwargs['img_resize'], kwargs['img_resize']), Image.BICUBIC),
            transforms.CenterCrop(kwargs['img_cropsize']),
            _convert_to_rgb,
            transforms.ToTensor(),
            transforms.Normalize(mean=mean_train, std=std_train)])

        self.gt_transform = transforms.Compose([
            transforms.Resize((kwargs['img_resize'], kwargs['img_resize']), Image.NEAREST),
            transforms.CenterCrop(kwargs['img_cropsize']),
            transforms.ToTensor()])
        
        #for cluster
        self.cluster_transform = transforms.Compose([
            transforms.Resize((kwargs['img_resize'] * 4, kwargs['img_resize'] * 4), Image.BICUBIC),
            transforms.CenterCrop(kwargs['img_cropsize'] * 4),
            _convert_to_rgb,
            transforms.ToTensor(),
            transforms.Normalize(mean=mean_train, std=std_train)])

    def get_model(self, n_ctx, n_pro, n_ctx_ab, n_pro_ab, class_name, backbone, pretrained_dataset):

        assert backbone in valid_backbones
        assert pretrained_dataset in valid_pretrained_datasets

        model, _, _ = CLIPAD.create_model_and_transforms(model_name=backbone, pretrained=pretrained_dataset, precision = self.precision)
        tokenizer = CLIPAD.get_tokenizer(backbone)
        model.eval()
        
        
        self.prompt_learner = FineGrainedPatchPromptLearner(n_ctx, n_pro, n_ctx_ab, n_pro_ab, class_name, model, self.precision)
        # self.prompt_learner = PromptLearner(n_ctx, n_pro, n_ctx_ab, n_pro_ab, class_name, model, self.precision)
        self.model = model.to(self.device)

        self.tokenizer = tokenizer
        self.normal_text_features = None
        self.abnormal_text_features = None
        self.grid_size = model.visual.grid_size
        self.visual_gallery = None
        self.visual_proj = model.visual.proj
        
        # self.large_grid_size = model.visual.large_grid_size
        # self.mid_grid_size = model.visual.mid_grid_size
        
        #self.prompt_learner.num_entity
        self.q_former = QueryFormer(self.prompt_learner.num_entity + 2, self.model.visual.output_dim, precision=self.precision).to(self.device)
        
        #加入区域聚类模块
        self.ctm0 = CTM(sample_ratio=2, embed_dim=self.model.visual.output_dim, dim_out=self.model.visual.output_dim, k = 8) #用于前背景划分
        self.block0 = TCBlock(dim=self.model.visual.output_dim, num_heads=10)
        self.ctm1 = CTM(sample_ratio=self.prompt_learner.num_entity + 1, embed_dim=self.model.visual.output_dim, dim_out=self.model.visual.output_dim, k = 5) #用于前景内实体token划分
        self.block1 = TCBlock(dim=self.model.visual.output_dim, num_heads=10)
        

        visual_gallery1 = torch.zeros((self.shot*self.grid_size[0]*self.grid_size[1], self.model.visual.embed_dim)) #[shot*grid_size[0]*grid_size[1], 640]
        self.register_buffer("feature_gallery1", visual_gallery1)

        visual_gallery2 = torch.zeros((self.shot*self.grid_size[0]*self.grid_size[1], self.model.visual.embed_dim))
        self.register_buffer("feature_gallery2", visual_gallery2)

        text_features = torch.zeros((2, self.model.visual.output_dim))
        self.register_buffer("text_features", text_features)
        
        background_features = torch.zeros((2, self.model.visual.output_dim))
        self.register_buffer("background_features", background_features)
        
        
        # self.entity_features_list = []
        entity_features_list = torch.zeros((self.prompt_learner.num_entity, 2, self.model.visual.output_dim))
        self.register_buffer("entity_features_list", entity_features_list)
        
        # text_patch_features = torch.zeros((self.grid_size[0]*self.grid_size[1], self.model.visual.output_dim)) #每一个patch对应一个text_feature(细粒度)
        # self.register_buffer("text_patch_features", text_patch_features)

        if self.precision == 'fp16':
            self.feature_gallery1  = self.feature_gallery1.half()
            self.feature_gallery2  = self.feature_gallery2.half()
            self.text_features  = text_features.half()
            self.entity_features_list = entity_features_list.half()
            self.background_features = background_features.half()
            # self.text_patch_features = text_patch_features.half()
        elif self.precision == 'bf16':
            self.feature_gallery1  = self.feature_gallery1.to(torch.bfloat16)
            self.feature_gallery2  = self.feature_gallery2.to(torch.bfloat16)
            self.text_features  = text_features.to(torch.bfloat16)
            self.entity_features_list = entity_features_list.to(torch.bfloat16)
            self.background_features = background_features.to(torch.bfloat16)

        # # for testing
        # p1, p2 = self.prompt_learner()
        self.tokenized_normal_prompts = self.prompt_learner.tokenized_normal_prompts
        self.tokenized_abnormal_prompts_handle = self.prompt_learner.tokenized_abnormal_prompts_handle
        self.tokenized_abnormal_prompts_learned = self.prompt_learner.tokenized_abnormal_prompts_learned
        self.tokenized_abnormal_prompts = torch.cat([self.tokenized_abnormal_prompts_handle, self.tokenized_abnormal_prompts_learned], dim=0)
        
        #background-level prompts
        self.tokenized_normal_background_prompts = self.prompt_learner.tokenized_normal_background_prompts
        self.tokenized_abnormal_background_prompts_handle = self.prompt_learner.tokenized_abnormal_background_prompts_handle
        self.tokenized_abnormal_background_prompts_learned = self.prompt_learner.tokenized_abnormal_background_prompts_learned
        self.tokenized_abnormal_background_prompts = torch.cat([self.tokenized_abnormal_background_prompts_handle, self.tokenized_abnormal_background_prompts_learned], dim=0)
        
        #for entity-level prompts
        self.tokenized_normal_entity_prompts_list = self.prompt_learner.tokenized_normal_entity_prompts_list
        self.tokenized_abnormal_entity_prompts_handle_list = self.prompt_learner.tokenized_abnormal_entity_prompts_handle_list
        self.tokenized_abnormal_entity_prompts_learned_list = self.prompt_learner.tokenized_abnormal_entity_prompts_learned_list
        self.tokenized_abnormal_entity_prompts_list = [torch.cat([tokenized_abnormal_entity_prompts_handle, tokenized_abnormal_entity_prompts_learned], dim=0) for tokenized_abnormal_entity_prompts_handle, tokenized_abnormal_entity_prompts_learned in zip(self.tokenized_abnormal_entity_prompts_handle_list, self.tokenized_abnormal_entity_prompts_learned_list)]
        
        # self.tokenized_entity_caption = self.prompt_learner.tokenized_entity_caption
        # self.entity_caption_embedding = self.prompt_learner.entity_caption_embedding

    @torch.no_grad()
    def encode_image(self, image: torch.Tensor):

        if self.precision == "fp16":
            image = image.half()
        elif self.precision == 'bf16':
            image = image.to(torch.bfloat16)
        image_features = self.model.encode_image(image)
        return [f / f.norm(dim=-1, keepdim=True) for f in image_features]


    @torch.no_grad()
    def encode_text(self, text: torch.Tensor):
        text_features = self.model.encode_text(text)
        # return [f / f.norm(dim=-1, keepdim=True) for f in text_features]
        return text_features

    def encode_text_embedding(self, text_embedding, original_tokens):
        text_features = self.model.encode_text_embeddings(text_embedding, original_tokens)
        return text_features

    @torch.no_grad()
    def build_text_feature_gallery(self):
        normal_text_embeddings, abnormal_text_embeddings_handle, abnormal_text_embeddings_learned, normal_entity_embedding_list, abnormal_entity_embedding_handle_list, abnormal_entity_embedding_learned_list = self.prompt_learner()
        abnormal_text_embeddings = torch.cat([abnormal_text_embeddings_handle, abnormal_text_embeddings_learned], dim=0)

        if self.version == "V1":
            normal_text_features = self.encode_text_embedding(normal_text_embeddings, self.tokenized_normal_prompts)
            abnormal_text_features = self.encode_text_embedding(abnormal_text_embeddings, self.tokenized_abnormal_prompts)
        elif self.version == "V2":
            normal_text_features = []
            for phrase_id in range(normal_text_embeddings.size()[0]):
                normal_text_feature = self.encode_text_embedding(normal_text_embeddings[phrase_id].unsqueeze(0), self.tokenized_normal_prompts)
                normal_text_feature = normal_text_feature/normal_text_feature.norm(dim=-1, keepdim=True)
                normal_text_features.append(normal_text_feature)
            normal_text_features = torch.cat(normal_text_features, 0).half()
            abnormal_text_features = []
            for phrase_id in range(abnormal_text_embeddings.size()[0]):
                abnormal_text_feature = self.encode_text_embedding(abnormal_text_embeddings[phrase_id].unsqueeze(0), self.tokenized_abnormal_prompts)
                abnormal_text_feature = abnormal_text_feature/abnormal_text_feature.norm(dim=-1, keepdim=True)
                abnormal_text_features.append(abnormal_text_feature)
            abnormal_text_features = torch.cat(abnormal_text_features, 0).half()
        else:
            raise NotImplementedError

        avr_normal_text_features = torch.mean(normal_text_features, dim=0, keepdim=True)
        avr_abnormal_text_features = torch.mean(abnormal_text_features, dim=0, keepdim=True)

        text_features_all = torch.cat([normal_text_features, abnormal_text_features], dim=0)
        text_features_all /= text_features_all.norm(dim=-1, keepdim=True)

        avr_normal_text_features = avr_normal_text_features
        avr_abnormal_text_features = avr_abnormal_text_features
        text_features = torch.cat([avr_normal_text_features, avr_abnormal_text_features], dim=0)
        self.text_features.copy_(text_features / text_features.norm(dim=-1, keepdim=True))
    
    @torch.no_grad()
    def build_text_feature_patch_gallery(self):
        normal_text_embeddings, abnormal_text_embeddings_handle, abnormal_text_embeddings_learned, normal_entity_embedding_list, abnormal_entity_embedding_handle_list, abnormal_entity_embedding_learned_list, normal_background_embeddings, abnormal_background_embeddings_handle, abnormal_background_embeddings_learned = self.prompt_learner()
        abnormal_text_embeddings = torch.cat([abnormal_text_embeddings_handle, abnormal_text_embeddings_learned], dim=0)

        abnormal_background_embeddings = torch.cat([abnormal_background_embeddings_handle, abnormal_background_embeddings_learned], dim=0)

        abnormal_entity_embedding_list = [torch.cat([abnormal_entity_embedding_handle, abnormal_entity_embedding_learned], dim=0) for abnormal_entity_embedding_handle, abnormal_entity_embedding_learned in zip(abnormal_entity_embedding_handle_list, abnormal_entity_embedding_learned_list)]
        
        
        if self.version == "V1":
            normal_text_features = self.encode_text_embedding(normal_text_embeddings, self.tokenized_normal_prompts)
            abnormal_text_features = self.encode_text_embedding(abnormal_text_embeddings, self.tokenized_abnormal_prompts)
            
            #background-level prompts
            normal_background_features = self.encode_text_embedding(normal_background_embeddings, self.tokenized_normal_background_prompts)
            abnormal_background_features = self.encode_text_embedding(abnormal_background_embeddings, self.tokenized_abnormal_background_prompts)
            
            
            normal_entity_features_list = [self.encode_text_embedding(normal_entity_embedding, tokenized_entity_caption) for normal_entity_embedding, tokenized_entity_caption in zip(normal_entity_embedding_list, self.tokenized_normal_entity_prompts_list)]
            abnormal_entity_features_list = [self.encode_text_embedding(abnormal_entity_embedding, tokenized_entity_caption) for abnormal_entity_embedding, tokenized_entity_caption in zip(abnormal_entity_embedding_list, self.tokenized_abnormal_entity_prompts_list)]
            
        else:
            raise NotImplementedError

        avr_normal_text_features = torch.mean(normal_text_features, dim=0, keepdim=True)
        avr_abnormal_text_features = torch.mean(abnormal_text_features, dim=0, keepdim=True)
        
        avr_normal_background_features = torch.mean(normal_background_features, dim=0, keepdim=True)
        avr_abnormal_background_features = torch.mean(abnormal_background_features, dim=0, keepdim=True)
        
        
        avr_normal_entity_features_list = [torch.mean(normal_entity_features, dim=0, keepdim=True) for normal_entity_features in normal_entity_features_list]
        avr_abnormal_entity_features_list = [torch.mean(abnormal_entity_features, dim=0, keepdim=True) for abnormal_entity_features in abnormal_entity_features_list]
        
        # print("avr_text_features shape: ", avr_normal_text_features.shape, avr_abnormal_text_features.shape)
        # print("avr_normal_entity_features_list shape: ", [entity_features.shape for entity_features in avr_normal_entity_features_list])
        # print("avr_abnormal_entity_features_list shape: ", [entity_features.shape for entity_features in avr_abnormal_entity_features_list])

        # text_features_all = torch.cat([normal_text_features, abnormal_text_features], dim=0)
        # text_features_all /= text_features_all.norm(dim=-1, keepdim=True)
        
        # entity_features_all_list = [torch.cat([normal_entity_features, abnormal_entity_features], dim=0) for normal_entity_features, abnormal_entity_features in zip(normal_entity_features_list, abnormal_entity_features_list)]
        # entity_features_all_list = [entity_features_all / entity_features_all.norm(dim=-1, keepdim=True) for entity_features_all in entity_features_all_list]

        # avr_normal_text_features = avr_normal_text_features
        # avr_abnormal_text_features = avr_abnormal_text_features
        text_features = torch.cat([avr_normal_text_features, avr_abnormal_text_features], dim=0)
        self.text_features.copy_(text_features / text_features.norm(dim=-1, keepdim=True))
        
        background_features = torch.cat([avr_normal_background_features, avr_abnormal_background_features], dim=0)
        self.background_features.copy_(background_features / background_features.norm(dim=-1, keepdim=True))
        
        
        entity_features_list = [torch.cat([avr_normal_entity_features, avr_abnormal_entity_features], dim=0) for avr_normal_entity_features, avr_abnormal_entity_features in zip(avr_normal_entity_features_list, avr_abnormal_entity_features_list)]
        entity_features_list = [entity_features / entity_features.norm(dim=-1, keepdim=True) for entity_features in entity_features_list]
        self.entity_features_list.copy_(torch.cat([entity_features.unsqueeze(0) for entity_features in entity_features_list], dim=0)) 
        # print("text_features shape: ", self.text_features.shape)
        # print("entity_features_list shape: ", self.entity_features_list.shape)
        # print("text_features shape: ", self.text_features.shape)
        # print("entity_features_list shape: ", [entity_features.shape for entity_features in self.entity_features_list])
    

    def build_image_feature_gallery(self, features1, features2):
        b1, n1, d1 = features1.shape
        self.feature_gallery1.copy_(F.normalize(features1.reshape(-1, d1), dim=-1))

        b2, n2, d2 = features2.shape
        self.feature_gallery2.copy_(F.normalize(features2.reshape(-1, d2), dim=-1))
        

    def calculate_textual_anomaly_score(self, visual_features, task):
        # t = 100
        t = self.model.logit_scale
        # t = self.t
        N = visual_features[1].shape[0]

        if task == 'seg':
            # ############################################## local tokens scores ############################
            # token_features = self.cross_attention(visual_features[1])
            token_features = visual_features[1]
            local_normality_and_abnormality_score = (t * token_features @ self.text_features.T).softmax(dim=-1)

            local_abnormality_score = local_normality_and_abnormality_score[:, :, 1]

            local_abnormality_score = torch.zeros((N, self.grid_size[0] * self.grid_size[1])) + local_abnormality_score.cpu()
            local_abnormality_score = local_abnormality_score.reshape((N, self.grid_size[0], self.grid_size[1])).unsqueeze(1)

            return local_abnormality_score.detach()

        elif task == 'cls':
            # ################################################ global cls token scores ##########################
            # global_feature = self.cross_attention(visual_features[0].unsqueeze(dim=1)).squeeze(dim=1)
            global_feature = visual_features[0]
            global_normality_and_abnormality_score = (t * global_feature @ self.text_features.T).softmax(dim=-1)

            global_abnormality_score = global_normality_and_abnormality_score[:, 1]

            global_abnormality_score = global_abnormality_score.cpu()

            return global_abnormality_score.detach().numpy()

        else:
            assert 'task error'
    
    
    
    def language_guided_progressive_region_aggregation(self, image_features, entity_features):
        #image_features shape: B, N, C
        
        #渐进式区域聚合：
        #首先聚合前背景区域，即聚类簇数为2，然后得到前景和背景的区分。然后将背景区域的token作为mask信息输入到前景区域的聚类中，从而避免背景对前景的干扰。
        
        new_image_features = []
        semantic_info = []
        
        
        for idx in range(image_features.shape[0]):
            image_feature = image_features[idx]
            #I, c * C, J -> i, j
            cs_matrix = torch.mm(image_feature, entity_features.t()) / (torch.norm(image_feature, dim = 1).unsqueeze(1) * torch.norm(entity_features, dim = 1).unsqueeze(0))
            new_image_features.append(cs_matrix)
            
            sim_background = cs_matrix[:, -1] #shape I
            # if len(sim_background.shape) == 1:
            #     sim_background = sim_background.unsqueeze(-1)
            #在-1维度上计算最大和最小值对应的索引
            max_idx = torch.argmax(sim_background, dim = -1)
            min_idx = torch.argmin(sim_background, dim = -1)
            # print("max_idx shape:", max_idx.shape)
            # print("max_idx:", max_idx)
            # print("min_idx shape:", min_idx.shape)
            # print("min_idx:", min_idx)
            #然后组成一个size为2的tensor存入semantic_info中
            if max_idx > min_idx:
                semantic_info.append(torch.stack([min_idx, max_idx], dim = 0))
            else:
                semantic_info.append(torch.stack([max_idx, min_idx], dim = 0))
            
        
        new_image_features = torch.stack(new_image_features, dim = 0)
        semantic_info = torch.stack(semantic_info, dim = 0)
        # print("new_image_features shape:", new_image_features.shape)
        # print("semantic_info shape:", semantic_info.shape)
        #用背景特征和图像特征计算相似度，选择激活值最大的index作为背景区域的聚类中心，激活值最小的index作为前景区域的聚类中心。聚类簇数为2。
        
        # torch.set_printoptions(profile="full")
        
        token_dict = {'x': new_image_features,
                              'token_num': new_image_features.size(1),
                              'idx_token': torch.arange(new_image_features.size(1))[None, :].repeat(
                                  new_image_features.size(0), 1),
                              'agg_weight': new_image_features.new_ones(new_image_features.size(0), new_image_features.size(1),
                                                                    1),
                              'mask': None,
                              'semantic_info':None, #torch.size(B, cluster_num)
                            #   'semantic_info':semantic_info, #torch.size(B, cluster_num)
                              'init_grid_size': (16, 16)}
        
        # token_dict = {'x': image_features,
        #                       'token_num': image_features.size(1),
        #                       'idx_token': torch.arange(image_features.size(1))[None, :].repeat(
        #                           image_features.size(0), 1),
        #                       'agg_weight': image_features.new_ones(image_features.size(0), image_features.size(1),
        #                                                             1),
        #                       'mask': None,
        #                       'semantic_info':None, #torch.size(B, cluster_num)
        #                     #   'semantic_info':semantic_info, #torch.size(B, cluster_num)
        #                       'init_grid_size': (16, 16)}
        
        first_token_dict = self.block0(self.ctm0(token_dict))
        
        first_idx_token = first_token_dict['idx_token']
        # print("first_idx_token:", first_idx_token)
        #两种策略，找到聚类里面的背景区域
        #1. 引入entity_feature中的背景特征，去和两种类型的平均特征计算相似度，来实现前背景类别的区分。
        #2. 直接取四角的token的类别，即为背景类别。
        
        
        # print("torch idx-token==0,shape:", torch.where(first_idx_token == 0)[0].shape)
        # print("torch idx-token==1,shape:", torch.where(first_idx_token == 1)[0].shape)
        
        # print("idx-token==1 shape:", (first_idx_token==1).shape)
        # print("idx-token==0 shape:", (first_idx_token==0).shape)
        
        #第一种策略
        normal_background_feature = entity_features[-1]
        # print("normal_background_feature shape:", normal_background_feature.shape)
        if len(normal_background_feature.shape) == 1:
            normal_background_feature = normal_background_feature.unsqueeze(0)
        
        #根据得到的idx_token，找到对应的token feature
        token_feature_0 = []
        token_feature_1 = []
        for idx in range(first_idx_token.shape[0]):
            token_feature_0.append(image_features[idx, (first_idx_token==0)[0], :])
            token_feature_1.append(image_features[idx, (first_idx_token==1)[0], :])
            
            # print("token_feature_0 shape:", token_feature_0.shape)
            # print("token_feature_1 shape:", token_feature_1.shape)
        token_feature_0 = torch.stack(token_feature_0, dim=0)
        token_feature_1 = torch.stack(token_feature_1, dim=0)
        
        # token_feature_0 = image_features[first_idx_token==0,:]
        # token_feature_1 = image_features[first_idx_token==1,:]
        # token_feature_0 = image_features[:,torch.where(first_idx_token == 0)[0],:]
        # token_feature_1 = image_features[:,torch.where(first_idx_token == 1)[0],:]
        # print("token_feature_0 shape:", token_feature_0.shape)
        # print("token_feature_1 shape:", token_feature_1.shape)
        
        #取特征的平均值
        token_feature_0 = token_feature_0.mean(dim = 1)
        token_feature_1 = token_feature_1.mean(dim = 1) #B * 640
        
        # print("avg token_feature_0 shape:", token_feature_0.shape)
        # print("avg token_feature_1 shape:", token_feature_1.shape)
        #计算和背景特征的相似度
        cs_matrix_0 = torch.mm(token_feature_0, normal_background_feature.t()) 
        cs_matrix_1 = torch.mm(token_feature_1, normal_background_feature.t())
        
        # print("cs_matrix_0 shape:", cs_matrix_0.shape) #B * 1
        # print("cs_matrix_1 shape:", cs_matrix_1.shape) #B * 1
        # print("cs_matrix_0:", cs_matrix_0) #B * 1
        # print("cs_matrix_1:", cs_matrix_1) #B * 1
        
        foreground_idx_token = torch.arange(new_image_features.size(1))[None, :].repeat(
                                             new_image_features.size(0), 1)
        
        result_first_idx_token = first_idx_token.clone().detach()
        for idx in range(cs_matrix_0.shape[0]):
            #对于batch内的每张图像
            #比较两个token的相似度，取更大的为背景区域，更小的为前景区域
            #总是0表示背景，1表示前景
            if cs_matrix_0[idx] < cs_matrix_1[idx]:
                result_first_idx_token[idx, (first_idx_token==0)[0]] = 1
                result_first_idx_token[idx, (first_idx_token==1)[0]] = 0
            foreground_idx_token[idx, (result_first_idx_token==0)[0]] = 0
        
        # print("result_first_idx_token:", result_first_idx_token)
        # print("foreground_idx_token:", foreground_idx_token)
        
        
        #得到了前背景的区分，然后将背景区域的token作为mask信息输入到前景区域的聚类中，从而避免背景对前景的干扰。
        # foreground_token_dict = {'x': image_features,
        #                         'token_num': image_features.size(1),
        #                         'idx_token': foreground_idx_token,
        #                         # 'idx_token': first_idx_token,
        #                         'agg_weight': image_features.new_ones(image_features.size(0), image_features.size(1),
        #                                                                 1),
        #                         'mask': result_first_idx_token,
        #                         'init_grid_size': (16, 16)}
        
        foreground_token_dict = {'x': new_image_features,
                                'token_num': new_image_features.size(1),
                                'idx_token': foreground_idx_token,
                                # 'idx_token': first_idx_token,
                                'agg_weight': new_image_features.new_ones(new_image_features.size(0), new_image_features.size(1),
                                                                        1),
                                'mask': result_first_idx_token,
                                'semantic_info': None,
                                'init_grid_size': (16, 16)}
        
        # foreground_token_dict = {'x': image_features,
        #                         'token_num': image_features.size(1),
        #                         'idx_token': foreground_idx_token,
        #                         # 'idx_token': first_idx_token,
        #                         'agg_weight': image_features.new_ones(new_image_features.size(0), new_image_features.size(1),
        #                                                                 1),
        #                         'mask': result_first_idx_token,
        #                         'semantic_info': None,
        #                         'init_grid_size': (16, 16)}
        
        # token_dict = {'x': image_features,
        #                       'token_num': image_features.size(1),
        #                       'idx_token': torch.arange(image_features.size(1))[None, :].repeat(
        #                           image_features.size(0), 1),
        #                       'agg_weight': image_features.new_ones(image_features.size(0), image_features.size(1),
        #                                                             1),
        #                       'mask': None,
        #                       'init_grid_size': (16, 16)}
        # token_dict_new, token_dict_old = self.ctm0(token_dict)
        # token_dict = self.block1(self.ctm1(token_dict))
        # token_dict = self.block0(self.ctm0(token_dict))
        
        #由于直接采用visual tokens的640维度来进行聚类的效果比较差，考虑引入语义指导
        #第一个思路，直接用现有的所有visual tokens和所有entity features计算余弦相似度的分数，将得到的每一个实体的相似度作为一个新的维度，在这个维度上做DPC-KNN的聚类。
        #实现代码如下：
        # matches = self.get_max_cosine_similarity_match(image_features, entity_features)
        
        # print("image_features shape:", image_features.shape)
        # print("entity_features shape:", entity_features.shape)
        
        # new_image_features = []
        # for idx in range(image_features.shape[0]):
        #     image_feature = image_features[idx]
        #     #I, c * C, J -> i, j
        #     cs_matrix = torch.mm(image_feature, entity_features.t()) / (torch.norm(image_feature, dim = 1).unsqueeze(1) * torch.norm(entity_features, dim = 1).unsqueeze(0))
        #     new_image_features.append(cs_matrix)
        
        # new_image_features = torch.stack(new_image_features, dim = 0)
        
        # print("new_image_features shape:", new_image_features.shape)
        
        # token_dict = {'x': new_image_features,
        #                       'token_num': new_image_features.size(1),
        #                       'idx_token': torch.arange(new_image_features.size(1))[None, :].repeat(
        #                           new_image_features.size(0), 1),
        #                       'agg_weight': new_image_features.new_ones(new_image_features.size(0), new_image_features.size(1),
        #                                                             1),
        #                       'mask': None,
        #                       'init_grid_size': (16, 16)}
        # token_dict_new, token_dict_old = self.ctm0(token_dict)
        token_dict = self.block1(self.ctm1(foreground_token_dict))
        # second_idx_token = token_dict['idx_token']
        # print("second_idx_token:", second_idx_token)
        # token_dict = self.block0(self.ctm0(token_dict))
        # torch.set_printoptions(profile="default")
        return token_dict
        
        
    
    
    def get_max_cosine_similarity_match(self, token_features, entity_features):
        # token_features:[n, i, c]
        # entity_features:[j, c]
        
        matches = []
        n, i, c = token_features.shape
        j = entity_features.shape[0]
        # print(n, i, c, j)
        # print_matches = []
        
        
        for idx in range(n):
            token_feature = token_features[idx] # [i, c]
            
            #计算余弦相似度矩阵
            # print("Shape in Match:", token_feature.shape, entity_features.shape)
            
            cosine_similarity_matrix = torch.mm(token_feature, entity_features.t()) / (torch.norm(token_feature, dim = 1).unsqueeze(1) * torch.norm(entity_features, dim=1).unsqueeze(0))

            # 将余弦相似度矩阵转换为距离矩阵
            # distance_matrix = 1 - cosine_similarity_matrix.cpu().numpy()
            
            # 使用匈牙利算法进行匹配
            # row_ind, col_ind = linear_sum_assignment(distance_matrix)
            
            # 对于每个 i，找到与 j 中余弦相似度最大的索引
            max_similarity_indices = torch.argmax(cosine_similarity_matrix, dim=1)
            
            # 存储匹配结果
            matches.append([[i, j.item()] for i, j in enumerate(max_similarity_indices)])
            # matches.append([[i, j.item()] for i, j in enumerate(max_similarity_indices)])
            
            # print_matches.append([j.item() for j in max_similarity_indices])
            # matches.append((row_ind, col_ind))
            # print(matches.size())
            # print(matches)
            # print(row_ind, col_ind)
        # print(matches)
        
        # print("Matches[0]: ", matches[0])
        
        return matches
    
    
    #patch级别的text特征
    def calculate_textual_patch_anomaly_score(self, visual_features, task):
        # t = 100
        t = self.model.logit_scale
        # t = self.t
        N = visual_features[1].shape[0]
        
        # print("Shape of entity_features_list: ", self.entity_features_list.shape)
        
        #根据token features(n,i,c)计算每个token的最接近的entity feature(2,c)(具体来说就是从entity_features_list中找到最相似的entity feature)

        if task == 'seg':
            # ############################################## local tokens scores ############################
            # token_features = self.cross_attention(visual_features[1])
            token_features = visual_features[1] # (n, i, c)
            entity_features_list = torch.chunk(self.entity_features_list, chunks=self.prompt_learner.num_entity, dim=0) #list of tensor, [2, c]
            entity_features_list = [entity_features.squeeze(0) for entity_features in entity_features_list]
            entity_features_list.append(self.text_features) #list of tensor, [2, c]
            entity_features_list.append(self.background_features) #list of tensor, [2, c]
            
            #取entity_features_list中每个元素的第一项，即[c]维度的tensor组成一个新的tensor，尺寸为[num of entity_features_list, c]

            normality_entity_features = torch.stack([features[0] for features in entity_features_list]) #shape: [num_entity, c]
            abnormality_entity_features = torch.stack([features[1] for features in entity_features_list]) #shape: [num_entity, c]
            
            intrinsic_entity_features = self.q_former(normality_entity_features, abnormality_entity_features) #shape: [num_entity, c]
            
            matches = self.get_max_cosine_similarity_match(token_features, intrinsic_entity_features) #list of (i, j)
            # matches = self.get_max_cosine_similarity_match(token_features, normality_entity_features) #list of (i, j)
            
            #根据得到的匹配结果，拼接出最后的异常分数
            local_normality_and_abnormality_score_list = []
            for i in range(token_features.shape[0]):
                local_normality_and_abnormality_score_list.append(torch.stack([(t * token_features[i][idx_t] @ entity_features_list[idx_e].T).softmax(dim=-1) for (idx_t, idx_e) in matches[i]])) 
            
            local_normality_and_abnormality_score = torch.stack(local_normality_and_abnormality_score_list)
            # local_normality_and_abnormality_score= torch.stack([(t * token_features @ entity_features.T).softmax(dim=-1) for entity_features in entity_features_list]).mean(dim=0)
            
            
            
            
            # print("token_features shape: ", token_features.shape)
            # return token_features
            # local_normality_and_abnormality_score = (t * token_features @ self.text_features.T).softmax(dim=-1)

            local_abnormality_score = local_normality_and_abnormality_score[:, :, 1]

            local_abnormality_score = torch.zeros((N, self.grid_size[0] * self.grid_size[1])) + local_abnormality_score.cpu()
            local_abnormality_score = local_abnormality_score.reshape((N, self.grid_size[0], self.grid_size[1])).unsqueeze(1)

            return local_abnormality_score.detach()

        elif task == 'cls':
            # ################################################ global cls token scores ##########################
            # global_feature = self.cross_attention(visual_features[0].unsqueeze(dim=1)).squeeze(dim=1)
            global_feature = visual_features[0] #(n, c)
            entity_features_list = torch.chunk(self.entity_features_list, chunks=self.prompt_learner.num_entity, dim=0) #list of tensor, [2, c]
            entity_features_list = [entity_features.squeeze(0) for entity_features in entity_features_list]
            entity_features_list.append(self.text_features) #list of tensor, [2, c]
            entity_features_list.append(self.background_features) #list of tensor, [2, c]
            
            # normality_entity_features = torch.stack([features[0] for features in entity_features_list])
            
            #取entity_features_list中每个元素的第一项，即[c]维度的tensor组成一个新的tensor，尺寸为[num of entity_features_list, c]

            normality_entity_features = torch.stack([features[0] for features in entity_features_list]) #shape: [num_entity, c]
            abnormality_entity_features = torch.stack([features[1] for features in entity_features_list]) #shape: [num_entity, c]
            
            intrinsic_entity_features = self.q_former(normality_entity_features, abnormality_entity_features) #shape: [num_entity, c]
            
            global_feature = global_feature.unsqueeze(1)
            matches = self.get_max_cosine_similarity_match(global_feature, intrinsic_entity_features) #list of (i, j)
            
            
            # global_feature = global_feature.unsqueeze(1)
            # matches = self.get_max_cosine_similarity_match(global_feature, normality_entity_features) #list of (i, j)
            
            global_normality_and_abnormality_score_list = []
            for i in range(global_feature.shape[0]):
                global_normality_and_abnormality_score_list.append(torch.stack([(t * global_feature[i][idx_t] @ entity_features_list[idx_e].T).softmax(dim=-1) for (idx_t, idx_e) in matches[i]]))
            
            global_normality_and_abnormality_score = torch.stack(global_normality_and_abnormality_score_list).squeeze(1)
            # print(global_normality_and_abnormality_score.shape)
            # global_normality_and_abnormality_score = torch.stack([(t * global_feature @ entity_features.T).softmax(dim=-1) for entity_features in entity_features_list]).mean(dim=0)
            # global_normality_and_abnormality_score = (t * global_feature @ self.text_features.T).softmax(dim=-1)

            global_abnormality_score = global_normality_and_abnormality_score[:, 1]

            global_abnormality_score = global_abnormality_score.cpu()

            return global_abnormality_score.detach().numpy()

        else:
            assert 'task error'

    def calculate_visual_anomaly_score(self, visual_features):
        N = visual_features[1].shape[0]

        score1, _ = (1.0 - visual_features[2] @ self.feature_gallery1.t()).min(dim=-1)
        score1 /= 2.0

        score2, _ = (1.0 - visual_features[3] @ self.feature_gallery2.t()).min(dim=-1)
        score2 /= 2.0

        score = torch.zeros((N, self.grid_size[0] * self.grid_size[1])) + 0.5 * (score1 + score2).cpu()

        return score.reshape((N, self.grid_size[0], self.grid_size[1])).unsqueeze(1)

    def forward(self, images, task):

        visual_features = self.encode_image(images)
        if task == 'seg':
            textual_anomaly_map = self.calculate_textual_patch_anomaly_score(visual_features, 'seg')
            # textual_anomaly_map = self.calculate_textual_anomaly_score(visual_features, 'seg')

            visual_anomaly_map = self.calculate_visual_anomaly_score(visual_features)
            #
            anomaly_map = 1. / (1. / textual_anomaly_map + 1. / visual_anomaly_map)  # harmonic mean (paper)
            # anomaly_map = textual_anomaly_map + visual_anomaly_map  # simple addition
            # anomaly_map = visual_anomaly_map #91.46
            # anomaly_map = textual_anomaly_map #90.33

            anomaly_map = F.interpolate(anomaly_map, size=(self.out_size_h, self.out_size_w), mode='bilinear', align_corners=False)

            am_pix = anomaly_map.squeeze(1).numpy()

            am_pix_list = []

            for i in range(am_pix.shape[0]):
                am_pix[i] = gaussian_filter(am_pix[i], sigma=4)
                am_pix_list.append(am_pix[i])

            return am_pix_list

        elif task == 'cls':
            # textual_anomaly = self.calculate_textual_anomaly_score(visual_features, 'cls')
            textual_anomaly = self.calculate_textual_patch_anomaly_score(visual_features, 'cls')
            

            visual_anomaly_map = self.calculate_visual_anomaly_score(visual_features)

            anomaly_map = F.interpolate(visual_anomaly_map, size=(self.out_size_h, self.out_size_w), mode='bilinear',
                                        align_corners=False)

            am_pix = anomaly_map.squeeze(1).numpy()

            am_pix_list = []

            for i in range(am_pix.shape[0]):
                am_pix_list.append(am_pix[i])

            am_img_list = []
            for i in range(textual_anomaly.shape[0]):
                am_img_list.append(textual_anomaly[i])

            return am_img_list, am_pix_list
        else:
            assert 'task error'

    def train_mode(self):
        self.model.train()

    def eval_mode(self):
        self.model.eval()

