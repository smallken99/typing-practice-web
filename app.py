from flask import Flask, render_template, request, jsonify
import random
import time
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)

# 倉頡字根映射表（改為中文字根）
CANGJIE_ROOTS = {
    'a': '日', 'b': '月', 'c': '金', 'd': '木', 'e': '水', 
    'f': '火', 'g': '土', 'h': '竹', 'i': '戈', 'j': '十', 
    'k': '大', 'l': '中', 'm': '一', 'n': '弓', 'o': '人', 
    'p': '心', 'q': '手', 'r': '口', 's': '尸', 't': '廿', 
    'u': '山', 'v': '女', 'w': '田', 'x': '難', 'y': '卜', 
    'z': '重'
}

# 中文詞彙庫和模板
CHINESE_NAMES = ["小明", "小紅", "小華", "小剛", "小麗"]
CHINESE_PLACES = ["公園", "學校", "圖書館", "超市", "咖啡店"]
CHINESE_ACTIONS = ["散步", "學習", "看書", "購物", "喝咖啡"]
CHINESE_WEATHER = ["晴朗", "陰天", "下雨", "多雲", "刮風"]
CHINESE_OBJECTS = ["書", "水果", "咖啡", "筆記本", "手機"]
CHINESE_SENTENCE_TEMPLATES = [
    "{name}今天去了{place}，天氣很{weather}。",
    "{name}在{place}{action}，感覺很愉快。",
    "{name}買了一些{object}，準備帶回家。",
    "在{place}，{name}遇到了朋友，一起{action}。",
    "{name}覺得{weather}的日子最適合{action}。"
]

# 英文詞彙庫和模板
ENGLISH_NAMES = ["Tom", "Mary", "John", "Alice", "Bob"]
ENGLISH_PLACES = ["park", "school", "library", "supermarket", "cafe"]
ENGLISH_ACTIONS = ["walking", "studying", "reading", "shopping", "drinking coffee"]
ENGLISH_WEATHER = ["sunny", "cloudy", "rainy", "windy", "foggy"]
ENGLISH_OBJECTS = ["book", "fruit", "coffee", "notebook", "phone"]
ENGLISH_SENTENCE_TEMPLATES = [
    "{name} went to the {place} today, and the weather was {weather}.",
    "{name} is {action} at the {place} and feels very happy.",
    "{name} bought some {object} to take home.",
    "At the {place}, {name} met a friend and they started {action} together.",
    "{name} thinks a {weather} day is perfect for {action}."
]

# 載入倉頡碼表
cangjie_dict = {}
file_path = os.path.join("static", "dime_cangjie.txt")
try:
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    cangjie_dict[parts[1]] = parts[0]
except FileNotFoundError:
    print("找不到 dime_cangjie.txt")

# 設定上傳資料夾和題目元資料檔案
UPLOAD_FOLDER = 'uploads'
QUESTION_METADATA_FILE = 'questions.json'

# 確保上傳資料夾存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_question_metadata():
    """載入題目元資料"""
    try:
        if os.path.exists(QUESTION_METADATA_FILE):
            with open(QUESTION_METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"載入元資料失敗: {e}")
        return {}

def save_question_metadata(metadata):
    """儲存題目元資料"""
    try:
        with open(QUESTION_METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"儲存元資料失敗: {e}")

def convert_to_cangjie_roots(code):
    return ''.join(CANGJIE_ROOTS.get(c.lower(), c) for c in code)

@app.route('/')
def index():
    return render_template('index.html')

 
@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    data = request.json
    try:
        word_count = int(data.get('word_count', 50))
        if word_count <= 0:
            return jsonify({'error': '字數必須為正數'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': '字數必須為有效數字'}), 400

    language = data.get('language', 'chinese')

    if language == 'english':
        NAMES, PLACES, ACTIONS, WEATHER, OBJECTS, SENTENCE_TEMPLATES = (
            ENGLISH_NAMES, ENGLISH_PLACES, ENGLISH_ACTIONS, ENGLISH_WEATHER, ENGLISH_OBJECTS, ENGLISH_SENTENCE_TEMPLATES
        )
    else:
        NAMES, PLACES, ACTIONS, WEATHER, OBJECTS, SENTENCE_TEMPLATES = (
            CHINESE_NAMES, CHINESE_PLACES, CHINESE_ACTIONS, CHINESE_WEATHER, CHINESE_OBJECTS, CHINESE_SENTENCE_TEMPLATES
        )

    questions = []
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
        if len(sentence) > 30:
            sentence = sentence[:30]
        if total_chars + len(sentence) > word_count:
            sentence = sentence[:word_count - total_chars]
        
        questions.append(sentence)
        total_chars += len(sentence)
    
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
                if len(line) > 20:
                    for i in range(0, len(line), 20):
                        questions.append(line[i:i+20])
                else:
                    questions.append(line)
            total_chars = sum(len(q) for q in questions)
            
            # 生成唯一檔案名稱
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}.txt"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # 儲存檔案
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新元資料
            metadata = load_question_metadata()
            display_name = request.form.get('name', file.filename)  # 使用者可指定名稱，預設為檔案名稱
            metadata[unique_id] = {
                'name': display_name,
                'filepath': filepath,
                'total_chars': total_chars,
                'uploaded_at': datetime.now().isoformat()
            }
            save_question_metadata(metadata)
            
            return jsonify({'questions': questions, 'total_chars': total_chars, 'id': unique_id})
        except UnicodeDecodeError:
            return jsonify({'error': '檔案必須為 UTF-8 編碼'}), 400
        except Exception as e:
            return jsonify({'error': f'檔案處理失敗：{str(e)}'}), 500
    else:
        return jsonify({'error': '僅支援 .txt 檔案'}), 400

@app.route('/list_questions', methods=['GET'])
def list_questions():
    metadata = load_question_metadata()
    question_list = [
        {
            'id': key,
            'name': value['name'],
            'total_chars': value['total_chars'],
            'uploaded_at': value['uploaded_at']
        }
        for key, value in metadata.items()
    ]
    return jsonify({'questions': question_list})

@app.route('/load_questions/<question_id>', methods=['GET'])
def load_questions(question_id):
    metadata = load_question_metadata()
    if question_id not in metadata:
        return jsonify({'error': '題目不存在'}), 404
    
    try:
        with open(metadata[question_id]['filepath'], 'r', encoding='utf-8') as f:
            content = f.read()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        questions = []
        for line in lines:
            if len(line) > 20:
                for i in range(0, len(line), 20):
                    questions.append(line[i:i+20])
            else:
                questions.append(line)
        total_chars = sum(len(q) for q in questions)
        return jsonify({'questions': questions, 'total_chars': total_chars, 'id': question_id})
    except Exception as e:
        return jsonify({'error': f'載入題目失敗：{str(e)}'}), 500

@app.route('/delete_questions/<question_id>', methods=['DELETE'])
def delete_questions(question_id):
    metadata = load_question_metadata()
    if question_id not in metadata:
        return jsonify({'error': '題目不存在'}), 404
    
    try:
        # 刪除檔案
        os.remove(metadata[question_id]['filepath'])
        # 更新元資料
        del metadata[question_id]
        save_question_metadata(metadata)
        return jsonify({'message': '題目已刪除'})
    except Exception as e:
        return jsonify({'error': f'刪除失敗：{str(e)}'}), 500

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)