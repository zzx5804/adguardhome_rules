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

## 金融服务（券商与香港银行）

- 合并规则：[classical/Finance.list](classical/Finance.list)
- 来源和转换记录：[classical/Finance.sources.json](classical/Finance.sources.json)
- 上游：[LingJingMaster/Shadowrocket-Rules](https://github.com/LingJingMaster/Shadowrocket-Rules)
- 合并 `HK_Broker.list`、`HSBC_HK.list`、`HK_Banks_Direct.list`，共 211 条规则，覆盖券商、汇丰香港及其他香港银行。

此规则集同时包含域名、关键词和 IP，使用一个 `classical/text` 提供者。MRS 只能单独保存域名或 IP，不能在一个 MRS 文件中保留全部这些规则。

上游唯一的 `URL-REGEX,^https?://www\.sc\.com/hk/` 转换为 `DOMAIN,www.sc.com`。Mihomo 无法按 HTTPS 路径匹配，因此会覆盖 `www.sc.com` 的所有路径；其余规则原样保留匹配语义，仅规范化 IP 网段并去除完全重复条目。源规则的 MIT 许可全文保留在合并文件的注释中。

合并后银行和券商统一跟随“金融服务”策略组。示例默认香港，也可选择单个订阅节点或 `DIRECT`。若需要银行直连而券商走代理，应拆成不同规则集。

```yaml
proxy-groups:
  - name: 金融服务
    type: select
    proxies: [香港策略, 默认代理, DIRECT]
    include-all: true

rule-providers:
  Finance:
    type: http
    behavior: classical
    format: text
    interval: 86400
    url: https://raw.githubusercontent.com/zzx5804/adguardhome_rules/main/mihomo/classical/Finance.list

rules:
  - RULE-SET,Finance,金融服务,no-resolve
```

金融规则应放在通用广告、直连和代理分流之前，以免银行与券商的专用接口被其他分类先匹配。客户端每天检查本仓库的规则更新；更新上游内容后运行下面命令重建，再提交生成文件：

```sh
python scripts/build-finance.py
```

使用 `--ref <commit>` 可复现指定上游版本。本规则集来源为社区维护的网络分流清单，下载和匹配成功不代表实际银行或券商账户服务可访问。
