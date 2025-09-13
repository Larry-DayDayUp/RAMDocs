import json
import os
import sys
import argparse
from typing import List, Dict, Any, Optional

# 配置项
DEFAULT_CONFIG = {
    "max_items": 10,
    "output_file": "ramdocs_viewer.html",
    "initial_state": "collapsed",  # 可选 'collapsed' 或 'expanded'
    "show_document_types": True,
    "show_rounds": True
}

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成RAMDocs结果的HTML查看器')
    parser.add_argument('--test_file', type=str, default='RAMDocs_test.jsonl',
                        help='原始测试数据文件 (默认: RAMDocs_test.jsonl)')
    parser.add_argument('--result_file', type=str, default='RAMDocs_test.jsonl_madam_rag_Qwen2-1.5B-Instruct_rounds3.jsonl',
                        help='模型结果文件 (默认: RAMDocs_test.jsonl_madam_rag_Qwen2-1.5B-Instruct_rounds3.jsonl)')
    parser.add_argument('--output', type=str, default=DEFAULT_CONFIG["output_file"],
                        help=f'输出HTML文件名 (默认: {DEFAULT_CONFIG["output_file"]})')
    parser.add_argument('--max_items', type=int, default=DEFAULT_CONFIG["max_items"],
                        help=f'最大显示项目数 (默认: {DEFAULT_CONFIG["max_items"]})')
    parser.add_argument('--expanded', action='store_true',
                        help='默认展开所有部分 (默认是折叠的)')
    return parser.parse_args()

def read_jsonl(filename: str, max_items: int = -1) -> List[Dict]:
    """读取JSONL文件，返回JSON对象列表"""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if max_items > 0 and i >= max_items:
                    break
                try:
                    data.append(json.loads(line))
                except Exception as e:
                    print(f"Error parsing line {i+1} in {filename}: {e}")
    except FileNotFoundError:
        print(f"文件未找到: {filename}")
    except Exception as e:
        print(f"读取文件 {filename} 时出错: {e}")
    
    return data

def get_css_styles() -> str:
    """返回CSS样式"""
    return """
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
    .header-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .controls {
        display: flex;
        gap: 10px;
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
    .btn {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 5px;
        cursor: pointer;
    }
    .btn:hover {
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
    #filter-container {
        margin: 10px 0;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
    }
    .filter-group {
        margin-bottom: 10px;
    }
    .filter-label {
        font-weight: bold;
        margin-right: 10px;
    }
    .stats {
        margin: 10px 0;
        padding: 10px;
        background-color: #e8f4f8;
        border-radius: 5px;
    }
    """

