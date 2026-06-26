package com.eodigage.franchise.application.brand.dto;

import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * ?꾨옖李⑥씠利?釉뚮옖??紐⑸줉 ?묐떟.
 *
 * <p>?뱀젙 ?낆쥌(svc_induty_cd)??釉뚮옖?쒕? 異붿젙留ㅼ텧 ?대┝李⑥닚?쇰줈 理쒕? 20媛?諛섑솚?쒕떎.
 * ?대? ?쒕퉬??market-service 異붿쿇)?먯꽌留??몄텧?섎?濡??섏씠吏?寃???듭뀡? ?먯? ?딅뒗??
 */
@Schema(description = "프랜차이즈 브랜드 목록(추정매출 상위)")
public record FranchiseBrandListResponse(
        List<FranchiseBrandResponse> items
) {
}
