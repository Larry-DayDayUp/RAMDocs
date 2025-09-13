import json

# 要查看的文件名列表
data_files = [
    'RAMDocs_test.jsonl',
    'RAMDocs_test.jsonl_madam_rag_Qwen2-1.5B-Instruct_rounds3.jsonl'
]

def print_simple(file, max_lines=5):
    print(f'===== {file} 前{max_lines}条简要内容 =====')
    try:
        with open(file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                try:
                    data = json.loads(line)
                    # 针对原始测试集
                    if 'question' in data:
                        print(f"Q{i+1}: {data.get('question')}")
                        docs = data.get('documents', [])
                        for j, doc in enumerate(docs[:2]):
                            text = doc.get('text', '')
                            print(f"  doc{j+1}:\n{text}\n")
                        print(f"  gold_answers: {data.get('gold_answers')}")
                        print(f"  wrong_answers: {data.get('wrong_answers')}")
                        # 打印explanation字段（如有）
                        explanation = data.get('explanation')
                        if explanation:
                            print(f"  explanation: {explanation}")
                        print('-'*40)
                    # 针对模型输出
                    elif 'final_aggregation' in data:
                        print(f"Q{i+1} final_aggregation: {data.get('final_aggregation')}")
                    else:
                        print(f"Q{i+1}: {str(data)[:100]}...")
                except Exception as e:
                    print(f'解析第{i+1}行失败: {e}')
    except FileNotFoundError:
        print(f'文件 {file} 未找到')
    print('-'*60)

for file in data_files:
    print_simple(file, max_lines=5)
