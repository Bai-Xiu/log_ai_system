# Information Security Log AI Analysis System / 信息安全日志AI分析系统

# 快速导航
- [English Version](#english-version)
- [中文版本](#中文版本)

##English-version

A PyQt5 and AI-based log analysis tool that helps security analysts quickly process and analyze multiple formats of log files, generating analysis results and summaries through natural language interaction.

## Key Updates

- **Expanded File Format Support**: Now supports CSV, Excel (.xlsx, .xls), JSON, TXT, and LOG files
- **Enhanced Robustness**: Multi-encoding support and improved error handling
- **Extensible Architecture**: New file types can be easily added through modular processors

## Features

- Supports import and management of multiple log formats (CSV, Excel, JSON, TXT, LOG)
- Automatically generates processing code and executes it through AI based on natural language analysis requirements
- Two analysis modes:
  - Code Processing (generates structured results)
  - Direct Answer (quickly obtains conclusions)
- Visual display of analysis results, with support for exporting results to CSV
- Configurable data directory, result saving directory, and API key

## Requirements

- Python 3.8+
- Dependent libraries: PyQt5, pandas, numpy, openpyxl, openai

## User Guide

### 1. Configuration Settings (First-time Use)
In the "Configuration" tab:
- Enter DeepSeek API key (required for AI analysis functionality)
- Set default data directory (for storing log files)
- Set default result directory (for saving analysis results)

### 2. File Selection
In the "File Selection" tab:
- Select a data directory (or use the default directory from configuration)
- Choose the log files to analyze from the list
- Import new log files using the "Add External Files" button
- Supported formats: CSV, Excel (.xlsx, .xls), JSON, TXT, LOG

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
│   ├── analysis_thread.py # Analysis thread (executes in background)
│   └── file_processors.py # File processing modules for different formats
├── ui/                   # UI components
│   ├── main_window.py    # Main window
│   ├── config_tab.py     # Configuration tab
│   ├── file_tab.py       # File selection tab
│   ├── analysis_tab.py   # Analysis tab
│   └── results_tab.py    # Results tab
├── utils/                # Utility functions
│   ├── config.py         # Configuration management
│   └── helpers.py        # Helper functions
├── resources/            # Resource files (icons, etc.)
├── config.json           # Configuration file
└── main.py               # Program entry point
```

## Notes

- Supported encodings: utf-8, gbk, gb2312, ansi
- Large log files may require longer processing time, please be patient
- Analysis results are for reference only; important security decisions should be combined with manual review
- To add support for new file formats, create a new processor class in `core/file_processors.py` and register it in the processor list

## Frequently Asked Questions

**Q: Unable to load files?**  
A: Check if the file format is supported, if the path contains special characters, or try changing the file encoding

**Q: AI analysis failed?**  
A: Check if the API key is valid, network connection is working, or try simplifying the analysis requirements

**Q: Result table display is abnormal?**  
A: May be caused by non-standard log file format, please check the file structure and formatting

---

## 中文版本

一款基于PyQt5和AI的日志分析工具，可帮助安全分析师快速处理和分析多种格式的日志文件，通过自然语言交互生成分析结果和总结。

## 主要更新

- **扩展文件格式支持**：现已支持CSV、Excel(.xlsx, .xls)、JSON、TXT和LOG文件
- **增强的健壮性**：多编码支持和改进的错误处理
- **可扩展架构**：通过模块化处理器轻松添加新文件类型

## 功能特点

- 支持多种日志格式（CSV、Excel、JSON、TXT、LOG）的导入与管理
- 通过自然语言描述分析需求，AI自动生成处理代码并执行
- 两种分析模式：
  - 代码处理（生成结构化结果）
  - 直接回答（快速获取结论）
- 可视化展示分析结果，支持结果导出为CSV
- 可配置数据目录、结果保存目录和API密钥

## 环境要求

- Python 3.8+
- 依赖库：PyQt5, pandas, numpy, openpyxl, openai

## 使用指南

### 1. 配置设置（首次使用）
在"配置"标签页中：
- 输入DeepSeek API密钥（必填，用于AI分析功能）
- 设置默认数据目录（存放日志文件）
- 设置默认结果目录（保存分析结果）

### 2. 文件选择
在"文件选择"标签页中：
- 选择数据目录（或使用配置中的默认目录）
- 从列表中选择需要分析的日志文件
- 可通过"添加外部文件"按钮导入新的日志文件
- 支持格式：CSV、Excel(.xlsx, .xls)、JSON、TXT、LOG

### 3. 数据分析
在"数据分析"标签页中：
- 输入分析需求（例如："统计各类型攻击的次数"、"列出出现频率最高的10个IP地址"）
- 选择处理模式：
  - 代码处理(生成CSV)：适合需要详细结果表格的场景
  - 直接回答：适合快速获取总结性结论
- 点击"开始分析"按钮

### 4. 查看结果
分析完成后自动跳转至"分析结果"标签页：
- 查看分析总结（关键结论）
- 查看结果表格（详细数据）
- 点击"保存结果"将表格数据导出为CSV

## 项目结构

```
log_ai_system/
├── core/                 # 核心功能模块
│   ├── processor.py      # 处理逻辑核心
│   ├── api_client.py     # AI API客户端
│   ├── analysis_thread.py # 分析线程（后台执行）
│   └── file_processors.py # 不同格式文件处理模块
├── ui/                   # 界面组件
│   ├── main_window.py    # 主窗口
│   ├── config_tab.py     # 配置标签页
│   ├── file_tab.py       # 文件选择标签页
│   ├── analysis_tab.py   # 分析标签页
│   └── results_tab.py    # 结果标签页
├── utils/                # 工具函数
│   ├── config.py         # 配置管理
│   └── helpers.py        # 辅助函数
├── resources/            # 资源文件（图标等）
├── config.json           # 配置文件
└── main.py               # 程序入口
```

## 注意事项

- 支持的编码格式：utf-8, gbk, gb2312, ansi
- 大型日志文件可能需要较长处理时间，请耐心等待
- 分析结果仅作为参考，重要安全决策请结合人工审核
- 如需添加新文件格式支持，可在`core/file_processors.py`中创建新的处理器类并在处理器列表中注册

## 常见问题

**Q: 无法加载文件？**  
A: 检查文件格式是否受支持，路径是否包含特殊字符，或尝试更换文件编码

**Q: AI分析失败？**  
A: 检查API密钥是否有效，网络连接是否正常，或尝试简化分析需求

**Q: 结果表格显示异常？**  
A: 可能是日志文件格式不规范导致，请检查文件结构和格式
