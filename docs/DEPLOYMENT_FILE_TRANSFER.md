# 文件传输指南（Base64分块传输）

## 方法说明

由于SSH连接问题，我们使用base64编码分块传输的方式上传项目代码。

## 操作步骤

### 第一步：在服务器上创建接收脚本

在服务器的Web终端中执行：

```bash
cd /root
cat > receive_file.sh << 'EOF'
#!/bin/bash
# 接收base64编码的文件块并合并

echo "开始接收文件..."
cat > Action_small_base64.txt << 'ENDOFFILE'
EOF

chmod +x receive_file.sh
```

### 第二步：逐步粘贴文件块

我会提供16个文件块的内容，你需要：
1. 在服务器的Web终端中执行 `cat >> Action_small_base64.txt << 'PART1'`
2. 粘贴我提供的第一个文件块内容
3. 输入 `PART1` 结束
4. 重复16次

### 第三步：解码并解压

```bash
cd /root
base64 -d Action_small_base64.txt > Action_small.tar.gz
tar -xzf Action_small.tar.gz
cd Action
ls
```

## 更简单的方法（推荐）

如果你有GitHub或Gitee账号，可以：
1. 在本地创建Git仓库并推送
2. 在服务器上直接 `git clone` 下载

这样更简单！

