# GENIEACS Management System

这是一个基于 Flask 的 GENIEACS 管理系统，用于管理和监控 TR-069 设备。

## 功能特点

- 用户认证和授权
- 设备列表和详情查看
- 设备参数管理
- 设备重启和恢复出厂设置
- 实时设备状态监控

## 安装要求

- Python 3.8+
- GENIEACS 服务器
- SQLite 数据库

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/genieacs-management.git
cd genieacs-management
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
创建 `.env` 文件并设置以下变量：
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
GENIEACS_URL=http://localhost:7557
GENIEACS_USERNAME=admin
GENIEACS_PASSWORD=admin
```

5. 初始化数据库：
```bash
flask init-db
```

## 运行应用

```bash
flask run
```

默认管理员账号：
- 用户名：admin
- 密码：admin

## 使用说明

1. 访问 http://localhost:5000 登录系统
2. 在设备列表中查看所有设备
3. 点击设备详情查看具体参数
4. 可以执行重启、恢复出厂设置等操作

## 开发

- 前端使用 Bootstrap 5
- 后端使用 Flask
- 数据库使用 SQLite

## 贡献

欢迎提交 Issue 和 Pull Request

## 许可证

MIT 