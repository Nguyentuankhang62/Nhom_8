# MÔ TẢ ĐỀ TÀI UDM_11 – DOWNLOAD NHIỀU FILE

## 1. Giới thiệu đề tài

Đề tài **UDM_11 – Download nhiều file** hướng đến việc xây dựng một ứng dụng tải nhiều tệp tin từ máy chủ (Server) về máy khách (Client) thông qua mạng máy tính. Ứng dụng có giao diện đồ họa trực quan, giúp người dùng dễ dàng xem danh sách tệp tin hiện có trên Server, lựa chọn các tệp cần tải và theo dõi quá trình tải xuống.

Khác với cách tải từng tệp riêng lẻ, hệ thống cho phép người dùng lựa chọn nhiều tệp trong cùng một lần thao tác. Các tệp được đưa vào danh sách tải xuống và xử lý theo cơ chế hàng đợi hoặc tải đồng thời, với số lượng tệp được tải cùng lúc do nhóm quy định. Trong quá trình tải, ứng dụng hiển thị trạng thái, tốc độ và tiến trình riêng cho từng tệp, giúp người dùng dễ dàng theo dõi và nhận biết kết quả của từng tác vụ.

Đề tài tập trung vào việc vận dụng kiến thức lập trình mạng để xây dựng mô hình giao tiếp Client–Server, truyền dữ liệu qua TCP Socket, kết hợp lập trình giao diện đồ họa và xử lý nhiều tác vụ tải xuống. Hệ thống cũng cần đảm bảo rằng khi một tệp tải xuống thất bại, các tệp còn lại vẫn có thể tiếp tục được xử lý.

## 2. Mục tiêu của đề tài

Mục tiêu chính của đề tài là xây dựng một ứng dụng có khả năng tải nhiều tệp tin từ Server thông qua giao diện đồ họa, đáp ứng các yêu cầu sau:

- Hiển thị danh sách các tệp tin hiện có trên Server để người dùng lựa chọn.
- Cung cấp khu vực riêng để hiển thị danh sách các tệp được yêu cầu tải xuống.
- Cho phép người dùng kéo thả một hoặc nhiều tệp từ danh sách trên Server sang khu vực tải xuống để bắt đầu tải.
- Hiển thị trạng thái, tốc độ tải và phần trăm tiến trình riêng cho từng tệp.
- Hỗ trợ hàng đợi hoặc tải đồng thời, đồng thời công bố giới hạn số tệp được tải cùng lúc.
- Xử lý lỗi độc lập cho từng tệp, tránh trường hợp một tệp bị lỗi làm dừng toàn bộ quá trình tải.
- Xây dựng quy tắc xử lý khi tệp cần tải đã tồn tại trong thư mục đích.
- Kiểm thử khả năng kết nối, truyền tệp và hoạt động của ứng dụng trong các tình huống khác nhau.

Thông qua quá trình thực hiện, nhóm có thể củng cố kiến thức về lập trình Socket, giao tiếp Client–Server, xử lý luồng dữ liệu, lập trình đa luồng và xây dựng giao diện đồ họa trong Python.

## 3. Đối tượng và phạm vi sử dụng

### 3.1. Đối tượng sử dụng

Ứng dụng hướng đến người dùng cần tải nhiều tệp tin từ một máy chủ trong mạng nội bộ hoặc môi trường mạng được cấu hình phù hợp. Ví dụ:

- Sinh viên tải nhiều tài liệu học tập từ máy chủ của lớp hoặc nhóm.
- Thành viên trong nhóm học tập trao đổi các tệp tài liệu và mã nguồn.
- Người dùng tải nhiều tệp được chia sẻ từ một máy tính đóng vai trò Server.

### 3.2. Phạm vi thực hiện

Trong phạm vi môn học, nhóm tập trung xây dựng phiên bản ứng dụng có các chức năng cốt lõi gồm kết nối Client–Server, lấy danh sách tệp trên Server, lựa chọn và tải nhiều tệp, hiển thị tiến trình và tốc độ tải, quản lý hàng đợi hoặc tải đồng thời, đồng thời xử lý các lỗi cơ bản.

