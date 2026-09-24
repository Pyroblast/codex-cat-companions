# 随行猫小队 · Codex Cat Companions

四只一起陪你完成任务的 Codex 自定义宠物。克隆仓库后，运行安装脚本即可把它们放到当前电脑的宠物目录中，无需重新生成图片。

| 栗栗 · lili | 苔苔 · taitai | 铠铠 · kaikai | 橘钳 · juqian |
| :---: | :---: | :---: | :---: |
| ![栗栗招手](previews/lili/waving.gif) | ![苔苔招手](previews/taitai/waving.gif) | ![铠铠招手](previews/kaikai/waving.gif) | ![橘钳招手](previews/juqian/waving.gif) |
| 红围巾、皮甲的冒险伙伴 | 苔绿兜帽与背包的林间旅伴 | 银灰盔甲、蓝围巾的小守卫 | 戴护目镜、系围裙的橘猫工匠 |

每只包含 **9 组标准动作 + 16 个视线方向**，采用 Codex v2 精灵图格式。

## 在另一台 Mac 上快速安装

需要：支持自定义 v2 宠物的 Codex 桌面客户端、Python 3.8+，以及访问此私有仓库的 GitHub 账号。

### 方式一：GitHub CLI

已安装 `gh` 且已登录具有仓库访问权限的账号时：

```bash
gh repo clone Pyroblast/codex-cat-companions
cd codex-cat-companions
python3 install.py
```

如果尚未登录，先运行 `gh auth login`。安装结束后，在 **Codex → 设置 → Pets → Refresh** 中刷新，再选择喜欢的猫。若没有立即出现，重新打开客户端后再检查。

### 方式二：下载 ZIP

1. 登录 GitHub，打开本仓库，点击 **Code → Download ZIP** 并解压。
2. 在终端进入解压后的 `codex-cat-companions-main` 文件夹。
3. 运行 `python3 install.py`，然后在 Codex 的 Pets 设置中刷新。

ZIP 方式无需 Git 或 GitHub CLI。安装脚本本身不联网，不需要 API 密钥，也不依赖任何第三方 Python 库。

## 其他安装方式

只安装一只或指定几只：

```bash
python3 install.py --pet lili
python3 install.py --pet taitai --pet juqian
```

默认安装目录为当前用户的 `~/.codex/pets/`；设置了 `CODEX_HOME` 时使用 `$CODEX_HOME/pets/`。也可以显式指定：

```bash
python3 install.py --dest "/path/to/codex-home/pets"
```

Windows 安装了 Python Launcher 后，可在仓库目录使用 `py -3 install.py`。默认目录为当前用户主目录下的 `.codex\pets`。脚本使用跨平台 Python 标准库，本次安装测试在 macOS 上执行。

不运行脚本也可以：把 `pets/` 下的四个宠物文件夹复制到目标电脑的 Codex 宠物目录。每个文件夹都必须包含 `pet.json` 与 `spritesheet.webp`。

## 从 GitHub 更新

在本地仓库目录运行：

```bash
git pull --ff-only
python3 install.py
```

- 相同版本自动跳过，不重复写入。
- 目标目录存在不同版本时，安装会在写入前停止，保留全部已有宠物。
- 确认要更新时，运行 `python3 install.py --replace`。旧文件夹会完整备份到同级的 `pets-backups/<名称>-<UTC时间>/`，再安装新版本。
- 其他名称的宠物不受影响。

安装前会核对所有选中宠物的 SHA-256 与配置。校验失败时不会写入目标目录；请重新拉取或下载仓库，不要忽略校验错误。

**GitHub 提供备份与分发，宠物仍安装在每台电脑本地。** 每台电脑需要安装一次；仓库后续有更新时，需要手动拉取并运行安装脚本。

## 动作与格式

| 动作 | 帧数 | 含义 |
| --- | ---: | --- |
| idle | 6 | 安静待机、呼吸与眨眼 |
| running-right | 8 | 向右移动 |
| running-left | 8 | 向左移动 |
| waving | 4 | 招手 |
| jumping | 5 | 跳跃 |
| failed | 8 | 沮丧与恢复 |
| waiting | 6 | 等待回应或确认 |
| running | 6 | 原地专注工作 |
| review | 6 | 仔细检查 |

精灵图：透明 WebP，1536 × 2288 像素，8 列 × 11 行，每格 192 × 208。`pet.json` 使用 `spriteVersionNumber: 2`。最后两行共 16 个视线方向，按顺时针从向上开始。

## 仓库内容

```text
pets/             四只猫的实际安装文件
previews/         待机、招手、工作、跳跃 GIF 预览
install.py        校验、安装、幂等跳过与备份更新
manifest.json     配置和精灵图的 SHA-256 清单
VALIDATION.json   可移植的交付检查摘要
tests/            安装脚本测试
```

宠物已完成精灵图尺寸、透明边缘、帧数、动作语义和方向检查；三位独立盲评员检查方向，随后进行完整视觉复核。部分斜向视线较含蓄、角度间隔不完全均匀，作为轻微差异保留；尤其橘钳的 112.5° 下方分量在单帧盲评中不明显，经相邻姿态复核后接受。具体方向记录见 `VALIDATION.json` 的 `accepted_direction_warnings`。

运行安装测试：

```bash
python3 -m unittest discover -s tests -v
```

测试使用临时目录，不会改动真实 Codex 宠物。覆盖初次安装、重复安装、冲突保护、旧版本备份、单只安装、损坏源文件拒绝和符号链接保护。

## 来源

这些是使用 AI 图像生成与确定性精灵图组装制作的冒险猫伙伴，不是游戏官方素材。此仓库用于个人跨电脑安装与维护，未附加开源许可证。

参考：[OpenAI 官方宠物使用说明](https://learn.chatgpt.com/docs/pets)。本仓库安装的是桌面客户端 v2 宠物，不依赖网页版宠物上传入口。
