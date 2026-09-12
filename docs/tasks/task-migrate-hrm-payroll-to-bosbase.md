# Task: Kế hoạch Chuyển đổi HRM & Payroll sang BosBase (Go) + BosBase-NextJS

**Mã công việc:** `TASK-MIGRATE-HRM-BOSBASE`  
**Trạng thái:** Sẵn sàng thực thi (Drafted & Approved for Sprint)  
**Ngày lập:** 2026-09-12  
**Mục tiêu:** Chuyển đổi toàn bộ phân hệ Quản lý nhân sự (HRM), Chấm công, Nghỉ phép, Tính lương (Payroll) và Hạch toán kế toán kép (GL Entries) từ kiến trúc Python/Lambda-ERP sang hệ sinh thái:
1. **Backend:** `Football/bosbase` (Go, PostgreSQL, built-in REST/Realtime, LangChainGo Text-to-SQL & RAG).
2. **Frontend Admin:** `Football/bosbase-nextjs` (Next.js 14 App Router, Shadcn UI, TanStack Query, i18n).

---

## 1. Lý do & Lợi ích kiến trúc

| Tiêu chí | Lambda-ERP cũ (Python) | BosBase Mới (Go + Next.js) |
| :--- | :--- | :--- |
| **Hiệu năng & Resource** | Python runtime, tốn RAM, xử lý concurrency nặng | Go compiled binary, lightweight, tốc độ cao |
| **Quản trị Schema** | Can thiệp core hoặc viết custom plugin hook phức tạp | Dynamic PocketBase-style Collections trực tiếp trên PostgreSQL |
| **API & Realtime** | REST tự viết qua Flask/FastAPI, thiếu event bus | Built-in CRUD REST APIs, SDK, SSE Realtime Subscriptions |
| **Tích hợp Trí tuệ nhân tạo** | Proxy OpenAI ngoài, dễ lỗi streaming | Built-in LangChainGo native: Text-to-SQL báo cáo HRM, RAG chính sách nhân sự |
| **Frontend UI** | Giao diện tĩnh gắn kèm backend | Next.js App Router, SSR, Tailwind/Shadcn hiện đại, module hoá cao |

---

## 2. Thiết kế Cấu trúc Collections (BosBase Schema)

Toàn bộ bảng được khởi tạo qua script migration hoặc SDK `init-collection.ts` trong `bosbase-nextjs`.

### 2.1 `employees` (Hồ sơ nhân viên)
- `code` (text, unique, required): Mã nhân viên (`EMP-001`).
- `full_name` (text, required): Họ và tên.
- `department` (text): Phòng ban.
- `designation` (text): Vị trí / Chức vụ.
- `date_of_joining` (date): Ngày vào làm.
- `status` (select: `Active`, `Inactive`, `Left`): Trạng thái làm việc.
- `user_id` (relation -> `users`, optional): Liên kết tài khoản đăng nhập.

### 2.2 `attendances` (Chấm công hàng ngày)
- `employee` (relation -> `employees`, required).
- `attendance_date` (date, required): Ngày chấm công (`YYYY-MM-DD`).
- `status` (select: `Present`, `Absent`, `On Leave`, `Half Day`, required).
- `working_hours` (number): Số giờ công (mặc định 8.0).
- `in_time` (text): Thời gian check-in (`HH:mm:ss`).
- `out_time` (text): Thời gian check-out (`HH:mm:ss`).
- *Index & Ràng buộc:* Unique compound `(employee, attendance_date)` tránh trùng lặp bản ghi trong ngày.

### 2.3 `leave_types` & `leave_applications` (Nghỉ phép)
- **`leave_types`**:
  - `code` (text, unique): Mã phép (`AL` - Annual Leave, `SL` - Sick Leave, `UL` - Unpaid Leave).
  - `name` (text): Tên loại phép.
  - `max_days_allowed` (number): Số ngày trần trong năm.
  - `is_lwp` (bool): Nghỉ không hưởng lương (`true`/`false`).
