import binascii
import os
import random
from math import gcd, ceil, log
from hashlib import sha256


# 原始数据变成二进制
def deal_data(data):
    print(f"原始data：\n {data}")
    data_bytes = bytes(data, encoding='ascii')

    data_hex = binascii.hexlify(data_bytes).decode('ascii')
    print(f"十六进制data：\n{data_hex}")

    data_bit = ''.join(format(int(char, 16), '04b') for char in data_hex)
    print(f"二进制data长度：{len(data_bit)}")
    return data_bit


# 系统参数 p, a, b, G, n, h
def generate_args():
    # 14页 椭圆曲线系统参数选取与验证
    # 90页 参照附录A数据
    p = '8542D69E 4C044F18 E8B92435 BF6FF7DE 45728391 5C45517D 722EDB8B 08F1DFC3'.replace(' ', '')
    a = '787968B4 FA32C3FD 2417842E 73BBFEFF 2F3C848B 6831D7E0 EC65228B 3937E498'.replace(' ', '')
    b = '63E4C6D3 B23B0C84 9CF84241 484BFE48 F61D59A5 B16BA06E 6E12D1DA 27C5249A'.replace(' ', '')
    xG = '421DEBD6 1B62EAB6 746434EB C3CC315E 32220B3B ADD50BDC 4C4E6C14 7FEDD43D'.replace(' ', '')
    yG = '0680512B CBB42C07 D47349D2 153B70C4 E5D7FDFC BFA36EA1 A85841B9 E46E09A2'.replace(' ', '')
    n = '8542D69E 4C044F18 E8B92435 BF6FF7DD 29772063 0485628D 5AE74EE7 C32E79B7'.replace(' ', '')
    h = 1
    print("椭圆曲线参数相关参数（十六进制表示）")
    print(f"p: {p} \na: {a} \nb: {b} \nxG: {xG} \nyG: {yG} \nn: {n} \nh: {h}")

    p, a, b, xG, yG, n = int(p, 16), int(a, 16), int(b, 16), int(xG, 16), int(yG, 16), int(n, 16)
    G = (xG, yG)
    args = (p, a, b, G, n, h)

    return args


# 对分母求逆求解分数模运算
def frac_to_int(numerator, denominator, p):
    denominator_inv = pow(denominator, -1, p)  # 求分母的逆元
    return (numerator * denominator_inv) % p


# Q = Q + G
def add_point(Q, G, p, a):
    if G == (0, 0):
        return Q
    if Q == (0, 0):
        return G
    x1, y1, x2, y2 = G[0], G[1], Q[0], Q[1]
    if x1 == x2 and y1 != y2:  # G + (-G) = 0
        return (0, 0)
    if G == Q:
        return double_point(G, p, a)

    lam_bda = frac_to_int(y2 - y1, x2 - x1, p)  # 计算斜率 lambda
    x3 = (lam_bda * lam_bda - x1 - x2) % p
    y3 = (lam_bda * (x1 - x3) - y1) % p

    return (x3, y3)


# Q = 2Q
def double_point(G, p, a):
    if G == (0, 0):
        return (0, 0)
    x1, y1 = G[0], G[1]

    if y1 == 0:  # 切线斜率不存在
        return (0, 0)

    lam_bda = frac_to_int(3 * x1 * x1 + a, 2 * y1, p)
    x3 = (lam_bda * lam_bda - 2 * x1) % p
    y3 = (lam_bda * (x1 - x3) - y1) % p

    return (x3, y3)


# 28页 多倍点运算 采用二进制展开法来实现 Q=kG k是倍数、G是基点、p是模数、a为椭圆曲线参数
def multiple_points(k, G, p, a):
    Q = (0, 0)  # 初始化为无穷远点
    k_bit = bin(k)[2:]
    for bit in k_bit:  # 输入的k为十进制转化为二进制字符串
        Q = double_point(Q, p, a)  # Q = 2Q
        if bit == '1':
            Q = add_point(Q, G, p, a)  # Q = Q + G

    return Q


# 判断是否为无穷远点
def is_infinite_point(point, G):
    if tuple(a + b for a, b in zip(point, G)) == G:
        return True
    else:
        return False


