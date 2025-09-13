import json
import os
import sys

# 要查看的文件名列表
data_files = [
    'RAMDocs_test.jsonl',
    'RAMDocs_test.jsonl_madam_rag_Qwen2-1.5B-Instruct_rounds3.jsonl'
]

def generate_html(max_items=10):
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>RAMDocs Results Viewer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f7f7f7;
                line-height: 1.6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1, h2, h3 {
                color: #333;
            }
            .item {
                background: white;
                margin-bottom: 20px;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .question {
                font-weight: bold;
                font-size: 18px;
                color: #2c3e50;
                margin-bottom: 10px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .question:hover {
                background-color: #f0f0f0;
            }
            .question:after {
                content: '\\25BC';
                font-size: 12px;
                color: #666;
            }
            .question.collapsed:after {
                content: '\\25B6';
            }
            .document {
                background: #f9f9f9;
                padding: 10px;
                margin: 10px 0;
                border-left: 3px solid #3498db;
                white-space: pre-wrap;
            }
            .answers {
                margin: 10px 0;
            }
            .gold {
                color: #27ae60;
                font-weight: bold;
            }
            .wrong {
                color: #e74c3c;
                text-decoration: line-through;
            }
            .round {
                border-left: 3px solid #9b59b6;
                padding: 5px 10px;
                margin: 10px 0;
            }
            .answer-item {
                margin: 5px 0;
                padding: 5px;
                background-color: #f9f9f9;
            }
            .explanation {
                font-style: italic;
                color: #666;
                padding: 5px;
                margin: 5px 0;
                background-color: #f5f5f5;
                border-left: 2px solid #ccc;
            }
            .final {
                background: #e8f4f8;
                padding: 10px;
                margin-top: 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            .collapsible-content {
                display: block;
                overflow: hidden;
            }
            .collapsible-content.collapsed {
                display: none;
            }
            .section {
                margin-bottom: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                overflow: hidden;
            }
            .section-header {
                background-color: #f0f0f0;
                padding: 10px;
                cursor: pointer;
                font-weight: bold;
                display: flex;
                justify-content: space-between;
            }
            .section-header:hover {
                background-color: #e0e0e0;
            }
            .section-header:after {
                content: '\\25BC';
                font-size: 12px;
            }
            .section-header.collapsed:after {
                content: '\\25B6';
            }
            .section-content {
                padding: 10px;
                background-color: white;
            }
            .section-content.collapsed {
                display: none;
            }
            .comparison {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }
            .column {
                flex: 1;
                padding: 15px;
                background: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .column h3 {
                margin-top: 0;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }
            .column-title {
                background-color: #3498db;
                color: white;
                padding: 10px;
                margin: -15px -15px 15px -15px;
                border-radius: 5px 5px 0 0;
            }
            .expand-all {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                margin: 10px 0;
                cursor: pointer;
            }
            .expand-all:hover {
                background-color: #2980b9;
            }
            .document-type {
                display: inline-block;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 12px;
                margin-right: 5px;
            }
            .document-type.correct {
                background-color: #d4edda;
                color: #155724;
            }
            .document-type.misinfo {
                background-color: #f8d7da;
                color: #721c24;
            }
            .document-type.noise {
                background-color: #fff3cd;
                color: #856404;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>RAMDocs Results Viewer</h1>
            <button class="expand-all" onclick="toggleAll()">展开/折叠全部</button>
            
            <div id="items-container">
    """
    
    # 读取原始测试数据
    test_data = []
    try:
        with open(data_files[0], 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_items:
                    break
                try:
                    test_data.append(json.loads(line))
                except Exception as e:
                    print(f"Error parsing line {i+1}: {e}")
    except FileNotFoundError:
        print(f"File {data_files[0]} not found")
    
    # 读取模型输出数据
    model_results = []
    try:
        with open(data_files[1], 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_items:
                    break
                try:
                    model_results.append(json.loads(line))
                except Exception as e:
                    print(f"Error parsing line {i+1}: {e}")
    except FileNotFoundError:
        print(f"File {data_files[1]} not found")
    
    # 为每个问题创建并排显示的原始数据和模型结果
    for i in range(min(len(test_data), len(model_results))):
        test_item = test_data[i]
        model_item = model_results[i]
        
        question = test_item.get('question', '')
        
        html_content += f"""
        <div class="item">
            <div class="question" onclick="toggleCollapsible(this)">
                Q{i+1}: {question}
            </div>
            <div class="collapsible-content">
                <div class="comparison">
                    <!-- 原始测试数据 -->
                    <div class="column">
                        <div class="column-title">原始测试数据</div>
        """
        
        # 添加文档
        docs = test_item.get('documents', [])
        for j, doc in enumerate(docs):
            text = doc.get('text', '').replace('\n', '<br>')
            doc_type = doc.get('type', 'unknown')
            type_class = "correct" if doc_type == "correct" else "misinfo" if doc_type == "misinfo" else "noise"
            
            html_content += f"""
            <div class="section">
                <div class="section-header" onclick="toggleSection(this)">
                    Document {j+1} <span class="document-type {type_class}">{doc_type}</span>
                </div>
                <div class="section-content">
                    {text}
                </div>
            </div>
            """
        
        # 添加答案
        gold_answers = test_item.get('gold_answers', [])
        wrong_answers = test_item.get('wrong_answers', [])
        
        html_content += """
                        <div class="answers">
                            <strong>Gold Answers:</strong> 
        """
        for ans in gold_answers:
            html_content += f'<span class="gold">{ans}</span>, '
        html_content = html_content.rstrip(', ') + """
                            <br><strong>Wrong Answers:</strong> 
        """
        for ans in wrong_answers:
            html_content += f'<span class="wrong">{ans}</span>, '
        html_content = html_content.rstrip(', ') + """
                        </div>
                    </div>
                    
                    <!-- 模型结果 -->
                    <div class="column">
                        <div class="column-title">模型结果</div>
    """
    
    # 读取模型输出数据
    model_results = []
    try:
        with open(data_files[1], 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_items:
                    break
                try:
                    model_results.append(json.loads(line))
                except Exception as e:
                    print(f"Error parsing line {i+1}: {e}")
    except FileNotFoundError:
        print(f"File {data_files[1]} not found")
    
    # 添加模型输出到HTML
    for i, data in enumerate(model_results):
        question = ""
        if i < len(test_data):
            question = test_data[i].get('question', '')
        
        html_content += f"""
        <div class="item">
            <div class="question">Q{i+1}: {question}</div>
        """
        
        # Round 1
        if 'round1' in data:
            html_content += """
            <div class="round">
                <h3>Round 1</h3>
            """
            
            # Answers
            html_content += "<strong>Answers:</strong><br>"
            for ans in data['round1'].get('answers', []):
                html_content += f'<div class="answer-item">{ans}</div>'
            
            # Explanations
            html_content += "<strong>Explanations:</strong><br>"
            for exp in data['round1'].get('explanations', []):
                html_content += f'<div class="explanation">{exp}</div>'
            
            # Aggregation
            if 'aggregation' in data['round1']:
                html_content += f"""
                <div class="final">
                    <strong>Round 1 Aggregation:</strong> {data['round1']['aggregation']}
                </div>
                """
            
            html_content += "</div>"  # Close round1
        
        # Round 2
        if 'round2' in data:
            html_content += """
            <div class="round">
                <h3>Round 2</h3>
            """
            
            # Answers
            html_content += "<strong>Answers:</strong><br>"
            for ans in data['round2'].get('answers', []):
                html_content += f'<div class="answer-item">{ans}</div>'
            
            # Explanations
            html_content += "<strong>Explanations:</strong><br>"
            for exp in data['round2'].get('explanations', []):
                html_content += f'<div class="explanation">{exp}</div>'
            
            # Aggregation
            if 'aggregation' in data['round2']:
                html_content += f"""
                <div class="final">
                    <strong>Round 2 Aggregation:</strong> {data['round2']['aggregation']}
                </div>
                """
            
            html_content += "</div>"  # Close round2
        
        # Round 3
        if 'round3' in data:
            html_content += """
            <div class="round">
                <h3>Round 3</h3>
            """
            
            # Answers
            html_content += "<strong>Answers:</strong><br>"
            for ans in data['round3'].get('answers', []):
                html_content += f'<div class="answer-item">{ans}</div>'
            
            # Explanations
            html_content += "<strong>Explanations:</strong><br>"
            for exp in data['round3'].get('explanations', []):
                html_content += f'<div class="explanation">{exp}</div>'
            
            # Aggregation
            if 'aggregation' in data['round3']:
                html_content += f"""
                <div class="final">
                    <strong>Round 3 Aggregation:</strong> {data['round3']['aggregation']}
                </div>
                """
            
            html_content += "</div>"  # Close round3
        
        # Final Aggregation
        if 'final_aggregation' in data:
            html_content += f"""
            <div class="final">
                <strong>Final Aggregation:</strong> {data['final_aggregation']}
            </div>
            """
        
        html_content += "</div>"  # Close item
    
    # 结束HTML页面
    html_content += """
            </div>
        </div>
        <script>
            function showTab(tabId) {
                // Hide all content
                document.querySelectorAll('.content').forEach(function(content) {
                    content.classList.remove('active');
                });
                
                // Deactivate all tabs
                document.querySelectorAll('.tab').forEach(function(tab) {
                    tab.classList.remove('active');
                });
                
                // Activate selected tab and content
                document.getElementById(tabId).classList.add('active');
                document.querySelector(`.tab[onclick="showTab('${tabId}')"]`).classList.add('active');
            }
        </script>
    </body>
    </html>
    """
    
    return html_content

# 创建HTML文件
html_content = generate_html(max_items=10)
with open('ramdocs_viewer.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML文件已生成: ramdocs_viewer.html")