import { z } from "zod";

/**
 * RFC 7807 Problem Details for HTTP APIs
 * 스프링 부트 등에서 표준으로 사용하는 에러 응답 규격입니다.
 */
export const problemDetailSchema = z.object({
  type: z.string().optional(),
  title: z.string().optional(),
  status: z.number().optional(),
  detail: z.string().optional(),
  instance: z.string().optional(),
});

/**
 * 프론트엔드 HTTP 클라이언트(Axios/Orval 등)에서 던지는 Error 객체 래퍼
 * (Error 인스턴스이면서, 백엔드가 내려준 에러 바디가 info 에 담겨있음)
 */
export const problemDetailErrorSchema = z.instanceof(Error).and(
  z.object({
    info: problemDetailSchema,
    status: z.number().optional(),
  })
);
