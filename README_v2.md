# 抖音监控 v2 - GitHub Actions 版

## 改进点

1. **历史时间序列** - history.json 保存每次记录，支持多天对比
2. **每小时运行** - 提高监控频率
3. **增长榜输出** - 自动排序显示增长最快的视频

## 文件说明

- `fetch_v2.py` - 改进版抓取脚本（支持历史序列）
- `.github/workflows/fetch_v2.yml` - GitHub Actions 配置
- `history.json` - 历史数据（时间序列）
- `data.json` - 最新数据（含增量）

## 部署步骤

1. 替换原有文件：
   ```bash
   # 备份旧版本
   mv fetch.py fetch_old.py
   mv .github/workflows/fetch.yml .github/workflows/fetch_old.yml
   
   # 使用新版本
   cp fetch_v2.py fetch.py
   cp .github/workflows/fetch_v2.yml .github/workflows/fetch.yml
   ```

2. 提交到 GitHub：
   ```bash
   git add .
   git commit -m "升级到 v2：支持历史时间序列"
   git push
   ```

3. 手动触发测试：
   - 进入 Actions 页面
   - 选择 "Douyin Monitor v2"
   - 点击 "Run workflow"

## history.json 结构

```json
{
  "7611118104329298353": [
    {"play_count": 100, "timestamp": 1772752000, "date": "2026-03-06"},
    {"play_count": 120, "timestamp": 1772838321, "date": "2026-03-07"}
  ]
}
```

## 下一步优化

- [ ] 添加 Discord 通知（爆款增长超阈值推送）
- [ ] 生成历史对比报告（24h/7d 增长榜）
- [ ] 导出 Excel 报表
