# Hướng dẫn chạy dự án AU Trend Analyzer

Dự án này bao gồm một công cụ thu thập dữ liệu (Scraper) và một ứng dụng web (App) để phân tích xu hướng từ các lớp học tại Autodesk University.

## Yêu cầu hệ thống

- Python 3.8 trở lên
- Trình duyệt web (Chrome/Edge/Firefox)

## Cài đặt

1.  **Cài đặt các thư viện cần thiết:**
    Mở terminal tại thư mục gốc của dự án và chạy lệnh sau:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Cài đặt trình duyệt cho Playwright:**
    Công cụ scraper sử dụng Playwright để tự động hóa trình duyệt. Bạn cần cài đặt các binary của trình duyệt:
    ```bash
    playwright install
    ```

## Cách chạy

### 1. Thu thập dữ liệu (Scraper)

Trước khi chạy ứng dụng phân tích, bạn cần có dữ liệu. Chạy scraper để thu thập thông tin các lớp học.

Lưu ý: Scraper sử dụng import tương đối, nên bạn cần chạy nó như một module từ thư mục gốc của dự án:

```bash
python -m src.scraper
```

*Mặc định, scraper được cấu hình để chạy thử nghiệm với giới hạn 5 lớp học (xem dòng cuối cùng trong `src/scraper.py`). Nếu muốn thu thập nhiều dữ liệu hơn, bạn có thể chỉnh sửa file `src/scraper.py` và thay đổi tham số `limit` hoặc bỏ giới hạn.*

Dữ liệu sẽ được lưu vào file: `data/au_2025.json`.

### 2. Chạy ứng dụng phân tích (App)

Sau khi đã có dữ liệu, bạn có thể khởi chạy giao diện web để xem phân tích:

```bash
streamlit run app.py
```

Sau khi chạy lệnh, ứng dụng sẽ tự động mở trong trình duyệt của bạn (thường là tại địa chỉ `http://localhost:8501`).

## Cấu trúc thư mục

- `app.py`: Ứng dụng chính (Streamlit dashboard).
- `src/scraper.py`: Mã nguồn thu thập dữ liệu từ web.
- `src/analyzer.py`: Logic phân tích dữ liệu.
- `src/recommender.py`: Logic gợi ý xu hướng tương lai.
- `data/`: Thư mục chứa dữ liệu đã thu thập (file JSON).
- `requirements.txt`: Danh sách các thư viện phụ thuộc.

## Khắc phục sự cố

- **Lỗi `ImportError` khi chạy scraper:** Đảm bảo bạn sử dụng lệnh `python -m src.scraper` thay vì `python src/scraper.py`.
- **Ứng dụng báo "No data found":** Hãy chắc chắn bạn đã chạy scraper thành công và file `data/au_2025.json` đã được tạo.
