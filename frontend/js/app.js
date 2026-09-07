/** 화면 조립 및 이벤트 처리. */

const state = {
  conversationId: null,  // 현재 열려 있는 대화 (null이면 새 대화)
  messages: [],
  editingId: null,       // 수정 중인 데이터 id
};

const $ = (sel) => document.querySelector(sel);
const el = {
  summary: $("#summary"),
  convList: $("#conversationList"),
  chatLog: $("#chatLog"),
  chatForm: $("#chatForm"),
  chatInput: $("#chatInput"),
  chatSend: $("#chatSend"),
  newChatBtn: $("#newChatBtn"),
  dataForm: $("#dataForm"),
  dataList: $("#dataList"),
  dateInput: $("#dateInput"),
  valueInput: $("#valueInput"),
  memoInput: $("#memoInput"),
  dataSubmit: $("#dataSubmit"),
  cancelEdit: $("#cancelEdit"),
  toast: $("#toast"),
  wakeNotice: $("#wakeNotice"),
};

/* ---------- 공통 ---------- */

let toastTimer;
function toast(message) {
  el.toast.textContent = message;
  el.toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.toast.hidden = true; }, 3000);
}

function setText(key, value) {
  const node = el.summary.querySelector(`[data-key="${key}"]`);
  if (node) node.textContent = value;
}

/* ---------- 데이터 요약 ---------- */

async function loadSummary() {
  try {
    const s = await API.getSummary();
    setText("period", s.period);
    setText("count", `${s.count}개`);
    setText("average", `${s.metrics.average}분`);
    setText("max", `${s.metrics.max}분`);
    setText("min", `${s.metrics.min}분`);
    setText("trend", s.trend);
  } catch (e) {
    toast(`요약을 불러오지 못했습니다: ${e.message}`);
  }
}

/* ---------- 데이터 CRUD ---------- */

async function loadData() {
  try {
    const rows = await API.listData();
    el.dataList.innerHTML = "";
    if (rows.length === 0) {
      el.dataList.innerHTML = '<li class="chat-empty">아직 데이터가 없습니다.</li>';
      return;
    }
    // 최신 날짜가 위로 오도록 뒤집는다.
    rows.slice().reverse().forEach((row) => {
      const li = document.createElement("li");

      const main = document.createElement("div");
      main.className = "data-main";
      main.innerHTML =
        `<div class="data-date">${row.date}</div>` +
        `<div><strong>${row.value}분</strong> <span class="data-memo">${row.memo || ""}</span></div>`;

      const editBtn = document.createElement("button");
      editBtn.className = "btn-icon";
      editBtn.textContent = "수정";
      editBtn.onclick = () => startEdit(row);

      const delBtn = document.createElement("button");
      delBtn.className = "btn-icon";
      delBtn.textContent = "삭제";
      delBtn.onclick = () => removeData(row.id);

      li.append(main, editBtn, delBtn);
      el.dataList.appendChild(li);
    });
  } catch (e) {
    toast(`데이터를 불러오지 못했습니다: ${e.message}`);
  }
}

function startEdit(row) {
  state.editingId = row.id;
  el.dateInput.value = row.date;
  el.valueInput.value = row.value;
  el.memoInput.value = row.memo || "";
  el.dataSubmit.textContent = "수정 저장";
  el.cancelEdit.hidden = false;
}

function resetForm() {
  state.editingId = null;
  el.dataForm.reset();
  el.dataSubmit.textContent = "추가";
  el.cancelEdit.hidden = true;
}

async function removeData(id) {
  if (!confirm("이 기록을 삭제할까요?")) return;
  try {
    await API.deleteData(id);
    toast("삭제했습니다.");
    await Promise.all([loadData(), loadSummary()]);
  } catch (e) {
    toast(`삭제 실패: ${e.message}`);
  }
}

el.dataForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    date: el.dateInput.value,
    value: Number(el.valueInput.value),
    memo: el.memoInput.value.trim(),
  };
  try {
    if (state.editingId) {
      await API.updateData(state.editingId, body);
      toast("수정했습니다.");
    } else {
      await API.createData(body);
      toast("추가했습니다.");
    }
    resetForm();
    await Promise.all([loadData(), loadSummary()]);
  } catch (err) {
    toast(`저장 실패: ${err.message}`);
  }
});

