/**
 * Vercel 빌드 시 실행된다. 환경 변수 API_BASE_URL 을 읽어 js/env.js 를 만든다.
 * 바닐라 JS에는 번들러가 없으므로 이 방식으로 환경 변수를 주입한다.
 */
const fs = require("fs");
const path = require("path");

const url = process.env.API_BASE_URL || "http://127.0.0.1:8000";
const out = path.join(__dirname, "..", "js", "env.js");

fs.writeFileSync(out, `window.API_BASE_URL = ${JSON.stringify(url)};\n`);
console.log(`js/env.js 생성 완료: ${url}`);
