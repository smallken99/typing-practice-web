from flask import Flask, render_template, request, jsonify
import random
import time

app = Flask(__name__)

# 倉頡字根映射表
CANGJIE_ROOTS = {
    'a': '日', 'b': '月', 'c': '金', 'd': '木', 'e': '水', 
    'f': '火', 'g': '土', 'h': '竹', 'i': '戈', 'j': '十', 
    'k': '大', 'l': '中', 'm': '一', 'n': '弓', 'o': '人', 
    'p': '心', 'q': '手', 'r': '口', 's': '尸', 't': '廿', 
    'u': '山', 'v': '女', 'w': '田', 'x': '難', 'y': '卜', 
    'z': '重'
}

# 詞彙庫和模板
NAMES = ["小明", "小紅", "小華", "小剛", "小麗"]
PLACES = ["公園", "學校", "圖書館", "超市", "咖啡店"]
ACTIONS = ["散步", "學習", "看書", "購物", "喝咖啡"]
WEATHER = ["晴朗", "陰天", "下雨", "多雲", "刮風"]
OBJECTS = ["書", "水果", "咖啡", "筆記本", "手機"]
SENTENCE_TEMPLATES = [
    "{name}今天去了{place}，天氣很{weather}。",
    "{name}在{place}{action}，感覺很愉快。",
    "{name}買了一些{object}，準備帶回家。",
    "在{place}，{name}遇到了朋友，一起{action}。",
    "{name}覺得{weather}的日子最適合{action}。"
]

# 載入倉頡碼表
cangjie_dict = {}
try:
    with open("dime_cangjie.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    cangjie_dict[parts[1]] = parts[0]
except FileNotFoundError:
    print("找不到 dime_cangjie.txt")

def convert_to_cangjie_roots(code):
    return ''.join(CANGJIE_ROOTS.get(c.lower(), c) for c in code)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    word_count = int(request.json.get('word_count', 50))
    questions = []
    current_text = ""
    total_chars = 0
    
    while total_chars < word_count:
        template = random.choice(SENTENCE_TEMPLATES)
        sentence = template.format(
            name=random.choice(NAMES),
            place=random.choice(PLACES),
            action=random.choice(ACTIONS),
            weather=random.choice(WEATHER),
            object=random.choice(OBJECTS)
        )
        if total_chars + len(sentence) > word_count:
            sentence = sentence[:word_count - total_chars]
        if len(current_text) + len(sentence) > 30:
            questions.append(current_text)
            current_text = sentence
        else:
            current_text += sentence
        total_chars += len(sentence)
    
    if current_text:
        questions.append(current_text)
    
    return jsonify({'questions': questions, 'total_chars': total_chars})

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '未選擇檔案'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未選擇檔案'}), 400
    
    if file and file.filename.endswith('.txt'):
        try:
            content = file.read().decode('utf-8')
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            questions = []
            for line in lines:
                if len(line) > 30:
                    # 若單行超過 30 字，分段處理
                    for i in range(0, len(line), 30):
                        questions.append(line[i:i+30])
                else:
                    questions.append(line)
            total_chars = sum(len(q) for q in questions)
            return jsonify({'questions': questions, 'total_chars': total_chars})
        except Exception as e:
            return jsonify({'error': f'檔案處理失敗：{str(e)}'}), 500
    else:
        return jsonify({'error': '僅支援 .txt 檔案'}), 400

@app.route('/get_cangjie', methods=['POST'])
def get_cangjie():
    char = request.json.get('char')
    english_code = cangjie_dict.get(char, "未知的倉頡碼")
    if english_code != "未知的倉頡碼":
        cangjie_code = convert_to_cangjie_roots(english_code)
    else:
        cangjie_code = english_code
    return jsonify({'char': char, 'cangjie': cangjie_code})

if __name__ == '__main__':
    app.run(debug=True)