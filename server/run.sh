#!/bin/bash

# 会议系统后端服务启动脚本

echo "正在启动会议系统后端服务..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告: .env 文件不存在，请从 .env.example 复制并配置"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "已创建 .env 文件，请编辑配置后重新运行"
        exit 1
    fi
fi

# 启动服务
echo "启动Flask服务..."
python3 app.py

