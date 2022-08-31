# Requirements
见requirements.txt

# Datasets
达观数据提供

# How to run

1. 数据预处理

先运行pre_data.py
把datasets\CCL2022\data中生成的train.py按4：1划分为训练集train.py和验证集dev.py
运行pre_cascading.py

2. Train/Dev/Test:
运行下面的命令

```
python -u main.py --output_model_path ./models_save/model.bin --do_train True --do_eval True --do_test True 
```
或在``/utils/params.py``中进行更改
使用预训练模型为``chinese-bert-wwm-ext`` ，可在huggingface在线下载到 plm文件夹中

3. 后处理将预测结果输出为原三元组形式：
运行afterrun.py
结果输出在results.json文件中




# Citation
模型在CASEE基础上修改

