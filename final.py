"""
作者：srxh
contact: qq2326378712
2020年6月

思路：
1、对文档jieba分词成列表，去掉停用词，再整理成集合形式
2、对集合中每一个元素进行检索，整理出字典类型的倒排记录表
3、将含有位置信息的倒排记录表转为无位置信息的，并对其进行布尔查询
4、对含有位置信息的倒排记录表 短语查询

倒排记录表 数据的结构  dp为带位置信息的倒排记录表
dp =
{   # 此处 1, 2, 5, 6 代表 “北京” 这个词在第几个个文档里出现过
    # 此处 7, 9, 1256 等四个列表表示这个词在对应的文档中的倒排记录表

    "北京":{
                1: [7, 9, 1256],
                2: [56, 89, 784],
                5: [略],
                6: [略],
            },
    "南京":{
                1: [3, 5],
                5: [5, 9],
            }
}

"""
import os
import jieba
import pprint


doc_path = r".\doc2"
stopwords_file = "./停用词标点.txt"
dp = dict()  # 倒排记录表
all_words = []  # 不重复的所有词项

def get_all_file(path):
    paths = os.listdir(path) # 列出指定路径下的所有目录和文件
    return paths

def rm_stop_words(after_jieba):#去掉停用词以及标点符号，传出一个去掉之后的列表
    # 去除停用词标点等
    stop_f = open(stopwords_file, "r", encoding='utf-8')
    stop_words = list()
    for line in stop_f.readlines():
        line = line.strip()
        if not len(line):
            continue
        stop_words.append(line)
    stop_f.close
    stop_words.extend(["\n", "\t", "\xa0", " "])
    after_rm_stop = [x for x in after_jieba if x not in stop_words]  # 使用去除停用词后的变量进行计算
    return after_rm_stop


def jieba_cut(path):#传入的参数是 文件地址 ，传出的参数是jieba分词完成后的词项列表
    str_all = open(path, encoding='utf-8').read()#.replace("\t", "").replace("\n", "").replace("\xa0", "")
    after_jieba = jieba.lcut(str_all, cut_all=False)
    after_jieba = [i for i in after_jieba if not i.isnumeric()]
    #print(after_jieba)
    return after_jieba


def rm_redundency(after_rm_stop):  # 删除冗余词项，传入的参数是删除停用词后的 after_rm_stop列表， 传出的参数是 after_rm_redundency 列表类型
    after_rm_redundency = list(set(after_rm_stop))
    #print(after_rm_redundency)
    return after_rm_redundency

def bool_retreive(dp):# 传入的参数是倒排记录表，打印布尔检索的结果。
    # for word in list(dp.keys()):
    #     dp_rm_loc[word] = list(dp[word].keys()) # 下面的生成器写法是这两句的高级写法， 目的是将包含位置信息的倒排记录表转变为不包含位置信息的倒排记录表
    dp_rm_loc ={word:list(dp[word].keys()) for word in list(dp.keys())}
    print("无位置信息的倒排记录表如下：")
    print(dp_rm_loc)
    menuver = 'or not'  # 布尔检索的操作
    input1 = "预计"
    input2 = "风险"
    input1 = input("请输入短语1")
    input2 = input("请输入短语2")
    menuver = input("请输入指令")

    print("输入词项无位置信息的倒排记录表如下：：")
    print(input1, dp_rm_loc[input1])
    print(input2, dp_rm_loc[input2])
    print("'{}' {} '{}'  布尔检索结果如下：".format(input1,menuver,input2))
    if menuver == 'and':
        ans = [doc_index for doc_index in dp_rm_loc[input1] if doc_index in dp_rm_loc[input2]]
        print(ans)
    if menuver == 'or':
        ans = list(set(dp_rm_loc[input1] + dp_rm_loc[input2]))  # 都统一为list
        print(ans)
    if menuver == 'and not':
        ans = [doc_index for doc_index in dp_rm_loc[input1] if doc_index not in dp_rm_loc[input2]]
        print(ans)
    if menuver == 'or not':
        ans = []
        for i in range(len(get_all_file(doc_path))):
            if i in dp_rm_loc[input1] or i not in dp_rm_loc[input2]:
                ans.append(i)
        #  除去第二个

        print(ans)


def duanyu_find(dp):  # 这个函数是短语查询的 ， 传入的参数是倒排记录表，打印短语查询的结果
    duanyu = "航空公司面对疫情"
    #duanyu = "票务部门负责人徐女士"
    duanyu = input("请输入要查询的词项")


    after_jieba = [i for i in jieba.lcut(duanyu, cut_all=False) if i in list(dp.keys())]  # 去掉停用词
    # print(after_jieba)
    # # 思路：先找词项共同存在的文档, 多个列表的合并，合并为一个集合
    # for word in after_jieba:
    #     print(word, dp[word])
    """集合里面的数字代表词项对应的 在第几篇文档出现过
    航空公司 {4, 5, 99}
    面对 {4, 88, 99, 101}
    疫情 {4, 99, 8989}
    
    合并完后：(意为所有的词都在这两篇里出现过)
    a = {4, 99}
    """
    a = set(list(dp[after_jieba[0]].keys())) #给a赋初值，某一个词项的 对应出现的 文档的列表转集合  例如 航空公司 a = {1,2,3}, 在1，2,3三篇文档中出现过

    for word in after_jieba:  # 合并所有词项对应的列表，得到一个总的，例如 三个 词项 都在 a（最终）的集合中出现过
        a = a.intersection(list(dp[word].keys()))


    # 再对每一篇文档进行检索 # 在共同存在的文档中再继续找
    is_retrieve = False
    for doc_index in a:
        for i in dp[after_jieba[0]][doc_index]:  #遍历 航空公司这个词在第 doc_index 篇的倒排记录表
            # p = dp[after_jieba[0]][doc_index][i] #p为指针
            p = i
            is_in = True
            for word in after_jieba[1:]:
                if p+1 not in dp[word][doc_index]:
                    is_in = False
                    break  #没能在这篇文档里一起出现，pass
                p+=1

            if is_in == True:
                is_retrieve = True
                print("在第{}篇文档里查询到短语，词项位置为{}".format(doc_index, p-len(after_jieba)+1))
    if is_retrieve == False:
        print("短语查询未找到结果！")

def main():#主函数，负责调度算法的实现
    paths = [os.path.join(doc_path, i) for i in get_all_file(doc_path)]
    for i in range(len(paths)):
        after_jieba = jieba_cut(paths[i])  # jieba分词
        after_rm_stop = rm_stop_words(after_jieba)  # 删除停用词以及标点符号 *** 记录了包含词项顺序的这篇文档的词项情况 ***
        after_rm_redundency = rm_redundency(after_rm_stop)

        for word in after_rm_redundency:
            if word not in list(dp.keys()):  # 补充倒排记录表的词项，将原来没有的词项添加进来
                dp[word] = dict()
            each_word_in_doc = [index for (index, value) in enumerate(after_rm_stop) if value == word]  # 统计得到这个词项在这篇文章里的倒排记录表
            dp[word][i] = each_word_in_doc  #将 word 词项在 i 这篇文档下面的dp记录表赋值

    print("****************************          欢迎来到信息检索系统         *********************************")
    tem1 = input("倒排记录表较大，是否输出 n/y :")
    if tem1 == "y":
        print("倒排记录表如下：")
        pprint.pprint(dp)
    while 1:
        instruction = input("布尔检索请按下1，短语查询请按2: ")
        if instruction == "1":
            bool_retreive(dp)
        else:
            duanyu_find(dp)




if __name__ == '__main__':
    main()