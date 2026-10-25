# SHEL ADS 통합 후 정규 시계열 계약

2026-10-25 검토. SHEL은 GEV의 분사 보통주와 다른 `SPONSORED_ADS / ADS_CLASS_UNIFICATION_SUCCESSOR` 사건으로 등록한다. 발행사 설립일이나 회사의 최초 상장일을 새로 정의하지 않는다.

## 확인한 원인과 자료

10월23일 미국 full 실행 `20261023T185657_local-scheduler-us-full`과 재개 `20261023T232607_local-scheduler-us-full`은 29종목 성공·SHEL 1종목 실패였다. SHEL의 KIS 전체 이력은 기존 5년 요청 범위를 충족하지 못해 거절됐다. 완전한 같은 시장 full 기준선이 없으면 후속 overlay도 거절하는 계약을 그대로 유지한다. 실패 원문에는 수집된 전체 시계열 영수증이 없으므로 이 감사만으로 당시 KIS의 첫 반환 행을 확정하지 않는다.

서로 다른 근거의 역할을 구분한다.

| 근거 | 확인 범위 |
|---|---|
| [Shell 2021 공시 모음](https://www.shell.com/news-and-insights/newsroom/news-and-media-releases/_jcr_content/root/main/section/simple_1285915735/call_to_action_copy__162139957/links/item0.stream/1742566965484/55dda471d98bce808e2b5d62df100a503d9b1ca8/2021-press-releases.pdf), 175~177쪽 | 2021-12-20의 **예정 일정**: 2022-01-31 SHEL WI 조건부 거래, 2022-02-01 SHEL 정규 거래. 새 ADS의 ISIN `US7802593050`, CUSIP `780259305`, SEDOL `BPK3CG3`와 이전 RDS.A/RDS.B 식별자를 구분한다. |
| [Shell 2022 공시 모음](https://www.shell.com/news-and-insights/newsroom/news-and-media-releases/_jcr_content/root/main/section/simple_1285915735/call_to_action_copy__876059154/links/item0.stream/1742566955507/e7fdc6470f3fac2d5279ce45b136e5d54038947e/2022-press-releases.pdf), 19쪽 | 2022-01-31 공시는 1월29일 A/B 통합과 Simplification 실행 완료를 확인하고 앞선 거래·정산 일정으로 연결한다. 이 문서만으로 2월1일 실제 거래 시작을 직접 관측했다고 주장하지 않는다. |
| [현재 Shell 주식 정보](https://www.shell.com/investors/information-for-shareholders/share-information.html) | 통합 완료, 이전 ADS 1개당 새 ADS 1개, 새 ADS 1개당 보통주 2개를 사후 확인한다. |
| 새 KIS 현재 metadata 영수증 | 실제 2026-10-25 14:15:07 UTC 수집. 같은 ISIN·SEDOL·명칭, NYSE/USD, `lstg_dt=20220201`, 상장 Y/폐지 N/현재 이전종목 필드 공백을 대조한다. |

따라서 정규 시작일은 예정 공시, 사후 통합 완료 확인, 현재 KIS의 정확한 식별자·상장일을 교차 검증해 사용한다. 공개 종목 master의 이름이나 첫 관측 봉으로 추정하지 않는다. 공개 master의 DR 표시만으로 ADS 여부를 확정하지 않는다.

## 적용과 보존

- 원래 5년 계산 요청은 영수증의 `original_requested_start`에 보존한다. 검증된 현재 ADS 후속 증권의 2022-02-01 이후 모든 완료 정규 거래일이 필요하다. 2022-01-31 when-issued 행은 별도 제외 목록에 기록한다.
- RDS.A/RDS.B를 조회하거나 해당 가격을 새 시계열에 이어 붙이지 않는다. 가격·거래량을 2배 또는 절반으로 바꾸지 않는다. 단일 SHEL MODP=1 원문을 사용하며 정규 구간의 누락·잘못된 날짜·불량 OHLCV·페이지 무진전·미완료 최신 봉은 계속 거절한다.
- 정확한 현재 ISIN·CUSIP·SEDOL·명칭·거래소·통화·상장일·비폐지 상태와 공백인 현재 이전종목 필드를 요구한다. 이름에 포함된 ADS당 보통주 비율도 일치해야 한다. 다른 ADS나 보통주를 자동 등록하지 않는다.
- 원문 공시 수집 완료 시각 `2026-10-25T14:19:03.925670Z` 이전 분석에는 새 사건 검토를 소급 적용하지 않는다. 현재 metadata도 실제 수집 시각 이후, 300초 이내일 때만 인정한다. 이전 성공·실패 manifest와 승인 시각은 수정하지 않는다.
- 지표의 실제 관측 개수 검사, 원래 재시도·페이지·시간 한도, 완전 기준선 검사와 GEV 계약은 유지한다. 200일 지표는 관측치가 부족하면 계속 실패한다. 원래 시작일이 후속 ADS의 정규 시작일 이후인 성숙한 요청에는 별도 metadata 조회나 기간 예외를 적용하지 않는다.

## 증거와 검증 범위

원문 PDF·현재 주식 정보·수집 시각·SHA는 `G:/TradingAgentsData/migration-audits/shel-ads-official-evidence-20261025/`에 보존했다. 직접 GCS·SEC HTML 수집의 403 실패는 `receipt.json`에 남겼고, 발행사 공식 PDF의 성공은 별도 `receipt-pdf.json`에 기록했다. 실패를 덮어쓰지 않았다.

| 원문 | SHA-256 |
|---|---|
| 2021 공시 PDF | `67b4db48fb4bdb3ccef5dab3ef3662b7bb76ef35bee17f9065e1d04adbe268ee` |
| 2022 공시 PDF | `afe021804e2ced43263b557215ea132b6979f9ba1b6d718ca2546e3c40744f42` |
| 현재 주식 정보 HTML | `1489b770469db50570b805b29bf8f50d43f32507604aa3898ea43511daa59966` |
| root의 현재 KIS metadata 영수증 | `361ebe8bf9a5af12f09ed1dd113fd3d2acda2d960c18fe29835bd54f602eb300` |

외부 API 없는 ADS·GEV·성숙 종목의 관련 테스트 166개가 통과했다. 새 ADS 테스트는 정상·빈 응답·미래/누락/잘못된 날짜·다른 식별자·ADS 비율·종류·이전종목·영수증 정정·당시 미가용 검토·정규 봉 누락·when-issued 제외·지표 관측 부족을 검증한다. 최초 두 실패는 Mock이 잘못된 날짜 행을 API 응답 전에 걸러내거나 KeyError를 내던 fixture 문제였고, 실제 응답에 포함되도록 고친 뒤 최종 결과를 확인했다.

이 구현의 offline 검증은 실제 KIS 전체 시계열, 후속 정상 연구 완료, 승인, 전략 주문·체결, 비용 성과를 증명하지 않는다. 10월23일 원래 일일 4회 예산은 모두 사용했으며 초기화하지 않는다. 후속 기존 승인된 정상 실행에서 새 수집 증거를 검증한다. 실계좌 주문과 자동 실투자 전환은 비활성이다.
