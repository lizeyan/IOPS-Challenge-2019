#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 08:57:21 2019

@author: Yang dian
"""

import numpy as np
import pandas as pd
import json
from sys import argv


def reconstruct_set(timestamp, set_):  # reconstruct the order
    if set_ == 'nan' or set_ == 'NaN':  # empty input
        return []
    set_ = set_.split(';')
    new_set = []

    for ele in set_:
        new_ele = sorted(ele.split('&'))
        new_set.append(new_ele)
        
    new_set = sorted(new_set)
    return new_set


def compute_f1(true_set, pred_set):
    TP = 0.0
    FP = 0.0
    FN = 0.0
    Precision = 0.0
    Recall = 0.0
    score = 0.0

    i_true = 0
    i_pred = 0
    while i_true < len(true_set) and i_pred < len(pred_set):
        if pred_set[i_pred] < true_set[i_true]:
            FP += 1
            i_pred += 1
            continue
        if true_set[i_true] < pred_set[i_pred]:
            FN += 1
            i_true += 1
            continue
        else:
            TP += 1
            i_pred += 1
            i_true += 1
    FP += (len(pred_set) - i_pred)
    # plus the rest number of unmatched element in pred_set, repeated output will be considered as FP
    FN += (len(true_set) - i_true)
    # plus the rest number of unmatched element in true_set

    if TP > 0:
        Precision = TP / (TP + FP)
        Recall = TP / (TP + FN)
    if (Precision + Recall) > 0:
        score = (2 * Precision * Recall) / (Precision + Recall)

    return score, TP, FP, FN


def root_evaluation(truth_file, result_file):
    data = {'result': False, 'total_fscore': "", 'message': ""}
    result_df = None
    
    if result_file[-4:] != '.csv':
        data['message'] = "提交的文件必须是csv格式"
        return json.dumps(data, ensure_ascii=False)
    else:
        result_df = pd.read_csv(result_file, engine='python', delimiter='\s*,\s*')

    if 'timestamp' not in result_df.columns or 'set' not in result_df.columns:
        data['message'] = "提交的文件必须包含'timestamp', 'set'两列，您的输入为{}".format(result_df.columns)
        return json.dumps(data, ensure_ascii=False)

    truth_df = pd.read_csv(truth_file)
    timestamps = np.unique(truth_df['timestamp'].values)

    f1_scores = []
    total_TP = 0.0
    total_FP = 0.0
    total_FN = 0.0

    for timestamp in timestamps:  # for each anomaly moment, compute its f1_score

        truth = truth_df[truth_df["timestamp"] == timestamp]
        true_set = reconstruct_set(timestamp, str(truth.iloc[0][1]).strip())
        if timestamp not in result_df["timestamp"].values:
            data['message'] = "提交的文件缺少timestamp %s 的结果" % timestamp
            return json.dumps(data, ensure_ascii=False)

        result = result_df[result_df["timestamp"] == timestamp]

        if len(result) > 1:  # in case there are more than one results for one single timestamp in result file
            data['message'] = "同一timestamp多次出现"
            return json.dumps(data, ensure_ascii=False)

        pred_set = reconstruct_set(timestamp, str(result.iloc[0]['set']).strip())

        f1_score, TP, FP, FN = compute_f1(true_set, pred_set)
        total_TP += TP
        total_FP += FP
        total_FN += FN
        f1_scores.append(f1_score)
    Precision = 0.0
    Recall = 0.0
    score = 0.0
    if total_TP > 0:
        Precision = total_TP / (total_TP + total_FP)
        Recall = total_TP / (total_TP + total_FN)
    if (Precision + Recall) > 0:
        score = (2 * Precision * Recall) / (Precision + Recall)
    data['result'] = True
    #data['average_fscore'] = round(sum(f1_scores) / len(f1_scores), 2)
    data['data'] = round(score, 4)
    data['message'] = '计算成功'

    return json.dumps(data, ensure_ascii=False)


if __name__ == '__main__':
    _, truth_file, result_file = argv
    print(root_evaluation(truth_file, result_file))
