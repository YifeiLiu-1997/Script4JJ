from flask import Flask, request, jsonify
import pandas as pd
import json

app = Flask(__name__)


# 读取CSV文件
def load_knowledge_base():
    try:
        # 读取CSV文件
        df = pd.read_csv('1.csv', encoding='utf-8-sig')

        # 创建知识库字典
        knowledge_base = {}

        for _, row in df.iterrows():
            question = str(row['Question']).strip()
            answers = []

            # 收集所有非空的答案列
            for col in df.columns[1:]:  # 从第二列开始
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
                    answers.append(str(row[col]).strip())

            if answers:  # 只保存有答案的问题
                knowledge_base[question] = answers

        return knowledge_base
    except Exception as e:
        print(f"加载知识库失败: {e}")
        return {}


# 加载知识库
knowledge_base = load_knowledge_base()


@app.route('/get_ans', methods=['POST'])
def get_ans():
    try:
        # 获取POST请求中的数据
        data = request.get_json()

        # 检查必要的键是否存在
        if not data or 'name' not in data or 'xword' not in data:
            return jsonify({
                'error': '请求数据格式错误',
                'message': '需要提供name和xword参数'
            }), 400

        name = data.get('name')
        xword = data.get('xword')

        # 根据name的值返回不同的响应
        if name == 'JYX':
            # 在xword中查找匹配的知识库问题
            matched_questions = []

            # 遍历知识库的所有问题
            for question in knowledge_base.keys():
                if question in xword:
                    matched_questions.append(question)

            if not matched_questions:
                return jsonify({
                    'status': 'success',
                    'result': '没有这个答案',
                    'matched_questions': []
                })

            # 处理所有匹配的问题
            results = []
            for question in matched_questions:
                answers = knowledge_base[question]
                if len(answers) == 1:
                    # 单列答案
                    results.append(f"{question}: {answers[0]}")
                else:
                    # 多列答案，用换行符连接
                    answer_text = '\n'.join([f"{i + 1}. {answer}" for i, answer in enumerate(answers)])
                    results.append(f"{question}:\n{answer_text}")

            # 将所有结果用两个换行符分隔
            final_result = '\n\n'.join(results)

            response_data = {
                'status': 'success',
                'result': final_result,
                'matched_count': len(matched_questions),
                'matched_questions': matched_questions
            }

            # 确保返回的是有效的JSON
            response = jsonify(response_data)
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response
        else:
            return jsonify({
                'status': 'error',
                'message': '接口有问题'
            }), 400

    except Exception as e:
        return jsonify({
            'error': '服务器内部错误',
            'message': str(e)
        }), 500


# 添加一个简单的GET测试接口，方便调试
@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'success',
        'message': '服务正常运行',
        'knowledge_base_size': len(knowledge_base)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=True)