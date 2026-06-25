-- 프랜차이즈(공정위) 업종을 서울시 상권분석 업종(market_service_industries)으로 매핑한다.
--
-- 목적: 행정동 프랜차이즈 추천 화면에서 업종명을 상권분석 분류(앱 정본)로 통일 표기.
-- 정책:
--   * 표시 정본 = 서울 상권분석 업종명. 여기서는 코드(svc_induty_cd)와 표시용 스냅샷명만 보관(교차 서비스 FK 없음).
--   * 공정위 '기타' 버킷, 상권분석에 대응 업종이 없는 분류는 NULL로 두고 화면에서 '기타' 섹션으로 노출.
--   * 1:N(예: 이미용→미용실/네일숍/피부관리실)은 대표 1개로 축약. 근사 매핑은 주석 [근사]로 표기.
ALTER TABLE franchise_industries
    ADD COLUMN market_svc_induty_cd varchar(20),
    ADD COLUMN market_svc_induty_cd_nm varchar(100);

COMMENT ON COLUMN franchise_industries.market_svc_induty_cd IS '대응 서울 상권분석 업종코드(svc_induty_cd). 미매핑이면 NULL(기타)';
COMMENT ON COLUMN franchise_industries.market_svc_induty_cd_nm IS '대응 서울 상권분석 업종명 스냅샷(표시용). 미매핑이면 NULL';

-- 외식
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100001', market_svc_induty_cd_nm = '한식음식점'   WHERE induty_mlsfc_nm = '한식';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100003', market_svc_induty_cd_nm = '일식음식점'   WHERE induty_mlsfc_nm = '일식';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100002', market_svc_induty_cd_nm = '중식음식점'   WHERE induty_mlsfc_nm = '중식';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100004', market_svc_induty_cd_nm = '양식음식점'   WHERE induty_mlsfc_nm = '서양식';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100004', market_svc_induty_cd_nm = '양식음식점'   WHERE induty_mlsfc_nm = '기타 외국식';   -- [근사] 상권분석엔 비한중일=양식만 존재
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100004', market_svc_induty_cd_nm = '양식음식점'   WHERE induty_mlsfc_nm = '피자';          -- [근사] 양식 계열로 분류
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100007', market_svc_induty_cd_nm = '치킨전문점'   WHERE induty_mlsfc_nm = '치킨';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100008', market_svc_induty_cd_nm = '분식전문점'   WHERE induty_mlsfc_nm = '분식';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100005', market_svc_induty_cd_nm = '제과점'       WHERE induty_mlsfc_nm = '제과제빵';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100006', market_svc_induty_cd_nm = '패스트푸드점' WHERE induty_mlsfc_nm = '패스트푸드';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100009', market_svc_induty_cd_nm = '호프-간이주점' WHERE induty_mlsfc_nm = '주점';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100010', market_svc_induty_cd_nm = '커피-음료'     WHERE induty_mlsfc_nm = '커피';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100010', market_svc_induty_cd_nm = '커피-음료'     WHERE induty_mlsfc_nm = '음료 (커피 외)';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS100010', market_svc_induty_cd_nm = '커피-음료'     WHERE induty_mlsfc_nm = '아이스크림/빙수'; -- [근사] 디저트음료로 분류
-- '기타 외식' -> NULL(기타)

-- 서비스
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200028', market_svc_induty_cd_nm = '미용실'       WHERE induty_mlsfc_nm = '이미용';        -- [근사] 네일숍/피부관리실 포함, 대표=미용실
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200002', market_svc_induty_cd_nm = '외국어학원'   WHERE induty_mlsfc_nm = '교육 (외국어)';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200001', market_svc_induty_cd_nm = '일반교습학원' WHERE induty_mlsfc_nm = '교육 (교과)';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200024', market_svc_induty_cd_nm = '스포츠클럽'   WHERE induty_mlsfc_nm = '스포츠 관련';   -- [근사] 스포츠강습 포함, 대표=스포츠클럽
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200025', market_svc_induty_cd_nm = '자동차수리'   WHERE induty_mlsfc_nm = '자동차 관련';   -- [근사] 정비/세차 혼재, 대표=자동차수리
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200019', market_svc_induty_cd_nm = 'PC방'         WHERE induty_mlsfc_nm = 'PC방';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200021', market_svc_induty_cd_nm = '기타오락장'   WHERE induty_mlsfc_nm = '오락';          -- [근사] 노래방/게임장 등 포괄
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200031', market_svc_induty_cd_nm = '세탁소'       WHERE induty_mlsfc_nm = '세탁';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200033', market_svc_induty_cd_nm = '부동산중개업' WHERE induty_mlsfc_nm = '부동산 중개';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS200034', market_svc_induty_cd_nm = '여관'         WHERE induty_mlsfc_nm = '숙박';          -- [근사] 게스트하우스/고시원 포함, 대표=여관
UPDATE franchise_industries SET market_svc_induty_cd = 'CS300016', market_svc_induty_cd_nm = '안경'         WHERE induty_mlsfc_nm = '안경';          -- [축차이] 상권분석은 도소매(CS3)에 위치
UPDATE franchise_industries SET market_svc_induty_cd = 'CS300018', market_svc_induty_cd_nm = '의약품'       WHERE induty_mlsfc_nm = '약국';          -- [축차이] 상권분석엔 '약국'이 없어 도소매 '의약품'에 매핑
UPDATE franchise_industries SET market_svc_induty_cd = 'CS300029', market_svc_induty_cd_nm = '애완동물'     WHERE induty_mlsfc_nm = '반려동물 관련';  -- [근사] 용품/미용/병원 혼재, 대표=애완동물(도소매)
-- '유아 관련 (교육 외)', '유아관련', '임대', '기타 교육', '배달', '이사', '운송', '인력 파견', '기타 서비스' -> NULL(기타)

-- 도소매
UPDATE franchise_industries SET market_svc_induty_cd = 'CS300002', market_svc_induty_cd_nm = '편의점'       WHERE induty_mlsfc_nm = '편의점';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS300011', market_svc_induty_cd_nm = '일반의류'     WHERE induty_mlsfc_nm = '의류 / 패션';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS300022', market_svc_induty_cd_nm = '화장품'       WHERE induty_mlsfc_nm = '화장품';
UPDATE franchise_industries SET market_svc_induty_cd = 'CS300001', market_svc_induty_cd_nm = '슈퍼마켓'     WHERE induty_mlsfc_nm = '종합소매점';     -- [근사] 종합소매=슈퍼마켓에 근접
-- '기타도소매', '농수산물', '(건강)식품' -> NULL(기타)
