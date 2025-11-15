# VTICS 前端项目

Vue 3 + TypeScript + Element Plus 前端应用

## 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全
- **Element Plus** - UI组件库
- **Vue Router** - 路由管理
- **Axios** - HTTP客户端
- **Vite** - 构建工具

## 项目结构

```
frontend/
├── src/
│   ├── api/          # API接口
│   ├── views/        # 页面组件
│   ├── router/       # 路由配置
│   ├── App.vue       # 根组件
│   └── main.ts       # 入口文件
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 安装依赖

```bash
cd frontend
npm install
```

## 开发

```bash
npm run dev
```

访问：http://localhost:3000

## 构建

```bash
npm run build
```

## 功能页面

- **热点监控** - 查看和管理热点
- **视频拆解** - 分析视频并查看拆解报告
- **脚本生成** - 生成和管理脚本
- **商品管理** - 管理商品信息
- **直播间管理** - 管理直播间配置

## API配置

前端通过代理访问后端API：
- 开发环境：`/api` → `http://localhost:8000/api`
- 生产环境：需要配置实际的后端地址