Server sẽ cung cấp một thư mục chứa các tệp được phép chia sẻ. Client kết nối đến Server bằng địa chỉ IP và cổng kết nối được cấu hình, sau đó yêu cầu lấy danh sách tệp và gửi yêu cầu tải những tệp đã chọn.

Phiên bản ban đầu ưu tiên hoạt động ổn định trong môi trường kiểm thử, chẳng hạn hai máy trong cùng mạng nội bộ hoặc hai chương trình chạy trên cùng máy tính để thử nghiệm. Việc triển khai qua Internet, xác thực người dùng, mã hóa dữ liệu, tải tiếp từ vị trí đã dừng và đồng bộ thư mục không nằm trong phạm vi bắt buộc của phiên bản cơ bản, trừ khi nhóm có thời gian mở rộng và được giảng viên chấp thuận.

## 4. Công nghệ dự kiến sử dụng

Nhóm dự kiến sử dụng các công nghệ sau:

- **Python:** Ngôn ngữ lập trình chính để xây dựng chương trình Client và Server.
- **Tkinter và ttk:** Xây dựng giao diện đồ họa, các danh sách tệp, nút chức năng, nhãn trạng thái và thanh tiến trình.
- **TCP Socket (`socket`):** Thiết lập kết nối giữa Client và Server, trao đổi yêu cầu và truyền nội dung tệp tin.
- **Threading hoặc cơ chế thực thi tác vụ tương đương:** Xử lý các tác vụ tải xuống để giao diện không bị treo và hỗ trợ tải nhiều tệp theo giới hạn đã đặt.
- **Queue hoặc cơ chế quản lý hàng đợi tương đương:** Quản lý thứ tự tải và số lượng tác vụ được thực hiện đồng thời.
- **Thư viện hỗ trợ kéo thả:** Có thể sử dụng `tkinterdnd2` để bổ sung thao tác kéo thả giữa các khu vực trong giao diện Tkinter.

Các công nghệ trên là lựa chọn dự kiến của nhóm và có thể được điều chỉnh trong quá trình thiết kế, nhưng phải đảm bảo đáp ứng đầy đủ yêu cầu của đề tài.

## 5. Mô hình hoạt động của hệ thống

Hệ thống được xây dựng theo mô hình Client–Server, gồm hai thành phần chính.

### 5.1. Server

Server đóng vai trò lưu trữ và cung cấp các tệp tin cho Client. Các nhiệm vụ chính gồm:

- Quản lý thư mục chứa các tệp được phép tải xuống.
- Tiếp nhận kết nối từ Client.
- Nhận yêu cầu lấy danh sách tệp và gửi danh sách tương ứng cho Client.
- Tiếp nhận yêu cầu tải một tệp cụ thể.
- Gửi thông tin cần thiết và nội dung tệp theo giao thức đã thống nhất.
- Phản hồi lỗi khi tệp không tồn tại, không thể đọc hoặc yêu cầu không hợp lệ.
- Đảm bảo dữ liệu được gửi đúng theo cấu trúc giao thức do nhóm thiết kế.

### 5.2. Client

Client là chương trình người dùng trực tiếp thao tác. Các nhiệm vụ chính gồm:

- Cho phép nhập địa chỉ IP và cổng của Server.
- Thiết lập kết nối và yêu cầu danh sách tệp hiện có trên Server.
- Hiển thị danh sách tệp để người dùng xem và lựa chọn.
- Cung cấp khu vực riêng hiển thị các tệp cần tải xuống.
- Cho phép kéo thả một hoặc nhiều tệp sang khu vực tải xuống để bắt đầu tải.
- Quản lý các tác vụ tải theo hàng đợi hoặc cơ chế tải đồng thời.
- Hiển thị trạng thái, tốc độ và phần trăm tiến trình riêng cho từng tệp.
- Lưu các tệp đã tải vào thư mục đích do người dùng lựa chọn.
- Thông báo kết quả khi tải thành công hoặc thất bại.

### 5.3. Luồng hoạt động tổng quát

Quá trình hoạt động của hệ thống dự kiến diễn ra theo các bước:

