<p>
  <img src="https://raw.githubusercontent.com/TryWorld2026/TryWorld2026/main/assets/hero-light.svg#gh-light-mode-only" alt="试界 TryWorld — 尝试，即世界。Explore by Trying." width="100%">
  <img src="https://raw.githubusercontent.com/TryWorld2026/TryWorld2026/main/assets/hero-dark.svg#gh-dark-mode-only" alt="试界 TryWorld — 尝试，即世界。Explore by Trying." width="100%">
</p>

# 试界 TryWorld

来自宁夏的创作者。用 AI、代码和好奇心，把想法做成可以使用的东西。维护自己的项目，也为开源项目贡献修复、测试和客户端集成。

[个人网站](https://tryworld.com.cn) · [精选项目](#精选项目) · [开源贡献](#开源贡献) · [技术方向](#技术方向) · [全部仓库](https://github.com/TryWorld2026?tab=repositories) · [English](https://github.com/TryWorld2026/TryWorld2026/blob/main/README.md)

## 精选项目

两个我持续在做的项目。其余仓库是我为了学习而做的东西，不列在这里。

### 灵屿 Lingyu

**免费开源的 Windows 桌面灵动岛与工作台** —— [官网](https://lingyu.tryworld.com.cn/) · [仓库](https://github.com/TryWorld2026/Lingyu)

音乐、真实天气、专注计时与 AI，装在一个桌面胶囊和一个可调整大小的工作台里。无广告、无会员、无付费墙；AI 可连接本地模型或你自己的 API Key。目前 16 个 release，其中包含把整个客户端用 C# / .NET 10 / WPF 重写的原生版——旧客户端仍保留 Electron 实现。上游 eIsland 的账号、支付与会员依赖已移除，逐项恢复被封锁的能力。

C# / .NET 10 / WPF · Electron · React · TypeScript · GPL-3.0

### 纸上算法 Paper Algorithm

**把一句话变成成片的口播视频的 AI 技能集** —— [仓库](https://github.com/TryWorld2026/paper-algorithm)

三个 Agent Skills 把选题、写稿、打磨、出片、封面、标题和四平台发布计划串成一条流水线。两道硬闸门要求显式确认后才能渲染，另有一道机器检查在脚本展示之前就拦掉套话。33 star、5 fork——这里唯一被其他人真正用起来的项目。

Python · Agent Skills · HyperFrames · CC BY-SA 4.0

其余仓库是我为了学习而做的东西：一个 B 站人格鉴定生成器、一个中式恐怖文字冒险、两个体育计分板、一份国产 AI 零基础教程。它们都是真的、都过了测试，但那是练习，不是作品集。去[仓库列表](https://github.com/TryWorld2026?tab=repositories)看。
## 开源贡献

<!-- CONTRIBUTIONS:START -->
**42 个已合并 PR · 4 个外部项目**

我向外部开源项目贡献的成果，已被上游合并。

| 项目 | 已合并 PR |
| --- | --- |
| [magpie-community/plugins](https://github.com/magpie-community/plugins) | 2 |
| [yetone/magpie](https://github.com/yetone/magpie) | 30 |
| [ShDH-CMYK/heikesong-zuopin](https://github.com/ShDH-CMYK/heikesong-zuopin) | 1 |
| [open-city-ai/haidian](https://github.com/open-city-ai/haidian) | 9 |

**最近合并**

- [magpie-community/plugins #27](https://github.com/magpie-community/plugins/pull/27) — word-guard 0.1.1: a Gemini reply is masked too, streamed or whole
- [yetone/magpie #924](https://github.com/yetone/magpie/pull/924) — fix\(agent\): a provider&#x27;s Compact at reaches Codex&#x27;s on-disk catalog
- [magpie-community/plugins #26](https://github.com/magpie-community/plugins/pull/26) — model-map 0.1.1: a Gemini request&#x27;s model is mapped, and its reply names it back
- [yetone/magpie #873](https://github.com/yetone/magpie/pull/873) — fix\(gateway\): an account Antigravity turned away doesn&#x27;t rest
- [yetone/magpie #849](https://github.com/yetone/magpie/pull/849) — fix\(gui\): skip scheme registration inside Flatpak
- [yetone/magpie #814](https://github.com/yetone/magpie/pull/814) — fix\(gateway\): a compaction that broke off keeps the conversation&#x27;s stick
- [yetone/magpie #744](https://github.com/yetone/magpie/pull/744) — davsync: scope provider and library credentials during partial sync
- [yetone/magpie #772](https://github.com/yetone/magpie/pull/772) — fix\(gui\): a reply that broke off is told as failed everywhere

[完整合并记录](https://github.com/TryWorld2026/TryWorld2026/blob/main/CONTRIBUTIONS.md) · [GitHub 已合并 PR](https://github.com/search?q=author%3ATryWorld2026+is%3Apr+is%3Apublic+is%3Amerged&type=pullrequests)

<sub>每天自动同步新合并的公开 PR。</sub>
<!-- CONTRIBUTIONS:END -->

## 技术方向

| 正在做的事 | 项目中使用的技术 |
| --- | --- |
| AI Agent 工具与客户端集成 | Go、API 网关、模型路由、配置管理与回归测试 |
| 桌面工具与交互 | TypeScript、React、Electron、C# / WPF |
| 实用 Web 产品与内容工作流 | JavaScript、Cloudflare Workers / D1、Python、Agent Skills |

项目问题、使用反馈和改进想法，欢迎在对应仓库提 Issue。想看每个项目的进展，[订阅 Releases](https://github.com/TryWorld2026?tab=repositories) 或直接到对应仓库提 Issue。

## 许可

本仓库（个人主页与贡献记录）采用 [MIT License](LICENSE)。各独立项目适用各自的许可证，见对应仓库。

---

<sub>尝试，即世界。Explore by Trying. · [tryworld.com.cn](https://tryworld.com.cn)</sub>