# 15页 密钥对的生成和公钥验证
def generate_B_key(args):
    p, a, b, G, n, h = args

    while True:
        dB = random.randint(1, n - 2)  # 在1 - n-2生成dB
        print(f"私钥d：{dB}")

        PB = multiple_points(dB, G, p, a)  # 多倍点运算
        # 验证
        if not is_infinite_point(PB, G):
            if 0 <= PB[0] <= p - 1 and 0 <= PB[1] <= p - 1:
                if (PB[0] * PB[0] * PB[0] + a * PB[0] + b) % p == (PB[1] * PB[1]) % p:
                    if is_infinite_point(multiple_points(n, PB, p, a), G):
                        print(f"公钥x：{PB[0]} \n公钥y：{PB[1]}")
                        print("选择的公钥PB是有效的")
                        return (dB, PB)


### 一堆子数据转换 ###

# 12页 4.2.5 域-->字节串  4.2.1 整数-->字节串
def domain_to_byte(data):
    q_hex = '8542D69E 4C044F18 E8B92435 BF6FF7DE 45728391 5C45517D 722EDB8B 08F1DFC3'.replace(' ', '')
    q_int = int(q_hex, 16)
    t = ceil(log(q_int, 2))  # 向上取整
    l = ceil(t / 8)

    data_byte = int_to_byte(data, l)
    return data_byte


# 11页 4.2.1 整数-->字节串
def int_to_byte(data, length):
    if data >= 2 ** (8 * length):
        raise ValueError("x must be less than 2^(8k)")
    byte_list = [(data >> (8 * (length - 1 - i))) & 0xFF for i in range(length)]
    return bytes(byte_list)


# 字节转化为bit
def byte_to_bit(data):
    s = ''.join(format(byte, '08b') for byte in data)
    return s


# bit转化为字节
def bit_to_byte(bit_string):
    if len(bit_string) % 8 != 0:
        raise ValueError("比特串长度必须是 8 的倍数")
    return bytes(int(bit_string[i:i + 8], 2) for i in range(0, len(bit_string), 8))


# 字节转化为hex
def byte_to_hex(data):
    h_list = []
    for i in data:
        e = hex(i)[2:].rjust(2, '0')
        h_list.append(e)
    h = ''.join(h_list)
    return h


# 字节转化hex
def hex_to_bytes(hex_data):
    return bytes.fromhex(hex_data)


# 13页 4.2.8 椭圆曲线上的点-->字节串  4.2.5域-->字节  4.2.4 字节-->比特
# #未压缩表示形式
def point_to_bit(data_point):
    # 域-->字节串
    x_byte = domain_to_byte(data_point[0])
    y_byte = domain_to_byte(data_point[1])
    PC = bytes([0x04])
    S = PC + x_byte + y_byte

    # 字节-->比特
    data_bit = byte_to_bit(S)

    return data_bit


