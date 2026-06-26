package com.eodigage.franchise.application.brand;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.eodigage.franchise.infrastructure.persistence.brand.FranchiseBrandJdbcRepository;

@ExtendWith(MockitoExtension.class)
class FranchiseBrandQueryServiceTest {

    @Mock
    private FranchiseBrandJdbcRepository repository;

    @InjectMocks
    private FranchiseBrandQueryService service;

    @Test
    void getBrands_passesRequestedSizeToRepositoryLimit() {
        when(repository.findTopBrandsByIndustry("CS100010", 37)).thenReturn(List.of());

        service.getBrands(" CS100010 ", 37);

        verify(repository).findTopBrandsByIndustry("CS100010", 37);
    }

    @Test
    void getBrands_normalizesNegativeSizeToZero() {
        when(repository.findTopBrandsByIndustry(null, 0)).thenReturn(List.of());

        service.getBrands(" ", -1);

        verify(repository).findTopBrandsByIndustry(null, 0);
    }
}
