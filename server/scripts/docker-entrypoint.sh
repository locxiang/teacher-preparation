#!/bin/bash
set -e

# 按需安装阿里云 NLS SDK（将 whl 放入 data/nls/ 目录即可）
for whl in /tmp/nls_whl/*.whl; do
  [ -f "$whl" ] || continue
  pip install -q "$whl" && echo "✓ NLS SDK 已安装" && break
done

exec python app.py