1. Người dùng khởi động Server và chỉ định thư mục chứa các tệp được chia sẻ.
2. Người dùng mở Client, nhập IP và cổng của Server rồi thực hiện kết nối.
3. Client gửi yêu cầu lấy danh sách tệp; Server phản hồi danh sách các tệp được phép tải.
4. Client hiển thị danh sách tệp trên giao diện.
5. Người dùng kéo thả một hoặc nhiều tệp sang khu vực tải xuống.
6. Client đưa các tệp được chọn vào hàng đợi và bắt đầu tải theo giới hạn đồng thời đã quy định.
7. Trong quá trình tải, Client cập nhật trạng thái, tốc độ và phần trăm tiến trình của từng tệp.
8. Khi một tệp hoàn tất, Client ghi nhận kết quả và tiếp tục xử lý các tệp đang chờ.
9. Nếu một tệp xảy ra lỗi, Client đánh dấu tệp đó là thất bại và tiếp tục xử lý các tệp còn lại.
10. Khi hoàn tất, người dùng có thể xem kết quả tải của từng tệp và kiểm tra các tệp trong thư mục đích.

## 6. Các chức năng chính

### 6.1. Kết nối đến Server

Người dùng nhập địa chỉ IP và cổng kết nối. Client thực hiện kết nối TCP và thông báo trạng thái kết nối thành công hoặc thất bại. Nếu không kết nối được, ứng dụng cần hiển thị thông báo dễ hiểu để người dùng kiểm tra lại thông tin kết nối hoặc trạng thái Server.

### 6.2. Hiển thị danh sách tệp trên Server

Sau khi kết nối thành công, Client gửi yêu cầu lấy danh sách tệp. Server trả về danh sách các tệp trong thư mục được chia sẻ. Client hiển thị danh sách này để người dùng xem và lựa chọn.

Nhóm có thể bổ sung thông tin tên tệp, kích thước và loại tệp để giao diện dễ sử dụng hơn.

### 6.3. Lựa chọn và tải nhiều tệp

Giao diện có hai khu vực riêng biệt: danh sách tệp trên Server và danh sách tệp được chọn tải xuống. Người dùng có thể kéo thả một hoặc nhiều tệp từ khu vực thứ nhất sang khu vực thứ hai. Sau thao tác này, ứng dụng đưa các tệp vào quá trình tải theo cơ chế mà nhóm đã thiết kế.

### 6.4. Quản lý hàng đợi và tải đồng thời

Để tránh tạo quá nhiều kết nối và làm giảm khả năng đáp ứng của ứng dụng, nhóm sẽ quy định số tệp tối đa được tải đồng thời. Các tệp vượt quá giới hạn sẽ nằm trong hàng đợi và được xử lý khi có tác vụ hoàn tất.

Ví dụ, nếu nhóm quy định tối đa hai tệp tải đồng thời, khi người dùng chọn năm tệp thì hai tệp đầu tiên được tải, ba tệp còn lại chờ đến lượt. Đây là giới hạn dự kiến và sẽ được nhóm xác nhận trong thiết kế cuối cùng.

### 6.5. Theo dõi tiến trình và tốc độ tải

Mỗi tệp trong danh sách tải xuống có thông tin theo dõi riêng, bao gồm:

- **Tên tệp:** Tệp đang được tải.
- **Trạng thái:** Chờ tải, đang tải, hoàn tất hoặc lỗi.
- **Tiến trình:** Phần trăm dữ liệu đã tải so với tổng dung lượng.
- **Tốc độ tải:** Lượng dữ liệu nhận được trong một đơn vị thời gian.

Thông tin được cập nhật trong quá trình tải để người dùng theo dõi tiến độ. Việc xử lý truyền dữ liệu cần được tách hợp lý khỏi luồng giao diện nhằm tránh làm cửa sổ bị treo.

### 6.6. Xử lý lỗi tải xuống

Hệ thống cần xử lý các tình huống như mất kết nối, tệp không tồn tại, không có quyền ghi vào thư mục đích hoặc dữ liệu truyền không đầy đủ. Khi một tệp gặp lỗi, ứng dụng ghi nhận trạng thái lỗi cho tệp đó và tiếp tục xử lý các tệp còn lại.

