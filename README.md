# Information Security Log AI Analysis System
## English
A PyQt5 and AI-based log analysis tool that helps security analysts security analysts security analystsay analysts quickly process and analyze log files in various formats (CSV, JSON, TXT, XML), generating generating analysis results and summaries through natural language interaction.

## Features

- Supports import and management of log files in multiple formats (CSV, JSON, TXT, XML)
- Automatically generates processing code and executes it through AI based on natural language analysis requirements
- Two analysis modes: Code Processing (generates structured results) and Direct Answer (quickly obtains conclusions)
- Visual display of analysis results, with support for exporting results to CSV
- Configurable data directory, result saving directory, and API key

## Requirements

- Python 3.8+
- Dependent libraries: `PyQt5`, `pandas`, `numpy`, `openai`, `json`, `xml.etree.ElementTree`

## User Guide

### 1. Configuration Settings (First-time Use)

In the "Configuration" tab:
- Enter DeepSeek API key (required for AI analysis functionality)
- Set default data directory (for storing log files)
- Set default result directory (for saving analysis results)

### 2. File Selection

In the "File Selection" tab:
- Select a data directory (or use the default directory from configuration)
- Choose the log files (CSV, JSON, TXT, XML) to analyze from the list
- Import new log files using the "Add External Files" button

### 3. Data Analysis

In the "Data Analysis" tab:
- Enter analysis requirements (e.g., "Count the number of each type of attack", "List the top 10 most frequent IP addresses")
- Select processing mode:
  - Code Processing (generates CSV): Suitable for scenarios requiring detailed result tables
  - Direct Answer: Suitable for quickly obtaining summary conclusions
- Click the "Start Analysis" button

### 4. View Results

After analysis completes, automatically jump to the "Analysis Results" tab:
- View analysis summary (key conclusions)
- View result table (detailed data)
- Click "Save Results" to export table data to CSV

## Project Structure

```
log_ai_system/
├── core/                 # Core functionality modules
│   ├── processor.py      # Core processing logic
│   ├── api_client.py     # AI API client
│   └── analysis_thread.py # Analysis thread (executes in background)
├── ui/                   # UI components
│   ├── main_window.py    # Main window
│   ├── config_tab.py     # Configuration tab
│   ├── file_tab.py       # File selection tab
│   ├── analysis_tab.py   # Analysis tab
│   └── results_tab.py    # Results tab
├── utils/                # Utility functions
│   ├── config.py         # Configuration management
│   ├── helpers.py        # Helper functions
│   └── parsers/          # Log format parsers
│       ├── csv_parser.py # CSV parser
│       ├── json_parser.py # JSON parser
│       ├── txt_parser.py # TXT parser
│       └── xml_parser.py # XML parser
├── resources/            # Resource files (icons, etc.)
├── config.json           # Configuration file
└── main.py               # Program entry point
```

## Notes

- Ensure log files are in supported formats (CSV, JSON, TXT, XML) with supported encodings (utf-8, gbk, gb2312, ansi)
- Large log files may require longer processing time, please be patient
- Analysis results are for reference only; important security decisions should be combined with manual review

## Frequently Asked Questions

1. **Q: Unable to load files?**  
   A: Check if the file is in a supported format, if the path contains special characters, or try changing the file encoding

2. **Q: AI analysis failed?**  
   A: Check if the API key is valid, network connection is working, or try simplifying the analysis requirements

3. **Q: Result table display is abnormal?**  
   A: May be caused by non-standard log file format, please check the file structure and formatting

# 信息安全日志AI分析系统
## 中文
一款基于PyQt5和AI的日志分析工具，可帮助安全分析师快速处理和分析多种格式（CSV、JSON、TXT、XML）的日志文件，通过自然语言交互生成分析结果和总结。

## 功能特点

- 支持多种格式（CSV、JSON、TXT、XML）日志文件的导入与管理
- 通过自然语言描述分析需求，AI自动生成处理代码并执行
- 两种分析模式：代码处理（生成结构化结果）和直接回答（快速获取结论）
- 可视化展示分析结果，支持结果导出为CSV
- 可配置数据目录、结果保存目录和API密钥

## 环境要求

- Python 3.8+
- 依赖库：`PyQt5`, `pandas`, `numpy`, `openai`, `json`, `xml.etree.ElementTree`

## 使用指南

### 1. 配置设置（首次使用）

- 在"配置"标签页中：
  - 输入DeepSeek API密钥（必填，用于AI分析功能）
  - 设置默认数据目录（存放日志文件）
  - 设置默认结果目录（保存分析结果）

### 2. 文件选择

- 在"文件选择"标签页中：
  - 选择数据目录（或使用配置中的默认目录）
  - 从列表中选择需要分析的日志文件（CSV、JSON、TXT、XML）
  - 可通过"添加外部文件"按钮导入新的日志文件

### 3. 数据分析

- 在"数据分析"标签页中：
  - 输入分析需求（例如："统计各类型攻击的次数"、"列出出现频率最高的10个IP地址"）
  - 选择处理模式：
    - 代码处理(生成CSV)：适合需要详细结果表格的场景
    - 直接回答：适合快速获取总结性结论
  - 点击"开始分析"按钮

### 4. 查看结果

- 分析完成后自动跳转至"分析结果"标签页：
  - 查看分析总结（关键结论）
  - 查看结果表格（详细数据）
  - 点击"保存结果"将表格数据导出为CSV

## 项目结构

```
log_ai_system/
├── core/                 # 核心功能模块
│   ├── processor.py      # 处理逻辑核心
│   ├── api_client.py     # AI API客户端
│   └── analysis_thread.py # 分析线程（后台执行）
├── ui/                   # 界面组件
│   ├── main_window.py    # 主窗口
│   ├── config_tab.py     # 配置标签页
│   ├── file_tab.py       # 文件选择标签页
│   ├── analysis_tab.py   # 分析标签页
│   └── results_tab.py    # 结果标签页
├── utils/                # 工具函数
│   ├── config.py         # 配置管理
│   ├── helpers.py        # 辅助函数
│   └── parsers/          # 日志格式解析器
│       ├── csv_parser.py # CSV解析器
│       ├── json_parser.py # JSON解析器
│       ├── txt_parser.py # TXT解析器
│       └── xml_parser.py # XML解析器
├── resources/            # 资源文件（图标等）
├── config.json           # 配置文件
└── main.py               # 程序入口
```

## 注意事项

- 确保日志文件为支持的格式（CSV、JSON、TXT、XML），且编码在支持范围内（utf-8, gbk, gb2312, ansi）
- 大型日志文件可能需要较长处理时间，请耐心等待
- 分析结果仅作为参考，重要安全决策请结合人工审核

## 常见问题

1. **Q: 无法加载文件？**  
   A: 检查文件是否为支持的格式，路径是否包含特殊字符，或尝试更换文件编码

2. **Q: AI分析失败？**  
   A: 检查API密钥是否有效，网络连接是否正常，或尝试简化分析需求

3. **Q: 结果表格显示异常？**  
   A: 可能是日志文件格式不规范导致，请检查文件结构和格式
