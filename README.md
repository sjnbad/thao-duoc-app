# Thảo Dược Chữa Bệnh

Ứng dụng web tra cứu bài thuốc thảo dược bằng tiếng Việt, tổng hợp từ bản tóm tắt của 14 cuốn sách về thảo dược, tinh dầu và chăm sóc sức khỏe tự nhiên.

> **Lưu ý:** nội dung chỉ để tham khảo, không thay thế chẩn đoán và điều trị của bác sĩ. Các bản tóm tắt được viết lại bằng lời riêng, kèm ghi chú an toàn của app; kho này **không** chứa văn bản gốc hay file PDF của các sách.

## Chạy app

- **Cách nhanh nhất:** mở `app/index.html` bằng trình duyệt (máy tính hoặc điện thoại). File này đã gộp sẵn toàn bộ dữ liệu, chạy được không cần mạng, không cần máy chủ.
- **Bản tách dữ liệu:** `app/index.src.html` + `app/data.json` + `app/lib.json` — cần chạy qua một máy chủ web, ví dụ:
  ```bash
  cd app && python3 -m http.server 8000
  # mở http://localhost:8000/index.src.html
  ```

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `app/` | App đã dựng (HTML + dữ liệu JSON) |
| `summaries/<sách>/*.md` | Bản tóm tắt tiếng Việt từng cuốn, định dạng Markdown |
| `tools/` | Script dựng dữ liệu app (`buildlib.py`, `assemble.py`, `build.py`), dựng PDF tóm tắt (`mkpdf.py`) và chụp màn hình kiểm thử (`shot*.py`) |

### Định dạng file tóm tắt

- `# Tiêu đề` — một chương.
- `## Tên mục — tr. N–M` — một mục; `tr.` là số trang trong sách gốc.
- Bên dưới là các gạch đầu dòng. Ghi chú an toàn viết dạng `*[Ghi chú của app: …]*`; gợi ý ngoài sách viết dạng `*Gợi ý thực hành (không có trong sách):*`.

## Các sách đã tóm tắt

| Mã thư mục | Sách |
|---|---|
| `herbal` | The Lost Book of Herbal Remedies |
| `axe` | Ancient Remedies for Modern Life — Dr. Josh Axe |
| `worwood` | The Complete Book of Essential Oils and Aromatherapy — Valerie Ann Worwood |
| `tisserand` | Essential Oil Safety — Robert Tisserand & Rodney Young |
| `cayenne` | Curing With Cayenne — Sam Biser & Richard Schulze |
| `aip` | The Autoimmune Protocol |
| `eden` | The Lost Garden of Eden |
| `survival` | Survival Herbal Remedies |
| `lb_prev`, `lb_healthy`, `lb_remedies`, `lb_youth`, `lb_superfoods` | Các cuốn Lost Book nhỏ |
| `viemxoang` | Bài báo "Tự chữa bệnh viêm xoang không cần thuốc" |

## Dựng lại

Các script trong `tools/` được viết cho môi trường làm việc ban đầu và dùng đường dẫn cố định (`/home/claude/sum`, `/home/claude/build`). Muốn chạy lại, sửa các đường dẫn đó cho khớp máy của bạn, rồi:

```bash
python3 tools/buildlib.py   # đọc summaries → lib.json
python3 tools/assemble.py   # ghép index.html
```

Cần Python 3; `mkpdf.py` cần thêm thư viện tạo PDF (xem phần `import` đầu file).