def get_javascript_functions() -> str:
    """返回JavaScript函数"""
    return """
    // 初始化页面
    document.addEventListener('DOMContentLoaded', function() {
        // 设置初始折叠状态
        var initialState = document.body.getAttribute('data-initial-state') || 'collapsed';
        
        if (initialState === 'collapsed') {
            // 折叠所有问题
            var questions = document.querySelectorAll('.question');
            questions.forEach(function(question) {
                toggleCollapsible(question, true);
            });
            
            // 折叠所有部分
            var sections = document.querySelectorAll('.section-header');
            sections.forEach(function(section) {
                toggleSection(section, true);
            });
        }
        
        // 更新统计信息
        updateStats();
    });
    
    function toggleCollapsible(element, init) {
        element.classList.toggle('collapsed');
        var content = element.nextElementSibling;
        
        if (!init && content.classList.contains('collapsed')) {
            content.classList.remove('collapsed');
        } else {
            content.classList.add('collapsed');
        }
        
        // 如果不是初始化调用，更新统计信息
        if (!init) {
            updateStats();
        }
    }
    
    function toggleSection(element, init) {
        element.classList.toggle('collapsed');
        var content = element.nextElementSibling;
        
        if (!init && content.classList.contains('collapsed')) {
            content.classList.remove('collapsed');
        } else {
            content.classList.add('collapsed');
        }
    }
    
    function toggleAll() {
        var allExpanded = false;
        
        // 检查是否所有都已经展开
        var questions = document.querySelectorAll('.question');
        var collapsedCount = 0;
        
        questions.forEach(function(question) {
            if (question.classList.contains('collapsed')) {
                collapsedCount++;
            }
        });
        
        allExpanded = (collapsedCount === 0);
        
        // 根据当前状态展开或折叠全部
        questions.forEach(function(question) {
            var content = question.nextElementSibling;
            
            if (allExpanded) {
                question.classList.add('collapsed');
                content.classList.add('collapsed');
            } else {
                question.classList.remove('collapsed');
                content.classList.remove('collapsed');
                
                // 同时展开所有section
                var sections = content.querySelectorAll('.section-header');
                sections.forEach(function(section) {
                    section.classList.remove('collapsed');
                    section.nextElementSibling.classList.remove('collapsed');
                });
            }
        });
        
        updateStats();
    }
    
    function filterByDocType() {
        var selectedTypes = [];
        var checkboxes = document.querySelectorAll('input[name="doc-type"]:checked');
        checkboxes.forEach(function(checkbox) {
            selectedTypes.push(checkbox.value);
        });
        
        var items = document.querySelectorAll('.item');
        
        if (selectedTypes.length === 0) {
            // 如果没有选择任何类型，显示所有项目
            items.forEach(function(item) {
                item.style.display = '';
            });
        } else {
            items.forEach(function(item) {
                var hasType = false;
                
                // 检查该项目是否包含选定的文档类型
                selectedTypes.forEach(function(type) {
                    var typeSpans = item.querySelectorAll('.document-type.' + type);
                    if (typeSpans.length > 0) {
                        hasType = true;
                    }
                });
                
                item.style.display = hasType ? '' : 'none';
            });
        }
        
        updateStats();
    }
    
    function updateStats() {
        var totalItems = document.querySelectorAll('.item').length;
        var visibleItems = document.querySelectorAll('.item:not([style*="display: none"])').length;
        var expandedItems = document.querySelectorAll('.item:not([style*="display: none"]) .question:not(.collapsed)').length;
        
        document.getElementById('stats-total').textContent = totalItems;
        document.getElementById('stats-visible').textContent = visibleItems;
        document.getElementById('stats-expanded').textContent = expandedItems;
    }
    """

def generate_html_header(title: str, initial_state: str) -> str:
    """生成HTML头部"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
        {get_css_styles()}
        </style>
    </head>
    <body data-initial-state="{initial_state}">
        <div class="container">
            <div class="header-controls">
                <h1>RAMDocs Results Viewer</h1>
                <div class="controls">
                    <button class="btn" onclick="toggleAll()">展开/折叠全部</button>
                </div>
            </div>
            
            <div id="filter-container">
                <div class="filter-group">
                    <span class="filter-label">按文档类型筛选:</span>
                    <input type="checkbox" id="filter-correct" name="doc-type" value="correct" onchange="filterByDocType()">
                    <label for="filter-correct">正确 (Correct)</label>
                    <input type="checkbox" id="filter-misinfo" name="doc-type" value="misinfo" onchange="filterByDocType()">
                    <label for="filter-misinfo">错误信息 (Misinfo)</label>
                    <input type="checkbox" id="filter-noise" name="doc-type" value="noise" onchange="filterByDocType()">
                    <label for="filter-noise">噪声 (Noise)</label>
                </div>
                <div class="stats">
                    总计: <span id="stats-total">0</span> 项 | 
                    可见: <span id="stats-visible">0</span> 项 | 
                    展开: <span id="stats-expanded">0</span> 项
                </div>
            </div>
            
            <div id="items-container">
    """

def generate_document_section(docs: List[Dict]) -> str:
    """生成文档部分的HTML"""
    html = ""
    for j, doc in enumerate(docs):
        text = doc.get('text', '').replace('\n', '<br>')
        doc_type = doc.get('type', 'unknown')
        type_class = "correct" if doc_type == "correct" else "misinfo" if doc_type == "misinfo" else "noise"
        
        html += f"""
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                Document {j+1} <span class="document-type {type_class}">{doc_type}</span>
            </div>
            <div class="section-content">
                {text}
            </div>
        </div>
        """
    return html

def generate_answers_section(gold_answers: List[str], wrong_answers: List[str]) -> str:
    """生成答案部分的HTML"""
    html = """
    <div class="answers">
        <strong>Gold Answers:</strong> 
    """
    if gold_answers:
        for ans in gold_answers:
            html += f'<span class="gold">{ans}</span>, '
        html = html.rstrip(', ')
    else:
        html += "<i>无</i>"
    
    html += """
        <br><strong>Wrong Answers:</strong> 
    """
    if wrong_answers:
        for ans in wrong_answers:
            html += f'<span class="wrong">{ans}</span>, '
        html = html.rstrip(', ')
    else:
        html += "<i>无</i>"
    
    html += """
    </div>
    """
    return html

