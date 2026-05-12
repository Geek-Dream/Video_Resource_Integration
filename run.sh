#!/bin/bash
# ===========================================
# 🎬 VID 启动器 — 跨平台一键配置
# 检测系统 → 注入 vid 到 PATH → 全局可用
# ===========================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VID_PATH="$SCRIPT_DIR/vid"

# 🎨 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║${RESET}   🎬 ${BOLD}VID 视频资源下载器${RESET} — 一键启动器      ${CYAN}║${RESET}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${RESET}"
echo ""

# ═══════════════════════════════════════════
# 🔍 检测操作系统
# ═══════════════════════════════════════════
detect_os() {
    case "$(uname -s)" in
        Darwin*)    OS="macOS" ;;
        Linux*)     OS="Linux" ;;
        MINGW*|MSYS*|CYGWIN*)  OS="Windows" ;;
        *)          OS="Unknown" ;;
    esac
    echo -e "  🖥️  检测到系统: ${GREEN}${OS}${RESET}"
    echo ""
}

# ═══════════════════════════════════════════
# 🍎 macOS — 注入 vid 到 PATH
# ═══════════════════════════════════════════
install_macos() {
    echo -e "  ${YELLOW}你想怎么使用 vid？${RESET}"
    echo ""
    echo -e "    ${CYAN}[1]${RESET} ⚡ 临时生效  ${GRAY}(仅当前终端窗口，关闭后失效)${RESET}"
    echo -e "    ${CYAN}[2]${RESET} 🔧 永久注入  ${GRAY}(写入 shell 配置文件，每次打开终端都可用)${RESET}"
    echo ""
    echo -ne "  ${BOLD}请选择 [1/2]: ${RESET}"
    read -r choice

    # 确保 vid 可执行
    chmod +x "$VID_PATH"

    case "$choice" in
        1)
            export PATH="$SCRIPT_DIR:$PATH"
            echo ""
            echo -e "  ✅ ${GREEN}vid 已临时注入！${RESET}"
            echo -e "  ${GRAY}提示：在当前终端输入 ${CYAN}vid${RESET}${GRAY} 即可运行${RESET}"
            echo -e "  ${GRAY}关闭此终端窗口后失效，下次需要重新运行此脚本${RESET}"
            echo ""
            # 直接启动 vid
            exec bash -c "export PATH=\"$SCRIPT_DIR:\$PATH\"; cd \"$SCRIPT_DIR\"; ./vid"
            ;;
        2)
            # 检测当前 shell
            local shell_name=$(basename "$SHELL")
            local rc_file=""
            case "$shell_name" in
                zsh)  rc_file="$HOME/.zshrc" ;;
                bash) rc_file="$HOME/.bash_profile" ;;
                *)    rc_file="$HOME/.zshrc" ;;
            esac

            # 检查是否已存在
            if grep -q "$SCRIPT_DIR" "$rc_file" 2>/dev/null; then
                echo ""
                echo -e "  ⚠️  ${YELLOW}vid 已经在 PATH 中了，无需重复注入${RESET}"
            else
                echo "" >> "$rc_file"
                echo "# 🎬 VID 视频资源下载器" >> "$rc_file"
                echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> "$rc_file"
                echo ""
                echo -e "  ✅ ${GREEN}vid 已永久注入到 ${rc_file}！${RESET}"
                echo -e "  ${GRAY}重新打开终端或执行 ${CYAN}source ${rc_file}${RESET}${GRAY} 后生效${RESET}"
            fi
            echo -e "  ${GRAY}之后在任何目录输入 ${CYAN}vid${RESET}${GRAY} 即可运行${RESET}"
            echo ""

            # 立即生效并启动
            export PATH="$SCRIPT_DIR:$PATH"
            exec bash -c "export PATH=\"$SCRIPT_DIR:\$PATH\"; cd \"$SCRIPT_DIR\"; ./vid"
            ;;
        *)
            echo -e "  ${RED}无效选择，直接启动 vid...${RESET}"
            export PATH="$SCRIPT_DIR:$PATH"
            exec bash -c "export PATH=\"$SCRIPT_DIR:\$PATH\"; cd \"$SCRIPT_DIR\"; ./vid"
            ;;
    esac
}

