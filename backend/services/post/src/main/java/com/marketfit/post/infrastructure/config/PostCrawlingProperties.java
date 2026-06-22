package com.marketfit.post.infrastructure.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.post.crawling")
public record PostCrawlingProperties(
        String defaultUrl,
        int timeoutSeconds,
        int articleDelayMillis,
        int maxInputCharacters
) {
    public PostCrawlingProperties(String defaultUrl, int timeoutSeconds) {
        this(defaultUrl, timeoutSeconds, 300, 12_000);
    }

    public PostCrawlingProperties {
        timeoutSeconds = timeoutSeconds <= 0 ? 10 : timeoutSeconds;
        articleDelayMillis = Math.max(0, articleDelayMillis);
        maxInputCharacters = maxInputCharacters <= 0 ? 12_000 : maxInputCharacters;
    }
}