def generate_round_section(round_data: Dict, round_num: int) -> str:
    """生成单个轮次的HTML"""
    html = f"""
    <div class="section">
        <div class="section-header" onclick="toggleSection(this)">
            Round {round_num}
        </div>
        <div class="section-content">
    """
    
    # Answers
    html += "<strong>Answers:</strong><br>"
    answers = round_data.get('answers', [])
    if answers:
        for ans in answers:
            html += f'<div class="answer-item">{ans}</div>'
    else:
        html += "<i>无回答</i><br>"
    
    # Explanations
    html += "<strong>Explanations:</strong><br>"
    explanations = round_data.get('explanations', [])
    if explanations:
        for exp in explanations:
            html += f'<div class="explanation">{exp}</div>'
    else:
        html += "<i>无解释</i><br>"
    
    # Aggregation
    if 'aggregation' in round_data:
        html += f"""
        <div class="final">
            <strong>Round {round_num} Aggregation:</strong> {round_data['aggregation']}
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    return html

def generate_model_results_section(model_item: Dict) -> str:
    """生成模型结果部分的HTML"""
    html = ""
    
    # 各轮结果
    for i in range(1, 4):  # 最多3轮
        round_key = f'round{i}'
        if round_key in model_item:
            html += generate_round_section(model_item[round_key], i)
    
    # Final Aggregation
    if 'final_aggregation' in model_item:
        html += f"""
        <div class="final">
            <strong>Final Aggregation:</strong> {model_item['final_aggregation']}
        </div>
        """
    
    return html

def generate_item_html(test_item: Dict, model_item: Dict, index: int) -> str:
    """生成单个问题项的HTML"""
    question = test_item.get('question', '')
    
    html = f"""
    <div class="item">
        <div class="question" onclick="toggleCollapsible(this)">
            Q{index+1}: {question}
        </div>
        <div class="collapsible-content">
            <div class="comparison">
                <!-- 原始测试数据 -->
                <div class="column">
                    <div class="column-title">原始测试数据</div>
    """
    
    # 添加文档
    docs = test_item.get('documents', [])
    html += generate_document_section(docs)
    
    # 添加答案
    gold_answers = test_item.get('gold_answers', [])
    wrong_answers = test_item.get('wrong_answers', [])
    html += generate_answers_section(gold_answers, wrong_answers)
    
    html += """
                </div>
                
                <!-- 模型结果 -->
                <div class="column">
                    <div class="column-title">模型结果</div>
    """
    
    # 添加模型结果
    html += generate_model_results_section(model_item)
    
    html += """
                </div>
            </div>
        </div>
    </div>
    """
    
    return html

def generate_html_footer() -> str:
    """生成HTML页脚"""
    return f"""
            </div>
        </div>
        <script>
        {get_javascript_functions()}
        </script>
    </body>
    </html>
    """

def generate_html_viewer(test_data: List[Dict], model_results: List[Dict], initial_state: str = 'collapsed') -> str:
    """生成完整的HTML查看器"""
    # 生成HTML头部
    html_content = generate_html_header("RAMDocs Results Viewer", initial_state)
    
    # 为每个问题生成并排显示的原始数据和模型结果
    for i in range(min(len(test_data), len(model_results))):
        html_content += generate_item_html(test_data[i], model_results[i], i)
    
    # 添加页脚
    html_content += generate_html_footer()
    
    return html_content

def main():
    # 解析命令行参数
    args = parse_arguments()
    
    # 确定初始状态
    initial_state = 'expanded' if args.expanded else 'collapsed'
    
    # 读取数据
    test_data = read_jsonl(args.test_file, args.max_items)
    model_results = read_jsonl(args.result_file, args.max_items)
    
    if not test_data:
        print(f"警告: 无法从 {args.test_file} 读取测试数据")
    
    if not model_results:
        print(f"警告: 无法从 {args.result_file} 读取模型结果")
    
    if not test_data or not model_results:
        print("错误: 无法继续生成HTML查看器，请检查输入文件")
        return
    
    # 生成HTML内容
    html_content = generate_html_viewer(test_data, model_results, initial_state)
    
    # 写入文件
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML文件已生成: {args.output}")
    except Exception as e:
        print(f"写入HTML文件时出错: {e}")

if __name__ == "__main__":
    main()