# ═══════════════════════════════════════════
# 🪟 Windows — Git Bash / MSYS2
# ═══════════════════════════════════════════
install_windows() {
    echo -e "  ${YELLOW}Windows 环境下有两种运行方式：${RESET}"
    echo ""
    echo -e "    ${CYAN}[1]${RESET} 🚀 直接启动 vid ${GRAY}(推荐，无需配置)${RESET}"
    echo -e "    ${CYAN}[2]${RESET} 🔧 尝试注入到系统 PATH ${GRAY}(可能需要管理员权限)${RESET}"
    echo ""
    echo -ne "  ${BOLD}请选择 [1/2]: ${RESET}"
    read -r choice

    chmod +x "$VID_PATH" 2>/dev/null || true

    case "$choice" in
        2)
            echo ""
            echo -ne "  ${YELLOW}注入到用户 PATH...${RESET} "
            # 尝试添加到用户 PATH（Windows 10+ 支持 setx）
            if command -v setx &>/dev/null; then
                local current_path=$(cmd.exe /c "echo %PATH%" 2>/dev/null | tr -d '\r')
                if ! echo "$current_path" | grep -q "$(cygpath -w "$SCRIPT_DIR" 2>/dev/null || echo "$SCRIPT_DIR")"; then
                    setx PATH "$current_path;$(cygpath -w "$SCRIPT_DIR" 2>/dev/null || echo "$SCRIPT_DIR")" >/dev/null 2>&1 && \
                        echo -e "${GREEN}✅ 成功！${RESET}" || \
                        echo -e "${RED}失败（可能需要管理员权限）${RESET}"
                else
                    echo -e "${YELLOW}已在 PATH 中${RESET}"
                fi
            else
                echo -e "${RED}setx 不可用，无法注入${RESET}"
                echo -e "  ${GRAY}退回直接启动模式...${RESET}"
                choice=1
            fi

            if [ "$choice" != "1" ]; then
                echo ""
                echo -e "  ${GRAY}新开终端窗口后输入 ${CYAN}vid${RESET}${GRAY} 即可运行${RESET}"
                echo -ne "  ${DIM}按回车启动 vid...${RESET}"; read -r
            fi
            ;;&
        *)
            # 直接启动 — 模拟 vid 界面
            echo ""
            echo -e "  🚀 ${GREEN}直接启动 vid...${RESET}"
            echo ""
            cd "$SCRIPT_DIR" && exec bash ./vid
            ;;
    esac

    # 如果选了2但注入失败，退回直接启动
    cd "$SCRIPT_DIR" && exec bash ./vid
}

# ═══════════════════════════════════════════
# 🐧 Linux
# ═══════════════════════════════════════════
install_linux() {
    echo -e "  ${YELLOW}你想怎么使用 vid？${RESET}"
    echo ""
    echo -e "    ${CYAN}[1]${RESET} ⚡ 临时生效"
    echo -e "    ${CYAN}[2]${RESET} 🔧 永久注入（写入 ~/.bashrc）"
    echo ""
    echo -ne "  ${BOLD}请选择 [1/2]: ${RESET}"
    read -r choice

    chmod +x "$VID_PATH"

    case "$choice" in
        2)
            if ! grep -q "$SCRIPT_DIR" "$HOME/.bashrc" 2>/dev/null; then
                echo "" >> "$HOME/.bashrc"
                echo "# 🎬 VID 视频资源下载器" >> "$HOME/.bashrc"
                echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> "$HOME/.bashrc"
                echo -e "  ✅ ${GREEN}vid 已永久注入到 ~/.bashrc${RESET}"
            else
                echo -e "  ⚠️  ${YELLOW}vid 已在 PATH 中${RESET}"
            fi
            ;;
    esac

    export PATH="$SCRIPT_DIR:$PATH"
    echo ""
    echo -e "  🚀 ${GREEN}启动 vid...${RESET}"
    cd "$SCRIPT_DIR" && exec bash ./vid
}

# ═══════════════════════════════════════════
# 🚀 主流程
# ═══════════════════════════════════════════
detect_os

case "$OS" in
    macOS)
        install_macos
        ;;
    Windows)
        install_windows
        ;;
    Linux)
        install_linux
        ;;
    *)
        echo -e "  ${YELLOW}未知系统，直接启动 vid...${RESET}"
        chmod +x "$VID_PATH"
        cd "$SCRIPT_DIR" && exec bash ./vid
        ;;
esac
