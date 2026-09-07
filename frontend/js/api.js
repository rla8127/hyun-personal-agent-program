/** 백엔드 호출 래퍼. 모든 요청의 에러 메시지를 한 곳에서 정규화한다. */
const API = (() => {
  async function request(path, options = {}) {
    const res = await fetch(`${window.API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });

    if (!res.ok) {
      let detail = `요청 실패 (${res.status})`;
      try {
        const body = await res.json();
        if (typeof body.detail === "string") detail = body.detail;
        // Pydantic 검증 오류는 배열로 온다.
        else if (Array.isArray(body.detail)) detail = body.detail[0]?.msg ?? detail;
      } catch (_) { /* 본문이 JSON이 아니면 기본 메시지를 쓴다 */ }
      throw new Error(detail);
    }
    return res.status === 204 ? null : res.json();
  }

  return {
    getSummary: () => request("/api/data/summary"),

    listData: () => request("/api/data"),
    createData: (body) => request("/api/data", { method: "POST", body: JSON.stringify(body) }),
    updateData: (id, body) => request(`/api/data/${id}`, { method: "PUT", body: JSON.stringify(body) }),
    deleteData: (id) => request(`/api/data/${id}`, { method: "DELETE" }),

    listConversations: () => request("/api/conversations"),
    getConversation: (id) => request(`/api/conversations/${id}`),
    deleteConversation: (id) => request(`/api/conversations/${id}`, { method: "DELETE" }),

    chat: (message, conversationId) =>
      request("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message, conversation_id: conversationId }),
      }),
  };
})();
