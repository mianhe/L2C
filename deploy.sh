#!/bin/bash

echo "=== Starting deployment ==="

# 更新系统包
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# 安装 Python 3.10 和相关工具
echo "Installing Python 3.10..."
sudo apt-get install -y python3.10 python3.10-venv python3-pip

# 使用当前目录作为项目目录
echo "Setting up project directory..."
PROJECT_DIR=$(pwd)
echo "Project directory: $PROJECT_DIR"

# 创建并激活虚拟环境
echo "Setting up virtual environment..."
python3.10 -m venv .venv
source .venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建环境变量文件
echo "Setting up environment variables..."
cat > .env << EOF
# 数据库配置
DATABASE_URL=sqlite:///l2c.db
# 其他环境变量
DEBUG=False
ENVIRONMENT=production
EOF

# 初始化数据库
echo "Initializing database..."
python -c "from app.db.database import init_db; init_db()"

# 安装和配置 supervisor
echo "Installing supervisor..."
sudo apt-get install -y supervisor

# 创建 supervisor 配置文件
echo "Configuring supervisor..."
sudo tee /etc/supervisor/conf.d/l2c.conf << EOF
[program:l2c]
directory=$PROJECT_DIR
command=$PROJECT_DIR/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
autostart=true
autorestart=true
stderr_logfile=/var/log/l2c.err.log
stdout_logfile=/var/log/l2c.out.log
user=$(whoami)
environment=PATH="$PROJECT_DIR/.venv/bin:%(ENV_PATH)s"
EOF

# 设置日志目录权限
sudo touch /var/log/l2c.err.log /var/log/l2c.out.log
sudo chown $(whoami): /var/log/l2c.err.log /var/log/l2c.out.log

# 重新加载 supervisor 配置
echo "Reloading supervisor..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart l2c

echo "=== Deployment completed ==="
echo "You can check the application status with: sudo supervisorctl status l2c"
echo "Application logs are available at: /var/log/l2c.out.log and /var/log/l2c.err.log"