# 87页 5.4.3 密钥派生函数KDF
def KDF(Z, k_len):
    v = 256  # sha256
    if k_len >= (2 ** 32 - 1) * v:
        raise ValueError("k_len must be <= (2**32-1) * v")
    count = 0x00000001
    hash_value = []
    if k_len % v == 0:
        l = k_len // v
    else:
        l = k_len // v + 1
    for i in range(l):
        all_bit = Z + bin(count)[2:].zfill(32)
        all_byte = bit_to_byte(all_bit)
        hash_byte = sha256(all_byte).digest()
        hash_bit = byte_to_bit(hash_byte)
        hash_value.append(hash_bit)
        count += 1
    if k_len % v != 0:
        hash_value[-1] = hash_value[-1][:k_len - v * (k_len // v)]
    k = ''.join(hash_value)
    return k


# 字节-->int
def bytes_to_int(byte_data, byteorder='big'):
    return int.from_bytes(byte_data, byteorder)


def byte_to_point(data, l):
    PC = data[0]
    if PC != 4:
        raise Exception("压缩类型错误！！")
    x, y = data[1: l + 1], data[l + 1: 2 * l + 1]
    xP = bytes_to_int(x)
    yP = bytes_to_int(y)
    P = (xP, yP)
    return P


def encrypt_SM2(args, data, PB):
    p, a, b, G, n, h = args
    k_len = len(data)  # 二进制数data长度

    while True:
        # 生成随机数k
        k = random.randint(1, n - 1)
        print(f"A1：选择的随机数k为  {k}")

        C1 = multiple_points(k, G, p, a)
        # 点-->比特
        C1_bit = point_to_bit(C1)
        print(f"A2：生成的C1点为\n{C1} \n转化为bit串为\n{C1_bit}")

        # S=[h]PB
        S = multiple_points(h, PB, p, a)
        if is_infinite_point(S, G):
            raise ValueError("S 是无穷远点")
        print(f"A3：生成的S点（不是无穷远点）为\n{S}")

        # x2 y2 --> 比特串
        x2, y2 = multiple_points(k, PB, p, a)
        x2_bit = byte_to_bit(domain_to_byte(x2))
        y2_bit = byte_to_bit(domain_to_byte(y2))
        print(f"A4：计算（x2，y2）bit串为\n{x2_bit} \n{y2_bit}")

        t = KDF(x2_bit + y2_bit, k_len)
        if int(t, 2) == 0:
            continue
        print(f"A5：KDF计算得到t（不为全0bit串）为\n{t}")

        C2_int = int(data, 2) ^ int(t, 2)
        C2_bit = bin(C2_int)[2:].zfill(len(data))
        print(f"A6：C2为\n{bit_to_byte(C2_bit)}")

        C3_byte = sha256(bit_to_byte((x2_bit + data + y2_bit))).digest()
        print(f"A7：C3 byte：\n {C3_byte}")

        C1_hex = byte_to_hex(bit_to_byte(C1_bit))
        C2_hex = byte_to_hex(bit_to_byte(C2_bit))
        C3_hex = byte_to_hex(C3_byte)
        C_hex = C1_hex + C2_hex + C3_hex
        print(f"A8：C hex：\n{C_hex}")

        return C_hex


# C是hex形式
def decrypt_SM2(args, C, dB):
    p, a, b, G, n, h = args
    t = ceil(log(p, 2))  # 向上取整
    l = ceil(t / 8)  # 字节数

    C1_byte_len = 2 * l + 1
    C1_hex_len = 2 * C1_byte_len
    C_byte = hex_to_bytes(C)
    C1_byte = C_byte[:C1_byte_len]
    # byte-->point
    C_1 = byte_to_point(C1_byte, l)
    # 判断P是否在椭圆曲线上
    if (C_1[0] * C_1[0] * C_1[0] + a * C_1[0] + b) % p != (C_1[1] * C_1[1]) % p:
        raise ValueError("P点不在椭圆曲线上")
    print(f"B1：C1 byte(且C1点在椭圆曲线上):\n{C1_byte}\n")

    # S=[h]C1
    S = multiple_points(h, C_1, p, a)
    if is_infinite_point(S, G):
        raise ValueError("S 是无穷远点")
    print(f"B2：S点计算为：\n{S}")

    # x2 y2 --> 比特串
    x2, y2 = multiple_points(dB, C_1, p, a)
    x2_bit = byte_to_bit(domain_to_byte(x2))
    y2_bit = byte_to_bit(domain_to_byte(y2))
    print(f"B3：计算得到x2、y2为：\n{x2_bit} \n{y2_bit}")

    C3_hex_len = 256 // 4
    C2_hex_len = len(C) - C1_hex_len - C3_hex_len
    k_len = 4 * C2_hex_len
    t = KDF(x2_bit + y2_bit, k_len)
    if int(t, 2) == 0:
        raise ValueError("t为全0比特串")
    print(f"B4：KDF计算得到t（不为全0bit串）为\n{t}")

    C2_hex = C[C1_hex_len:C1_hex_len + C2_hex_len]
    M_int = int(t, 2) ^ int(C2_hex, 16)
    M_bit = bin(M_int)[2:].zfill(len(data))
    print(f"B5：计算得到C2 hex：\n{C2_hex}\n计算得到M bit：\n{M_bit}")

    u_byte = sha256(bit_to_byte((x2_bit + M_bit + y2_bit))).digest()
    u_hex = byte_to_hex(u_byte)
    C3_hex = C[-C3_hex_len:]
    print(f"B6：u hex：\n{u_hex}\n C3 hex：\n{C3_hex}")

    if C3_hex != u_hex:
        raise ValueError("解密失败！！！")
    else:
        print("解密成功！！！")
        M = str(bit_to_byte(M_bit), encoding='ascii')
        print(f"B7：解密消息为：\n{M}")
        return M


if __name__ == '__main__':
    data_path = '实验5测试数据'
    data_index = [0]
    for idx in data_index:
        single_path = os.path.join(data_path, f"{idx + 6}.txt")
        with open(single_path, 'r') as f:
            data = f.readline()

        # 原始数据转化为二进制字符串
        print("第一步：处理数据")
        data = deal_data(data)

        # args = (p, a, b, G, n, h) 10进制整型
        print("\n第二步：生成系统参数")
        args = generate_args()

        print("\n第三步：生成公私钥")
        dB, PB = generate_B_key(args)

        print("\n第四步：公钥数据加密")
        C = encrypt_SM2(args, data, PB)

        print("\n第五步：私钥数据解密与验证")
        M = decrypt_SM2(args, C, dB)
