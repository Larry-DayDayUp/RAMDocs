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
                        # 打印前2个document的text字段摘要
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
                        question = ""
                        # 尝试从原始测试集找对应问题
                        try:
                            with open(data_files[0], 'r', encoding='utf-8') as test_file:
                                for j, test_line in enumerate(test_file):
                                    if j == i:  # 相同索引
                                        test_data = json.loads(test_line)
                                        question = test_data.get('question', '')
                                        break
                        except Exception:
                            pass
                            
                        print(f"Q{i+1}: {question}")
                        # 显示round1的answers和explanations
                        if 'round1' in data:
                            print("  Round 1 answers:")
                            for ans in data['round1'].get('answers', []):
                                print(f"    - {ans}")
                            print("  Round 1 explanations:")
                            for exp in data['round1'].get('explanations', []):
                                print(f"    - {exp[:100]}..." if len(exp) > 100 else f"    - {exp}")
                        
                        # 显示round2的answers和explanations
                        if 'round2' in data:
                            print("  Round 2 answers:")
                            for ans in data['round2'].get('answers', []):
                                print(f"    - {ans}")
                            print("  Round 2 explanations:")
                            for exp in data['round2'].get('explanations', []):
                                print(f"    - {exp[:100]}..." if len(exp) > 100 else f"    - {exp}")
                        
                        # 显示round3的answers和explanations（如有）
                        if 'round3' in data:
                            print("  Round 3 answers:")
                            for ans in data['round3'].get('answers', []):
                                print(f"    - {ans}")
                            print("  Round 3 explanations:")
                            for exp in data['round3'].get('explanations', []):
                                print(f"    - {exp[:100]}..." if len(exp) > 100 else f"    - {exp}")
                        
                        # 显示最终聚合结果
                        print(f"  Final Aggregation: {data.get('final_aggregation')}")
                        print('-'*40)
                    else:
                        print(f"Q{i+1}: {str(data)[:100]}...")
                except Exception as e:
                    print(f'解析第{i+1}行失败: {e}')
    except FileNotFoundError:
        print(f'文件 {file} 未找到')
    print('-'*60)

for file in data_files:
    print_simple(file, max_lines=5)