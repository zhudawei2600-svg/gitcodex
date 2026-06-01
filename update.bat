@echo off
chcp 65001 >nul
title 极光导航 - 数据更新工具

echo.
echo    ╔══════════════════════════════════════╗
echo    ║     极光导航 - 一键数据更新         ║
echo    ╚══════════════════════════════════════╝
echo.
echo    步骤 1/4: 拉取 GitHub 高星仓库...
cd /d "%~dp0scripts"
python fetch_github.py
if %errorlevel% neq 0 (
    echo    [失败] GitHub 数据拉取出错
    pause
    exit /b 1
)

echo.
echo    步骤 2/4: AI 生成中文内容...
python generate_ai.py
if %errorlevel% neq 0 (
    echo    [失败] AI 内容生成出错
    pause
    exit /b 1
)

echo.
echo    步骤 3/4: 构建静态站点...
cd /d "%~dp0nuxt-app"
call npm run generate
if %errorlevel% neq 0 (
    echo    [失败] 站点构建出错
    pause
    exit /b 1
)

echo.
echo    步骤 4/4: 部署到 Cloudflare Pages...
call npx wrangler pages deploy .output/public --project-name=gitcodex --branch=master
if %errorlevel% neq 0 (
    echo    [失败] 部署出错
    pause
    exit /b 1
)

echo.
echo    ╔══════════════════════════════════════╗
echo    ║     更新完成！                       ║
echo    ║     https://gitcodex.pages.dev       ║
echo    ╚══════════════════════════════════════╝
echo.
pause
