# 数据库配置说明

## 数据库类型

项目已切换至 **PolarDB for PostgreSQL**。

## 当前配置

数据库连接信息已配置在 `app/core/config.py` 中：

```python
DB_USER = "beewise_tester"
DB_PASSWORD = "z_13731790081"
DB_HOST = "beewise-e2e-test.rwlb.rds.aliyuncs.com"
DB_PORT = "5432"
DB_NAME = "beewise_e2e_db"
```

连接URL格式：
```
postgresql+psycopg2://beewise_tester:z_13731790081@beewise-e2e-test.rwlb.rds.aliyuncs.com:5432/beewise_e2e_db
```

## 环境变量配置

### 方式1：使用独立字段（推荐）

在 `.env` 文件中配置：

```env
DB_USER=beewise_tester
DB_PASSWORD=z_13731790081
DB_HOST=beewise-e2e-test.rwlb.rds.aliyuncs.com
DB_PORT=5432
DB_NAME=beewise_e2e_db
```

### 方式2：使用完整URL

如果需要在环境变量中直接设置完整的数据库URL：

```env
DATABASE_URL=postgresql+psycopg2://beewise_tester:z_13731790081@beewise-e2e-test.rwlb.rds.aliyuncs.com:5432/beewise_e2e_db
```

**注意**：如果设置了 `DATABASE_URL`，它将覆盖独立字段的配置。

## 数据库驱动

项目使用 `psycopg2-binary` 作为PostgreSQL驱动，已在 `requirements.txt` 中配置：

```
psycopg2-binary==2.9.9
```

## 数据模型兼容性

所有数据模型已兼容PostgreSQL：

- ✅ JSON字段：SQLAlchemy的JSON类型会自动映射到PostgreSQL的JSON类型
- ✅ 字符串字段：String类型映射到VARCHAR
- ✅ 日期时间：DateTime类型映射到TIMESTAMP
- ✅ 外键：ForeignKey正常工作
- ✅ 索引：所有索引定义兼容

## 数据库迁移

使用Alembic进行数据库迁移：

### 初始化迁移（首次）

```bash
cd backend
alembic revision --autogenerate -m "Initial migration"
```

### 应用迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
alembic downgrade -1
```

## 连接测试

### 使用Python测试连接

```python
from app.core.database import engine
from sqlalchemy import text

# 测试连接
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
```

### 使用psql命令行测试

```bash
psql -h beewise-e2e-test.rwlb.rds.aliyuncs.com \
     -p 5432 \
     -U beewise_tester \
     -d beewise_e2e_db
```

## 注意事项

1. **安全性**：生产环境请勿将数据库密码硬编码在代码中，应使用环境变量或密钥管理服务
2. **连接池**：SQLAlchemy已配置连接池（pool_pre_ping=True, pool_recycle=3600）
3. **时区**：确保应用服务器和数据库服务器的时区设置一致
4. **SSL连接**：如果需要SSL连接，可以在DATABASE_URL中添加参数：
   ```
   postgresql+psycopg2://user:pass@host:port/dbname?sslmode=require
   ```

## 故障排查

### 连接失败

1. 检查网络连接
2. 验证数据库主机、端口、用户名、密码
3. 检查防火墙规则
4. 确认数据库服务正在运行

### 编码问题

PostgreSQL默认使用UTF-8编码，确保数据库创建时使用正确的编码：

```sql
CREATE DATABASE beewise_e2e_db WITH ENCODING 'UTF8';
```

### JSON字段查询

PostgreSQL支持JSON操作符，可以在查询中使用：

```python
# 查询JSON字段
from sqlalchemy import text

result = session.execute(
    text("SELECT * FROM hotspots WHERE tags->>'category' = 'fashion'")
)
```

## 性能优化建议

1. **使用JSONB**：如果需要频繁查询JSON字段，考虑使用JSONB类型（需要修改迁移文件）
2. **索引优化**：为常用查询字段添加索引
3. **连接池大小**：根据实际负载调整连接池大小

## 相关文件

- `backend/app/core/config.py` - 数据库配置
- `backend/app/core/database.py` - 数据库连接
- `backend/migrations/env.py` - Alembic环境配置
- `backend/requirements.txt` - 依赖包（包含psycopg2-binary）

