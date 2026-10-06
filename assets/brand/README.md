# 品牌资产 · Brand assets

试界 TryWorld 的主标与署名文件。主标几何取自 `avatar.svg` 与 `signature-*.svg`，不要用图像模型重画。

## 文件

| 文件 | 用途 |
| --- | --- |
| `avatar.svg` | 主标源文件，512×512 视框，深绿 tw 连写落在骨白底，圆角 72 |
| `avatar-1024.png` | GitHub / 微信等要求方形位图的场合 |
| `avatar-512.png` | GitHub 头像推荐尺寸 |
| `avatar-256.png` | 站内小尺寸引用 |
| `signature-green.svg` | 骨白底上的署名 |
| `signature-light.svg` | 深色底上的署名 |

## 上传为 GitHub 头像

GitHub 不接受 SVG 作为头像，请上传 PNG：

1. 打开 <https://github.com/settings/profile>
2. Profile picture → Upload new
3. 选 `avatar-512.png`
4. 拖到合适位置裁切后保存

缩小到 32px 时 tw 仍可辨认，这是验收标准。

## 生成方式

SVG 为唯一几何出处；PNG 由该 SVG 渲染导出，不是另行绘制：

```powershell
# 渲染（Edge 无头模式，无需额外依赖）
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu `
  --screenshot="avatar-512.png" --window-size=512,512 "avatar.html"
```

导出尺寸：1024 / 512 / 256，各尺寸等比缩放，均不裁切不溢出。