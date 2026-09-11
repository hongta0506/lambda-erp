# Task: HRM, Chấm công, Nghỉ phép & Tính lương (Payroll)

**Trạng thái:** Hoàn thành (Implemented & Verified)  
**Ngày:** 2026-09-11  
**Kiến trúc:** Plugin `erp_hr/` (Zero Core Modification tới `lambda_erp/`), kết hợp Frontend Plugin `frontend/src/plugins/hr.tsx`.

---

## 1. Nghiệp vụ chi tiết

### 1.1 Chấm công theo ngày (Daily Attendance)
- **Doctype:** `Attendance` (Mã tiền tố: `ATT-`)
- **Trường dữ liệu:**
  - `employee`: Mã nhân viên (Link -> `Employee`).
  - `attendance_date`: Ngày chấm công (`YYYY-MM-DD`).
  - `status`: Trạng thái (`Present` - Có mặt, `Absent` - Vắng mặt, `On Leave` - Nghỉ phép, `Half Day` - Nửa ngày).
  - `working_hours`: Số giờ làm việc (Mặc định 8.0h).
  - `in_time`, `out_time`: Giờ vào / giờ ra.
  - `leave_type`: Loại nghỉ phép nếu trạng thái là `On Leave`.
- **Ràng buộc:**
  - Chống trùng lặp chấm công: 1 nhân viên chỉ có 1 bản ghi chấm công hợp lệ trên 1 ngày (`docstatus != 2`).

### 1.2 Quản lý Ngày phép & Đơn xin nghỉ (Leave Management)
- **Master:** `Leave Type` (Loại ngày phép)
  - `name`: Tên viết tắt (AL - Annual Leave / Nghỉ phép năm, SL - Sick Leave / Ốm đau, UL - Unpaid Leave / Không lương, v.v.).
  - `max_days_allowed`: Số ngày tối đa được hưởng trong năm.
  - `is_lwp`: Đánh dấu nghỉ không hưởng lương (Leave Without Pay).
- **Doctype:** `Leave Application` (Đơn xin nghỉ phép - Mã tiền tố: `LV-`)
  - `employee`: Nhân viên nộp đơn.
  - `leave_type`: Loại phép đăng ký.
  - `from_date`, `to_date`: Khoảng thời gian nghỉ.
  - `total_leave_days`: Tự động tính số ngày nghỉ (`to_date - from_date + 1`).
  - `status`: `Open` -> `Approved` / `Rejected` / `Cancelled`.
  - **Kiểm tra quỹ phép:** Xác thực số ngày nghỉ luỹ kế không vượt quá `max_days_allowed` của `Leave Type`.

### 1.3 Cấu trúc Lương theo ngạch, Lương cơ bản, Phụ cấp & Giảm trừ (Salary Structure)
- **Master:** `Salary Component` (Khoản mục lương)
  - `type`: `Earning` (Thu nhập) hoặc `Deduction` (Khấu trừ).
  - Phân loại:
    - **Thu nhập (Earnings):** Lương cơ bản (Base Salary), Phụ cấp chức vụ, Phụ cấp ăn trưa, Thưởng hiệu quả.
    - **Khấu trừ (Deductions):** BHXH (8%), BHYT (1.5%), BHTN (1%), Thuế TNCN (Personal Income Tax).
- **Doctype:** `Salary Structure` (Cơ cấu lương nhân viên)
  - Quy định các khoản Earning và Deduction cố định hoặc theo ngạch lương cho nhân viên.
  - Tự động cộng tổng Earning, Deduction và tính Net Pay dự kiến.

### 1.4 Phiếu lương & Tính lương thực nhận NET (Salary Slip & Net Calculation)
- **Doctype:** `Salary Slip` (Phiếu lương - Mã tiền tố: `SAL-`)
  - `employee`, `posting_date`, `start_date`, `end_date`.
  - Bảng con `earnings`: Chi tiết các khoản thu nhập.
  - Bảng con `deductions`: Chi tiết các khoản khấu trừ (BHXH, BHYT, Thuế TNCN).
  - **Công thức tính:**
    $$\text{Gross Pay} = \sum \text{Earnings}$$
    $$\text{Total Deduction} = \sum \text{Deductions}$$
    $$\text{Net Pay} = \text{Gross Pay} - \text{Total Deduction}$$
  - **Tích hợp Chấm công:**
    - Tính toán số ngày công thực tế (`payment_days`), số ngày vắng mặt (`absent_days`), số ngày nghỉ không lương (`leave_without_pay`) trong kỳ từ bảng `Attendance`.
  - **Hạch toán kế toán kép (GL Entry):**
    - Khi `Submit` phiếu lương:
      - Nợ (Debit): `Salary Expense` (Tài khoản chi phí lương) = Gross Pay.
      - Có (Credit): `Salary Payable` (Tài khoản phải trả người lao động) = Net Pay.
      - Có (Credit): Các tài khoản trích theo lương / thuế nếu cấu hình.
    - Khi `Cancel`: Tự động tạo bút toán đảo (Reverse GL Entry).

---

## 2. Cấu trúc Triển khai (Codebase)

- `erp_hr/schema.py`: Toàn bộ DDL của bảng Master và Transaction.
- `erp_hr/models.py`: Logic xử lý `Attendance`, `LeaveApplication`, `SalaryStructure`, `SalarySlip`, tính thuế/phụ cấp/net pay và GL posting.
- `erp_hr/actions.py`: Server actions tạo phiếu lương tự động từ Attendance và Salary Structure.
- `erp_hr/plugin.py`: Điểm kích hoạt nạp plugin thông qua biến `LAMBDA_ERP_PLUGINS=erp_hr`.
- `frontend/src/plugins/hr.tsx`: Đăng ký Master, Doctype view và Sidebar Navigation "HR & Payroll".
- `tests/test_hr_plugin.py`: Test coverage tự động cho toàn bộ chu trình HR.
