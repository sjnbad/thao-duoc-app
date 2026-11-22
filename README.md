# Thảo Dược Chữa Bệnh

Ứng dụng web tra cứu bài thuốc thảo dược bằng tiếng Việt, tổng hợp từ bản tóm tắt của 14 cuốn sách về thảo dược, tinh dầu và chăm sóc sức khỏe tự nhiên.

> **Lưu ý:** nội dung chỉ để tham khảo, không thay thế chẩn đoán và điều trị của bác sĩ. Các bản tóm tắt được viết lại bằng lời riêng, kèm ghi chú an toàn của app. App không chứa văn bản gốc của sách; dữ liệu tóm tắt được nén và mã hoá khi nhúng vào app.

## Cách app hoạt động

- Người dùng gõ triệu chứng → app liệt kê các cách chữa **từ dễ đến khó** (Dễ / Vừa / Khó). Mặc định chỉ hiện mức dễ nhất; mức vừa và khó bấm “Hiện thêm” mới thấy.
- Mức độ được tính theo nguyên liệu (dễ kiếm / cần mua / cây hoang dã khó kiếm ở VN) và cách làm (làm nhanh / cần pha chế, đun nấu / ngâm nhiều tuần, cầu kỳ). Cây có độc tính luôn xếp mức Khó và có nhãn cảnh báo.
- Mỗi cách có nút “Tôi chọn cách này”. Trên bản Claude, lượt chọn được đếm chung (cơ sở dữ liệu của artifact) và cách được chọn nhiều nhất được đề xuất lên đầu. Trên bản GitHub Pages, lựa chọn chỉ lưu trên máy người dùng.
- Không cho chọn chữ, sao chép, kéo thả, chuột phải hoặc in nội dung (chỉ ngăn sao chép thông thường, không ngăn được chụp màn hình).

## Chạy app

- **Cách nhanh nhất:** mở `app/index.html` bằng trình duyệt (máy tính hoặc điện thoại). File này đã gộp sẵn toàn bộ dữ liệu, chạy được không cần mạng, không cần máy chủ.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `app/` | `index.html` (app đã dựng) và `app.tpl.html` (mẫu giao diện, chưa có dữ liệu) |
| `summaries/<sách>/*.md` | Bản tóm tắt tiếng Việt từng cuốn, định dạng Markdown |
| `tools/build_app.py` | Dựng `app/index.html` từ `summaries/` và `tools/app_data/` |
| `tools/app_data/` | Từ điển triệu chứng, bảng “tóm tắt nhanh” kèm mức độ khó và cảnh báo cho từng triệu chứng |
| `tools/` (còn lại) | Script cũ: dựng PDF tóm tắt (`mkpdf.py`), chụp màn hình kiểm thử (`shot*.py`) |

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

```bash
pip install markdown
python3 tools/build_app.py      # đọc summaries/ + tools/app_data/ → app/index.html
```

`mkpdf.py` dùng đường dẫn cố định của môi trường làm việc ban đầu và cần thêm thư viện tạo PDF (xem phần `import` đầu file).
