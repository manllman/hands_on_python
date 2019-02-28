from PIL import Image
import argparse


def arg_parse():
    '''
    构建命令行输入参数处理实例
    增加namesapce[file,-o,--width,--height]
    分别为输入输出文件，输出字符画的宽和高

    '''
    parse = argparse.ArgumentParser()
    parse.add_argument('file')  # 输入文件
    parse.add_argument("-o", "--output")  # 输出文件
    parse.add_argument('--width', type=int, default=80)  # 输出字符画宽度
    parse.add_argument('--height', type=int, default=80)  # 输出字符画高度

    return parse.parse_args()  # 返回解析后的参数（namespace）


# 输入文件路径
IMG = arg_parse().file

# 字符画宽度
WIDTH = arg_parse().width

# 字符画的高度
HEIGHT = arg_parse().height

# 字符画输出路径
OUTPUT = arg_parse().output

# 定义以后要用到的转码字符集,list()函数将字符串转换成list
# 反过来需要用''.join(list)

ascii_char = list(
    "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")


def rgb2char(r, g, b, alpha=256):
    if alpha == 0:
        return " "
    # 获取字符集长度
    length = len(ascii_char)

    # 将RGB值转换成灰度值，范围是0-255
    # 以下是经验公式，非精度转换
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

    # 灰度值范围为0-255，而字符集只有70
    # 需要处理才能映射到指定的字符上
    unit = (256.0 + 1) / length

    # 返回灰度值对应的字符
    return ascii_char[int(gray / unit)]


if __name__ == '__main__':
    # PIL处理图片
    # 输入的是图片路径.lazyopen()
    im = Image.open(IMG)
    '''
	Image.NEAREST:低质量
	Image.BILINEAR:双线性
	Image.BICUBIC:三次样条插值
	Image.ANTIALIAS:高质量
	'''
    im = im.resize((WIDTH, HEIGHT), Image.NEAREST)

    # 初始化输出字符串
    text = ""

    # 遍历图片每一行
    for i in range(HEIGHT):
        for j in range(WIDTH):
            # 将（j,i)坐标的RGB像素转换成字符后添加到text
            # *im.getpixel((j,i)) ,返回rgb和alpha值，*元组作为参数传递给函数
            text += rgb2char(*im.getpixel((j, i)))
        text += '\n'

    if OUTPUT:
        with open(OUTPUT, 'w') as f:
            f.write(text)
    else:
        with open("output.txt", 'w') as f:
            f.write(text)
