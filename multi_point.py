def xor_binary(data, t):
    if len(data) != len(t):
        raise ValueError("Input binary strings must have the same length")

    # 按位异或
    C2_int = int(data, 2) ^ int(t, 2)

    # 确保结果的长度与输入相同
    C2_bit = bin(C2_int)[2:]  # 填充到原始长度
    return C2_bit


# 示例
data = "1" * 712  # 712 位全 1
t = "0" * 712  # 712 位全 0
result = xor_binary(data, t)
print(f"Result length: {len(result)}")  # 应该是 712
print(f"Result: {result}")
