package com.eodigage.franchise.api.brand;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.eodigage.franchise.application.brand.FranchiseBrandQueryService;
import com.eodigage.franchise.application.brand.dto.FranchiseBrandListResponse;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

import lombok.RequiredArgsConstructor;

/**
 * ?꾨옖李⑥씠利?釉뚮옖?쒕퀎 李쎌뾽?덉긽鍮꾩슜/異붿젙留ㅼ텧 API.
 *
 * <p>?대? ?쒕퉬??market-service 異붿쿇)?먯꽌留??몄텧?쒕떎. ?낆쥌(industryCode, svc_induty_cd)?쇰줈
 * ?꾪꽣??異붿젙留ㅼ텧 ?대┝李⑥닚 理쒕? 20媛쒕? 諛섑솚?섎ŉ, 寃???뺣젹/?섏씠吏??듭뀡? ?먯? ?딅뒗??
 */
@RestController
@RequestMapping("/api/v1/franchises")
@Tag(name = "franchise")
@RequiredArgsConstructor
public class FranchiseBrandController {

    private final FranchiseBrandQueryService franchiseBrandQueryService;

    @GetMapping
    @Operation(
            operationId = "getFranchiseBrands",
            summary = "?낆쥌蹂??꾨옖李⑥씠利?釉뚮옖??紐⑸줉(異붿젙留ㅼ텧 ?곸쐞)"
    )
    public FranchiseBrandListResponse getBrands(
            @Parameter(description = "?곴텒遺꾩꽍 ?낆쥌肄붾뱶(svc_induty_cd) ?꾪꽣")
            @RequestParam(required = false) String industryCode,
            @Parameter(description = "반환 개수(기본 20). market-service가 전달한 추천 개수를 LIMIT으로 사용")
            @RequestParam(defaultValue = "20") int size
    ) {
        return franchiseBrandQueryService.getBrands(industryCode, size);
    }
}