- **`leave_applications`**:
  - `employee` (relation -> `employees`, required).
  - `leave_type` (relation -> `leave_types`, required).
  - `from_date` (date, required).
  - `to_date` (date, required).
  - `total_leave_days` (number, required): Tự động tính = `to_date - from_date + 1`.
  - `status` (select: `Open`, `Approved`, `Rejected`, `Cancelled`).
  - `reason` (text): Lý do nghỉ.

### 2.4 `salary_components` & `salary_structures` (Cơ cấu lương)
- **`salary_components`**:
  - `name` (text, unique): Tên khoản mục (Lương cơ bản, Phụ cấp ăn trưa, BHXH 8%, BHYT 1.5%, PIT...).
  - `type` (select: `Earning`, `Deduction`).
  - `default_amount` (number).
- **`salary_structures`**:
  - `employee` (relation -> `employees`, required).
  - `base_salary` (number, required): Mức lương cơ bản thỏa thuận.
  - `earnings` (json): Danh sách các khoản phụ cấp cộng thêm `[{ name, amount }]`.
  - `deductions` (json): Danh sách các khoản giảm trừ tỷ lệ/cố định `[{ name, amount, rate }]`.
  - `is_active` (bool): Trạng thái áp dụng.

### 2.5 `salary_slips` (Phiếu lương & Tính thực nhận NET)
- `employee` (relation -> `employees`, required).
- `payroll_period` (text): Kỳ lương (`2026-09`).
- `start_date` (date), `end_date` (date).
- `payment_days` (number): Số ngày công thực tế tính từ `attendances`.
- `absent_days` (number): Số ngày nghỉ không phép.
- `leave_without_pay_days` (number): Số ngày nghỉ không lương (LWP).
- `gross_pay` (number): Tổng thu nhập chịu thuế/chưa khấu trừ.
- `total_deduction` (number): Tổng khấu trừ (BHXH 8%, BHYT 1.5%, BHTN 1%, Thuế TNCN).
- `net_pay` (number): Tiền lương thực nhận = `gross_pay - total_deduction`.
- `status` (select: `Draft`, `Submitted`, `Cancelled`).
- `earnings_detail` (json), `deductions_detail` (json).

### 2.6 `gl_entries` (Sổ cái kế toán kép)
- `posting_date` (date, required).
- `account` (text, required): Ví dụ `Salary Expense`, `Salary Payable`.
- `debit` (number, default 0).
- `credit` (number, default 0).
- `voucher_type` (text): `Salary Slip`.
- `voucher_no` (text): ID của Salary Slip.
- `is_cancelled` (bool, default false).

---

## 3. Nghiệp vụ Hooks & Logic Tính toán

1. **Ràng buộc Chấm công:**
   - Khi ghi nhận chấm công: kiểm tra tồn tại `employee` + `attendance_date`. Nếu đã có bản ghi -> báo lỗi duplicate hoặc cho phép ghi đè trạng thái.
2. **Duyệt Đơn Nghỉ Phép (Leave Workflow):**
   - Khi `leave_applications` được chuyển sang `Approved`:
     - Kiểm tra tổng ngày đã nghỉ của nhân viên trong năm đối với loại phép đó <= `max_days_allowed`.
     - Tự động sinh bản ghi `attendances` tương ứng các ngày nghỉ với trạng thái `On Leave`.
3. **Tính Lương Chuẩn Việt Nam (Payroll Math):**
   - Số ngày làm việc tiêu chuẩn: 22 hoặc 26 ngày/tháng.
   - $\text{Lương ngày công} = \frac{\text{Base Salary}}{\text{Standard Days}} \times \text{Payment Days}$.
   - $\text{Gross Pay} = \text{Lương ngày công} + \sum \text{Earnings}$.
   - Khấu trừ bảo hiểm:
     - BHXH: $8\% \times \text{Lương đóng bảo hiểm}$.
     - BHYT: $1.5\% \times \text{Lương đóng bảo hiểm}$.
     - BHTN: $1\% \times \text{Lương đóng bảo hiểm}$.
   - Thuế TNCN: Tính lũy tiến trên phần thu nhập chịu thuế sau giảm trừ gia cảnh.
   - $\text{Net Pay} = \text{Gross Pay} - \text{Total Deduction}$.
