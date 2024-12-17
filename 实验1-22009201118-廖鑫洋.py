import os.path
import random
import time

random.seed(2024)


def extended_euclidean(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = extended_euclidean(b % a, a)
        return gcd, y - (b // a) * x, x


def mod_exp(a, b, c):
    result = 1
    base = a
    while b > 0:
        if b % 2 == 1:
            result = (result * base) % c
        b //= 2
        base = (base * base) % c
    return result


K = 5

data_path = "实验1测试数据"
data_index = [1, 3]
data = 0
for idx in data_index:
    start_time = time.time()
    save_path = os.path.join(data_path, f"{idx}.txt")
    with open(save_path, 'r') as file:
        data = file.readline()
        data = int(data)
        print(f"第{idx}个测试数据: {data}")
    for idx_k in range(K + 1):
        a = random.randint(2, data - 2)  # 包含2和m-2
        gcd, x, y = extended_euclidean(a, data)
        if gcd != 1:
            print(f"第{idx}个数据为合数")
        else:
            # 快速模指数算法 底数 指数 模数
            result = mod_exp(a, data - 1, data)
            if result != 1:
                print(f"第{idx}个数据为合数")
            else:
                print(f"第{idx}个数据为素数的概率为{1 - (1 / 2) ** (idx_k + 1)}")
            continue
    all_time = time.time() - start_time
    print(f"spend time : {all_time}")