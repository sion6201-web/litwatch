#!/bin/bash
# 매주 실행용 래퍼: conda 활성화 후 최근 7일 조회
cd "$(dirname "$0")"
source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true
python3 litwatch.py --since 7
