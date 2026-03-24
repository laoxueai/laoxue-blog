# laoxue-blog

老薛的个人博客框架，基于：

- Hugo
- PaperMod
- GitHub
- Cloudflare Pages

## 本地预览

```bash
cd laoxue-blog
hugo server -D
```

打开 <http://localhost:1313>

## 构建

```bash
hugo --minify
```

产物在 `public/`

## 目录结构

- `content/posts/`：文章
- `static/`：静态文件（favicon、图片等）
- `themes/PaperMod/`：主题
- `hugo.toml`：站点配置
- `wrangler.jsonc`：Cloudflare Pages 输出配置

## GitHub 建仓建议

仓库名建议：`laoxue-blog`

```bash
git add -A
git commit -m "init: Hugo blog scaffold"
# 之后创建 GitHub 仓库并 push
```

## Cloudflare Pages 配置

- Framework preset: `Hugo`
- Build command: `hugo --minify`
- Build output directory: `public`
- Environment variable:
  - `HUGO_VERSION=0.159.0`

## 域名建议

建议二选一：

1. **主站直接做博客**：`laoxue.ai`
   - 适合你把博客当作个人官网
2. **子域名单独做博客**：`blog.laoxue.ai`
   - 更灵活，以后主域还能做首页/名片站/导航站

如果没有强烈偏好，我建议你：

- `laoxue.ai` 先做一个极简主页或后续再做
- **博客先上 `blog.laoxue.ai`**

这样不容易把主域用死。
