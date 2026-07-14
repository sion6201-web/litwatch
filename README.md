# litwatch

관심 분야 키워드셋에 대해 **PubMed E-utilities + bioRxiv/medRxiv API + Europe PMC**를
한 번에 조회하고, 신규 문헌을 하나의 표로 뽑아주는 단일 파일 도구.

출력 표 컬럼: **date / original(원논문 여부) / relevance(직접 관련성) / preprint** + field / source / journal / title / doi / url / matched_keywords

- **Europe PMC** — 출판논문 + preprint 통합, abstract 포함(관련성 채점의 핵심 소스)
- **PubMed** — 권위 있는 출판논문(E-utilities esearch/esummary)
- **bioRxiv/medRxiv** — 네이티브 preprint(날짜 범위 + 제목 기반 필터)

세 소스는 DOI(없으면 정규화 제목) 기준으로 중복 제거된다.

## 설치

```bash
pip install -r requirements.txt        # requests, pyyaml 뿐
```

## 사용

```bash
python litwatch.py                     # config.yaml, 최근 since_days일
python litwatch.py --since 14          # 최근 14일
python litwatch.py --config my.yaml --out output/
```

결과는 `output/litwatch_YYYY-MM-DD.csv`(전량) 와 `.md`(요약, `report_min_relevance` 이상)로 저장.

## 설정 (`config.yaml`)

- `fields`: 관심 분야 목록. 각 field의 `keywords`는 **OR**로 묶여 검색된다. 여러 단어 구는 자동으로 `"..."` 처리.
- `since_days`: 기본 검색 기간(일).
- `report_min_relevance`: `high|medium|low` — 표/콘솔 표시 하한. **CSV엔 항상 전량 저장**.
- `sources`: europepmc/pubmed/biorxiv 개별 on/off.
- `ncbi_api_key`: 있으면 PubMed rate limit 3→10 req/s.
- `max_per_source`: 소스·분야당 상한.

### 관련성(relevance) 채점

- **high** — 키워드가 **제목**에 등장(또는 abstract에 2개 이상)
- **medium** — abstract에만 1개
- **low** — 쿼리엔 걸렸으나 반환 텍스트에 표면적으로 없음(제목/초록 미제공 등)

> 팁: bare 단어(예: `cortisol`)는 임상·내분비 논문을 대량 끌어온다.
> `cortisol biosensor`, `cortisol aptamer` 같이 **문맥 구(phrase)** 로 좁히면 신호대잡음이 크게 오른다.

## 매주 자동 실행 (cron)

```cron
# 매주 월요일 08:00, 최근 7일
0 8 * * 1 cd /home/synbeelab/litwatch && ./run_weekly.sh >> cron.log 2>&1
```

`crontab -e` 에 위 줄을 추가. `run_weekly.sh`가 conda 활성화 후 실행한다.

## 연구 wiki 연동(선택)

`output/*.md` 표를 그대로 paper-wiki 워치리스트/§13 분류 카드의 입력으로 쓸 수 있다.
high 관련성 + preprint 항목을 우선 트리아지하면 된다.

## 한계

- bioRxiv 날짜범위 API는 abstract를 안 주므로 **제목·카테고리 기반 필터**(Europe PMC가 같은 preprint를 abstract와 함께 커버하므로 대개 보완됨).
- PubMed esummary도 abstract가 없어 제목 기반 채점(Europe PMC MED 레코드가 보완).
- 관련성은 키워드 표면 매칭이라 의미기반이 아니다. 키워드셋 품질이 결과 품질을 좌우한다.
