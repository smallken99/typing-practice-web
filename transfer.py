# 定義倉頡字根與英文字母的對應關係
cangjie_roots = {
    'a': '日', 'b': '月', 'c': '金', 'd': '木', 'e': '水', 
    'f': '火', 'g': '土', 'h': '竹', 'i': '戈', 'j': '十', 
    'k': '大', 'l': '中', 'm': '一', 'n': '弓', 'o': '人', 
    'p': '心', 'q': '手', 'r': '口', 's': '尸', 't': '廿', 
    'u': '山', 'v': '女', 'w': '田', 'x': '難', 'y': '卜', 
    'z': '重'
}

def convert_cangjie_line(line):
    # 分割每一行的字母碼和中文字符
    parts = line.strip().split()
    if len(parts) != 2:
        return None  # 如果格式不正確，跳過這一行
    code, char = parts[0], parts[1]
    
    # 將字母碼轉換為字根名稱
    root_names = ''.join(cangjie_roots.get(letter, letter) for letter in code)
    # 返回新格式：字符,字根
    return f"{char},{root_names}"

def process_file(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            for line in infile:
                # 跳過空行或非字根定義行
                if not line.strip() or line.startswith('%'):
                    continue
                converted = convert_cangjie_line(line)
                if converted:
                    outfile.write(converted + '\n')
        print(f"轉換完成！結果已保存到 {output_file}")
    except FileNotFoundError:
        print(f"錯誤：找不到文件 {input_file}")
    except Exception as e:
        print(f"發生錯誤：{e}")

# 指定輸入和輸出文件
input_filename = 'dime_cangjie.txt'
output_filename = 'converted_cangjie.txt'

# 執行轉換
process_file(input_filename, output_filename)