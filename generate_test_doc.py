#!/usr/bin/env python
"""
从测试文件中提取 docstring 并生成 Markdown 或 HTML 格式的测试文档
使用方法: python generate_test_doc.py <测试文件路径> [--html] [--output <输出文件>]
"""
import argparse
import importlib.util
import inspect
import os
import re
import sys

# 导入但未使用的模块，暂时注释掉
# import markdown


class TestDocGenerator:
    """测试文档生成器"""

    def __init__(self, module_path):
        """初始化生成器"""
        self.module_path = module_path
        self.module_name = os.path.basename(module_path).replace(".py", "")

    def extract_docstrings(self):
        """提取测试模块中的所有 docstring"""
        # 加载模块
        spec = importlib.util.spec_from_file_location(self.module_name, self.module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 提取文档
        docs = {"module_name": self.module_name, "module_doc": inspect.getdoc(module) or "", "classes": []}

        # 查找所有测试类
        for name, obj in inspect.getmembers(module):
            # 确保只包含直接定义在模块中的类，而不是导入的类
            if inspect.isclass(obj) and name.startswith("Test") and obj.__module__ == self.module_name:
                class_info = self._extract_class_info(obj, name)
                docs["classes"].append(class_info)

        return docs

    def _extract_class_info(self, obj, name):
        """提取类信息的辅助方法"""
        class_info = {"name": name, "doc": inspect.getdoc(obj) or "", "methods": []}

        # 查找所有测试方法，并按照源代码中的顺序排序
        methods = []
        for method_name, method_obj in inspect.getmembers(obj):
            if (
                inspect.isfunction(method_obj)
                and method_name.startswith("test_")
                and method_obj.__module__ == self.module_name
            ):
                method_info = {
                    "name": method_name,
                    "doc": inspect.getdoc(method_obj) or "",
                    "source": inspect.getsource(method_obj),
                    "line_number": inspect.getsourcelines(method_obj)[1],
                }
                methods.append(method_info)

        # 按源码行号排序
        class_info["methods"] = sorted(methods, key=lambda x: x["line_number"])
        return class_info

    def extract_code_examples(self, source):
        """从测试源码中提取请求示例和响应示例"""
        examples = {}

        # 提取请求示例
        request_pattern = r"# 构造请求.*?\n(.*?)# 发送请求"
        request_matches = re.findall(request_pattern, source, re.DOTALL)
        if request_matches:
            examples["request"] = request_matches[0].strip()

        # 提取响应示例
        response_pattern = r"# 验证响应.*?\n(.*?)(?=\n\s*(?:#|$))"
        response_matches = re.findall(response_pattern, source, re.DOTALL)
        if response_matches:
            examples["response"] = response_matches[0].strip()

        return examples

    def generate_markdown(self):
        """生成 Markdown 格式的文档"""
        docs = self.extract_docstrings()
        md = f"# {docs['module_name']} 测试文档\n\n"

        if docs["module_doc"]:
            md += f"{docs['module_doc']}\n\n"

        # 如果没有找到测试类，显示警告
        if not docs["classes"]:
            md += "> **警告**: 在文件中未找到测试类。请确保测试类是直接定义在此文件中，而不是导入的。\n\n"
            return md

        md += "## 目录\n\n"

        # 生成目录 - 修改后的目录结构
        for cls in docs["classes"]:
            md += f"- [{cls['name']}](#{cls['name'].lower()})\n"
            if cls["methods"]:
                for method in cls["methods"]:
                    # 使用缩进表示层级关系，测试方法降低一级
                    md += f"  - [{method['name']}](#{method['name'].lower()})\n"

        md += "\n---\n\n"

        # 生成详细内容
        for cls in docs["classes"]:
            md += f"## {cls['name']}\n\n"
            if cls["doc"]:
                md += f"{cls['doc']}\n\n"

            # 如果没有测试方法，显示提示
            if not cls["methods"]:
                md += "> 此测试类中未找到测试方法。\n\n"
                continue

            for method in cls["methods"]:
                md += f"### {method['name']}\n\n"
                if method["doc"]:
                    md += f"{method['doc']}\n\n"

                # 提取示例代码
                examples = self.extract_code_examples(method["source"])
                if "request" in examples:
                    md += "**请求示例:**\n\n```python\n"
                    md += examples["request"]
                    md += "\n```\n\n"
                if "response" in examples:
                    md += "**响应断言:**\n\n```python\n"
                    md += examples["response"]
                    md += "\n```\n\n"

            md += "---\n\n"

        return md

    def generate_html(self):
        """生成 HTML 格式的文档，直接构建定制的HTML而不依赖markdown转换"""
        docs = self.extract_docstrings()

        # 手动构建HTML内容，确保目录结构正确
        content = f"""
        <h1>{docs['module_name']} 测试文档</h1>
        {f'<p>{docs["module_doc"]}</p>' if docs["module_doc"] else ''}
        <h2>目录</h2>
        <div class="toc-container">
        """

        # 手动构建目录，确保层次结构
        if not docs["classes"]:
            content += '<p class="warning">警告: 在文件中未找到测试类。' "请确保测试类是直接定义在此文件中，而不是导入的。</p>"
        else:
            content += '<ul class="toc-root">'
            for cls in docs["classes"]:
                cls_id = cls["name"].lower()
                content += (
                    f'<li class="toc-class"><a href="#{cls_id}">' f'<span class="class-icon">📋</span> {cls["name"]}</a>'
                )
                if cls["methods"]:
                    content += "<ul>"
                    for method in cls["methods"]:
                        method_id = method["name"].lower()
                        content += (
                            f'<li class="toc-method"><a href="#{method_id}">'
                            f'<span class="method-icon">✓</span> {method["name"]}</a></li>'
                        )
                    content += "</ul>"
                content += "</li>"
            content += "</ul>"

        content += "</div><hr>"

        # 生成详细内容部分
        for cls in docs["classes"]:
            cls_id = cls["name"].lower()
            content += f'<h2 id="{cls_id}"><span class="class-icon">📋</span> {cls["name"]}</h2>'
            if cls["doc"]:
                content += f'<p>{cls["doc"]}</p>'

            if not cls["methods"]:
                content += '<p class="warning">此测试类中未找到测试方法。</p>'
                continue

            for method in cls["methods"]:
                method_id = method["name"].lower()
                content += f'<h3 id="{method_id}"><span class="method-icon">✓</span> {method["name"]}</h3>'
                if method["doc"]:
                    content += f'<p>{method["doc"]}</p>'

                # 提取并添加代码示例
                examples = self.extract_code_examples(method["source"])
                if "request" in examples:
                    content += "<p><strong>请求示例:</strong></p>" '<pre><code class="python">'
                    content += examples["request"].replace("<", "&lt;").replace(">", "&gt;")
                    content += "</code></pre>"
                if "response" in examples:
                    content += "<p><strong>响应断言:</strong></p>" '<pre><code class="python">'
                    content += examples["response"].replace("<", "&lt;").replace(">", "&gt;")
                    content += "</code></pre>"

            content += "<hr>"

        # 生成完整HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{docs['module_name']} 测试文档</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        h1 {{ font-size: 28px; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }}
        h2 {{ font-size: 24px; border-bottom: 1px solid #eaecef; padding-bottom: 6px; }}
        h3 {{ font-size: 20px; }}
        code, pre {{
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
        }}
        pre {{
            padding: 16px;
            overflow: auto;
            line-height: 1.45;
        }}
        code {{
            padding: 0.2em 0.4em;
        }}
        .warning {{
            color: #856404;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 12px;
            border-radius: 4px;
            margin: 12px 0;
        }}
        .toc-container {{
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            background-color: #f6f8fa;
        }}
        .toc-root {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc-class {{
            margin: 8px 0;
        }}
        .toc-class > ul {{
            list-style-type: none;
            padding-left: 20px;
        }}
        .toc-method {{
            margin: 4px 0;
        }}
        .class-icon, .method-icon {{
            margin-right: 5px;
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        hr {{
            border: 0;
            border-top: 1px solid #eaecef;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""
        return html


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="从测试文件生成文档")
    parser.add_argument("test_file", help="测试文件路径")
    parser.add_argument("--html", action="store_true", help="生成HTML格式文档")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.test_file):
        print(f"错误: 文件 '{args.test_file}' 不存在")
        sys.exit(1)

    # 生成文档
    generator = TestDocGenerator(args.test_file)
    if args.html:
        content = generator.generate_html()
        default_ext = ".html"
    else:
        content = generator.generate_markdown()
        default_ext = ".md"

    # 确定输出路径
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.test_file)[0]
        output_file = f"{base_name}_doc{default_ext}"

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"文档已生成: {output_file}")


if __name__ == "__main__":
    main()
