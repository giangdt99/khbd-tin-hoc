# Web Kế hoạch bài dạy Tin học 7 và 8

Trang web tĩnh (HTML/CSS/JS thuần), gồm 20 giáo án đã sửa, trang tổng quan chỉnh sửa, tìm kiếm, và link tải .docx/.pdf. Có màn hình nhập mật khẩu.

## Cấu trúc

- `docs/` : trang web đã build, đây là thư mục đem đi publish
- `source/` : 2 file .docx, file PDF tổng quan và `overview.json` (nội dung trang tổng quan)
- `build.py` : script tạo lại `docs/` từ `source/` (cần Python 3 và pandoc)
- `config.json` : tên trang, mật khẩu, bật/tắt hình ảnh

## Đưa lên GitHub Pages

1. Tạo repository mới trên GitHub (ví dụ `khbd-tin-hoc`), đặt Public (GitHub Pages bản miễn phí cần repo Public).
2. Tải toàn bộ thư mục này lên repository (nút "Add file" > "Upload files", hoặc `git push`).
3. Vào **Settings > Pages**. Ở mục **Build and deployment**, chọn Source = **Deploy from a branch**, Branch = **main**, thư mục = **/docs**, rồi Save.
4. Chờ 1-2 phút. Địa chỉ web sẽ là `https://<ten-tai-khoan>.github.io/<ten-repo>/`.

## Đổi mật khẩu hoặc tên trang

1. Sửa `config.json` (mục `password`, `site_title`, `site_subtitle`).
2. Cài pandoc (https://pandoc.org/installing.html), rồi chạy `python3 build.py`.
3. Upload lại thư mục `docs/` lên GitHub.

Mật khẩu mặc định: `tinhoc2026` (nên đổi ngay).

## Cập nhật nội dung

Thay file .docx mới trong `source/` (giữ nguyên tên file và thứ tự bài), chạy lại `python3 build.py`. Nếu thêm hoặc bớt bài, sửa danh sách `ids` ở đầu `build.py`.

## Lưu ý quan trọng

- **Mật khẩu chỉ là lớp chắn đơn giản chạy trong trình duyệt.** Nội dung vẫn nằm trong file HTML của repo Public, ai biết địa chỉ file hoặc xem mã nguồn đều đọc được. Đừng dùng cho nội dung cần bảo mật thật sự. Nếu cần bảo mật, dùng Cloudflare Access, Netlify password hoặc repo Private (GitHub Pro).
- Trang có thẻ `noindex` và `robots.txt` chặn công cụ tìm kiếm, nhưng điều này không ngăn người có link truy cập.
- Một số hình trong giáo án trích từ SGK (có bản quyền NXB Giáo dục Việt Nam). Nếu không muốn công khai hình, đặt `"include_images": false` trong `config.json` rồi build lại.
- Chạy thử trên máy: trong thư mục `docs/` gõ `python3 -m http.server 8000`, mở http://localhost:8000. Không mở trực tiếp bằng file:// vì màn hình mật khẩu cần chế độ https hoặc localhost.
