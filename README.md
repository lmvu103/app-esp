# ⚡ ESP Engineer Assistant (v1.2.0)

![Logo](logo.png)

**ESP Engineer Assistant** là ứng dụng web chuyên nghiệp được phát triển để hỗ trợ các kỹ sư dầu khí trong việc thiết kế, theo dõi vận hành và tối ưu hóa hệ thống Máy bơm điện chìm (Electrical Submersible Pump - ESP).

## 🚀 Tính năng chính

### 1. ESP Design Wizard (Trình thuật sĩ thiết kế 8 bước)
Quy trình thiết kế bài bản từ đầu đến cuối:
- **Bước 1: Nhập dữ liệu (Data Input)**: Thông tin giếng, vỉa và chất lưu.
- **Bước 2: Tính toán khí (Gas Calc)**: Đánh giá ảnh hưởng của khí tự do và lựa chọn thiết bị xử lý khí (Separator/AGH).
- **Bước 3: Chọn bơm (Pump Selection)**: Tự động tính toán số tầng bơm (stages) và kiểm tra đường cong hiệu suất.
- **Bước 4: Chọn Protector**: Cấu hình buồng giãn nở phù hợp với điều kiện giếng.
- **Bước 5: Chọn Motor**: Tính toán công suất yêu cầu và kiểm tra tải động cơ.
- **Bước 6: Mô phỏng (Simulation)**: Xem trước điểm vận hành dự kiến trên biểu đồ.
- **Bước 7: Kiểm tra độ bền (Integrity)**: Kiểm tra áp suất burst và vận tốc làm mát.
- **Bước 8: Xuất báo cáo (Report)**: Tổng hợp cấu hình thiết bị cuối cùng.

### 2. Theo dõi vận hành (Operations Monitoring)
- Nhập thông số vận hành hàng ngày (Tần số, WHP, Lưu lượng, Amps).
- Tự động tính toán điểm vận hành thực tế và trực quan hóa trên đường cong bơm.
- Đánh giá hiệu suất bơm theo thời gian thực.

### 3. Tối ưu hóa (Optimization)
- Mô phỏng thay đổi Tần số (Frequency) và Áp suất miệng giếng (WHP/Choke).
- Dự báo lưu lượng khai thác và điểm vận hành mới để tối ưu hóa sản lượng.

## 🛠 Cài đặt & Sử dụng

### Yêu cầu hệ thống
- Python 3.10+
- Trình quản lý gói `uv` (khuyến nghị) hoặc `pip`.

### Cài đặt môi trường
Sử dụng `uv`:
```bash
uv sync
```
Hoặc sử dụng `pip`:
```bash
pip install -r requirements.txt
```

### Chạy ứng dụng
```bash
streamlit run streamlit_app.py
```

## 🧰 Công nghệ sử dụng
- **Ngôn ngữ**: Python
- **Giao diện**: Streamlit (Layout Wide, Custom CSS)
- **Xử lý dữ liệu**: Pandas, Numpy
- **Biểu đồ tương tác**: Plotly Graph Objects

## 👨‍💻 Tác giả
- **Le Vu**
- Phiên bản: 1.2.0 (Stable)

---
*Ghi chú: Đây là công cụ hỗ trợ tính toán kỹ thuật, kết quả cần được kiểm chứng bởi kỹ sư chuyên môn trước khi áp dụng thực tế.*
