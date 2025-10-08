#!/bin/bash

# 修复前端依赖缺失问题
echo "🔧 修复前端依赖..."

cd frontend

# 安装缺失的 Tailwind 插件
echo "安装 @tailwindcss/forms 和 @tailwindcss/typography..."
npm install @tailwindcss/forms@^0.5.3 @tailwindcss/typography@^0.5.9

# 重新安装所有依赖以确保一致性
echo "重新安装所有依赖..."
rm -rf node_modules package-lock.json
npm install

echo "✅ 依赖修复完成！"
echo "现在可以运行: npm run dev"