import os
import random
import math
import sympy

def extended_euclidean(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = extended_euclidean(b % a, a)
        return gcd, y - (b // a) * x, x

def mod_inverse(a, b):
    gcd, x, y = extended_euclidean(a, b)
    return x % b

def mod_exp(a, b, c):
    result = 1
    base = a
    while b > 0:
        if b % 2 == 1:
            result = (result * base) % c
        b //= 2
        base = (base * base) % c
    return result


def fermat_primality_test(n, k=5):
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False

    for _ in range(k):
        a = random.randint(2, n - 2)
        if extended_euclidean(a, n)[0] != 1:
            return False
        else:
            if mod_exp(a, n - 1, n) != 1:
                return False
    return True

def generate_p_q():
    # 生成一个强素数p=2q+1
    while True:
        q = random.randint(pow(10, 150), pow(10, 150 + 1))
        if fermat_primality_test(q) and fermat_primality_test(2 * q + 1):
            p = 2 * q + 1
            print(f"找到p：{p}")
            return p, q

def generate_p_q():
    while True:
        q = sympy.randprime(pow(10, 150), pow(10, 150 + 1))
        if sympy.isprime(q):
            p = 2 * q + 1
            if sympy.isprime(p):
                print(f"选择的p为：{p}")
                return p, q


def found_primitive_root(p, q):
    # p=2q+1的素数，fai p为2q，2q的素因子为2，q
    # 确保g和p互素
    for g in range(2, p):
        if extended_euclidean(g, p)[0] == 1 and mod_exp(g, 2, p) != 1 and mod_exp(g, q, p) != 1:
            print(f"找到的原根g为：{g}")
            return g

def encrypt_data(data, p, g, g_a):
    # 随机生成k
    while True:
        k = random.randint(1, p-2)
        if extended_euclidean(k, p-1)[0] == 1:
            print(f"选择的k为：{k}")
            break

    # C1 C2
    C_1 = mod_exp(g, k, p)
    C_2 = (data * mod_exp(g_a, k, p)) % p

    print(f"C_1 ：{C_1}")
    print(f"C_2 ：{C_2}")
    return C_1, C_2

def decrypt_data(C_1, C_2, p, a):
    V = mod_exp(C_1, a, p)
    v_inverse = mod_inverse(V, p)
    mess = C_2 * v_inverse % p
    return mess


data_path = '实验4测试数据'
data_index = [0]
for idx in data_index:
    single_path = os.path.join(data_path, f"secret{idx}.txt")
    with open(single_path, 'r') as f:
        data = f.readline()
        print(f"读取到的整数位数：{len(data)}")
        data = int(data)
        print(f"读取到的data为：{data}")
    p, q = generate_p_q()

    # 求p的原根g
    g = found_primitive_root(p, q)

    # 产生私钥a，范围为1 - p-1不包括1和p-1
    a = random.randint(2, p-2)
    g_a = mod_exp(g, a, p)
    print(f"g的a次幂为：{g_a}")

    C_1, C_2 = encrypt_data(data, p, g, g_a)
    mess = decrypt_data(C_1, C_2, p, a)

    if mess == data:
        print("加解密结果一致")
    else:
        print("错误！！！")
