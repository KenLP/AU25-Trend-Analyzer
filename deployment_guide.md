# Hướng dẫn đưa Web App lên Online (Streamlit Cloud)

Cách nhanh nhất, miễn phí và ổn định nhất để đưa ứng dụng Python này lên web là sử dụng **Streamlit Community Cloud**.

### Bước 1: Chuẩn bị mã nguồn
Dữ liệu của bạn hiện đã được lưu đầy đủ trong `data/au_2025.json`. Vì Streamlit Cloud không thể chạy trình duyệt ảo (scraper) dễ dàng, chúng ta sẽ đưa **file dữ liệu đã cào sẵn** lên đó. Website sẽ hoạt động như một công cụ hiển thị (Dashboard).

Bạn cần đảm bảo thư mục dự án có các file sau (mình đã chuẩn bị xong hết):
- `app.py`: File chính chạy web.
- `requirements.txt`: Danh sách thư viện (streamlit, pandas...).
- `packages.txt`: (Tùy chọn, không cần thiết cho dashboard tĩnh).
- `data/au_2025.json`: Dữ liệu phân tích.
- `src/`: Thư mục mã nguồn xử lý.

### Bước 2: Đẩy code lên GitHub
Bạn cần có một tài khoản GitHub.
1. Tạo một repository mới trên GitHub (ví dụ: `au-trend-analyzer`).
2. Upload toàn bộ các file trong thư mục dự án hiện tại lên đó.

### Bước 3: Kết nối với Streamlit Cloud
1. Truy cập [share.streamlit.io](https://share.streamlit.io/) và đăng nhập bằng GitHub.
2. Nhấn nút **"New app"**.
3. Chọn repository `au-trend-analyzer` bạn vừa tạo.
4. Ở mục "Main file path", điền `app.py`.
5. Nhấn **"Deploy!"**.

### Kết quả
Sau khoảng 2-3 phút, Streamlit sẽ cài đặt các thư viện và cung cấp cho bạn một đường link dạng `https://au-trend-analyzer.streamlit.app`.

Bạn có thể chia sẻ link này cho bất kỳ ai. Mỗi khi bạn chạy scraper ở máy local và có dữ liệu mới, bạn chỉ cần upload đè file `data/au_2025.json` mới lên GitHub, website sẽ tự động cập nhật theo.
