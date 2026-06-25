-- 브랜드 업종은 상권분석 매핑/시각화를 위한 대표 업종으로만 관리한다.
-- 창업비용/매출통계 fact는 브랜드와 연도 기준의 지표로 저장한다.

ALTER TABLE franchise_brands
    RENAME COLUMN industry_id TO primary_industry_id;

ALTER TABLE franchise_brands
    RENAME CONSTRAINT franchise_brands_industry_id_fkey
    TO franchise_brands_primary_industry_id_fkey;

ALTER INDEX IF EXISTS idx_franchise_brands_industry
    RENAME TO idx_franchise_brands_primary_industry;

ALTER TABLE franchise_startup_costs
    DROP COLUMN IF EXISTS industry_id;

ALTER TABLE franchise_sales_stats
    DROP COLUMN IF EXISTS industry_id;
