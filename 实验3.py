import math
import os
import random


def extended_euclidean(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = extended_euclidean(b % a, a)
        return gcd, y - (b // a) * x, x


def judge_prime(list):
    for idx, data in enumerate(list):
        for ii in range(idx + 1, len(list)):
            gcd, _, _ = extended_euclidean(data, list[ii])
            if gcd != 1:
                return True
    return False


def mod_inverse(a, b):
    gcd, x, y = extended_euclidean(a, b)
    return x % b


def generate_subkey(secret):
    # 选取n个整数，递增关系且两两互素，随机产生整数
    choose_d = []
    weishu = len(str(abs(secret)))
    xiaxian = int(weishu / t)
    d_std = random.randint(pow(10, xiaxian), pow(10, xiaxian + 1))
    choose_d.append(d_std)
    while True:
        # 标志看新增的d是否与原本的互素
        flag = 1
        d = random.randint(pow(10, xiaxian), pow(10, xiaxian + 1))
        if d <= d_std:
            continue
        for idx, data in enumerate(choose_d):
            gcd, _, _ = extended_euclidean(data, d)
            if gcd != 1:
                flag = 0
                break
        if flag == 1:
            choose_d.append(d)
        d_std = d
        if len(choose_d) == n:
            break

    # 计算N M
    N, M = 1, 1
    for idx, data in enumerate(choose_d, start=1):
        if idx <= t:
            N *= data
        if idx >= n - t + 2:
            M *= data

    # 生成子密钥
    sub_key = []
    for idx, data in enumerate(choose_d, start=1):
        k_i = secret % data
        sub_key.append((k_i, data))
    return choose_d, N, M, sub_key


def Chinese_Remainder(a_list, m_list):
    # 判断m1 m2 m3是否两两互素
    if judge_prime(m_list):
        print("不能直接利用中国剩余定理")
        return 0
    m = math.prod(m_list)

    M = []
    for idx, data in enumerate(m_list):
        M_i = m // m_list[idx]
        M.append(M_i)

    M_inverse = []
    for idx, (M_i, m_i) in enumerate(zip(M, m_list)):
        M_i_reverse = mod_inverse(M_i, m_i)
        M_inverse.append(M_i_reverse)

    x = []
    for idx, (M_i, M_i_reverse, a_i) in enumerate(zip(M, M_inverse, a_list)):
        x_i = (M_i * M_i_reverse * a_i) % m
        x.append(x_i)

    x = sum(x) % m
    return x


def revert_key(sub_key, choose_num):
    # 随机选t个子密钥
    choose_sub_key = random.sample(sub_key, choose_num)

    a_list, m_list = [], []
    for idx, data in enumerate(choose_sub_key):
        a_list.append(data[0])
        m_list.append(data[1])
    revert = Chinese_Remainder(a_list, m_list)
    return revert


print("基于中国剩余定理的秘密共享方案")
t = int(input("请输入t值\n"))
n = int(input("请输入n值\n"))
print("方案参数 t : {t} n : {n}".format(t=t, n=n))

data_path = "实验3测试数据"
data = [1]
for idx in data:
    single_data_path = os.path.join(data_path, f'secret{idx}.txt')
    with open(single_data_path, 'r') as f:
        secret = f.readline()
        secret = int(secret)
        print(f"读取秘密{idx} : {secret}")
    while True:
        choose_d, N, M, sub_key = generate_subkey(secret)
        if N > secret > M:
            for idx, d in enumerate(choose_d):
                print(f"d{idx + 1} : {d}")
            print(f"N:{N}")
            print(f"M:{M}")
            # print(f"子密钥 : {sub_key}")
            break
        else:
            print("选择N M不合适，重新选择中……")
    for num in range(1, t+2):
        revert_t = revert_key(sub_key, num)
        print(f"当t={num}时, 恢复出的秘密为 : {revert_t}")
        if revert_t == secret:
            print(f"当t={num}, 时恢复秘密成功！")
        else:
            print(f"当t={num}, 时恢复秘密失败！")
