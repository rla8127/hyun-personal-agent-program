/**
 * 백엔드 API 주소.
 * - 로컬: 아래 기본값(http://127.0.0.1:8000)이 사용된다.
 * - Vercel 배포: 빌드 시 scripts/build-config.js 가 env.js 를 생성해 이 값을 덮어쓴다.
 */
window.API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";
