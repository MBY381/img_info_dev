# 打开文件
with open("top.txt", "r") as f:
    # 读取所有行
    lines = f.readlines()
    num_count = None
    print("?"
          "")
    for i, line in enumerate(lines):
        # 去除行结尾的换行符，并将字符串拆分为数字列表
        nums = line.strip().split()

        if not num_count:
            num_count = len(nums)
        elif num_count != len(nums):
            print(f"第 {i + 1} 行数字数量 {len(nums)} 和第 1 行数字数量 {num_count} 不一致！")

        # 判断是否有重复数字，不包括 -1
        s = set()
        for num in nums:
            if num == "-1":
                continue
            if num in s:
                print(f"第 {i + 1} 行中有重复数字 {num}！")
            else:
                s.add(num)
