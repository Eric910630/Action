# 数据库配置说明

## 📋 数据库信息

### PolarDB for PostgreSQL
- **数据库类型**: PostgreSQL (PolarDB)
- **主机**: beewise-e2e-test.rwlb.rds.aliyuncs.com
- **端口**: 5432
- **数据库名**: beewise_e2e_db
- **用户名**: beewise_tester

## 🔧 配置方式

### 方式1: 使用环境变量（推荐）

在 `.env` 文件中配置：

```env
# 数据库配置 (PolarDB for PostgreSQL)
DB_USER=beewise_tester
DB_PASSWORD=z_13731790081
DB_HOST=beewise-e2e-test.rwlb.rds.aliyuncs.com
DB_PORT=5432
DB_NAME=beewise_e2e_db
DATABASE_ECHO=False
```

### 方式2: 使用DATABASE_URL

也可以直接设置 `DATABASE_URL` 环境变量：

```env
DATABASE_URL=postgresql+psycopg2://beewise_tester:z_13731790081@beewise-e2e-test.rwlb.rds.aliyuncs.com:5432/beewise_e2e_db
```

## 🔍 配置验证

### 检查配置是否正确

```bash
cd backend
python -c "from app.core.config import settings; print(settings.database_url)"
```

应该输出：
```
postgresql+psycopg2://beewise_tester:z_13731790081@beewise-e2e-test.rwlb.rds.aliyuncs.com:5432/beewise_e2e_db
```

### 测试数据库连接

```bash
cd backend
python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print('连接成功:', result.fetchone()[0][:50])
"
```

## 📝 配置说明

### 配置优先级

1. **DATABASE_URL环境变量** - 如果设置了，将优先使用
2. **DB_USER/DB_PASSWORD/DB_HOST等** - 如果未设置DATABASE_URL，将使用这些配置构建连接URL

### 自动构建连接URL

`app/core/config.py` 中的 `database_url` 属性会自动根据配置构建连接URL：

```python
@computed_field
@property
def database_url(self) -> str:
    if self.DATABASE_URL and self.DATABASE_URL.startswith(('postgresql', 'postgres')):
        return self.DATABASE_URL
    return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
```

## 🚀 数据库迁移

### 初始化数据库

```bash
cd backend
alembic upgrade head
```

### 创建新的迁移

```bash
cd backend
alembic revision --autogenerate -m "描述信息"
alembic upgrade head
```

## ⚠️ 注意事项

1. **密码安全**: `.env` 文件包含敏感信息，不要提交到版本控制系统
2. **连接池**: 已配置连接池，自动重连和回收
3. **SSL连接**: 如果需要SSL连接，可以在连接URL中添加参数

## 🔐 安全建议

1. 使用环境变量管理敏感信息
2. 在生产环境中使用密钥管理服务
3. 定期轮换数据库密码
4. 限制数据库访问IP白名单

---

**最后更新**: 2024年12月