el.cancelEdit.addEventListener("click", resetForm);

/* ---------- 채팅 ---------- */

function renderChat() {
  el.chatLog.innerHTML = "";
  if (state.messages.length === 0) {
    el.chatLog.innerHTML = '<p class="chat-empty">질문을 입력해 대화를 시작하세요.</p>';
    return;
  }
  state.messages.forEach((m) => {
    const div = document.createElement("div");
    div.className = `msg ${m.role}`;
    div.textContent = m.content;
    el.chatLog.appendChild(div);
  });
  el.chatLog.scrollTop = el.chatLog.scrollHeight;
}

function showLoading() {
  const div = document.createElement("div");
  div.className = "msg assistant loading";
  div.id = "loadingBubble";
  div.textContent = "AI가 답변을 작성하는 중...";
  el.chatLog.appendChild(div);
  el.chatLog.scrollTop = el.chatLog.scrollHeight;
}

el.chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = el.chatInput.value.trim();
  if (!message) return;

  state.messages.push({ role: "user", content: message });
  renderChat();
  el.chatInput.value = "";
  el.chatSend.disabled = true;
  showLoading();

  try {
    const res = await API.chat(message, state.conversationId);
    state.conversationId = res.conversation_id;
    state.messages.push({ role: "assistant", content: res.reply });
    renderChat();
    await loadConversations();
  } catch (err) {
    // 실패한 질문은 되돌려 사용자가 다시 시도할 수 있게 한다.
    state.messages.pop();
    renderChat();
    el.chatInput.value = message;
    toast(`답변 실패: ${err.message}`);
  } finally {
    el.chatSend.disabled = false;
  }
});

/* ---------- 대화 기록 ---------- */

async function loadConversations() {
  try {
    const rows = await API.listConversations();
    el.convList.innerHTML = "";
    if (rows.length === 0) {
      el.convList.innerHTML = '<li class="chat-empty">저장된 대화가 없습니다.</li>';
      return;
    }
    rows.forEach((c) => {
      const li = document.createElement("li");
      if (c.id === state.conversationId) li.classList.add("active");

      const title = document.createElement("span");
      title.className = "conv-title";
      title.textContent = `${c.title} (${c.message_count})`;
      title.onclick = () => openConversation(c.id);

      const delBtn = document.createElement("button");
      delBtn.className = "btn-icon";
      delBtn.textContent = "×";
      delBtn.onclick = (e) => { e.stopPropagation(); removeConversation(c.id); };

      li.append(title, delBtn);
      el.convList.appendChild(li);
    });
  } catch (e) {
    toast(`대화 목록을 불러오지 못했습니다: ${e.message}`);
  }
}

async function openConversation(id) {
  try {
    const conv = await API.getConversation(id);
    state.conversationId = conv.id;
    state.messages = conv.messages;
    renderChat();
    await loadConversations();
  } catch (e) {
    toast(`대화를 불러오지 못했습니다: ${e.message}`);
  }
}

async function removeConversation(id) {
  if (!confirm("이 대화를 삭제할까요?")) return;
  try {
    await API.deleteConversation(id);
    if (state.conversationId === id) startNewChat();
    await loadConversations();
  } catch (e) {
    toast(`삭제 실패: ${e.message}`);
  }
}

function startNewChat() {
  state.conversationId = null;
  state.messages = [];
  renderChat();
  loadConversations();
}

el.newChatBtn.addEventListener("click", startNewChat);

/* ---------- 초기화 ---------- */

async function init() {
  el.dateInput.value = new Date().toISOString().slice(0, 10);
  renderChat();

  // Render 무료 티어는 첫 요청이 느리다. 3초 넘게 걸리면 안내를 띄운다.
  const noticeTimer = setTimeout(() => { el.wakeNotice.hidden = false; }, 3000);
  await Promise.all([loadSummary(), loadData(), loadConversations()]);
  clearTimeout(noticeTimer);
  el.wakeNotice.hidden = true;
}

init();
