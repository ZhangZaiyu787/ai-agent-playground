# Mac 下 Python 多版本管理最佳方案
结合你的场景（AI 开发、多项目并行、需要干净隔离），**最推荐 `pyenv + venv` 组合**：pyenv 管全局多版本切换，venv 管项目级依赖，轻量、干净、不污染系统，是开发者最通用的方案。

---

## 一、核心方案：pyenv 管理 Python 版本
### pyenv 是什么
- 专门用来在一台机器上安装、切换**多个 Python 版本**的工具
- 所有版本都装在用户目录下，**完全不碰系统自带的 Python**，不会搞坏系统
- 支持全局默认版本、按项目目录指定版本、临时 shell 指定版本

### 1. 安装 pyenv
```bash
# 用 Homebrew 安装
brew install pyenv

# 验证安装
pyenv --version
```

### 2. 配置 Shell 环境（必须做，否则不生效）
根据你用的 shell 把下面的配置加到对应配置文件里：

**zsh（Mac 默认）→ 编辑 `~/.zshrc`**
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# 生效
source ~/.zshrc
```

**bash → 编辑 `~/.bash_profile` 或 `~/.bashrc`**

### 3. 安装你需要的 Python 版本
```bash
# 查看可安装的所有版本
pyenv install --list

# 安装 3.11.9（选一个具体的 3.11 小版本）
pyenv install 3.11.9

# 也保留 3.9，兼容老项目
pyenv install 3.9.19

# 查看已安装的版本
pyenv versions
# 输出类似：
#   3.9.19
# * 3.11.9 (set by /Users/xxx/.pyenv/version)
```

> 安装慢的话可以挂代理，或者用国内镜像源。

export PYTHON_BUILD_MIRROR_URL="https://registry.npmmirror.com/-/binary/python"
export PYTHON_BUILD_MIRROR_URL_SKIP_CHECKSUM=1

### 4. 三种切换方式（灵活使用）
#### ① 全局默认版本（平时默认用这个）
```bash
pyenv global 3.11.9
python --version  # Python 3.11.9
```
新开终端默认就是 3.11，日常开发、AI 项目都用这个。

#### ② 单项目指定版本（最常用）
进入项目目录，执行一次，以后进这个目录自动切对应版本：
```bash
# 进入你的 AI 学习项目
cd ~/Documents/agent/ai-agent-playground

# 指定这个项目用 3.11
pyenv local 3.11.9
```
执行后会在目录下生成一个 `.python-version` 文件，里面写着版本号。以后只要 `cd` 进这个目录，pyenv 会**自动切换**到对应版本，完全无感。

#### ③ 临时当前终端用某个版本
```bash
pyenv shell 3.9.19
# 关掉终端就失效，适合临时跑老脚本
```

---

## 二、配合 venv 管理项目依赖（两层隔离）
pyenv 只管 Python 解释器版本，**每个项目的依赖包仍然用 venv 隔离**，形成双层隔离：

```
系统层：pyenv 管理 3.9 / 3.11 / 3.12 多个解释器
    ↓
项目层：每个项目一个 venv 虚拟环境，依赖互不干扰
```

### 标准工作流（新项目必走流程）
```bash
# 1. 进入项目目录
cd my-project

# 2. 先指定 Python 版本（用 pyenv）
pyenv local 3.11.9

# 3. 用当前版本创建虚拟环境
python -m venv venv

# 4. 激活
source venv/bin/activate

# 5. 装依赖，都装在项目自己的 venv 里
pip install instructor langchain
```

### 老项目迁移到 3.11 的步骤
以你现在的 ai-agent-playground 为例：
```bash
cd ai-agent-playground

# 1. 指定项目用 3.11
pyenv local 3.11.9

# 2. 删除旧的 3.9 虚拟环境
rm -rf venv

# 3. 用 3.11 重建
python -m venv venv
source venv/bin/activate
# 退出虚拟环境
deactivate

# 4. 重装依赖（如果有 requirements.txt）
pip install -r requirements.txt
# 或者手动装需要的包
pip install openai instructor python-dotenv
```

---

## 三、常用命令速查表
| 命令 | 作用 |
|------|------|
| `pyenv install 3.11.9` | 安装指定版本 |
| `pyenv uninstall 3.9.19` | 删除某个版本 |
| `pyenv versions` | 查看所有已安装版本 |
| `pyenv global 3.11.9` | 设置全局默认版本 |
| `pyenv local 3.11.9` | 设置当前目录项目版本 |
| `pyenv shell 3.9.19` | 当前终端临时切换 |
| `pyenv which python` | 查看当前 python 的实际路径 |

