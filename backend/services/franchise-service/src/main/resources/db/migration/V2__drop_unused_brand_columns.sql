-- 두 가맹사업 OpenAPI가 제공하지 않는 브랜드 확장 컬럼을 제거한다.
-- 브랜드-업종 관계는 현재 유지하고, 원본 업종은 fact 테이블의 industry_id로 조회한다.

ALTER TABLE franchise_brands
    DROP COLUMN IF EXISTS operation_type,
    DROP COLUMN IF EXISTS description,
    DROP COLUMN IF EXISTS official_url,
    DROP COLUMN IF EXISTS metadata_json;
