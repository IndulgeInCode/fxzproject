# -*- coding: UTF-8 -*-

from gensim.models import Word2Vec
import dbConnect
import sys  # 提供了许多函数和变量来处理 Python 运行时环境的不同部分.
import jieba
import numpy as np
import re
import matplotlib.pyplot as plt
import hierarchicalAttention as hAT

reload(sys)
sys.setdefaultencoding('utf-8')

# 正则过滤表达式
r = "（|）|；|、|！|，|。|\*|？|~|\<|\>|\s+"
maxSeqLength = 250
minSeqLength = 100
EMBEDDING_DIM = 10
LONG_TRAINTYPE = 3
LONG_TESTTYPE = 2
TRAINTYPE = 1
TESTTYPE = 0
BUCKET_LEN = 4

def buildModel():
    # 所有词集合，包括重复词
    # allSentences = []

    data = dbConnect.getData(begin=0,end=22000)

    sentences = []
    for x in data:
        line = re.sub(r,'', str(x[1]))
        se_list = jieba.cut(line, cut_all = True)
        result = list(se_list)
        # allSentences.extend(result)
        sentences.append(result)

    # min_count指定了需要训练词语的最小出现次数，默认为5
    # size指定了训练时词向量维度，默认为100
    # worker指定了完成训练过程的线程数，默认为1不使用多线程。只有注意安装Cython的前提下该参数设置才有意义
    model = Word2Vec(sentences, min_count = 1, size = EMBEDDING_DIM)

    # 保存模型
    model.save("word2vecModel/word2vecModel")



# 将句子变成向量形式
def getTrainSenteceVec(type):
    if type == TRAINTYPE:
        data = dbConnect.getData(begin = 0, end = 8000)
    elif type ==  TESTTYPE:
        data = dbConnect.getData(begin=8000, end=7000)

    return getVec(data)

#将获取长数据
def getLongRecord(type):
    if type == TRAINTYPE:
        longData = dbConnect.getData(begin=0, end=8000)
    elif type == TESTTYPE:
        longData = dbConnect.getData(begin=6000, end=7000)

    return getSplitVec(longData)



def getVec(data):
    model = Word2Vec.load('word2vecModel/word2vecModel')
    # print (model[u'罗技'])
    x = []
    y = []
    seq_length = []

    # 遍历每条数据，并转换为向量形式
    for row in data:
        sentenVec = np.zeros([maxSeqLength, EMBEDDING_DIM], dtype='float32')
        sentence = row[1]
        sentence = re.sub(r, '', str(sentence))
        se_list = jieba.cut(sentence)

        count = 0
        for out in se_list:
            if (count < maxSeqLength and out in model):
                sentenVec[count] = model[out]
                count += 1
        seq_length.append(count)
        x.append(sentenVec)

        if(row[3] > 2):
            y.append(1)
        else :
            y.append(0)

    return np.array(x, dtype=np.float32), np.array(y, dtype=np.float32), np.array(seq_length, dtype=np.int32)

def getSplitVec(data):
    model = Word2Vec.load('word2vecModel/word2vecModel')
    # print (model[u'罗技'])
    x = []
    y = []
    seq_length = []

    # 遍历每条数据，并转换为向量形式
    for row in data:
        sentenVec = np.zeros([minSeqLength, EMBEDDING_DIM], dtype='float32')

        sen_cut = []
        sentence = row[1]
        #将一个句子分成bucket份
        sentence = hAT.splitSentence(sentence)
        for i in range(len(sentence)):
            cut = re.sub(r, '', str(sentence[i]))
            sen_cut.append(jieba.cut(cut))

        #x 维度为[size, bucket, sentence, dimention]
        for bucket_number in range(len(sen_cut)):
            count = 0
            for out in sen_cut[bucket_number]:
                if (count < minSeqLength and out in model):
                    sentenVec[count] = model[out]
                    count += 1
                    seq_length.append(count)

            if(count < minSeqLength):
                for i in range(minSeqLength - count):
                    seq_length.append(0)
            x.append(sentenVec)

        if(row[3] > 2):
            y.append(1)
        else :
            y.append(0)
    return np.array(x, dtype=np.float32), np.array(y, dtype=np.float32), np.array(seq_length, dtype=np.int32)

def getContentStatistic():
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(20, 10))
    x = range(500)
    y = dbConnect.getLengthStatistic()
    plt.plot(x, y, 'k-', mec='k', label=u'length', lw=2)

    plt.grid(True, ls='--')
    plt.legend(loc='upper right')
    plt.title('Content length')
    plt.show()




if __name__ == '__main__':
    # getContentStatistic()
    buildModel()
    # result = getTrainSenteceVec()
    # print result[0]
