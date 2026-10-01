<p>
  <img src="https://raw.githubusercontent.com/TryWorld2026/TryWorld2026/main/assets/hero-light.svg#gh-light-mode-only" alt="TryWorld — Explore by Trying. AI tools, desktop utilities, and open source." width="100%">
  <img src="https://raw.githubusercontent.com/TryWorld2026/TryWorld2026/main/assets/hero-dark.svg#gh-dark-mode-only" alt="TryWorld — Explore by Trying. AI tools, desktop utilities, and open source." width="100%">
</p>

# TryWorld · 试界

**尝试，即世界。Explore by Trying.**

我把想法做成能用的工具：AI 工作流、桌面应用，以及解决日常问题的 Web 产品。维护自己的项目，也为开源项目贡献修复、测试和客户端集成。

[开源贡献](#开源贡献) · [技术方向](#技术方向) · [全部仓库](https://github.com/TryWorld2026?tab=repositories) · [English](https://github.com/TryWorld2026/TryWorld2026/blob/main/README.en.md)

## 开源贡献

为 [Magpie](https://github.com/yetone/magpie) 贡献 Agent 集成、网关可靠性和配置数据保护。下面的贡献已被上游合并，讨论、测试和具体改动都可以在原 PR 中查看。

| 已合并贡献 | PR |
| --- | --- |
| 修正推理强度 `off` 被拒绝时的重试行为 | [#401](https://github.com/yetone/magpie/pull/401) |
| 遇到不可读的供应商配置时保留原文件，避免编辑覆盖 | [#415](https://github.com/yetone/magpie/pull/415) |
| 无密钥导出时排除余额查询令牌 | [#418](https://github.com/yetone/magpie/pull/418) |
| 保留配置快照中的默认字段值 | [#421](https://github.com/yetone/magpie/pull/421) |
| 覆盖会话路由轮询中间更新的回归测试 | [#424](https://github.com/yetone/magpie/pull/424) |

**近期提交**

- [Reasonix Studio 2.x 原生适配 · #427](https://github.com/yetone/magpie/pull/427)：客户端检测、模型与模型组选择、配置恢复、原生 CLI 接入。
- [顶部导航缩放修复 · #428](https://github.com/yetone/magpie/pull/428)：处理 Windows 小数坐标误差，让放大后的窗口恢复正确布局。

近期提交的合并状态以各 PR 页面为准。

## 技术方向

| 正在做的事 | 项目中使用的技术 |
| --- | --- |
| AI Agent 工具与客户端集成 | Go、API 网关、模型路由、配置管理与回归测试 |
| 桌面工具与交互 | TypeScript、React、Electron |
| 实用 Web 产品与内容工作流 | JavaScript、Cloudflare Workers / D1、Python、Agent Skills |

项目问题、使用反馈和改进想法，欢迎在对应仓库提 Issue。

<sub>从好奇开始，在实践中完善，分享给更多人。</sub>
