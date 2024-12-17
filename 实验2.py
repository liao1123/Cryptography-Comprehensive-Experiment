import math
import os.path
import time


def extended_euclidean(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = extended_euclidean(b % a, a)
        return gcd, y - (b // a) * x, x


def mod_inverse(a, b):
    gcd, x, y = extended_euclidean(a, b)
    return x % b


def judge_prime(list):
    for idx, data in enumerate(list):
        for ii in range(idx + 1, len(list)):
            gcd, _, _ = extended_euclidean(data, list[ii])
            if gcd != 1:
                return True
    return False


def Chinese_Remainder(a_list, m_list):
    # 判断m1 m2 m3是否两两互素
    if judge_prime(m_list):
        print("不能直接利用中国剩余定理")
        return 0
    m = math.prod(m_list)
    print(f"m1 * m2 * m3 = m = {m}")

    M = []
    for idx, data in enumerate(m_list):
        M_i = m // m_list[idx]
        M.append(M_i)
        print(f"M_{idx+1} : {M_i}")

    M_inverse = []
    for idx, (M_i, m_i) in enumerate(zip(M, m_list)):
        M_i_reverse = mod_inverse(M_i, m_i)
        M_inverse.append(M_i_reverse)
        print(f"M_{idx+1}逆元 : {M_i_reverse}")

    x = []
    for idx, (M_i, M_i_reverse, a_i) in enumerate(zip(M, M_inverse, a_list)):
        x_i = (M_i * M_i_reverse * a_i) % m
        x.append(x_i)
        print(f"x_{idx+1} : {x_i}")

    x = sum(x) % m
    print(f"x finally : {x}")
    print(f"x \u2261 {x} \nmod\n {m} ")


data_path = "实验2测试数据"
data_index = [7]
for idx in data_index:
    start_time = time.time()
    print(f"第{idx}个测试数据")
    data_save = []
    save_path = os.path.join(data_path, f"{idx}.txt")
    with open(save_path, "r") as file:
        for data in file:
            data_save.append(int(data.strip()))
    a_list = data_save[:len(data_save) // 2]
    m_list = data_save[len(data_save) // 2:]

    for i, data in enumerate(a_list):
        print(f"a{i + 1} : {data}")
    for i, data in enumerate(m_list):
        print(f"m{i + 1} : {data}")

    Chinese_Remainder(a_list, m_list)
