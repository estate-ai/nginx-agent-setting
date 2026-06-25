-- franchise-service 스키마 (공정거래위원회 가맹사업 공개정보 적재용).
-- 출처: 공공데이터포털 15110265 getBrandFntnStats(예상 창업비용),
--       15110241 getBrandFrcsStats(평균 월매출/가맹점 통계).
-- 서비스 간 FK는 만들지 않고(code+snapshot 정책), 같은 논리 DB 안에서만 FK를 유지한다.

CREATE TABLE IF NOT EXISTS franchise_data_sources (
    id BIGSERIAL PRIMARY KEY,
    source_code VARCHAR(100) NOT NULL UNIQUE,
    source_name VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    source_url TEXT NOT NULL,
    api_name VARCHAR(150),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS franchise_ingest_batches (
    id BIGSERIAL PRIMARY KEY,
    source_id BIGINT NOT NULL REFERENCES franchise_data_sources(id) ON DELETE CASCADE,
    requested_path TEXT,
    request_params_json JSONB,
    result_code VARCHAR(50),
    result_message TEXT,
    total_count INTEGER,
    fetched_count INTEGER,
    fetched_at TIMESTAMP NOT NULL DEFAULT NOW(),
    raw_response_ref TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS franchise_industries (
    id BIGSERIAL PRIMARY KEY,
    industry_code VARCHAR(80) NOT NULL UNIQUE,
    induty_lclas_nm VARCHAR(100) NOT NULL,
    induty_mlsfc_nm VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (induty_lclas_nm, induty_mlsfc_nm)
);

CREATE TABLE IF NOT EXISTS franchise_brands (
    id BIGSERIAL PRIMARY KEY,
    brand_code VARCHAR(120) NOT NULL UNIQUE,
    brand_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    industry_id BIGINT REFERENCES franchise_industries(id) ON DELETE SET NULL,
    operation_type VARCHAR(100),
    description TEXT,
    official_url TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (brand_name, company_name)
);

-- 공공데이터포털 15110265 getBrandFntnStats (예상 창업비용)
CREATE TABLE IF NOT EXISTS franchise_startup_costs (
    id BIGSERIAL PRIMARY KEY,
    brand_id BIGINT NOT NULL REFERENCES franchise_brands(id) ON DELETE CASCADE,
    industry_id BIGINT REFERENCES franchise_industries(id) ON DELETE SET NULL,
    source_id BIGINT REFERENCES franchise_data_sources(id) ON DELETE SET NULL,
    ingest_batch_id BIGINT REFERENCES franchise_ingest_batches(id) ON DELETE SET NULL,
    base_year INTEGER NOT NULL,
    jng_bzmn_jng_amt BIGINT,
    jng_bzmn_edu_amt BIGINT,
    jng_bzmn_etc_amt BIGINT,
    jng_bzmn_assrnc_amt BIGINT,
    smtn_amt BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (brand_id, base_year)
);

-- 공공데이터포털 15110241 getBrandFrcsStats (평균 월매출 / 가맹점 통계)
CREATE TABLE IF NOT EXISTS franchise_sales_stats (
    id BIGSERIAL PRIMARY KEY,
    brand_id BIGINT NOT NULL REFERENCES franchise_brands(id) ON DELETE CASCADE,
    industry_id BIGINT REFERENCES franchise_industries(id) ON DELETE SET NULL,
    source_id BIGINT REFERENCES franchise_data_sources(id) ON DELETE SET NULL,
    ingest_batch_id BIGINT REFERENCES franchise_ingest_batches(id) ON DELETE SET NULL,
    base_year INTEGER NOT NULL,
    frcs_cnt INTEGER,
    new_frcs_rgs_cnt INTEGER,
    ctrt_end_cnt INTEGER,
    ctrt_cncltn_cnt INTEGER,
    nm_chg_cnt INTEGER,
    avrg_sls_amt BIGINT,
    ar_unit_avrg_sls_amt BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (brand_id, base_year)
);

CREATE INDEX IF NOT EXISTS idx_franchise_brands_name
    ON franchise_brands (brand_name);
CREATE INDEX IF NOT EXISTS idx_franchise_brands_industry
    ON franchise_brands (industry_id);
CREATE INDEX IF NOT EXISTS idx_franchise_startup_costs_base_year
    ON franchise_startup_costs (base_year);
CREATE INDEX IF NOT EXISTS idx_franchise_sales_stats_base_year
    ON franchise_sales_stats (base_year);
