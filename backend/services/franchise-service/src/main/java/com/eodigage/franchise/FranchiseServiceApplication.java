package com.eodigage.franchise;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class FranchiseServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(FranchiseServiceApplication.class, args);
    }
}
