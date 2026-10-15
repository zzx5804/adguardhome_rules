# Mihomo 规则集

## Padlet

- 源规则：[domain/Padlet.yaml](domain/Padlet.yaml)
- MRS 文件：[domain/Padlet.mrs](domain/Padlet.mrs)
- 域名来源：[Padlet 官方网络白名单](https://padlet.help/l/en/article/kl421e5wy6-which-padlet-s-domains-should-my-network-whitelist)
- 核对日期：2026-10-15，共 12 条，覆盖网站、实时协作、图片、文件和视频附件。

`+.example.com` 同时匹配域名本身和所有子域名；未加 `+.` 的两条规则只匹配指定主机。三项视频 CDN（`mediadelivery.net`、`b-cdn.net`、`cloudflarestream.com`）是共享服务，其上的其他网站流量也会匹配。此清单包含当前白名单，不包含官方单独列出的旧版存储域名。

配置示例（`默认代理` 替换成配置中已有的代理组）：

```yaml
proxy-groups:
  - name: Padlet
    type: select
    proxies: [默认代理, DIRECT]
    include-all: true

rule-providers:
  Padlet:
    type: http
    behavior: domain
    format: mrs
    interval: 86400
    url: https://raw.githubusercontent.com/zzx5804/adguardhome_rules/main/mihomo/domain/Padlet.mrs

rules:
  - RULE-SET,Padlet,Padlet
```

将规则放在通用直连、代理和兜底规则之前。策略组支持单独选择节点。

修改源文件后，用 Mihomo 重新生成 MRS，并将两份文件一起提交：

```sh
mihomo convert-ruleset domain yaml mihomo/domain/Padlet.yaml mihomo/domain/Padlet.mrs
```

这些文件用于 Mihomo 分流，不是 AdGuard Home 的广告过滤清单。
