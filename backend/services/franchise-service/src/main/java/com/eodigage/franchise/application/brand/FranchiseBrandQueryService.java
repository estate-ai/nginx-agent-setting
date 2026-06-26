package com.eodigage.franchise.application.brand;

import java.util.List;

import org.springframework.stereotype.Service;

import com.eodigage.franchise.application.brand.dto.FranchiseBrandListResponse;
import com.eodigage.franchise.application.brand.dto.FranchiseBrandResponse;
import com.eodigage.franchise.infrastructure.persistence.brand.FranchiseBrandJdbcRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class FranchiseBrandQueryService {


    private final FranchiseBrandJdbcRepository repository;

    public FranchiseBrandListResponse getBrands(String industryCode, int size) {
        String filterIndustryCode = blankToNull(industryCode);
        int safeSize = Math.max(0, size);

        List<FranchiseBrandResponse> items = repository
                .findTopBrandsByIndustry(filterIndustryCode, safeSize)
                .stream()
                .map(FranchiseBrandResponse::from)
                .toList();

        return new FranchiseBrandListResponse(items);
    }

    private static String blankToNull(String value) {
        return (value == null || value.isBlank()) ? null : value.trim();
    }
}