Các thông báo lỗi cần đủ rõ ràng để người dùng biết nguyên nhân cơ bản và có thể thử lại khi phù hợp.

### 6.7. Xử lý tệp trùng tên

Nếu tệp tải xuống có tên trùng với tệp đã tồn tại trong thư mục đích, ứng dụng sẽ hỏi người dùng có muốn ghi đè hay không. Nếu người dùng không đồng ý hoặc không xác nhận, ứng dụng không được tự ý ghi đè tệp hiện có.

### 6.8. Thông báo kết quả tải

Sau khi từng tác vụ kết thúc, Client cập nhật trạng thái tương ứng. Người dùng có thể phân biệt tệp tải thành công, tệp đang chờ và tệp tải thất bại ngay trên giao diện.

## 7. Giao thức giao tiếp dự kiến

Nhóm dự kiến sử dụng TCP Socket để trao đổi yêu cầu và truyền dữ liệu giữa Client và Server. TCP cung cấp kênh truyền dữ liệu tin cậy, nhưng không tự xác định ranh giới của từng thông điệp ứng dụng. Vì vậy, nhóm cần thiết kế quy tắc đóng gói thông điệp để hai bên xác định chính xác phần yêu cầu, thông tin tệp và lượng dữ liệu cần nhận.

Các loại thông điệp dự kiến gồm:

- **LIST_FILES:** Client yêu cầu danh sách tệp trên Server.
- **FILE_LIST:** Server trả về danh sách tệp và thông tin liên quan.
- **DOWNLOAD:** Client yêu cầu tải một tệp cụ thể.
- **FILE_INFO:** Server gửi thông tin như tên tệp và kích thước tệp.
- **FILE_DATA:** Dữ liệu tệp được truyền từ Server đến Client theo từng khối.
- **ERROR:** Server hoặc Client thông báo lỗi theo quy tắc giao thức.

Tên thông điệp trên là quy ước dự kiến của nhóm, không phải giao thức tiêu chuẩn bắt buộc. Trong quá trình thiết kế, nhóm cần thống nhất cấu trúc thông điệp, cách biểu diễn kích thước dữ liệu, cách xác định kết thúc truyền và cách xử lý khi kết nối bị ngắt giữa chừng.

## 8. Phạm vi không triển khai trong phiên bản cơ bản

Để đảm bảo hoàn thành trong thời gian môn học, nhóm ưu tiên các chức năng cốt lõi theo đề tài. Các tính năng sau chưa nằm trong phạm vi:

- Tạm dừng và tiếp tục tải từ vị trí đã tải trước đó.
- Khôi phục phiên tải sau khi mất kết nối.
- Đồng bộ thư mục giữa nhiều máy.
- Xác thực người dùng và phân quyền nâng cao.
- Mã hóa dữ liệu truyền qua mạng.
- Triển khai hệ thống máy chủ công cộng trên Internet.

Các chức năng mở rộng chỉ được thực hiện khi những chức năng bắt buộc đã hoạt động ổn định và nhóm có đủ thời gian.

## 9. Kết quả dự kiến

Sau khi hoàn thành, nhóm dự kiến có một ứng dụng gồm chương trình Server và chương trình Client, cho phép Client kết nối đến Server, xem danh sách tệp được chia sẻ, lựa chọn và tải nhiều tệp về máy. Giao diện Client có khu vực danh sách tệp trên Server, khu vực danh sách tải xuống và thông tin trạng thái, tốc độ, tiến trình riêng cho từng tệp.

Ứng dụng phải thể hiện được cơ chế hàng đợi hoặc tải đồng thời theo giới hạn đã công bố, xử lý lỗi độc lập giữa các tệp và tuân thủ quy tắc khi tệp đích đã tồn tại. Nhóm sẽ kiểm thử các chức năng này, ghi nhận kết quả và chuẩn bị kịch bản trình diễn để chứng minh hệ thống đáp ứng yêu cầu đề tài.