4. **Hạch toán Kế toán Kép (GL Entries):**
   - Khi `salary_slips.status` chuyển thành `Submitted`:
     - Tạo GL 1: Debit `Chi phí lương (Salary Expense)` = Gross Pay.
     - Tạo GL 2: Credit `Phải trả nhân viên (Salary Payable)` = Net Pay.
     - Tạo GL 3..N: Credit các quỹ bảo hiểm / Thuế phải nộp tương ứng khoản khấu trừ.
   - Khi chuyển sang `Cancelled`: Tự động tạo bút toán đảo (Reverse GL Entries).

---

## 4. Tích hợp AI / LangChainGo Native trong BosBase

Sử dụng trực tiếp endpoint có sẵn trong `Football/bosbase/apis/langchaingo.go`:
- **Text-to-SQL Reporting (`POST /api/langchaingo/sql`):**
  - Cho phép người dùng hoặc Admin truy vấn:
    - *"Thống kê tổng quỹ lương tháng 09/2026 theo từng phòng ban."*
    - *"Danh sách nhân viên đi muộn hoặc vắng mặt quá 3 ngày trong tháng."*
  - LLM chuyển prompt tiếng Việt thành câu lệnh PostgreSQL tối ưu trên schema của BosBase.
- **RAG Policy & Legal Assistant (`POST /api/langchaingo/rag`):**
  - Đọc hiểu tài liệu nội quy công ty, chính sách tính thưởng, biểu thuế lũy tiến TNCN và luật lao động đã được index trong `_llm_documents`.

---

## 5. Lộ trình Triển khai Sprint (Action Plan)

### Bước 1: Khởi tạo Schema Collections trên BosBase
- Viết file khởi tạo `Football/bosbase-nextjs/src/lib/bosbase/init-hrm-collections.ts`.
- Định nghĩa đầy đủ 7 collections: `employees`, `attendances`, `leave_types`, `leave_applications`, `salary_components`, `salary_structures`, `salary_slips`, `gl_entries`.
- Thêm route API `/api/bosbase/init-hrm` để kích hoạt migration nhanh qua giao diện web hoặc CLI.

### Bước 2: Viết Business Service & Payroll Engine
- Triển khai helper tính lương theo công thức Việt Nam tại `Football/bosbase-nextjs/src/services/hrm/payroll.ts`.
- Triển khai helper tự động tạo và đảo bút toán sổ cái tại `Football/bosbase-nextjs/src/services/hrm/accounting.ts`.

### Bước 3: Xây dựng Giao diện Quản trị (Admin UI)
- Tạo menu "Quản lý Nhân sự & Lương" trong Admin Layout (`/admin/layout.tsx`).
- Xây dựng trang danh sách và biểu mẫu:
  - `/admin/hrm/employees`: Quản lý hồ sơ nhân viên.
  - `/admin/hrm/attendances`: Bảng chấm công hàng ngày.
  - `/admin/hrm/leaves`: Duyệt đơn xin nghỉ phép.
  - `/admin/hrm/payroll`: Bảng tính lương và chi tiết phiếu lương (Salary Slip).
  - `/admin/hrm/gl-entries`: Sổ nhật ký kế toán tiền lương.

### Bước 4: Kiểm thử Tự động & Nghiệm thu
- Kiểm thử khởi tạo collections thành công trên database.
- Kiểm thử quy trình: Chấm công -> Nộp đơn nghỉ phép -> Tính lương NET -> Hạch toán GL -> Hủy phiếu lương (đảo sổ cái).
- Kiểm thử lệnh hỏi đáp Text-to-SQL qua API `langchaingo`.
