import torch
import numpy as np
from utils.data_loader import get_relative_pos, get_trigger_mask

TRI_LEN = 20
ARG_LEN_DICT = {
    'unit':15,
}


def extract_all_items_without_oracle(model, device, idx, content: str, token, seg, mask, seq_len, threshold_0, threshold_1, threshold_2, threshold_3, threshold_4, id_type: dict, id_args: dict, ty_args_id: dict):
    assert token.size(0) == 1
    content = content[0]
    result = {'id': idx, 'content': content}
    text_emb = model.plm(token, seg, mask)

    args_id = {id_args[k]: k for k in id_args}
    args_len_dict = {args_id[k]: ARG_LEN_DICT[k] for k in ARG_LEN_DICT}

    p_type, type_emb = model.predict_type(text_emb, mask)
    # print("阈值",p_type)
    max=np.max(p_type)
    if max<threshold_0:
        p_type=np.where(p_type<max,0,p_type)
        type_pred = np.array(p_type > 1e-5, dtype=bool)
    else:
        type_pred = np.array(p_type > threshold_0, dtype=bool)
    type_pred = [i for i, t in enumerate(type_pred) if t]
    events_pred = []

    for type_pred_one in type_pred:
        type_rep = type_emb[type_pred_one, :]
        type_rep = type_rep.unsqueeze(0)
        p_s, p_e, text_rep_type = model.predict_trigger(type_rep, text_emb, mask)
        
   
   
        
        # max=np.max(p_s)
        # if max<threshold_1:
        #     p_s=np.where(p_s<max,0,p_s)
        #     trigger_s = np.where(p_s > 1e-5)[0]
        # else:
        #     trigger_s = np.where(p_s > threshold_1)[0]
            
        # max=np.max(p_e)
        # if max<threshold_2:
        #     p_e=np.where(p_e<max,0,p_e)
        #     trigger_e = np.where(p_e > 1e-5)[0]
        # else:
        #     trigger_e = np.where(p_e > threshold_2)[0]    
             
        # trigger_spans = []

        # for i in trigger_s:
        #     es = trigger_e[trigger_e >= i]
        #     if len(es) > 0:
        #         e = es[0]
        #         if e - i + 1 <= TRI_LEN:
        #             trigger_spans.append((i, e))


        max_ps=np.max(p_s)
        max_pe=np.max(p_e)
        if max_ps<threshold_1 or max_pe<threshold_2:
            # p_s=np.where(p_s<max,0,p_s)
            trigger_s = np.where(p_s > 0.01)[0]
            trigger_e = np.where(p_e > 0.01)[0]
            
            trigger_spans = []
            
            f=0
            for i in trigger_s:
                es = trigger_e[trigger_e >= i]
                if len(es) > 0:
                    e = es[0]
                    if e - i + 1 <= TRI_LEN:
                        if f==0 or f< p_s[i]+p_e[e]:
                            trigger_spans=[(i, e)]
                            f=p_s[i]+p_e[e]
            
            
        else:
            trigger_s = np.where(p_s > threshold_1)[0]
            trigger_e = np.where(p_e > threshold_2)[0] 
     
            trigger_spans = []

            for i in trigger_s:
                es = trigger_e[trigger_e >= i]
                if len(es) > 0:
                    e = es[0]
                    if e - i + 1 <= TRI_LEN:
                        trigger_spans.append((i, e))


        # 对于每个trigger
        for k, span in enumerate(trigger_spans):
            rp = get_relative_pos(span[0], span[1], seq_len)
            rp = [p + seq_len for p in rp]
            tm = get_trigger_mask(span[0], span[1], seq_len)
            rp = torch.LongTensor(rp).to(device)
            tm = torch.LongTensor(tm).to(device)
            rp = rp.unsqueeze(0)
            tm = tm.unsqueeze(0)

            p_s, p_e, type_soft_constrain = model.predict_args(text_rep_type, rp, tm, mask, type_rep)

            p_s = np.transpose(p_s)
            p_e = np.transpose(p_e)

            type_name = id_type[type_pred_one]
            pred_event_one = {'type': type_name}
            pred_trigger = {'span': [int(span[0]) - 1, int(span[1]) + 1 - 1], 'word': content[int(span[0]) - 1:int(span[1]) + 1 - 1]}  # remove <CLS> token
            pred_event_one['trigger'] = pred_trigger
            pred_args = {}

            args_candidates = ty_args_id[type_pred_one]
            
            for i in args_candidates:
                pred_args[id_args[i]] = []
                #输出满足条件元素的坐标：门槛值是0.5
                
                max_as=np.max(p_s[i])
                max_ae=np.max(p_e[i])
                if max_as < threshold_3 or max_ae < threshold_4:
                    args_s = np.where(p_s[i] > 0.01)[0]
                    args_e = np.where(p_e[i] > 0.01)[0]
                    
                    l=0;
                    for j in args_s:
                        es = args_e[args_e >= j]
                        if len(es) > 0:
                            e = es[0]
                            if e - j + 1 <= args_len_dict[i]:
                                # print("置信度",(p_s[i][j]+p_e[i][e])/2)
                                if l==0 or l<(p_s[i][j]+p_e[i][e]):
                                    pred_arg = {'span': [int(j) - 1, int(e) + 1 - 1], 'word': content[int(j) - 1:int(e) + 1 - 1], 'confidence_score':(p_s[i][j]+p_e[i][e])/2}  # remove <CLS> token
                                    # pred_arg = {'span': [int(j) - 1, int(e) + 1 - 1], 'word': content[int(j) - 1:int(e) + 1 - 1]}
                                    pred_args[id_args[i]]=[pred_arg]
                                    l=(p_s[i][j]+p_e[i][e])
                
                
                
                else: 
                    args_s = np.where(p_s[i] > threshold_3)[0]
                    args_e = np.where(p_e[i] > threshold_4)[0]

                    for j in args_s:
                        es = args_e[args_e >= j]
                        if len(es) > 0:
                            e = es[0]
                            if e - j + 1 <= args_len_dict[i]:
                                # print("置信度",(p_s[i][j]+p_e[i][e])/2)
                                pred_arg = {'span': [int(j) - 1, int(e) + 1 - 1], 'word': content[int(j) - 1:int(e) + 1 - 1], 'confidence_score':(p_s[i][j]+p_e[i][e])/2}  # remove <CLS> token
                                # pred_arg = {'span': [int(j) - 1, int(e) + 1 - 1], 'word': content[int(j) - 1:int(e) + 1 - 1]}
                                pred_args[id_args[i]].append(pred_arg)
            # print(pred_args,events_pred)
            
            # if pred_args=={} and events_pred == []:
            
            #     for i in args_candidates:
            #         pred_args[id_args[i]] = []
            #         #输出满足条件元素的坐标：门槛值是0.5
                    
            #         max_as=np.max(p_s[i])
            #         max_ae=np.max(p_e[i])
            #         if max_as < threshold_3:
            #             args_s = np.where(p_s[i] > 0.01)[0]
            #         else: args_s = np.where(p_s[i] > threshold_3)[0]
            #         if max_ae < threshold_4:   
            #             args_e = np.where(p_e[i] > 0.01)[0]
            #         else: args_e = np.where(p_e[i] > threshold_4)[0]

            #         l=0;
            #         for j in args_s:
            #             es = args_e[args_e >= j]
            #             if len(es) > 0:
            #                 e = es[0]
            #                 if e - j + 1 <= args_len_dict[i]:
            #                     # print("置信度",(p_s[i][j]+p_e[i][e])/2)
            #                     if l==0 or l<(p_s[i][j]+p_e[i][e]):
            #                         pred_arg = {'span': [int(j) - 1, int(e) + 1 - 1], 'word': content[int(j) - 1:int(e) + 1 - 1], 'confidence_score':(p_s[i][j]+p_e[i][e])/2}  # remove <CLS> token
            #                         # pred_arg = {'span': [int(j) - 1, int(e) + 1 - 1], 'word': content[int(j) - 1:int(e) + 1 - 1]}
            #                         pred_args[id_args[i]]=[pred_arg]
            #                         l=(p_s[i][j]+p_e[i][e])
            
            
               
            pred_event_one['args'] = pred_args
            
            events_pred.append(pred_event_one)
    
    result['events'] = events_pred
    return result
