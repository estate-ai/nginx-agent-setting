-- V6/V7 키워드 분류 후에도 미분류('기타/거친분류')로 남은 브랜드 중,
-- 추정매출 상위 30개를 브랜드 식별(웹검색/개별판단) 기반으로 서울 100업종에 명시적으로 매핑한다.
-- 키워드 규칙으로는 단서가 없어 잡히지 않던 추상 브랜드명을 brand_code 단위로 직접 override한다.
--
-- 효과 컬럼: COALESCE(franchise_brands.market_svc_induty_cd, franchise_industries.market_svc_induty_cd).
-- 서울 상권분석에 대응 업종이 없는 브랜드(운송/식자재유통/배달대행/복지서비스/키즈놀이터 등)는
-- 잘못된 분류를 만들지 않기 위해 의도적으로 NULL로 남긴다(아래 '제외' 목록 참고).

-- ===== 슈퍼마켓 (CS300001) : 종합소매/식료품 매장 =====
UPDATE franchise_brands SET market_svc_induty_cd='CS300001', market_svc_induty_cd_nm='슈퍼마켓'
 WHERE brand_code='FB6d0e0ec487a8aba56b39742f8f8d47'; -- 홈플러스익스프레스(SSM)
UPDATE franchise_brands SET market_svc_induty_cd='CS300001', market_svc_induty_cd_nm='슈퍼마켓'
 WHERE brand_code='FB34f8605c1720d5e8ad236bfb8718d1'; -- 자연드림(유기농 종합매장)

-- ===== 분식전문점 (CS100008) =====
UPDATE franchise_brands SET market_svc_induty_cd='CS100008', market_svc_induty_cd_nm='분식전문점'
 WHERE brand_code='FB04aef03146f7651432c62fcf8640ee'; -- 삼진어묵(어묵/분식)

-- ===== 한식음식점 (CS100001) : 한식/고기구이/탕·찜/냉면/샤브샤브 =====
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FB6eadc92c1b6104e67197500057b29b'; -- 우텐더(한우 전문)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FB30da61c6e387e2f93f7c060b87006e'; -- 황금소(소고기 전문)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FB477e662840aa7a9798f1d17037f9cc'; -- 마장동골목집(고기구이)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FB2d0373f2819b571dedd520d4500393'; -- 오장동흥남집(함흥냉면)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FB88b599b0ab6fd9a6e6df03154e16ce'; -- 소담촌(보쌈/한식)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FBe3f038fa66d31bf103f3d301707543'; -- 신도세기(고기 무한리필)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FB810e7cddaed34badb907554c899615'; -- 미미옥(들기름막국수/한식)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FBf3341e830ccdac64a6f84f935ea554'; -- 돈수백(돼지고기 전문)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FB88529c4b5076f7949635e5554a12a7'; -- 농장사람들(쌈밥/한식)
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FB8806d9d481e5e7dede1aca41eafbce'; -- 봄담아(샤브샤브 전문) [웹검색 확인]
UPDATE franchise_brands SET market_svc_induty_cd='CS100001', market_svc_induty_cd_nm='한식음식점'
 WHERE brand_code='FBa863c061bd50326cab3a6523f8ee99'; -- 무야호랜드(고기 무한리필) [웹검색 확인]

-- ===== 양식음식점 (CS100004) =====
UPDATE franchise_brands SET market_svc_induty_cd='CS100004', market_svc_induty_cd_nm='양식음식점'
 WHERE brand_code='FBa3d5bbb2384b48a952f5f2b160ddcd'; -- 로니로티(파스타/스테이크/피자) [웹검색 확인]

-- ===== 호프-간이주점 (CS100009) =====
UPDATE franchise_brands SET market_svc_induty_cd='CS100009', market_svc_induty_cd_nm='호프-간이주점'
 WHERE brand_code='FB22475da13a52c32f8b0d6212cac113'; -- 골치기(안주/술집) [웹검색 확인]

-- ===== 안경 (CS300016) =====
UPDATE franchise_brands SET market_svc_induty_cd='CS300016', market_svc_induty_cd_nm='안경'
 WHERE brand_code='FB5df8202f6a121d0a54771adb0d17f4'; -- 하파크리스틴(컬러렌즈) [웹검색 확인]

-- ===== 시계및귀금속 (CS300017) : 웨딩주얼리 =====
UPDATE franchise_brands SET market_svc_induty_cd='CS300017', market_svc_induty_cd_nm='시계및귀금속'
 WHERE brand_code='FBd933e16454f4238d95855595a3376c'; -- 반조애(VANZOE, 웨딩주얼리) [웹검색 확인]
UPDATE franchise_brands SET market_svc_induty_cd='CS300017', market_svc_induty_cd_nm='시계및귀금속'
 WHERE brand_code='FB42419010a58a1e40f3a1a831a0dddb'; -- 바이가미(BYGAMI, 웨딩주얼리) [웹검색 확인]

-- ===== 제외(서울 상권분석에 대응 업종 없음 → NULL 유지) =====
-- FBee19eb2e00d65965ac0e96aaf244af 장집사(장애인 집수리 복지서비스)
-- FB4564b1b08795922eb318afd5338020 고요한택시 / FBbb2568c0f24ab9d1fccf1de21a8a4c 동방 (운송)
-- FBff31d5f9175b45b888178f7b8d1531 푸드머스(SL) / FB42ef16fd74b00b72fe88d5bc88e2e9 푸드머스(KIDS)
-- FB9a3f43958a9c3f39c4a00893e7dea2 풀무원(냉장) / FB4410d38701faf897b78869c8cb0555 알파오메가 (식자재/생활용품 유통)
-- FBa7ad5049cc06a81f517ce0f7f95c96 히어로플레이파크(키즈 실내놀이터)
-- FBdad238293385cb0fb3a9f284e4f1dc 메이크어딜리버리(배달대행)
-- FB194f664c07ed504e4312ed7ca47aaa 사랑마루 / FBc486d7dd29cbe3b7bec07c307d11a9 남부 (메뉴/업종 단서 없음)
