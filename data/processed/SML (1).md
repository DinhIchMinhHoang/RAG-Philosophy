<!-- Page 27 -->
# Chương 1 Giới thiệu Trong chương này, chúng ta sẽ tiếp cận khái niệm Học máy từ những góc nhìn cơ bản nhất, bao gồm: học máy là gì, phạm vi ứng dụng và các tình huống áp dụng thực tế.

Chương này làm bước đệm để người học nắm bắt và kết nối được với toàn bộ nội dung của cuốn sách, từ bài toán phân lớp (Chương 2) đến các mô hình nơ-ron phức tạp (Chương 3, 4, 5) và các hướng nâng cao như mô hình sinh (Chương 11) hay mô hình đồ thị xác suất (Chương 12). 1.1 Học máy là gì ? Học máy là một ngành khoa học về các thuật toán và các chương trình máy tính tự động cải tiến thông qua kinh nghiệm. Trong đó, các thuật toán học máy được thiết kế để phân tích dữ liệu, nhận biết mẫu và học từ kinh nghiệm mà không cần phải lập trình cụ thể. Học máy là một phần của trí tuệ nhân tạo và liên quan với việc phát triển các mô hình dự đoán và quyết định. Một số ví dụ của học máy bao gồm:

<!-- Page 28 (Heavy) -->
Hình 1.1: Tỉ lệ băng thông email là thư rác.

<!-- image -->

Ví dụ 1.1 (Phân loại thư rác) . Các chương trình quản lý thư điện tử hiện nay không thể thiếu mô-đun phân loại và lọc thư rác do số lượng thư rác quá lớn. Hình 1.1 cho thấy tỉ lệ băng thông dành cho thư rác giảm qua nhiều năm liên tục, một phần là do các mô-đun lọc thư rác ngày càng hiệu quả. Để xây dựng mô-đun lọc thư rác, thuật toán lọc thư quan sát và học từ một tập dữ liệu lớn gồm hàng triệu thư điện tử được gán nhãn là thư thường hoặc thư rác. Thuật toán tự điều chỉnh để tìm cách mô tả được mối quan hệ giữa nội dung thư với nhãn của nó. Sau khi học xong, thuật toán được sử dụng để phân loại, lọc các thư điện tử mới không có trong tập dữ liệu nói trên. Điểm đặc biệt là độ chính xác khi phân loại thư ngày càng tăng nếu tập dữ liệu ban đầu lớn hơn.

Ví dụ 1.2 (Phân loại chữ số viết tay) . Thư từ, bưu phẩm trong hệ thống bưu điện của Mỹ được phân loại theo mã số bưu điện của từng vùng. Khi gửi bưu phẩm, người gửi ghi mã số bưu điện vào các ô được định sẵn (Hình 1.2). Khi nhận bưu phẩm, các bưu trạm sử dụng hệ thống đọc chữ số viết tay tự động để phân luồng, phân phối bưu phẩm do số lượng bưu phẩm hàng ngày của nước Mỹ rất

<!-- Page 29 -->
## 1.1 HỌC MÁY LÀ GÌ ? 3 Hình 1.2:

Bộ dữ liệu chữ số viết tay MNIST. lớn (6,2 tỉ bưu phẩm vào năm 2019). Bộ dữ liệu chữ số viết tay MNIST được thu thập và công bố bởi Viện Tiêu chuẩn và Công nghệ của Mỹ bao gồm 70.000 ảnh chữ số viết tay kích thước 28x28, được gán nhãn từ 0 đến 9 là bộ dữ liệu “Hello World” dành cho ngành Học máy. Nhiều mô hình Học máy khi phát minh ra được đánh giá bởi bộ dữ liệu MNIST. Qua các ví dụ trên, ta thấy để giải quyết một nhiệm vụ hoặc một vấn đề bằng cách tiếp cận Học máy, trước tiên, cần định nghĩa nhiệm vụ T bằng cách chỉ rõ đầu vào, đầu ra cần có của thuật toán; sau đó, chọn một độ đo hiệu năng P cho thuật toán cần tìm, độ đo này nói chung không phụ thuộc vào thuật toán cụ thể mà chỉ phụ thuộc vào đầu ra của thuật toán cùng đầu ra đích mong muốn; cuối cùng, xây dựng bộ dữ liệu hoặc kinh nghiệm E từ những hoạt động lịch sử của nhiệm vụ đó để thuật toán học (Hình 1.3). Định nghĩa 1.3 (Thuật toán Học máy - Tom Mitchell). Thuật toán được coi là học từ kinh nghiệm E đối với lớp bài toán (hoặc A lớp nhiệm vụ) T và độ đo hiệu năng P nếu hiệu năng đo bằng P của đối với nhiệm vụ trong T tăng với kinh nghiệm E. A

<!-- Page 30 (Heavy) -->
Hình 1.3: Giải quyết vấn đề bằng cách tiếp cận Học máy.

<!-- image -->

Thuật toán A khi huấn luyện trên kinh nghiệm E cho ta mô hình học máy A ( E ) đã được huấn luyện. Mục tiêu của ngành Học máy có thể chia ra làm ba hướng chính: nghiên cứu cách tiếp cận học máy cho các lớp nhiệm vụ T ; phát triển các thuật toán học máy A ; và đánh giá chất lượng, hiệu năng của mô hình học máy A ( E ) đã được huấn luyện.

## 1.2 Ứng dụng của Học máy

Trong những năm gần đây và trong tương lai gần, Học máy đã, đang và sẽ có ứng dụng trong nhiều ngành nghề, đi vào mọi mặt đời sống của con người. Học máy hiện là phân ngành mũi nhọn của ngành học về Trí tuệ nhân tạo. Liên tục có hàng loạt nghiên cứu, công nghệ mới về Học máy được áp dụng ở quy mô công nghiệp. Trong phần này, chúng ta cùng xem xét một số ứng dụng nổi bật của Học máy đã làm thay đổi tư duy, công việc và lối sống của con người.

<!-- Page 31 -->
## 1.2 ỨNG DỤNG CỦA HỌC MÁY 5 • Y tế và chăm sóc sức khoẻ.

Học máy đã sản sinh nhiều kỹ thuật và công cụ trong chẩn đoán và tiên lượng tình hình sức khoẻ, bệnh tật trong lĩnh vực y tế. Dự đoán diễn biến của bệnh - dịch bệnh, trích xuất tri thức y khoa từ kết quả nghiên cứu lâm sàng, hỗ trợ điều trị tâm lý và quản lý bệnh nhân nói chung là những lĩnh vực y tế đã cho thấy ứng dụng của Học máy. Ngoài ra, Học máy còn phân tích hồ sơ bệnh án, xử lý mất mát thông tin, giám sát các thông số từ cảm biến tại phòng chăm sóc đặc biệt để cảnh báo. • Giao thông. Học máy đang được sử dụng hàng ngày khi chúng ta sử dụng các ứng dụng bản đồ như Google Maps để di chuyển. Học máy xác định và dự đoán tình hình giao thông giúp người dùng tránh các cung đường đông đúc và đến đích đúng giờ. Học máy sử dụng thông tin vị trí và vận tốc của hàng triệu người dùng đang bật định vị Hệ thống định vị toàn cầu - GPS để hình thành bản đồ giao thông và phân tích, dự đoán các vị trí có thể tắc nghẽn. Ngoài ra, các hãng xe chia sẻ như Uber, Grab sử dụng thông tin vị trí xe và vị trí người đặt xe làm đầu vào cho mô hình Học máy dùng để xếp lịch, lập kế hoạch cung đường, thời điểm đến đích cũng như giá từng cuốc xe. • Mạng xã hội Hầu hết chúng ta đều có một hoặc nhiều tài khoản mạng xã hội. Mạng xã hội đem lại niềm vui và có thể gây nghiện. Mạng xã hội giúp mọi người gần nhau hơn trong đời sống số, chia sẻ với nhau về công nghệ, những kỹ năng thú vị, tin tức nóng nổi và hơn hết giữ liên lạc với những người chúng ta muốn. Học máy đóng vai trò cốt lõi trong việc phát triển các nền tảng mạng xã hội. Tính năng Giới thiệu bạn bè sử dụng Học máy để dự đoán hai người có thân quen với nhau trong cuộc sống thật hay không thông qua các mối liên hệ giữa hai người và những người quen chung, các sở thích, các nhóm và nơi làm việc chung. Tính năng Nhận dạng khuôn mặt sử dụng mô hình Học máy

<!-- Page 32 -->

<!-- Page 33 -->
## 1.2 ỨNG DỤNG CỦA HỌC MÁY 7 tự đường dẫn của nó cần phải cập nhật lại để lần sau phục vụ tốt hơn. • Giám sát - an ninh.

Đối với một người hoặc một nhóm nhân viên an ninh, việc theo dõi màn hình của hàng trăm camera liên tục truyền tải hình ảnh về trung tâm an ninh là việc làm cực kì mệt mỏi và buồn tẻ. Tương tự như vậy, với tổ chức và doanh nghiệp hoạt động dựa trên uy tín, việc giám sát thông tin trên mạng xã hội có ý nghĩa sống còn nhưng khả năng giám sát hàng trăm trang web, hàng triệu người dùng, bài viết bằng tay và mắt người cực kì hạn chế. Các thuật toán Học máy ngày nay đã có khả năng thực hiện các nhiệm vụ giám sát camera, mạng xã hội để phát hiện ra các hành vi không mong muốn và tự động cảnh báo, giảm công sức giám sát bằng người và giảm thiệt hại cho cộng đồng, tổ chức. Trong hệ thống thanh toán, ngân hàng, các thuật toán Học máy đã giúp cảnh báo các giao dịch giả mạo, làm không gian số trong sạch và tạo niềm tin cho con người giao dịch trên đó. Các hệ thống thanh toán ngày nay có một loạt các công cụ giúp giám sát giao dịch, phân biệt giữa giao dịch hợp lệ và không hợp lệ. • Chăm sóc khách hàng. Bạn đã từng thấy cửa sổ chat bật lên mỗi khi bạn ghé thăm website của một cửa hàng? Khả năng cao đó là một tác tử hội thoại tự động được lập trình bởi các kỹ thuật Học máy. Những tác tử hội thoại này đóng vai trò nhân viên chăm sóc khách hàng, có nhiệm vụ giúp đỡ, trả lời các câu hỏi của khách. Bằng khả năng phân tích ngôn ngữ và khả năng truy xuất vào cơ sở dữ liệu của cửa hàng, tác tử hội thoại có thể trả lời khá chính xác yêu cầu của khách, tăng đáng kể xác suất mua hàng và sự hài lòng của khách hàng.

<!-- Page 34 -->

<!-- Page 35 -->
## 1.3 CÁC TÌNH HUỐNG ÁP DỤNG HỌC MÁY 9 này cũng đúng khi phải phân tích các mẫu dữ liệu có hàng nghìn hoặc hàng triệu thông tin như các thuật toán đánh giá sở thích người dùng để hiển thị quảng cáo trên website.

Các thông tin đơn lẻ này không những nhiều mà còn có thể có mối tương quan với nhau mà không một chương trình nào có thể mô tả bằng các lệnh rẽ nhánh trực tiếp. Khi đó sử dụng một mô hình Học máy là lựa chọn hợp lý. • Nhiệm vụ thay đổi thường xuyên: Một số bài toán thường xuyên thay đổi theo thời gian khiến cho chương trình phải cập nhật liên tục. Ví dụ như khi phân tích một trang web để tìm ra giá cả của sản phẩm. Nếu lập trình tường minh, chúng ta sẽ tìm các thẻ HTML chứa giá của sản phẩm. Tuy nhiên, cách tiếp cận này gặp phải vấn đề khi trang web cập nhật hoặc được thiết kế lại, thẻ HTML ban đầu có thể không còn đúng. Khi đó một thuật toán Học máy đã được huấn luyện bằng hàng triệu trang web sản phẩm, từ hàng nghìn website có thể sẽ tự động đoán được giá sản phẩm trên trang web mới. • Nhiệm vụ là vấn đề nhận thức: Ngày nay, khi làm việc với văn bản, ảnh, âm thanh hoặc phim, rất khó để không dùng Học máy. Các mô hình Học máy hiện đại gần đây như mạng nơ-ron sâu đã có khả năng thực hiện các nhiệm vụ nhận thức như: phân loại hình ảnh, phát hiện vị trí vật thể, phân vùng ngữ nghĩa trên ảnh, phân tích cấu trúc văn bản, phát hiện thực thể trong văn bản, trả lời hội thoại, dịch văn bản, nhận dạng âm thanh và tổng hợp âm thanh. Các mô hình Học máy đã thực hiện các nhiệm vụ nhận thức trên ở mức độ xấp xỉ khả năng của con người, trong đó đã vượt qua con người ở một số nhiệm vụ trong các đánh giá khách quan. Do đó, khi phải thực hiện một nhiệm vụ nhận thức trên các loại dữ liệu trên, hãy thử cách tiếp cận bằng Học máy. • Nhiệm vụ chưa được nghiên cứu kỹ lưỡng: Với các hiện tượng

<!-- Page 36 -->

<!-- Page 37 -->
## 1.4 CÁC PHƯƠNG PHÁP VÀ BÀI TOÁN TRONG HỌC MÁY 11 gán nhãn và xử lý dữ liệu.

Việc huấn luyện và triển khai sử dụng mô hình yêu cầu nhân lực được đào tạo chuyên sâu về Học máy và một số máy móc đặc biệt có thể khá đắt đỏ. Việc giám sát và bảo trì mô hình cũng đòi hỏi nguồn lực để liên tục duy trì sự hoạt động của mô hình. Do đó, ngay cả khi có thể áp dụng Học máy, chúng ta cũng cần tính đến hiệu quả chi phí của việc vận hành một hệ thống như vậy. 1.4 Các phương pháp và bài toán trong Học máy Các bài toán cơ bản trong Học máy được phân thành ba loại chính: Học có giám sát, Học không giám sát và Học tăng cường. Mỗi loại bài toán này đều có những đặc điểm riêng và yêu cầu các phương pháp, mô hình khác nhau. Cách chia này dựa trên thông tin mà mô hình Học máy nhận được từ dữ liệu. Chúng ta sẽ tìm hiểu kỹ hơn về mỗi loại bài toán này trong các mục sau. 1.4.1 Học có giám sát Đây là bài toán Học máy yêu cầu xây dựng mô hình mô tả mối quan hệ giữa đầu vào và đầu ra dựa trên dữ liệu là một tập hợp các cặp đầu vào - đầu ra. Đầu ra đóng vai trò hướng dẫn, giám sát của người thầy đối với mô hình hoặc thuật toán Học máy. Bài toán Học có giám sát thường được phát biểu dưới dạng: Định nghĩa 1.4 (Học có giám sát). Cho tập dữ liệu = (x ,y ) ,i = 1,2,...,n, trong đó x là i i i D { } ∈ X tập đầu vào, y là tập đầu ra, n là kích thước của dữ liệu , i ∈ Y D hãy tìm một hàm f : xấp xỉ mối quan hệ giữa đầu vào và X → Y đầu ra được chỉ ra trong tập dữ liệu , đánh giá bởi độ đo hiệu D suất P(f). Ví dụ 1.5 (Phân loại thư rác theo tiêu đề). Khi là tập các tiêu X đề thư điện tử, = thư rác,thư thường , ta có bài toán Học phân Y { }

<!-- Page 38 (Heavy) -->
Bảng 1.1: Ví dụ về bộ dữ liệu trong bài toán phân loại thư rác theo tiêu đề

|   Chỉ số | Tiêu đề                          | Phân loại   | |----------|----------------------------------|-------------| |        1 | Cuộc họp vào thứ 6 tuần này      | Thư thường  | |        2 | Giảm giá 50% cho tất cả sản phẩm | Thư rác     | |        3 | Thông báo về việc tăng lương     | Thư thường  |

lớp thư rác - thư thường dùng trong các chương trình quản lý thư điện tử như Outlook, Thunderbird, Gmail. Bảng 1.1 là một ví dụ về bộ dữ liệu trong bài toán phân loại thư rác theo tiêu đề có số lượng mẫu n = 3 . Cụ thể với mẫu thứ nhất, đầu vào x 1 là tiêu đề thư điện tử 'Cuộc họp vào thứ 6 tuần này' và đầu ra y 1 là nhãn 'thư thường'.

Ví dụ 1.6 (Dự đoán giá) . Khi X là giá cổ phiếu trong lịch sử tính trong khoảng thời gian nhất định như trong 1 ngày hoặc 1 tuần. Khi đó, giá trị mục tiêu Y = R + sẽ là giá cổ phiếu tại thời điểm sắp tới. Với thiết lập này, ta có bài toán Học dự đoán giá cổ phiếu tương lai.

Khi Y là tập hợp rời rạc, ta nói bài toán Học máy là bài toán phân lớp . Khi Y là tập số thực R , ta nói bài toán học máy là bài toán hồi quy .

Hiệu suất P ( f ) trong bài toán phân lớp (Chương 2) thường là số lỗi trung bình trên tập dữ liệu D , còn được gọi là hàm lỗi 0-1 và được định nghĩa như công thức (1.1).

̸

<!-- formula-not-decoded -->

Trong định nghĩa trên, I ( · ) là hàm chỉ báo được định nghĩa như sau:

<!-- formula-not-decoded -->

<!-- Page 39 -->
## 1.4 CÁC PHƯƠNG PHÁP VÀ BÀI TOÁN TRONG HỌC MÁY 13 Ví dụ, nếu ta tính được giá trị lỗi P(f) = 0,1, ta nói hàm f chính xác 90% trên tập dữ liệu .

D Hiệu suất P(f) trong bài toán hồi quy (Chương 7) được tính bằng trung bình bình phương sai số MSE (mean squared error) trên tập dữ liệu và được định nghĩa như công thức (1.2). D n 1 (cid:88) P(f) = (f(x ) y )2. (1.2) i i n − i=1 1.4.2 Học không giám sát Đây là bài toán Học máy yêu cầu xây dựng mô hình mô tả hoặc trích xuất quy luật của dữ liệu. Đặc điểm của các bài toán học không giám sát là không có dữ liệu về đầu ra mong muốn (tập ). Y Thuật toán, mô hình học không giám sát cần hiểu dữ liệu mà không cần thông tin về đầu ra. Có ba loại bài toán chính trong Học không giám sát, bao gồm: • Phân cụm (Chương 11): Tìm kiếm các nhóm, các cụm “gần nhau” trong dữ liệu; • Ước lượng mật độ (Chương 11): Ước lượng phân bố xác suất của dữ liệu. • Trích xuất đặc trưng (Chương 10): Tìm kiếm các đặc trưng quan trọng, các biểu diễn ẩn của dữ liệu. Trong thiết lập không cần dữ liệu mục tiêu để học, việc triển khai các thuật toán Học không giám sát thường dựa trên các giả định về cấu trúc của dữ liệu hoặc các quy luật tiềm ẩn trong dữ liệu. Vì thế với mỗi bài toán, chúng ta lại có những độ đo riêng để đánh giá hiệu suất của mô hình Học không giám sát. Ví dụ, trong bài toán phân cụm, chúng ta có thể sử dụng độ đo về khoảng cách trung bình tương đối của các cụm để đánh giá chất lượng phân

<!-- Page 40 -->

<!-- Page 41 -->
## 1.4 CÁC PHƯƠNG PHÁP VÀ BÀI TOÁN TRONG HỌC MÁY 15 1.4.4 Các bài toán lai 1.4.4.1 Học bán giám sát Đây là bài toán Học máy khi chúng ta có cả dữ liệu có nhãn và dữ liệu chưa gán nhãn.

Mục tiêu của các thuật toán học bán giám sát là tận dụng tất cả dữ liệu đang có, kể cả khi chưa được gán nhãn. Các tiếp cận này đặc biệt hữu dụng bởi lượng dữ liệu chưa được gán nhãn lớn hơn nhiều so với lượng dữ liệu đã được gán nhãn. Điều này đúng đối với dữ liệu ảnh, dữ liệu văn bản và dữ liệu âm thanh trong trường hợp việc gán nhãn dữ liệu rất đắt đỏ. Về mặt cách tiếp cận, Học bán giám sát có thể sử dụng các kỹ thuật Học không giám sát để hình thành quy luật của dữ liệu, sau đó kết hợp với việc sử dụng Học có giám sát để gán nhãn dữ liệu dựa trên quy luật đã tìm được. Hiện nay cách tiếp cận này rất phổ biến trong các mô hình học sâu, đặc biệt là trong các mô hình ngôn ngữ lớn. 1.4.4.2 Học tự giám sát Đây là cách tiếp cận trong Học không giám sát nhưng sử dụng phương pháp Học có giám sát. Kỹ thuật thường dùng ở đây là sử dụng chính dữ liệu đầu vào x để chế tạo ra đầu ra y = f(x) (trong trường hợp đơn giản nhất, có thể y = x). Sau đó sử dụng Học có giám sát trên tập dữ liệu gồm các cặp (x,y) đã được tạo ra. Như vậy, mô hình học tự giám sát sẽ học được một biểu diễn mới của x có tính bất biến với một số biến đổi được thiết kế bởi biến đổi f. Ví dụ 1.7 (Tô màu ảnh đen trắng). Giả sử ta có một tập ảnh màu I ,...,I . Ta thiết kế dữ liệu như sau = (x = Gray(I ),y = 1 n i i i D { I ) ,i = 1,...,n. Trong đó Gray( ) là hàm biến đổi ảnh màu thành i } · ảnh đen trắng. Nếu áp dụng một thuật toán Học có giám sát lên tập dữ liệu , ta sẽ thu được một mô hình có khả năng nhận vào D một ảnh đen trắng và tô màu ảnh đó.

<!-- Page 42 -->

<!-- Page 43 -->
## 1.4 CÁC PHƯƠNG PHÁP VÀ BÀI TOÁN TRONG HỌC MÁY 17 1.4.5.3 Học trực tuyến Đây là kỹ thuật huấn luyện, cập nhật tham số của mô hình học máy ngay khi có dữ liệu mới.

Hình thức học trực tuyến rất có ích khi dữ liệu đến theo luồng hoặc phân bố của dữ liệu thay đổi theo thời gian. Do đó, mô hình cũng phải thay đổi thường xuyên để đảm bảo hiệu suất khi có thay đổi trong dữ liệu. Để đánh giá thuật toán học trực tuyến, ta thường dùng đại lượng “độ hối tiếc” (regret) là hiệu số giữa hiệu suất thực tế khi học trực tuyến và hiệu suất khi biết trước toàn bộ dữ liệu. Mục tiêu của việc huấn luyện là giảm độ hối tiếc nhỏ nhất có thể. Ví dụ, đối với bài toán phân lớp n n 1 (cid:88) 1 (cid:88) R = I(f (x ) = y ) min I(f(x ) = y ). (1.3) i i i i i n ̸ − f n ̸ i=1 i=1 Trong đó min 1 (cid:80)n I(f(x ) = y ) là số lỗi trung bình tốt nhất có f n i=1 i ̸ i thể nếu ta biết trước toàn bộ tập dữ liệu còn 1 (cid:80)n I(f (x ) = y ) n i=1 i i ̸ i là số lỗi trung bình thực tế trong quá trình cập nhật mô hình trực tuyến f f ... f . 1 2 n → → → 1.4.5.4 Học chuyển đổi Học chuyển đổi (Mục 5.6) là kỹ thuật huấn luyện mô hình trên một nhiệm vụ, sau đó mô hình được huấn luyện tiếp cho một nhiệm vụ đích khác. Cách huấn luyện này cho phép xây dựng mô hình cho nhiệm vụ đích với ít dữ liệu có sẵn nhưng tận dụng tối đa các nguồn dữ liệu của nhiệm vụ khác có liên quan đến nhiệm vụ đích. Học chuyển đổi khác Học đa nhiệm vụ ở chỗ mô hình cho từng nhiệm vụ được huấn luyện tuần tự. Ngoài ra, khi chuyển đổi từ nhiệm vụ này sang nhiệm vụ khác, mô hình có thể được thay đổi đôi chút để phù hợp với nhiệm vụ mới nhưng vẫn giữ phần lớn các cấu trúc mô hình của nhiệm vụ cũ. Học chuyển đổi là kỹ thuật được áp dụng phổ biến, đặc biệt cho các mô hình Học sâu.

<!-- Page 44 -->

<!-- Page 45 (Heavy) -->
Hình 1.4: Quá trình phát triển, triển khai mô hình Học máy.

<!-- image -->

khai, cần chú ý đến các vấn đề như hiệu năng, bảo mật và tính ổn định của mô hình.

6. Sử dụng mô hình : Mô hình được sử dụng để giải quyết các vấn đề thực tế, đưa ra dự đoán, phân loại, gợi ý, tối ưu hóa, phân cụm, phân tích dữ liệu.
7. Giám sát mô hình : Mô hình cần được giám sát thường xuyên theo các tiêu chí đề ra ban đầu của mô hình. Các vấn đề xảy ra trong quá trình sử dụng mô hình cần được phát hiện và xử lý kịp thời.
8. Bảo trì mô hình : Mô hình cần được bảo trì, cập nhật để đảm bảo giữ được hiệu suất. Đặc biệt, khi dữ liệu thay đổi, mô hình cần được cập nhật để phù hợp với dữ liệu mới.

Tám bước trong vòng đời phát triển - triển khai mô hình Học máy nêu trên được vận dụng một cách linh hoạt. Nếu có vấn đề xảy ra cần thay đổi ở các bước trước, chúng ta có thể quay lại các bước trước đó để chỉnh sửa, hoàn thiện (xem Hình 1.4). Tại mỗi bước, thường các lập trình viên sử dụng các công cụ hoặc nền tảng có sẵn nhưng đôi khi họ phải tự xây dựng công cụ mới do yêu cầu nhiệm vụ hoặc yêu cầu về dữ liệu đặt ra.

<!-- Page 46 -->

<!-- Page 47 -->
## 1.7 BÀI TẬP 21 9.

Làm thế nào học máy có thể hỗ trợ việc phân tích các trang web liên tục thay đổi như trong ví dụ tìm kiếm giá sản phẩm? 10. Hãy so sánh hai phương pháp học có giám sát và học không giám sát. Đưa ra ví dụ thực tế cho mỗi phương pháp. 11. Giải thích bài toán phân loại thư rác và bài toán dự đoán giá cổ phiếu trong ngữ cảnh học có giám sát. 12. Trong các kỹ thuật học tăng cường, đâu là thách thức chính khi thiết kế một mô hình có phản hồi chậm từ môi trường? Bạn có ý tưởng nào để giải quyết thách thức này? 13. Hãy mô tả các bước chính trong vòng đời phát triển một mô hình học máy. 14. Tại sao việc thu thập và chuẩn bị dữ liệu là một bước quan trọng trong vòng đời của mô hình học máy? 15. Hãy giải thích vai trò của bước trích chọn đặc trưng và tại sao bước này giúp cải thiện hiệu năng của mô hình.

<!-- Page 48 -->

<!-- Page 49 -->
Tài liệu tham khảo [1] Jordan, Michael I. and Mitchell, Tom M., Machine learning: Trends, perspectives, and prospects, Science, vol. 349, no. 6245, pp. 255–260, 2015. [2] Bishop, Christopher M., Pattern recognition and machine learning, Springer, 2006. [3] Domingos, Pedro, A few useful things to know about machine learning, Communications of the ACM, vol. 55, no. 10, pp. 78–87, 2012. [4] Sutton, Richard S. and Barto, Andrew G., Reinforcement learning: An introduction, MIT Press, 2018. [5] Goodfellow, Ian, Bengio, Yoshua, and Courville, Aaron, Deep learning, MIT Press, 2016. [6] Amershi, Saleema, Begel, Andrew, Bird, Christian, DeLine, Robert, Gall, Harald, Kamar, Ece, Nushi, Besmira, et al., Soft- ware engineering for machine learning: A case study, Proceed- ings of the 41st International Conference on Software Engi- neering, pp. 291–300, 2019.

<!-- Page 50 -->
24 TÀI LIỆU THAM KHẢO [7] LeCun, Yann, Bengio, Yoshua, and Hinton, Geoffrey, Deep learning, Nature, vol. 521, no. 7553, pp. 436–444, 2015. [8] Mitchell, Tom M., Machine learning, McGraw Hill, 1997.

<!-- Page 51 -->
# Chương 2 Bài toán phân lớp Chương 2 tập trung vào một trong những bài toán quan trọng nhất của Học máy:

Bài toán phân lớp. Con người có một khả năng đặc biệt là khả năng phân biệt các đối tượng khác nhau và hình thành các khái niệm. Về mặt toán học, một khái niệm là một tập hợp các thực thể cùng loại. Ví dụ, khái niệm quả cam là tập hợp tất cả các quả cam, khái niệm ô tô là tập hợp mọi chiếc ô tô mà con người đã từng và sẽ làm ra. Như vậy, khả năng hình thành một khái niệm trong ý thức của con người là khả năng phân loại đối tượng thành hai lớp: các đối tượng thuộc về khái niệm đó và các đối tượng khác, không thuộc về khái niệm đó. Trong Học máy, ta gọi đó là bài toán phân lớp. Ta sẽ tìm hiểu dữ liệu huấn luyện, cách đánh giá tính sẵn sàng và mức độ đại diện của dữ liệu, cũng như các mô hình phân lớp thống kê cơ bản như Hồi quy Logistic, K láng giềng gần nhất hay Cây quyết định. Chương này có mối liên hệ mật thiết với Chương 7 về các mô hình hồi quy và Chương 4 về mô hình máy vector hỗ trợ vì cả ba đều hướng tới nhiệm vụ dự đoán dựa trên dữ liệu có nhãn.

<!-- Page 52 (Heavy) -->
## 2.1 Định nghĩa

Tổng quát hơn, ta có thể phân lớp các thực thể (hoặc đối tượng) thành nhiều lớp. Phát biểu một bài toán phân lớp như sau

Định nghĩa 2.1 (Bài toán phân lớp) . Cho X là tập đầu vào, Y = { 1 , 2 , . . . , C } là tập các phân lớp của X và tập dữ liệu huấn luyện D = { ( x i , y i ) } , i = 1 , 2 , . . . , n với ( x i , y i ) ∈ X × Y sao cho y i = f ( x i ) với f : X → Y là một hàm phân lớp ẩn chưa biết (hàm mục tiêu). Hãy tìm một hàm phân lớp h : X → Y sao cho h ( x ) gần giống với f ( x ) với mọi x ∈ X .

Tập huấn luyện D còn gọi là tập dữ liệu dùng để xác định các tham số của mô hình học máy. Trong tập dữ liệu D , mỗi giá trị ( x i , y i ) được gọi là mẫu huấn luyện. Trong đó, x i ∈ X được gọi là đặc trưng và y i ∈ Y được gọi là nhãn. Chúng ta có hai định nghĩa cơ bản về không gian đặc trưng và không gian nhãn như sau:

Định nghĩa 2.2 (Không gian đặc trưng) . Không gian đặc trưng là tập hợp tất cả các véc-tơ biểu diễn đầu vào của bài toán phân lớp. Không gian đặc trưng thường là không gian số thực R d với d chiều.

Định nghĩa 2.3 (Không gian nhãn) . Không gian nhãn là tập tất cả các nhãn của bài toán phân lớp. Không gian nhãn thường là tập rời rạc Y với C lớp.

Ví dụ 2.4 (Một số bài toán phân lớp) . Để làm quen với khái niệm phân lớp, ta sẽ cùng tìm hiểu một số thiết lập bài toán phân lớp đơn giản.

1. Bài toán phân lớp hàm logic XOR: trong bài toán phân lớp hàm logic XOR, nhiệm vụ đặt ra là học ra được mô hình dự đoán kết quả của phép toán logic XOR dựa trên giá trị đầu vào. Dữ liệu được thể hiện ở bảng 2.1. Tập dữ liệu D có tổng cộng bốn mẫu,

<!-- Page 53 (Heavy) -->
Bảng 2.1: Dữ liệu cho bài toán phân lớp học hàm XOR

|     |   x 1 |   x 2 |   y | |-----|-------|-------|-----| | x 1 |     0 |     0 |   0 | | x 2 |     0 |     1 |   1 | | x 3 |     1 |     0 |   1 | | x 4 |     1 |     1 |   0 |

mỗi mẫu có hai đặc trưng tương ứng. Các đặc trưng của mẫu huấn luyện được kí hiệu là x 1 và x 2 , nhận giá trị 0 hoặc 1. Do tính ràng buộc về giá trị logic nên các đặc trưng này được coi là rời rạc. Kết quả phân lớp thành tập y = 0 và y = 1 nên số lớp C = 2 . Trong ví dụ cơ bản này, chúng ta thấy được số lượng mẫu cần thiết để phân lớp chỉ cần bốn mẫu.

2. Bài toán phân lớp hoa IRIS: trong bài toán phân lớp hoa IRIS, dữ liệu đầu vào là tập các đặc trưng của cánh hoa và đài hoa. Từ đó, các giá trị này được sử dụng để phân lớp vào các lớp con của loài hoa IRIS. Tập đặc trưng được sử dụng là: chiều dài và chiều rộng của cánh hoa và đài hoa. Các đặc trưng này nhận giá trị thực, nên không gian đặc trưng là R 4 . Số lớp con là ba lớp nên C = 3 .
3. Bài toán phân lớp MNIST: trong bài toán phân lớp MNIST, mỗi đối tượng là một ảnh chữ số đã được rời rạc hóa thành các điểm ảnh. Chiều dài và chiều rộng của một ảnh MNIST là 28 nên số đặc trưng tổng cộng có 28 × 28 = 784 . Các chữ số nhận giá trị từ 0 đến 9 nên tổng cộng số lớp phải phân lớp là C = 10 .

Trong định nghĩa trên, C gọi là số lớp của bài toán phân lớp. Khi C bằng 2, ta nói đây là bài toán phân lớp nhị phân . Trên thực tế việc phân lớp với C bằng 2 có ý nghĩa quan trọng về mặt lý thuyết. Vì nếu có thể phân lớp đúng được với hai lớp bất kì thì

<!-- Page 54 -->

<!-- Page 55 -->
## 2.3 CÁCH TIẾP CẬN HỌC MÁY THỐNG KÊ 29 liệu được sử dụng.

Để giải quyết vấn đề này, chúng ta có thể tiếp cận bài toán phân lớp qua lăng kính của ngành xác suất thống kê. Định nghĩa 2.5 (Bài toán phân lớp thống kê). Cho là tập đầu X vào, = 1,2,...,C là tập các phân lớp của và tập dữ liệu Y { } X huấn luyện D = (x ,y ) ,i = 1,2,...,n với (x ,y ) được i i i i { } ∈ X × Y lấy mẫu theo phân bố dữ liệu (x,y), hãy tìm một mô hình phân P lớp h : phân lớp tốt trên phân bố . Nghĩa là xác suất lỗi X → Y P phân lớp P h(X) = Y nhỏ. (X,Y)∼P { ̸ } Trong đó sự kiện phân lớp sai h(X) = Y là một sự kiện ngẫu { ̸ } nhiên trong phân bố ngẫu nhiên của các biến ngẫu nhiên X,Y . P Điểm khác của Định nghĩa 2.5 so với Định nghĩa 2.1 là các mẫu dữ liệu (x,y) được lấy mẫu theo một phân bố xác suất nhất P định. Định nghĩa 2.5 cho phép mô tả sự không chắc chắn của nhãn y trong bài toán phân lớp, khác với Định nghĩa 2.1 nhãn y được xác định hoàn toàn bởi hàm mục tiêu f(x). Mọi tính toán định lượng của bài toán phân lớp được tính toán trên phân bố P. Ta gọi xác suất của sự kiện phân lớp sai là xác suất lỗi, tỉ lệ lỗi hay rủi ro kì vọng của mô hình phân lớp h. Xác suất này được định nghĩa theo công thức sau: err (h) = P h(X) = Y = E I[h(X) = Y ], (2.1) P (X,Y)∼P P { ̸ } ̸ với I là hàm chỉ thị (indicator function) của sự kiện phân lớp sai  1, nếu h(X) = Y, I[h(X) = Y ] = ̸ ̸ 0, nếu h(X) = Y. Việc giải bài toán phân lớp thống kê là tìm một mô hình phân lớp h⋆ sao cho h⋆ = arg minerr (h). (2.2) P h

<!-- Page 56 (Heavy) -->
Trên thực tế, nói chung ta không biết chính xác phân bố P của dữ liệu mà chỉ biết tập dữ liệu D được giả sử lấy mẫu từ phân bố này. Do đó, đại lượng err P ( h ) không thể tính được mà phải ước lượng thông qua tập dữ liệu D . Tức là ta xấp xỉ err P ( h ) bằng đại lượng ̂ err D ( h ) được tính trên tập dữ liệu D :

̸

<!-- formula-not-decoded -->

Đại lượng ̂ err D ( h ) ở công thức (2.3) được gọi là tỉ lệ lỗi (error rate) hoặc rủi ro thực nghiệm (empirical risk) của h trên tập dữ liệu D .

## 2.4 Ước lượng xác suất lỗi

Xấp xỉ err P ( h ) bằng ̂ err D ( h ) tốt đến mức nào? Định lý sau cho chúng ta biết rằng nếu tập dữ liệu D càng lớn thì xấp xỉ này càng chính xác.

Định lý 2.6 (Xấp xỉ rủi ro kì vọng bằng rủi ro thực nghiệm) . Xét một hàm phân lớp h cố định, nếu các mẫu dữ liệu ( x i , y i ) được lấy mẫu độc lập từ phân bố P thì với mọi giá trị ϵ &gt; 0 ,

<!-- formula-not-decoded -->

Hay nói cách khác, với mọi giá trị ϵ, δ &gt; 0 , với xác suất không thấp hơn 1 -δ trên tập dữ liệu D có n ≥ 1 2 ϵ 2 ln ( 2 δ ) mẫu dữ liệu, ta có

<!-- formula-not-decoded -->

Chứng minh: Áp dụng định lý Hoeffding với X i = I [ h ( x i ) = y i ] và µ = err P ( h ) = E P [ X i ] , ta có 0 ≤ X i ≤ 1 nên

̸

<!-- formula-not-decoded -->

<!-- Page 57 (Heavy) -->
Giải bất đẳng thức trên ta có

<!-- formula-not-decoded -->

Định lý 2.6 cho thấy, khi số mẫu dữ liệu n càng lớn thì xác suất để lỗi thực nghiệm gần bằng lỗi kì vọng ngày càng lớn. Ví dụ, nếu ϵ = 1% , n = 100000 , tỉ lệ lỗi trung bình trên 100.000 mẫu dữ liệu là 10% thì tỉ lệ lỗi thực tế nằm trong khoảng [10% ± 1%] với xác suất không thấp hơn 1 -2 e -20 ≈ 1 -4 . 10 -9 , tức là gần bằng 1. Đây cũng là một trong các lý do tại sao Học máy lại cần nhiều dữ liệu để huấn luyện mô hình như vậy. Ước lượng sai số của Định lý 2.6 là cận dưới đúng với mọi phân bố P nên ước lượng này thường được xem là ước lượng không chặt.

Như vậy, khi có nhiều dữ liệu, việc cực tiểu hóa rủi ro thực nghiệm ̂ err D ( h ) có thể dẫn đến việc cực tiểu hóa rủi ro kì vọng err P ( h ) . Ta gọi cách tiếp cận này là nguyên tắc Tối thiểu hóa rủi ro thực nghiệm (Empirical Risk Minimization - ERM). Trong cách tiếp cận này, ta sẽ chọn một hàm phân lớp h D trong một tập các hàm phân lớp sao cho

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Trong trường hợp đơn giản nhất là chọn h trong một tập hữu hạn các hàm phân lớp H có chứa h ⋆ , nguyên tắc Tối thiểu hóa rủi ro thực nghiệm có thể xấp xỉ được h ⋆ với xác suất cao (PAC - Probably Approximately Correct). Định lý này được phát biểu như sau:

Định lý 2.7 (Học xấp xỉ với xác suất cao (PAC Learning)) . Xét lớp hàm phân lớp hữu hạn và một hàm phân lớp h ⋆ , nếu

H ∈ H

H

<!-- Page 58 (Heavy) -->
- ·
- n ≥ 2 ϵ 2 ln ( 2 |H| δ ) mẫu dữ liệu ( x i , y i ) , i = 1 , 2 , . . . , n được lấy mẫu độc lập từ phân bố P và
- err P ( h ⋆ ) = 0 ,

thì với mọi giá trị ϵ &gt; 0 và δ &gt; 0 , với xác suất không thấp hơn 1 -δ trên tập dữ liệu D , ta có:

<!-- formula-not-decoded -->

Chứng minh: Sử dụng Định lý 2.6, với mỗi h ∈ H , ta có

<!-- formula-not-decoded -->

Do đó để xác suất tồn tại ít nhất một h ∈ H như trên là

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Vậy ta có xác suất để cùng lúc mọi h ∈ H đều có | ̂ err D ( h ) -err P ( h ) ϵ/ 2 ít nhất là 1 δ .

| ≤ -

Ta có với xác suất không thấp hơn 1 δ ,

-

<!-- formula-not-decoded -->

Giải 2 |H| e -nϵ 2 / 2 ≤ δ ta có

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

□

<!-- Page 59 -->
## 2.4 ƯỚC LƯỢNG XÁC SUẤT LỖI 33 Định lý 2.7 cho thấy rằng nếu số mẫu dữ liệu n đủ lớn, ta có thể sử dụng nguyên tắc Tối thiểu hóa rủi ro thực nghiệm để tìm ra một hàm phân lớp h có xác suất lỗi err (h ) nhỏ hơn một giá trị D P D ϵ bất kì với xác suất cao 1 δ.

Định lý này cũng cho thấy rằng số − mẫu dữ liệu n cần thiết tỉ lệ thuận với kích thước log . Hay nói |H| cách khác, độ lớn của lớp hàm phân lớp phần nào quyết định độ H khó của bài toán phân lớp. Một giả thiết của Định lý 2.7 là lớp hàm phân lớp là hữu H hạn. Giả thiết này có thật sự không thực tế? Trong thực hành, khi ta lập trình các mô hình học máy, ta thường sử dụng các hàm phân lớp có thể được biểu diễn bằng một số lượng hữu hạn các tham số là số thực (64 bit). Giả sử một mô hình cần N bit nhị phân để biểu diễn thì số lượng mô hình khác nhau mà ta có thể tạo ra là = 2N. Do đó, số lượng mô hình khác nhau mà ta có thể tạo ra |H| là hữu hạn. Khi đó sử dụng Định lý 2.7 là hợp lý và số lượng mẫu dữ liệu cần thiết là (cid:18) (cid:19) 2 1 n N + 1 + ln . ≥ ϵ2 δ Việc giới hạn độ lớn của lớp hàm phân lớp là một trong những H cách để giảm độ khó của bài toán phân lớp cũng như tăng khả năng tổng quát của mô hình. Định lý 2.8 (Không có bữa trưa miễn phí) cho thấy rằng nếu là tập tất cả các hàm phân lớp (không bị giới H hạn) thì không có thuật toán huấn luyện nào có thể tìm ra hàm phân lớp h với xác suất lỗi err (h ) nhỏ hơn một giá trị ϵ bất kì D P D với xác suất cao 1 δ cho mọi phân bố . − P Định lý 2.8 (Không có bữa trưa miễn phí). Cho là tập tất cả H các hàm phân lớp trên tập đầu vào . Nếu tập dữ liệu D có n dữ X liệu được lấy mẫu độc lập từ phân bố , sao cho 2n < thì với P |X| mọi thuật toán huấn luyện A, luôn tồn tại một phân bố sao cho P P [err (A(D)) > 1/8] 1/7. D∼Pn P ≥

<!-- Page 60 -->

<!-- Page 61 -->
## 2.5 HÀM PHÂN LỚP TỐI ƯU BAYES 35 Đại lượng err (h,x) = (cid:80) I[h(x) = y]P(y x) là xác suất xảy P y ̸ | ra lỗi khi áp dụng hàm phân lớp h trên dữ liệu x.

Với nhận xét I[h(x) = y] chỉ khác 0 khi h(x) = y, ta có thể tính được err (h,x) P ̸ ̸ như sau: (cid:88) err (h,x) = P(y x) = 1 P(h(x) x). (2.7) P | − | y̸=h(x) Như vậy, để tối thiểu hóa xác suất lỗi trên từng mẫu dữ liệu x ta phải chọn h⋆ sao cho err (h⋆,x) nhỏ nhất hay P(h⋆(x) x) lớn nhất. P | Định nghĩa 2.9 (Hàm phân lớp tối ưu Bayes). Hàm phân lớp tối ưu Bayes là hàm phân lớp thỏa mãn đẳng thức: h⋆(x) = arg maxP(y x), (2.8) y | trong đó, P(y x) được gọi là phân bố hậu nghiệm của nhãn y khi | biết đầu vào x trong phân bố . P Dễ thấy, do err (h⋆,x) err (h,x), h,x nên err (h⋆) err (h) P P P P ≤ ∀ ≤ với mọi h. Hàm phân lớp h⋆ đạt giá trị tối ưu R⋆ là xác suất lỗi phân lớp nhỏ nhất có thể trên phân bố . P Dựa theo công thức (2.8) để tìm h⋆ ta phải biết phân bố hậu nghiệm P(y x). Trong thực tế, việc ước lượng P(y x) một cách | | chính xác là không khả thi do chúng ta chỉ biết tập dữ liệu D = (x ,y ) ,i = 1,...n mà không biết phân bố . Tuy nhiên, công i i { } P thức (2.8) này cũng chỉ ra phương hướng để chúng ta tìm h⋆ hoặc ít nhất là xấp xỉ h⋆. Có hai cách tiếp cận chính trong Học máy xuất phát từ định nghĩa này. • Mô hình sinh (Chương 11): Là mô hình Học máy ước lượng trực tiếp xác suất p(x,y) (hoặc mật độ xác suất) là xác suất sinh ra cặp dữ liệu (x,y) từ phân bố . Từ phân bố này, ta có thể tìm P

<!-- Page 62 (Heavy) -->
h ⋆ theo khai triển sau:

<!-- formula-not-decoded -->

- Mô hình phân biệt (Các chương 3, 4, 7): Là mô hình Học máy ước lượng xác suất P ( y | x ) hoặc trực tiếp hàm phân lớp h ⋆ ( x ) .

Trong các mục sau của chương này và các chương kế tiếp của giáo trình, chúng ta sẽ tìm hiểu một loạt thuật toán và mô hình Học máy tuân theo một trong hai cách tiếp cận trên.

## 2.6 Mô hình hồi quy Logistic

Định nghĩa 2.10 (Mô hình hồi quy Logistic nhị phân) . Xét bài toán phân lớp nhị phân với X = R d và Y = {± 1 } , mô hình hồi quy Logistic là mô hình ước lượng xác suất hậu nghiệm P ( y | x ) như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Trong đó, f ( x ) = w T x + b là hàm tuyến tính (tuyến tính đối với bộ tham số w , b ) còn σ ( z ) = 1 1+ e -z gọi là hàm sigmoid . Nếu chúng ta lợi dụng tính chất y = ± 1 thì có thể kết hợp cả hai công thức trên lại thành một công thức rút gọn như sau:

<!-- formula-not-decoded -->

Đại lượng s = yf ( x ) gọi là điểm số của mẫu dữ liệu ( x , y ) .

Theo hàm phân lớp tối ưu Bayes, trong pha suy luận, ta sẽ chọn nhãn y ⋆ = arg max y = ± 1 P ( y | x ) . Nhưng do tổng các xác suất bằng

<!-- Page 63 -->
## 2.6 MÔ HÌNH HỒI QUY LOGISTIC 37 1 nên ta chỉ cần tìm y⋆ sao cho P(y⋆ x) > 0,5.

Thế vào các công | thức trên, trong pha suy luận, ta sẽ dùng luật phân lớp sau:  +1, f(x) 0 h(x) = ≥ .  1, f(x) < 0 − Lỗi của mô hình xảy ra khi h(x) = y hay s = yf(x) < 0, tức là ̸ I(h(x) = y) = I(yf(x) < 0). ̸ Cũng như mọi mô hình Học máy khác, trước khi sử dụng mô hình Logistic để dự đoán, chúng ta cần phải huấn luyện mô hình sử dụng một tập dữ liệu huấn luyện D = (x ,y ) ,i = 1,2,...,n. i i { } Mục tiêu của việc huấn luyện là tìm bộ trọng số Θ = (w,b) hợp lý nhất (hoặc ít “lỗi” nhất) trên bộ dữ liệu này. 2.6.1 Nguyên lý Ước lượng hợp lý cực đại Ta xét một mẫu dữ liệu (x,y) . Xác suất của nhãn y theo mô ∼ P hình Logistic là P(y x) = σ(yf(x)). Rõ ràng, nếu xác suất này càng | lớn thì khả năng mô hình phân lớp mẫu dữ liệu này càng chính xác. Như vậy L = P(y x) có thể coi như là sự hợp lý của mô hình đối | với mẫu dữ liệu (x,y). Bây giờ xét tập dữ liệu D có n mẫu dữ liệu. Nếu giả sử các mẫu dữ liệu của D độc lập xác suất thì sự hợp lý của mô hình đối với D là tích độ hợp lý của các mẫu dữ liệu. Định nghĩa 2.11 (Độ hợp lý của mô hình Logistic). Đại lượng n n (cid:89) (cid:89) L(Θ;D) = P(y x ) = σ(y f(x )) i i i i | i=1 i=1 gọi là độ hợp lý (likelihood) của mô hình Logistic đối với dữ liệu D. Ta còn nói L(Θ;D) là độ hợp lý của bộ trọng số Θ của mô hình.

<!-- Page 64 (Heavy) -->
Lưu ý L (Θ; D ) là một hàm của bộ trọng số Θ , còn D có thể coi là hằng số do D là dữ liệu được cung cấp để huấn luyện mô hình. Sử dụng độ hợp lý của mô hình, ta có thể huấn luyện mô hình bằng cách tìm bộ trọng số Θ cực đại hoá độ hợp lý này theo Nguyên lý ước lượng hợp lý cực đại.

Định nghĩa 2.12 (Nguyên lý Ước lượng hợp lý cực đại) . Mô hình tốt nhất là mô hình có độ hợp lý cực đại MLE (Maximum Likelihood Estimation) được định nghĩa là:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Trong định nghĩa này, ta cũng sử dụng hàm log để tính toán do độ hợp lý thường là tích của độ hợp lý trên các mẫu dữ liệu. Một phương pháp cực tiểu hoá hàm số là cập nhật trọng số theo hướng ngược của đạo hàm. Hay thường được gọi tắt là phương pháp tối ưu xuống đồi bằng đạo hàm GD (gradient descent). Xét hàm âm lô-ga-rít của độ hợp lý như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Hình 2.1 cho thấy hàm -log σ ( s ) với s = yf ( x ) là cận trên của hàm lỗi 0-1 do -log 2 σ ( s ) ≥ I ( s &lt; 0) . Như vậy, có thể nói nguyên lý ước lượng hợp lý cực đại cực tiểu hóa một cận trên của hàm lỗi 0-1.

<!-- Page 65 (Heavy) -->
Hình 2.1: Hàm lỗi Logistic -log σ ( s ) với s = yf ( x ) .

<!-- image -->

## 2.6.2 Thuật toán huấn luyện

Sử dụng đẳng thức σ ′ ( z ) = σ ( z )(1 -σ ( z )) , ta có thể biến đổi đạo

hàm của hàm ℓ như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Sử dụng một hệ số huấn luyện λ &gt; 0 , ta có thể cập nhật Θ , theo công thức sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Hình 2.2 minh hoạ kết quả cập nhật của trọng số theo hướng của đạo hàm với một bước. Ở bước ban đầu trọng số w xuất phát

<!-- Page 66 (Heavy) -->
Hình 2.2: Minh hoạ kết quả cập nhật của trọng số theo hướng của đạo hàm.

<!-- image -->

từ vùng có lỗi lớn tại vị trí w 0 = (0 . 5 , 0 . 5) . Tại vị trí này, chiều cập nhật đạo hàm là véc-tơ theo hướng đường đi được dấu và sau một bước cập nhật trọng số trọng số w đã đi đến vị trí w 1 (điểm màu đỏ). Trọng số tối ưu trong ví dụ trên được đánh dấu bằng dấu chấm xanh, là mục tiêu cần đạt được của quá trình huấn luyện mô hình.

Nhận xét đại lượng 1 -σ ( y i f ( x i )) = 1 -P ( y i | x i ) chính là phần còn thiếu để xác suất P ( y i | x i ) = 1 , mục tiêu của việc huấn luyện. Như vậy các công thức cập nhật trên có xu hướng giúp đẩy các xác suất P ( y i | x i ) tăng lên. Ngoài ra nếu mỗi lần huấn luyện chúng ta chỉ đưa một mẫu dữ liệu vào huấn luyện (học trực tuyến) thì các công thức trên trở thành:

<!-- formula-not-decoded -->

Công thức trên có một hệ số tuyến tính (1 -σ ( y i f ( x i ))) có thể

<!-- Page 67 (Heavy) -->
coi là sai số về xác suất của mô hình trên mẫu dữ liệu ( x i , y i ) . Các thuật toán huấn luyện mô hình Logistic được liệt kê ở Thuật toán 2.1 và Thuật toán 2.2.

## Thuật toán 2.1 Thuật toán huấn luyện mô hình hồi quy Logistic

` 1: procedure TrainLogistic ( D = { ( x i , y i ) } n i =1 , λ ) 2: Khởi tạo w ← 0 , b ← 0 3: for epoch = 1 , 2 , . . . do 4: w ← w + λ n ∑ i =1 (1 -σ ( y i f ( x i ))) y i x i 5: b ← b + λ n ∑ i =1 (1 -σ ( y i f ( x i ))) y i 6: if điều kiện dừng then break 7: end for 8: return w , b 9: end procedure `

Thuật toán 2.2 Thuật toán huấn luyện trực tuyến mô hình hồi quy Logistic

` 1: procedure TrainLogisticOnline ( D = { ( x i , y i ) } n i =1 , λ ) 2: Khởi tạo w ← 0 , b ← 0 3: for epoch = 1 , 2 , . . . do 4: for all ( x i , y i ) ∈ D do 5: w ← w + λ (1 -σ ( y i f ( x i ))) y i x i 6: b ← b + λ (1 -σ ( y i f ( x i ))) y i 7: end for 8: if điều kiện dừng then break 9: end for 10: return w , b 11: end procedure `

Điều kiện dừng của các thuật toán huấn luyện trên có thể là

- Khi số epoch đủ lớn;

<!-- Page 68 (Heavy) -->
- Khi log-likelihood ℓ (Θ; D ) thay đổi không nhiều;
- Khi hiệu suất phân lớp trên tập dữ liệu kiểm thử không tăng sau nhiều epoch .

Về hệ số huấn luyện λ , ta sẽ xem xét kỹ hơn ở các mục sau trong giáo trình. Thường ta thử chọn λ trong các giá trị { 10 i } với i = -5 , -4 , . . . , 0 .

## 2.7 Thuật toán K láng giềng gần nhất

Một trong những thuật toán phân lớp đầu tiên của Học máy là thuật toán K-láng giềng gần nhất, thường được viết tắt là KNN. Thuật toán này hoạt động trên tập đầu vào là không gian số thực m chiều với hàm khoảng cách d ( x , x ′ ) . Hàm khoảng cách d có thể là một hàm khoảng cách bất kỳ thỏa mãn bất đẳng thức tam giác (thường dùng khoảng cách Euclid d ( x , x ′ ) = ∥ x -x ′ ∥ 2 2 ).

Thuật toán KNN là thuật toán theo hướng tiếp cận mô hình phân biệt. Giả sử ta có tập dữ liệu huấn luyện D = { ( x i , y i ) } , i = 1 , 2 , . . . , n với x i ∈ R m và y i ∈ Y = { 1 , 2 , . . . C } . Thuật toán KNN ước lượng xác suất hậu nghiệm P ( y | x ) đối với mỗi mẫu dữ liệu x bằng cách xét một lân cận V của x trong không gian R m chứa đúng k mẫu dữ liệu trong D . Khi đó, ta ước lượng P ( y | x ) bằng đại lượng:

<!-- formula-not-decoded -->

trong đó, tử số là số mẫu dữ liệu có nhãn y i = y nằm trong lân cận V . Nếu ta dùng ̂ P ( y | x ) thay thế cho P ( y | x ) để tạo ra hàm h KNN , dễ thấy h KNN ( x ) sẽ là nhãn y xuất hiện nhiều nhất trong các mẫu dữ liệu huấn luyện nằm trong lân cận V (Hình 2.3).

Thuật toán KNN (Thuật toán 2.3) khá đơn giản. Trong pha huấn luyện, thuật toán KNN không làm gì ngoài việc lưu trữ tất

<!-- Page 69 -->
## 2.7 THUẬT TOÁN K LÁNG GIỀNG GẦN NHẤT 43 Hình 2.3:

Thuật toán KNN với k = 3 và k = 5. Thuật toán 2.3 Thuật toán KNN 1: procedure KNN(x,D,k) 2: Tìm k mẫu dữ liệu gần x nhất trong D theo khoảng cách d(x ,x) i 3: Đếm số lượng các nhãn c ,c ,...,c trong k mẫu dữ liệu 1 2 C gần nhất 4: return yˆ arg max c y y ← 5: end procedure cả các mẫu dữ liệu huấn luyện trong D. Trong pha suy luận , KNN chọn nhãn xuất hiện nhiều nhất trong k mẫu dữ liệu huấn luyện gần x nhất. Độ phức tạp thuật toán trong pha suy luận chủ yếu nằm ở bước tìm kiếm k “láng giềng” của x. Để tối ưu thời gian suy luận, người ta thường dùng các cấu trúc tìm kiếm không gian như cây kd, cây bóng. Chi tiết cài đặt các cấu trúc dữ liệu tìm kiếm không gian nằm ngoài phạm vi của giáo trình. Tuy nhiên thời gian tìm kiếm có thể rút ngắn còn cỡ O(mk log n) cho việc tìm kiếm k “láng giềng” gần nhất của x trong không gian m chiều. Định lý 2.13 (Cận trên tỉ lệ lỗi của KNN với k = 1). Khi số mẫu

<!-- Page 70 (Heavy) -->
huấn luyện n →∞ , ta có ước lượng tỉ lệ lỗi err P ( h KNN ) của KNN với k = 1 như sau:

<!-- formula-not-decoded -->

Trong đó, R ⋆ là xác suất lỗi tối ưu Bayes.

Định lý 2.13 cho thấy chỉ cần với k = 1 , khi có đủ dữ liệu, xác suất lỗi của hàm phân lớp h KNN không vượt quá hai lần so với xác suất lỗi tối ưu R ⋆ . Với k > 1 càng lớn thì err P ( h KNN ) càng tiến đến sát R⋆ . Đây là một kết quả thú vị nhưng nó đòi hỏi số mẫu huấn luyện n rất lớn so với k.

## 2.8 Thuật toán Cây quyết định

Thuật toán phân lớp dùng Cây quyết định (Decision Tree - DT) có cách tiếp cận tương tự như thuật toán KNN. Theo đó, thuật toán DT cũng ước lượng xác suất P ( y | x ) trong một lân cận V của x . Tuy nhiên, khác với thuật toán KNN tính toán lân cận V trong pha suy luận (bằng cách tìm lân cận chứa k láng giềng), thuật toán DT tính toán lân cận V trong pha huấn luyện bằng cách phân vùng tập dữ liệu đầu vào X thành các vùng riêng biệt nhờ chuỗi các quyết định đơn giản (lệnh rẽ nhánh) sao cho việc phân lớp trong mỗi vùng trở nên dễ dàng hơn (Hình 2.4 mô tả cây quyết định 'Đi bộ' hay 'Đi xe buýt').

Giả sử tập đầu vào X gồm các dữ liệu x = ( x 1 , . . . , x m ) gồm m thuộc tính, kí hiệu A = { A 1 , A 2 , . . . , A m } , trong đó x k ∈ A k . Các thuộc tính A k có thể rời rạc (ví dụ: thuộc tính màu sắc) hoặc liên tục (ví dụ: thuộc tính cân nặng). Xét các trường hợp sau:

- A k là thuộc tính rời rạc: thuộc tính A k chia tập đầu vào X thành n k = | A k | tập con ứng với từng quyết định x k = v với v là các

<!-- Page 71 (Heavy) -->
Hình 2.4: Cây quyết định phân lớp.

<!-- image -->

Hình 2.5: Cây quyết định phân chia tập đầu vào cho bài toán phân lớp.

<!-- image -->

giá trị trong A k . Ví dụ: thuộc tính Thời tiết trong Hình 2.4 có các giá trị 'Nắng', 'Mây mù', 'Mưa'.

<!-- formula-not-decoded -->

- A k là thuộc tính liên tục, A k ⊂ R : nếu ta chọn một ngưỡng θ ∈ R thì tập đầu vào X được chia thành hai tập con ứng với các quyết định x k ≤ θ và x k &gt; θ (ví dụ: thuộc tính Thời gian đến giờ làm việc trong Hình 2.4 được so sánh với ngưỡng 60 phút).

<!-- formula-not-decoded -->

Nếu ta gắn các quyết định như trên lên một cấu trúc dạng cây, ta đã phân chia tập đầu vào X một cách đệ quy thành các phân vùng

<!-- Page 72 -->

<!-- Page 73 -->
## 2.8 THUẬT TOÁN CÂY QUYẾT ĐỊNH 47 là số lượng mẫu ít nhất ở lá.

Tham số này là một tham số của thuật toán sẽ được lựa chọn để tránh hiện tượng học quá. Một điều kiện dừng khác là tập D chỉ còn duy nhất một nhãn phân lớp. • Cách chọn thuộc tính phân chia Ak (hàm chooseAttribute) và cách chọn ngưỡng θ khi Ak là thuộc tính liên tục: Đây chính là điểm phân biệt các thuật toán huấn luyện Cây quyết định. Trong bài này, chúng ta xem xét hai cách chọn thuộc tính phân chia của thuật toán ID3 và thuật toán C4.5. 2.8.1 Thuật toán ID3 Thuật toán ID3 lựa chọn thuộc tính dựa trên khái niệm độ tăng thông tin. Trong xác suất thống kê, khái niệm thông tin xuất phát từ định nghĩa về entropy thông tin là một thang đo mức độ ngẫu nhiên. Vì các nhãn phân lớp là rời rạc, ta có thể đo lường mức độ ngẫu nhiên của các nhãn này bằng entropy. Giả sử trong bài toán phân lớp, ta có một tập dữ liệu huấn luyện D = (x ,y ) ,i = 1,2,...,n gồm n mẫu dữ liệu với các nhãn i i { } (y ,y ,...,y ). Entropy của tập các nhãn này được định nghĩa là: 1 2 n C (cid:88) c c y y H(D) = log , (2.10) − n 2 n y=1 trong đó c là số lần nhãn y xuất hiện trong D. Có thể chứng minh y H(D) = 0 nếu tồn tại y để c = n (dãy các nhãn toàn bằng y, y entropy bằng 0, rất dễ đoán ra nhãn y). Còn khi c = n với mọi y y C thì H(D) đạt giá trị cực đại (entropy cực đại, rất khó để đoán nhãn y). Entropy H(D) càng nhỏ thì lựa chọn nhãn y⋆ = arg max c đại y y diện cho tập D có xác suất lỗi càng nhỏ. Giả sử ta lựa chọn thuộc tính Ak để phân chia và D bị chia thành n tập con D ,...,D . Khi đó, mỗi tập D sẽ có H(D ) là k 1 n i i k

<!-- Page 74 -->

<!-- Page 75 (Heavy) -->
Thuật toán C4.5 lựa chọn thuộc tính A k sao cho IGR ( D,A k ) tính theo các công thức (2.13), (2.14) đạt cực đại.

## 2.8.3 Thuộc tính liên tục

Khi thuộc tính A k rời rạc, ta có thể nhanh chóng tính các tập con D i tương ứng với từng giá trị v ∈ A k (độ phức tạp thuật toán O ( n + n k C ) ). Nhưng khi thuộc tính A k liên tục, ta còn phải xác định ngưỡng θ để phân chia D thành hai tập con D 1 , D 2 theo công thức sau:

<!-- formula-not-decoded -->

Về mặt lý thuyết chúng ta phải tìm θ trên toàn bộ tập số thực R . Tuy nhiên, để ý rằng dù chọn θ thế nào thì cũng chỉ có n +1 khả năng cho D 1 , D 2 do chỉ có nhiều nhất n giá trị của x k trong D . Dựa trên nhận xét này, chúng ta có thể xây dựng một thuật toán hiệu quả để dò ngưỡng θ như sau:

` Thuật toán 2.5 Dò ngưỡng θ cho thuộc tính liên tục A k 1: function FindThreshold ( D,A k ) 2: Sắp xếp D : x 1 ≤ x 2 ≤ . . . ≤ x n 3: Khởi tạo n y = 0 , c y = ∑ n i =1 I ( y i = y ) , ∀ y = 1 , 2 , . . . , C 4: H ( D | A k ) = ∞ 5: for i = 1 đến n do 6: Cập nhật n y i ← n y i +1 . 7: H ( D 1 ) ← Entropy ( n y , i = 1 . . . C ) 8: H ( D 2 ) ← Entropy ( c y -n y , i = 1 . . . C ) 9: H ( D | A k ) ← min( H ( D | A k ) , i n H ( D 1 ) + n -i n H ( D 2 )) 10: end for 11: return ngưỡng θ = x i có giá trị H ( D | A k ) nhỏ nhất 12: end function `

Thuật toán dò ngưỡng trên có độ phức tạp O ( n log n + nC ) .

<!-- Page 76 -->

<!-- Page 77 -->
## 2.9 TÌNH HUỐNG ÁP DỤNG:

PHÂN LỚP HOA IRIS 51 • pandas: Thư viện xử lý dữ liệu, giúp dễ dàng thao tác với dữ liệu dạng bảng. • seaborn: Thư viện trực quan hóa dữ liệu. 2.9.3 Các bước triển khai chính Dựa trên các thư viện đã giới thiệu ở trên, chúng ta sẽ thực hiện các bước sau để xây dựng mô hình phân lớp với bộ dữ liệu IRIS: • Phân tích đặc trưng dữ liệu: ở bước này, chúng ta sẽ sử dụng các hàm trong thư viện pandas và seaborn để phân tích dữ liệu. Trong đó, chúng ta sẽ vẽ đồ thị để trực quan hóa dữ liệu và tìm hiểu mối quan hệ giữa các đặc trưng, và giữa đặc trưng với nhãn. • Tiền xử lý dữ liệu: Dữ liệu sẽ được chuẩn hoá và phân chia thành 2 tập dữ liệu huấn luyện và kiểm tra. • Xây dựng mô hình hồi quy Logistic: Chúng ta có thể khai báo mô hình hồi quy Logistic, sử dụng thư viện scikit-learn với các tham số được lựa chọn. Và tiến hành huấn luyện mô hình với tập dữ liệu huấn luyện. • Đánh giá mô hình: Sử dụng tập dữ liệu kiểm tra, chúng ta sẽ đánh giá độ chính xác của mô hình hồi quy vừa được huấn luyện. Đối với dữ liệu hoa IRIS, chúng ta có thể dựa trên ma trận nhầm lẫn để đánh giá độ chính xác của mô hình. Người học có thể xem ví dụ về việc sử dụng mô hình hồi quy Logistic để phân lớp trên dữ liệu IRIS tại https://gist.github. com/cuongtv312/36f280a51c2e15d87a5ea7a5828a177a

<!-- Page 78 -->

<!-- Page 79 (Heavy) -->
Bảng 2.2: Dữ luyện phân lớp cho cây quyết định

|   N |   x 1 |   x 2 |   y | |-----|-------|-------|-----| |   1 |     1 |     1 |   0 | |   2 |     1 |     2 |   0 | |   3 |     2 |     1 |   0 | |   4 |     2 |     2 |   0 | |   5 |     3 |     1 |   0 | |   6 |     3 |     4 |   1 | |   7 |     4 |     4 |   1 | |   8 |     4 |     5 |   1 | |   9 |     5 |     4 |   1 | |  10 |     5 |     5 |   1 |

3. [Lập trình] Cài đặt thuật toán hồi quy Logistic cho bài toán hồi quy Logistic với hàm lỗi là hàm cross-entropy sử dụng dữ liệu D 1 ở câu trên:
- a) Giả sử số vòng lặp huấn luyện là N = 10 , tốc độ học α = 0 . 1 , in ra các giá trị tìm được của θ = [ w, b ] và giá trị hàm lỗi sau mỗi vòng lặp, biết rằng trọng số khởi tạo là w = [1 . 0 , -1 . 0] và hệ số tự do b = 1 . 0 .
- b) Giả sử các tham số khởi tạo θ = [ w, b ] được sinh ngẫu nhiên trong khoảng [0 , 1] , sử dụng thiết lập tốc độ học α = 0 . 1 . Số lần lặp được tăng lên để đảm bảo tính hội tụ của thuật toán. Đánh giá vị trí của điểm hội tụ tìm được khi chạy thuật toán với các tham số khởi tạo khác nhau.
4. Biên quyết định của cây quyết định có hình dạng thế nào? Minh hoạ câu trả lời bằng cho một ví dụ cụ thể trên tập dữ liệu D 2 có 10 mẫu và 2 đặc trưng, như sau
5. [Lập trình] Cài đặt thuật toán 2.5 cho tập dữ liệu D 2 ở câu trên.
- a) In ra cấu trúc cây quyết định tìm được

<!-- Page 80 -->

<!-- Page 81 -->
Tài liệu tham khảo [1] Vapnik, V. N., Principles of risk minimization for learning theory, Advances in Neural Information Processing Systems, 1992. [2] Cox, D. R., The regression analysis of binary sequences, Jour- nal of the Royal Statistical Society: Series B, 1958. [3] Quinlan, J. R., Induction of decision trees, Machine Learning, vol. 1, no. 1, pp. 81–106, 1986. [4] Cover, T. and Hart, P., Nearest neighbor pattern classification, IEEE Transactions on Information Theory, vol. 13, no. 1, pp. 21–27, 1967. [5] Hastie, T., Tibshirani, R., and Friedman, J., The elements of statistical learning, Springer, 2001. [6] Bishop, C. M., Pattern recognition and machine learning, Springer, 2006. [7] Wolpert, D. H., and Macready, W. G. (1997). No free lunch theorems for optimization. IEEE transactions on evolutionary computation, 1(1), 67-82.

<!-- Page 82 -->
56 TÀI LIỆU THAM KHẢO [8] Shalev-Shwartz, S., and Ben-David, S., Understanding ma- chine learning: From theory to algorithms, Cambridge Univer- sity Press, 2014.

<!-- Page 83 -->
# Chương 3 Mạng nơ-ron nhiều lớp Từ sau năm 2010, các mô hình học máy “nông” như hồi quy tuyến tính, hồi quy Logistic hay SVM dần trở nên không còn phù hợp để xử lý dữ liệu ngày càng phức tạp và đa dạng.

Trong khi đó, mô hình đồ thị xác suất có khả năng biểu diễn tốt nhưng bị giới hạn về hiệu suất do thiếu thuật toán hiệu quả trên nhiều loại đồ thị. Do đó, nhu cầu cấp thiết là tìm kiếm mô hình vừa có khả năng biểu diễn mạnh, vừa đảm bảo hiệu năng tính toán. Mạng nơ-ron nhân tạo là một cấu trúc tính toán phù hợp, đặc biệt với sự phát triển của Học sâu (Deep Learning) trong thập kỷ qua. Các kiến trúc học sâu hiện đạt độ chính xác cao nhất trong nhiều bài toán, thậm chí vượt cả con người. Chương này giới thiệu mạng nơ-ron từ cơ bản đến nâng cao, bao gồm cơ chế lan truyền tới, lan truyền ngược và các thuật toán tối ưu như Xuống đồi bằng đạo hàm, đạo hàm ngẫu nhiên và Adam. Những nội dung này là nền tảng cho việc học các kiến trúc mạng sâu hơn trong các chương tiếp theo như mạng tích chập (CNN) (Chương 5) và mạng hồi quy (RNN) (Chương 7).

<!-- Page 84 (Heavy) -->
## 3.1 Mô hình

Đầu tiên chúng ta sẽ tìm hiểu mô hình của một nơ-ron, sau đó chúng ta sẽ ghép các nơ-ron lại thành một lớp rồi một mạng nơ-ron nhiều lớp.

## 3.1.1 Mô hình nơ-ron đơn vị

Một nơ-ron nhân tạo được tạo nên từ hai bộ phận: một bộ phận so sánh đầu vào với một véc-tơ trọng số thông qua tích vô hướng, một bộ phận phi tuyến hoá kết quả (Hình 3.1).

Định nghĩa 3.1 (Nơ-ron) . Mô hình nơ-ron là ánh xạ từ đầu vào x ∈ R m đến đầu ra o ∈ R

<!-- formula-not-decoded -->

Trong đó véc-tơ w ∈ R m và giá trị ngưỡng b ∈ R là các tham số của nơ-ron và hàm f : R → R gọi là hàm kích hoạt .

Hình 3.1: Mô hình nơ-ron.

<!-- image -->

Phép tính tích vô hướng đạt cực đại khi x có cùng hướng với w . Vì thế, nơ-ron đã dò biết được x có cùng cấu tạo như véc-tơ trọng số của nó hay không. Hàm kích hoạt f có mục đích phi tuyến hoá đầu ra, giúp cho mạng nơ-ron có thể tính toán phức tạp hơn. Bảng 3.1 đưa ra công thức một số hàm kích hoạt phổ biến và đạo hàm

<!-- Page 85 (Heavy) -->
Bảng 3.1: Bảng các hàm kích hoạt thông dụng

| Hàm số                               | Công thức                                                                                                      | Đạo hàm                                                                                          | |--------------------------------------|----------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------| | Tuyến tính Relu Sigmoid Tan-hyperbol | f ( z ) = z f ( z ) = max(0 , z ) f ( z ) = σ ( z ) = 1 1+ e - z f ( z ) = tanh( z ) = e z - e - z e z + e - z | f ′ ( z ) = 1 f ′ ( z ) = I ( z ≥ 0) f ′ ( z ) = σ ( z )(1 - σ ( z )) f ′ ( z ) = 1 tanh 2 ( z ) |

-

tương ứng của chúng. Theo định nghĩa này, với f là hàm sigmoid và bài toán phân lớp nhị phân, chúng ta sẽ thu được công thức cơ bản của mô hình hồi quy logistic ở Mục 2.6. Trong các chương tiếp theo, chúng ta sẽ gặp các dạng biểu diễn tương tự với mô hình Perceptron ở Chương 4 và mô hình hồi quy tuyến tính ở Chương 7.

Để tiện trình bày và biến đổi các công thức, ta thêm số 1 vào véc-tơ đầu vào x và đưa b vào trong véc-tơ w

<!-- formula-not-decoded -->

## 3.1.2 Lớp nơ-ron

Mỗi nơ-ron theo Định nghĩa 3.1 tính toán một kết quả đầu ra dựa trên tổ hợp các thông tin đặc trưng vào. Lớp nơ-ron tiếp tục mở rộng định nghĩa trên thành một tập hợp nơ-ron hoạt động trên cùng một đầu vào x . Mỗi nơ-ron có một đầu ra riêng biệt như thể hiện trong Hình 3.2.

Định nghĩa 3.2 (Lớp nơ-ron) . Lớp nơ-ron là ánh xạ từ đầu vào x ∈ R m đến đầu ra o ∈ R p với p nơ-ron

<!-- formula-not-decoded -->

Trong đó ma trận trọng số W có các hàng là các véc-tơ trọng số của các nơ-ron

<!-- formula-not-decoded -->

và hàm kích hoạt f tác động lên từng phần tử của véc-tơ W x .

<!-- Page 86 (Heavy) -->
Hình 3.2: Một lớp nơ-ron có p đầu ra.

<!-- image -->

Phân lớp nhiều lớp bằng lớp nơ-ron . Sử dụng công thức (3.2), chúng ta có thể mở rộng bài toán phân lớp từ hai lớp thành nhiều lớp hơn. Trước tiên, ta mô tả xác suất p ( y | x ) với giá trị y ∈ { 1 , 2 , . . . , p } bằng hàm softmax

<!-- formula-not-decoded -->

Đây là hàm tổng quát hoá hàm sigmoid để dành cho phân lớp đa lớp. Sử dụng nguyên lý Ước lượng hợp lý cực đại, ta cần cực tiểu hóa hàm lỗi sau

<!-- formula-not-decoded -->

Trong đó ℓ ( o, y ) = -∑ p c =1 I [ y = c ] ln p ( y = c | o ) là hàm lỗi trên một mẫu dữ liệu ( x, y ) . Hàm lỗi này được gọi là hàm lỗi entropy chéo (cross-entropy).

Chúng ta tiếp tục tính đạo hàm của hàm lỗi entropy chéo . Đặt MS = ∑ p c =1 exp { o c } và dùng đẳng thức p ( y = c | o ) = exp { o c } / MS ,

<!-- Page 87 (Heavy) -->
ta có khai triển sau:

<!-- formula-not-decoded -->

Sử dụng công thức đạo hàm hàm hợp để tính đạo hàm của hàm lỗi ℓ ( o, y ) với trọng số w c , ta có:

<!-- formula-not-decoded -->

Và công thức tổng quát đạo hàm của hàm lỗi trên tập dữ liệu D là

<!-- formula-not-decoded -->

Đây là các đạo hàm có thể dùng để điều chỉnh bộ trọng số W bằng phương pháp xuống đồi bằng đạo hàm, tương tự như phương pháp huấn luyện hàm hồi quy Logistic như trình bày trong phần 2.6.

## 3.1.3 Mạng nơ-ron nhiều lớp lan truyền tới

Trong phần trình bày ở mục 3.2, chúng ta thấy với một lớp nơ-ron nhất định, đặc trưng bởi ma trận trọng số W ∈ R p × m có thể ánh xạ dữ liệu từ không gian đầu vào R m sang một không gian mới R p . Thay vì ngay lập tức mô hình xác suất đầu ra qua hàm softmax,

<!-- Page 88 (Heavy) -->
chúng ta có thể tiếp tục xây các ánh xạ này cho đến một độ sâu tuỳ ý bằng cách coi không gian R p là không gian đầu vào mới. Đây là cấu trúc xếp lớp cơ bản của mạng học sâu dựa trên nơ-ron. Cụ thể hơn, đầu ra của lớp nơ-ron phía trước là đầu vào của lớp nơ-ron kế tiếp. Như vậy, đầu vào của lớp nơ-ron đầu tiên chính là x , còn đầu ra của lớp nơ-ron cuối cùng là đầu ra của toàn bộ mô hình (Hình 3.3). Cấu trúc này gọi là mạng nơ-ron nhiều lớp lan truyền tới , viết tắt là MLP (Multi Layer Perceptron).

Hình 3.3: Mạng nơ-ron nhiều lớp lan truyền tới.

<!-- image -->

Cụ thể, giả sử ta có L lớp nơ-ron nối tiếp nhau. Lớp thứ i có p i đầu ra sử dụng bộ trọng số được cho bởi:

<!-- formula-not-decoded -->

Ta có công thức tổng quát để tính toán trên đầu ra của lớp i -1 là

<!-- formula-not-decoded -->

với f i là hàm kích hoạt ở lớp thứ i và đầu vào của lớp đầu tiên chính là dữ liệu đầu vào x

<!-- formula-not-decoded -->

và đầu ra của lớp thứ L cuối cùng là đầu ra của toàn bộ mô hình:

<!-- formula-not-decoded -->

<!-- Page 89 -->
## 3.1 MÔ HÌNH 63 Một cách tổng quát chúng ta có định nghĩa về mạng nơ-ron nhiều lớp như sau:

Định nghĩa 3.3 (Mạng nơ-ron nhiều lớp). Một mạng nơ-ron L lớp là ánh xạ từ véc-tơ đầu vào x đến véc-tơ kết quả o theo công thức o = f (x) = f (W f (W f (...f (W x)))). (3.7) θ L L L−1 L−1 L−2 1 1 trong đó, θ = (W ,...,W ) là bộ tham số và các hàm f ,...,f là 1 L 1 L các hàm kích hoạt tại các lớp nơ-ron. Trong công thức (3.7), chúng ta tạm thời coi các ma trận tham số có số chiều tương thích. Ngoài không gian đầu vào của x và không gian đầu ra của o, các kết quả trung gian o ở các lớp 1 < i < L i trong công thức (3.2) được gọi là các miền biểu diễn đặc trưng ẩn (latent feature) hoặc gọi tắt là miền ẩn (latent space). Điểm mạnh của mạng nơ-ron đến từ việc các lớp đơn lẻ khi kết nối với nhau có thể biểu diễn một hàm phi tuyến hết sức phức tạp, có thể xấp xỉ hầu hết các hàm số với độ chính xác cao. Kết quả này được trình bày trong Định lý Xấp xỉ toàn cục của mạng nơ-ron hai lớp do Cybenko [5] đề xuất như sau: Định lý 3.4 (Định lý xấp xỉ toàn cục). Với số lượng nơ-ron hữu hạn và hàm kích hoạt phi tuyến thích hợp, mạng nơ-ron hai lớp có thể xấp xỉ một hàm liên tục bất kì trên không gian con trù mật của Rm với độ chính xác ϵ > 0 bất kì. Việc chứng minh Định lý Xấp xỉ toàn cục cần kiến thức cơ sở về giải tích hàm vượt qua ngoài phạm vi của giáo trình. Kết quả định lý chỉ ra rằng mạng nơ-ron hai lớp đủ linh hoạt để thể hiện một hàm số liên tục thoã mãn một số điều kiện cho trước. Vì thế, nếu hàm số cần phải học được biết trước, thì chỉ cần tìm kiếm hàm số đó trong không gian tham số của mạng nơ-ron hai lớp với số

<!-- Page 90 (Heavy) -->
lượng nơ-ron đủ lớn. Trong thực tế của bài toán học máy thông kê, hàm số cần học không được biết trước, mà chỉ được ước lượng từ dữ liệu. Vì thế, việc xây dựng một mạng nơ-ron nhiều lớp với số lượng nơ-ron và số lớp lớn hơn được kì vọng là sẽ có kết quả xấp xỉ tốt hơn.

## 3.2 Huấn luyện mô hình mạng nơ-ron nhiều lớp

Pha huấn luyện của mạng nơ-ron MLP sử dụng một thuật toán nổi tiếng có tên thuật toán lan truyền ngược (back propagation). Thuật toán có mục tiêu tính đạo hàm của lỗi ℓ ( o, y ) đối với tất cả các trọng số W i tại các lớp nơ-ron. Ý tưởng chính của thuật toán này là sử dụng công thức đạo hàm hàm hợp để lan truyền ngược đạo hàm từ lớp cuối về lớp đầu tiên (ngược hướng tính toán đầu ra của mạng). Đầu tiên, ta khai triển từ dạng tổng quát của hàm lỗi theo công thức là:

<!-- formula-not-decoded -->

Trong đó, ma trận Jacobian J i +1 = [ ∂o i +1 ∂o i ] ∈ R p i +1 × p i là ma trận đạo hàm của o i +1 đối với o i . Vì o i +1 = f i +1 ( W t +1 o i ) nên xét phần tử dòng j , cột k của ma trận J i +1 , ta có công thức đạo hàm của o j i +1 đối với o k i như sau:

<!-- formula-not-decoded -->

<!-- Page 91 (Heavy) -->
Tiếp tục quá trình biển đổi tương tự và nhóm lại các đạo hàm theo công thức sau:

<!-- formula-not-decoded -->

trong đó, ∇ f i là ma trận đường chéo đạo hàm của hàm kích hoạt tại lớp nơ-ron thứ i thì ta có công thức tổng quát cho ma trận Jacobian J i +1 được rút gọn lại như sau:

<!-- formula-not-decoded -->

## Thuật toán 3.1 Thuật toán lan truyền ngược

1: procedure BackPropagation ( ∂ℓ ( o L ,y ) ∂o L , ∇ f i , i = 1 , . . . , L )

2: Khởi tạo δ L = ∂ℓ ∂o L

, L

, . . . ,

do

5: Lan truyền ngược δ i = J T i +1 δ i +1

3: for i = L --4: Tính J i +1 = W i +1 ∇ f i +1

6: end for

7:

return

δ

i

, i

= 1

8: end procedure

Sau khi có giá trị δ i = ∂ℓ ( o,y ) ∂o i cho tất cả các lớp nơ-ron, ta có thể khai triển và sau đó tính đạo hàm của lỗi theo biến đổi sau

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Một nhận xét thú vị của thuật toán lan truyền ngược là thuật toán này có thể dùng để tính δ 0 = ∂ℓ ( o,y ) ∂x . Đây là đạo hàm của hàm

,

, . . . , L

<!-- Page 92 (Heavy) -->
lỗi đối với đầu vào x của mạng. Nhiều thuật toán học máy đã dùng đạo hàm này để tìm các mẫu dữ liệu đầu vào thoả mãn những tính chất nhất định. Ví dụ như tìm ảnh có phong cách giống với phong cách của một hoạ sĩ, tìm dữ liệu có khả năng phá hoại mô hình và nhiều ứng dụng khác.

Để thuật toán lan truyền ngược hoạt động, ta cần cung cấp đầu vào ∂ℓ ∂o là đạo hàm của hàm lỗi đối với đầu ra của lớp cuối cùng. Trong trường hợp tổng quát của bài toán phân lớp, khi đó số đầu ra ở lớp cuối p L = C là số lớp cần phân loại, ta sử dụng hàm lỗi entropy chéo ℓ ( o, y ) = -∑ C c =1 I [ y = c ] ln p ( c | o ) . Viết lại công thức tính đạo hàm (3.5) ở dạng véc-tơ, ta thu được công thức sau:

<!-- formula-not-decoded -->

trong đó, e y là véc-tơ cơ sở chuẩn, gồm toàn giá trị 0 ở những vị trí khác giá trị nhãn mục tiêu y và giá trị 1 ở vị trí nhãn mục tiêu y . Điều này giống với việc chúng ta chỉ cần tính đạo hàm của hàm lỗi đối với nhãn mục tiêu y . Ở pha suy luận, ta chỉ cần chọn c ⋆ = arg max c o c là nhãn có xác suất p ( y = c | o ) lớn nhất.

Đạo hàm ∂ℓ ( o,y ) ∂W ở trên mới chỉ tính trên một mẫu dữ liệu, còn đối với một tập dữ liệu D = { ( x i , y i ) } , i = 1 , 2 , . . . , n , ta tính đạo hàm của hàm tổng các lỗi trên từng dữ liệu bằng cách cộng từng đạo hàm của từng mẫu dữ liệu lại với nhau. Kết quả ta có thuật toán huấn luyện mạng nơ-ron MLP (Thuật toán 3.2).

Thuật toán 3.2 duyệt qua bộ dữ liệu theo từng epoch. Với mỗi epoch, đầu tiên ta khởi tạo đạo hàm bằng 0. Sau đó, với từng dữ liệu, thực hiện lan truyền tới, lan truyền ngược để tính đạo hàm rồi tích luỹ đạo hàm bằng cách cộng dồn. Kết thúc mỗi epoch, ta cập nhật lại trọng số ở các lớp theo phương pháp xuống đồi bằng

<!-- Page 93 (Heavy) -->
` 1: procedure TrainMLP ( D,λ ) 2: Khởi tạo W 1 , W 2 , . . . , W L ngẫu nhiên 3: for epoch = 1 , 2 , . . . do 4: for k = 1 to L do 5: ∂ℓ ∂W k ← 0 6: end for 7: for all dữ liệu ( x i , y i ) trong D do 8: Lan truyền tới, tính o 1 , o 2 , . . . , o L , ∇ f 1 , ∇ f 2 , . . . , ∇ f L 9: Tính đạo hàm hàm lỗi: ∂ℓ ( o L ,y i ) ∂o L 10: δ L , δ L -1 , . . . , δ 0 = BACKPROPAGATION ( ∂ℓ ( o L , y i ) ∂o L , ∇ f 1 ...L ) 11: for k = 1 to L do 12: ∂ℓ ∂W k ← ∂ℓ ∂W k + ∇ f k δ k o T k -1 13: end for 14: end for 15: for k = 1 to L do 16: W k ← W k -λ · ∂ℓ ∂W k 17: end for 18: end for 19: return W 1 , W 2 , . . . , W L 20: end procedure `

Thuật toán 3.2 Thuật toán huấn luyện mạng nơ-ron MLP

đạo hàm. Tất nhiên, còn có nhiều phương pháp tối ưu khác, chúng ta sẽ tìm hiểu ở một phần riêng của giáo trình.

## 3.3 Các thuật toán tối ưu

Thuật toán tối ưu được trình bày trong Thuật toán 3.2 yêu cầu đạo hàm được tính toàn bộ tập dữ liệu, sau đó lỗi này sẽ được lan truyền ngược lại và cập nhật đối với từng trọng số. Trước khi đi vào các thuật toán tối ưu, chúng ta sẽ xem xét đến tính hội tụ của các tham số trong mô hình mạng lan truyền tới với thiết lập cơ bản.

<!-- Page 94 (Heavy) -->
## 3.3.1 Tính hội tụ của phương pháp xuống đồi bằng đạo hàm

Xét trường hợp mạng nơ-ron một lớp trong định nghĩa 3.1 và được huấn luyện thông qua hàm lỗi entropy chéo (công thức (3.3)) trên tập dữ liệu D cho trước.

Theo Thuật toán huấn luyện mạng nơ-ron MLP, ta có thể thấy rằng, ở bước thứ t ứng với tham số θ t (gồm tất cả các ma trận trọng số W k , k = 1 , . . . , L ), ta có thể viết lại công thức cập nhật θ t +1 như sau:

<!-- formula-not-decoded -->

Sử dụng công thức cập nhật trên, xuất phát từ tham số khởi tạo θ 0 ta có các giá trị hàm lỗi ℓ ( θ t ) ứng với giá trị θ t được cập nhật tại bước thứ t . Chúng ta quan tâm đến có tồn tại giá trị θ ∗ nào đó sao cho dãy giá trị

<!-- formula-not-decoded -->

có hội tụ về giá trị cố định ℓ ( θ ∗ ) hay không. Nếu tồn tại giá trị θ ∗ sao cho dãy giá trị hàm lỗi hội tụ về ℓ ( θ ∗ ) , thì ta có thể nói rằng thuật toán tối ưu hội tụ về giá trị ℓ ( θ ∗ ) .

Để trả lời câu hỏi này, chúng ta cần xét đến một trong những đặc điểm quan trọng của hàm lỗi đó là tính trơn của hàm lỗi.

Định nghĩa 3.5 (Tính trơn của hàm lỗi) . Một hàm F : R m → R được gọi là có hàm trơn theo L nếu F liên tục, khả vi và tồn tại một hằng số L &gt; 0 sao cho với mọi x, y ∈ R m ta có:

<!-- formula-not-decoded -->

Với định nghĩa hàm lỗi ℓ ( θ ) theo công thức (3.3) và giá trị đạo hàm ∇ ℓ ( θ ) = ∂ℓ ∂θ tương ứng, ta có thể thấy rằng hàm lỗi ℓ ( θ ) thoả mãn định nghĩa về tính trơn của hàm lỗi. Bên cạnh đó hàm lỗi ℓ ( θ ) cũng có thể được xem như là một hàm lồi dựa theo tính chất của

<!-- Page 95 (Heavy) -->
hàm softmax và hàm entropy chéo. Từ dữ kiện này, chúng ta có thể lựa chọn tốc độ học η để đảm bảo tính hội tụ của dãy ℓ ( θ t ) ∞ t =0 theo định lý sau:

Định lý 3.6 (Tính hội tụ của hàm lỗi) . Giả sử hàm lỗi ℓ ( θ ) có đạo hàm trơn theo L và tồn tại một giá trị θ ∗ sao cho ℓ ( θ ∗ ) = min θ ℓ ( θ ) . Nếu tốc độ học η được chọn sao cho 0 &lt; η &lt; 1 L , thì

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Chứng minh: Để chứng minh định lý này, ta sẽ sử dụng một số tính chất của hàm lồi và hàm trơn. Dựa theo khai triển Taylor bậc nhất của hàm lồi f tại điểm x và với điểm y bất kì ta có:

<!-- formula-not-decoded -->

Thay x = θ t và y = θ t +1 , sử dụng khai triển trên ta có:

<!-- formula-not-decoded -->

Trong đó, bất đẳng thức cuối cùng do η ≤ 1 L , nên 1 -Lη 2 ≥ 1 2 .

Sử dụng tính chất hàm lồi, với θ bất kì

<!-- formula-not-decoded -->

và

<!-- Page 96 (Heavy) -->
ta có

<!-- formula-not-decoded -->

Cộng các bất đẳng thức trên với t = 0 , 1 , . . . , T -1 ta có:

<!-- formula-not-decoded -->

Từ bất đẳng thức trên, suy ra:

<!-- formula-not-decoded -->

Do giá trị nhỏ nhất luôn bé hơn trung bình cộng nên

<!-- formula-not-decoded -->

và, do tính chất của hàm lồi

<!-- formula-not-decoded -->

ta có điều phải chứng minh.

□

Như vậy hoặc ta lấy trung bình cộng của giá trị tham số trong quá trình huấn luyện hoặc ta lấy tham số tương ứng với giá trị hàm lỗi nhỏ nhất trong quá trình huấn luyện. Trong thực hành, người

<!-- Page 97 (Heavy) -->
ta thường sử dụng phép lấy tổng có trọng số mũ của các giá trị tham số trong khi huấn luyện. Cụ thể như sau

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

với 0 &lt; α &lt; 1 là một hằng số nhỏ (ví dụ, 10 -2 , 10 -3 ).

Để đảm bảo tính hội tụ của thuật toán tối ưu theo công thức (3.10) chúng ta cần đảm bảo tính trơn và lồi của hàm lỗi. Trong trường hợp của mạng nơ-ron với một lớp nơ-ron duy nhất, hàm lỗi được định nghĩa theo công thức (3.3) thoả mãn điều kiện này. Khi số lớp nơ-ron trong mạng lan truyền tới tăng lên hai hoặc ba lớp, hàm lỗi không còn là hàm lồi nữa. Điều này dẫn đến việc không thể đảm bảo tính hội tụ của thuật toán tối ưu theo công thức (3.10). Chúng ta không đi sâu vào vấn đề hội tụ của thuật toán tối ưu xuống đồi bằng đạo hàm với trường hợp mạng nơ-ron có cấu trúc phức tạp hơn.

Về mặt thực nghiệm, có hai vấn đề xảy ra với thuật toán xuống đồi bằng đạo hàm thông thường:

- Lấy trung bình giá trị cập nhật theo hướng đạo hàm giảm trên toàn tập dữ liệu làm cho các sai số cộng trừ lẫn nhau dẫn đến bước tiến của thuật toán tối ưu sẽ nhỏ, khó tìm được điểm hội tụ thích hợp.
- Mỗi lần lặp cần phải duyệt cả tập dữ liệu, độ phức tạp là O ( K | D | ) trong đó K là độ phức tạp đối với thuật toán lan truyền ngược trên một điểm dữ liệu. Có thể tính gần đúng là tuyến tính với số tham số trong mô hình mạng lan truyền tới.

Điều này dẫn đến thuật toán không khả thi nếu số lượng mẫu dữ liệu rất lớn. Trên thực tế, chúng ta sẽ tìm một hướng đi dẫn đến cập nhật tham số cho mô hình nơ-ron đủ tốt trong thời gian cho

<!-- Page 98 -->

<!-- Page 99 (Heavy) -->
` 1: procedure TrainMLP ( D,λ,b ) 2: Khởi tạo W 1 , W 2 , . . . , W L ngẫu nhiên 3: for e = 1 , 2 , . . . do 4: for k = 1 to L do 5: ∂ℓ ∂W k ← 0 6: end for 7: Chọn ngẫu nhiên tập con D e ⊂ D gồm b phần tử 8: for all ( x i , y i ) ∈ D e do 9: Lan truyền tới, tính o 1 , . . . , o L và ∇ f 1 , . . . , ∇ f L 10: Tính đạo hàm lỗi: ∂ℓ ( o L ,y i ) ∂o L 11: Lan truyền ngược, tính δ L , . . . , δ 0 12: for k = 1 to L do 13: ∂ℓ ∂W k ← ∂ℓ ∂W k + ∇ f k δ k o T k -1 14: end for 15: end for 16: for k = 1 to L do 17: W k ← W k -λ · ∂ℓ ∂W k 18: end for 19: end for 20: return W 1 , W 2 , . . . , W L 21: end procedure `

Thuật toán 3.3 Thuật toán SGD huấn luyện mạng nơ-ron MLP

tối ưu là các miền nhấp nhô không đồng đều, thuật toán SGD có thể mất rất nhiều thời gian để đi thoát được khỏi miền tối ưu đấy.

Trong trường hợp này, SGD được thêm vào thành phần quán tính. Sử dụng quán tính giúp cho thuật toán SGD có thể được tăng tốc theo chiều đúng hướng đồng thời giảm độ dao động đối với các tín hiệu đạo hàm bị nhiễu. Chúng ta có thể hiểu quán tính là một đại lượng đặc trưng cho tốc độ của quá trình hội tụ và được cập nhật theo phương trình sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 100 (Heavy) -->
Trong công thức trên, đại lượng λ là tốc độ học. Đại lượng ∇ θ J ( θ ) đặc trưng cho đạo hàm được tính qua tốc độ học thành đại lượng vận tốc v t được cập nhật vào tham số θ ở phương trình dưới. Đại lượng quán tính γ đặc trưng cho tốc độ đang có, thường được chọn là 0.9 trong thực nghiệm.

Một cách dễ hình dung, việc sử dụng quán tính trong cập nhật trọng số ở công thức (3.13) giống như việc thả một trái bóng lăn xuống dốc. Khi ở đỉnh dốc tốc độ chậm nhưng càng di chuyển tốc độ sẽ càng nhanh và giảm dần khi gần đến vị trí hội tụ tại cục bộ địa phương. Song song với việc tốc độ tăng theo hướng hội tụ, các nhiễu của đạo hàm cũng được loại bỏ. Kết quả là chúng ta sẽ có được một thuật toán cho phép tốc độ hội tụ cao và giảm tính giao động ảnh hưởng bởi nhiễu.

Về mặt tính toán, so với thuật toán SGD, thuật toán SGD với quán tính phải thêm vào một biến phụ để lưu lại vận tốc tại thời điểm t ứng với mỗi tham số trong mô hình θ . Về mặt độ phức tạp tính toán thì cả hai tương đương nhau.

## 3.3.4 Thuật toán ước lượng quán tính thay đổi - Adam

Thuật toán ước lượng quán tính thay đổi hay viết ngắn gọn là Adam là một phương pháp tối ưu dựa trên thuật toán SGD. Về mặt ý tưởng, thuật toán Adam đưa vào khái niệm ma sát cản trở chuyển động khi quả bóng lăn xuống dốc. Thay vì sử dụng một giá trị quán tính duy nhất γ như trong thuật toán SGD quán tính, Adam sử dụng một ước lượng dựa trên giá trị giảm trung bình theo hàm mũ với gia tốc của v t . Bên cạnh đó Adam vẫn sử dụng giá trị trung bình theo thời gian của v t làm đại lượng quán tính tương tự với thuật toán SGD quán tính.

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 101 (Heavy) -->
Trong công thức trên, g t là đại lượng ứng với gia tốc của vận tốc v t , nói một cách khác là đạo hàm sự thay đổi của đạo hàm theo thời gian ứng với một tham số cần tối ưu. Giá trị m t và v t là ước lượng tương của mô-men thứ nhất và mô-men thứ hai của đạo hàm. Hai giá trị này sẽ được sử dụng để cập nhật tham số θ của mô hình

<!-- formula-not-decoded -->

Trong thực nghiệm, β 1 thường được chọn là 0 . 9 và β 2 thường được chọn à 0 . 999 . Ở những bước khởi tạo, với v 0 = 0 và g 0 = 0 , giá trị thường bị nhiễu và tiến dần đến 0. Tham số ϵ thường chọn khá bé, khoảng 10 -8 . Để hạn chế điều này, hàm ước lượng mô-men m t và v t có thể được nhân với một hàm chuẩn hóa theo thời gian So với thuật toán SGD quán tính thì thuật toán Adam phải lưu thêm biến phụ m t , g t đối với mỗi trọng số cần tối ưu.

Thuật toán Adam thường được sử dụng rộng rãi trong thực nghiệm vì khả năng tìm được các điểm cục bộ địa phương hiệu quả. Việc lựa chọn tốc độ học cho thuật toán Adam cũng dễ hơn các thuật toán khác ví dụ như SGD.

## 3.4 Các vấn đề liên quan đến tính hội tụ

Các phương pháp tối ưu ở trên có những cách cập nhật trong số trực tiếp khác nhau theo giá trị đạo hàm ở thời điểm t . Tuy nhiên tất cả đều dựa trên thuật toán gốc là GD ngẫu nhiên.

Hướng nghiên cứu lý thuyết trong bài toán học sâu thường quan tâm đến tính hội tụ của thuật toán GD. Các mạng học sâu có thể bao gồm vài chục đến vài trăm lớp với hàng triệu tham số cần tối ưu. Các hàm lỗi cần tối ưu thường là các hàm phức tạp, không có tính tuyến tính. Một số hướng nghiên cứu chính về tính hội tụ của thuật toán GD trong mạng học sâu bao gồm:

<!-- Page 102 -->

<!-- Page 103 -->
## 3.5 TÌNH HUỐNG ÁP DỤNG:

NHẬN DẠNG CHỮ SỐ MNIST 77 theo khoảng cách đến không gian đầu ra. Kỹ thuật này thường được áp dụng trong các bài toán liên quan đến việc tinh chỉnh tham số của một mạng xương sống cho trước. 3.5 Tình huống áp dụng: Nhận dạng chữ số MNIST Bộ dữ liệu MNIST là tập dữ liệu phổ biến dùng để nhận diện chữ số viết tay (0-9), bao gồm 60.000 hình ảnh cho tập huấn luyện và 10.000 hình ảnh cho tập kiểm tra. Trong phần áp dụng này, thư viện PyTorch sẽ được dùng để xây dựng và huấn luyện mạng học sâu với bộ dữ liệu MNIST. 3.5.1 Giới thiệu thư viện Pytorch PyTorch1 là một thư viện linh hoạt để xây dựng các mô hình học sâu. Hai chức năng chính của PyTorchlà hỗ trợ tính toán Xuống đồi bằng đạo hàm và tính toán song song trên các đơn vị tính toán đồ hoạ (GPU). Các mô hình học sâu trong PyTorch được xây dựng dựa trên các lớp trừu tượng torch.nn.Module. Người sử dụng có thể dùng các lớp có sẵn trong thư viện hoặc tự định nghĩa các lớp mới bằng cách kế thừa lớp nn.Module. Các lớp được định nghĩa sẵn bao gồm các lớp mạng nơ-ron phổ biến, các lớp kích hoạt. PyTorch cũng cung cấp các lớp tối ưu hoá như Adam, SGD, Adagrad, RMSprop. 3.5.2 Xây dựng mô hình mạng nơ-ron nhiều lớp Khi sử dụng mạng nơ-ron nhiều lớp, chúng ta cần thực hiện định nghĩa các lớp mô hình mạng nơ-ron và mô hình tính toán. Trong thư viện PyTorch, chúng ta có thể định nghĩa mô hình bằng cách kế thừa lớp nn.Module, và định nghĩa các lớp con cho các lớp mạng nơ-ron. Cùng với đó, chúng ta cũng định nghĩa mô hình tính toán, được thể hiện ở phần hàm forward. Hàm này sẽ xác định cách mà 1https://pytorch.org/

<!-- Page 104 (Heavy) -->
dữ liệu đầu vào được truyền qua các lớp của mạng nơ-ron và trả về kết quả đầu ra cuối cùng, ứng với véc-tơ đầu ra của mạng nơ-ron theo Định nghĩa 3.3. Trừ lớp ẩn cuối cùng, các lớp ẩn đều sử dụng hàm kích hoạt ReLU. Chúng ta sử dụng hàm kích hoạt softmax cho lớp đầu ra vì chúng ta cần một phân phối xác suất cho các lớp đầu ra. Lớp đầu ra sẽ trả về một véc-tơ có kích thước bằng số lớp cần phân loại.

Bảng 3.2 mô tả cấu trúc của mạng nơ-ron nhiều lớp cho bài toán MNIST. Với khai báo này, mô hình sẽ gồm có 109386 tham số.

Bảng 3.2: Cấu trúc mạng nơ-ron nhiều lớp cho bài toán MNIST

| Lớp            |   Kích thước đầu vào |   Kích thước đầu ra | |----------------|----------------------|---------------------| | Lớp ẩn 1 - fc1 |                  784 |                 128 | | Lớp ẩn 2 - fc2 |                  128 |                  64 | | Đầu ra - fc3   |                   64 |                  10 |

## 3.5.3 Các bước triển khai chính

Trong phần này, chúng ta sẽ thực hiện các bước sau để xây dựng mô hình phân lớp với bộ dữ liệu MNIST. Các bước chính bao gồm:

- Chuẩn bị dữ liệu: Tải dữ liệu MNIST, chuẩn hóa và tạo bộ dữ liệu huấn luyện/kiểm tra.
- Xây dựng mô hình mạng nơ-ron nhiều lớp: Định nghĩa các lớp mạng nơ-ron và mô hình tính toán.
- Huấn luyện mô hình: Sử dụng hàm lỗi và bộ tối ưu hoá để huấn luyện mô hình.
- Đánh giá kết quả dự đoán trên tập dữ liệu kiểm thử: Sử dụng tập dữ liệu kiểm thử để đánh giá độ chính xác của mô hình.

<!-- Page 105 -->
## 3.6 TỔNG KẾT CHƯƠNG 79 • Lưu trữ và sử dụng lại mô hình đã huấn luyện:

Lưu trữ mô hình đã huấn luyện để sử dụng lại trong tương lai. Mô hình có thể đạt độ chính xác khoảng 97-98% trên tập kiểm thử. Người học có thể tham khảo mã nguồn tại https://gist.github. com/cuongtv312/9a69c1004619be658eca90b3ac8c6bd3 3.6 Tổng kết chương Chương 3 đã giới thiệu mạng nơ-ron nhiều lớp (MLP) – nền tảng cốt lõi của Học sâu. Người học được tiếp cận từ kiến trúc mạng, thuật toán huấn luyện, đến các vấn đề về tính hội tụ và hiệu quả mô hình. Ứng dụng phân loại ảnh viết tay MNIST minh họa rõ khả năng vượt trội của MLP so với các mô hình học máy truyền thống. Chương này cũng nhấn mạnh vai trò trung tâm của thuật toán lan truyền ngược và các kỹ thuật tối ưu như Xuống đồi bằng đạo hàm, đạo hàm ngẫu nhiên, kỹ thuật quán tính, thuật toán Adam. Kỹ năng xây dựng và huấn luyện MLP là nền tảng cần thiết để tiếp cận các mạng học sâu hơn trong các chương kế tiếp. Bài tập 1. Xét cấu trúc mạng nơ-ron được minh hoạ ở Hình 3.2 với p = 2. Chúng ta thấy rằng trong trường hợp này, có thể huấn luyện trực tiếp bằng cách sử dụng mô hình hồi quy Logistic. So sánh sự giống nhau và khác nhau giữa mô hình ở Hình 3.2 với mô hình hồi quy Logistic về số lượng tham số, cách tính toán đầu ra và cách huấn luyện. 2. Xây dựng một mạng nơ-ron nhiều lớp với 2 lớp ẩn, mỗi lớp có 10 nơ-ron. Dữ liệu đầu vào có 5 chiều và kết quả đầu ra dùng

<!-- Page 106 (Heavy) -->
Bảng 3.3: Dữ liệu phân lớp

|   N |    x |   y |   N |    x |   y | |-----|------|-----|-----|------|-----| |   1 |  0.3 |   1 |   6 |  0.9 |   1 | |   2 |  1.2 |   1 |   7 | -0.3 |   0 | |   3 |  0.6 |   0 |   8 |  2.4 |   1 | |   4 |  0.3 |   1 |   9 |  2.8 |   1 | |   5 | -0.5 |   0 |  10 | -0.7 |   1 |

để nhận dạng giá trị Có/Không. Trừ lớp đầu ra, các lớp ẩn đều sử dụng hàm ReLU là hàm kính hoạt.

- a) Vẽ hình minh hoạ cho mạng nơ-ron này
- b) Xác định các tham số huấn luyện và viết hàm tính toán đầu ra của mạng nơ-ron này.
3. [Tìm hiểu] Tìm một ví dụ mà SGD hội tụ nhưng GD luôn nhận được lượng cập nhật bằng 0.
4. Cho mô hình được cho bởi công thức dưới đây, biết rằng a làm hàm ReLU có công thức:

<!-- formula-not-decoded -->

với tham số ϕ = [ ϕ 0 , ϕ 1 , ϕ 2 ] và θ = [ θ 10 , θ 11 , θ 20 , θ 21 ] .

- a) Vẽ hình minh hoạ
- b) Viết hàm tính toán đạo hàm của hàm hồi quy logistic theo các tham số ϕ và θ .
5. [Lập trình] Cho tập dữ liệu phân lớp D = { ( x i , y i ) } 10 i =1 như Bảng 3.3. Trong đó x i là đầu vào của mạng nơ-ron, y i là đầu ra của mạng nơ-ron. Sử dụng mô hình được định nghĩa theo công thức (3.17) để học dữ liệu trên.

<!-- Page 107 -->
## 3.6 TỔNG KẾT CHƯƠNG 81 a) Cài đặt hàm f và tính toán đạo hàm b) Sử dụng phương pháp đạo hàm trên cả tập D để huấn luyện mạng nơ-ron. c) Sử dụng phương pháp đạo hàm ngẫu nhiên SGD để huấn luyện mạng nơ-ron.

So sánh với kết quả thu được ở câu trên. 6. Giải thích tại sao trong huấn luyện mạng học sâu cần phải chia ra tập huấn luyện và tập kiểm thử? 7. Nêu vai trò của quán tính trong việc huấn luyện mạng nơ-ron bằng phương pháp Xuống đồi bằng đạo hàm ngẫu nhiên SGD. Làm sao để ước lượng quán tính một cách chính xác dưới sự ảnh hưởng của nhiễu trong SGD? 8. [Lập trình]Trong phần tình huống áp dụng, thay đổi số lớp ẩn và số lượng nơ-ron mỗi lớp ẩn. Bạn có nhận xét gì về các kết quả thử nghiệm nhận được?

<!-- Page 108 -->

<!-- Page 109 -->
Tài liệu tham khảo [1] Rosenblatt, F., The perceptron: A probabilistic model for in- formation storage and organization in the brain, Psychological Review, vol. 65, no. 6, pp. 386–408, 1958. [2] Rumelhart, D. E., Hinton, G. E., and Williams, R. J., Learning representations by back-propagating errors, Nature, vol. 323, no. 6088, pp. 533–536, 1986. [3] Bishop, C. M., Neural networks for pattern recognition, Oxford University Press, 1995. [4] LeCun, Y., Bottou, L., Bengio, Y., and Haffner, P., Gradient- based learning applied to document recognition, Proceedings of the IEEE, vol. 86, no. 11, pp. 2278–2324, 1998. [5] Cybenko, G. (1989) Approximation by superpositions of a sigmoidal function, Mathematics of Control, Sig- nals, and Systems, 2(4), pp. 303-–314. Available at: https://doi.org/10.1007/BF02551274.

<!-- Page 110 -->

<!-- Page 111 -->
# Chương 4 Máy véc-tơ hỗ trợ Chương này giới thiệu Máy véc-tơ hỗ trợ SVM (Support Vector Machine), một thuật toán học máy cổ điển nhưng vẫn giữ vai trò quan trọng trong các bài toán phân lớp và hồi quy.

SVM phát triển từ mô hình Perceptron – một trong những kiến trúc phân lớp đầu tiên trong học máy – với nhiều cải tiến đáng kể về lý thuyết và hiệu quả thực nghiệm. Nguyên lý hoạt động cốt lõi của SVM là cực đại hoá lề giữa các lớp, nhằm tìm ra siêu phẳng phân tách với khoảng cách tối đa đến các điểm dữ liệu gần nhất thuộc mỗi lớp. Về mặt toán học, SVM là lời giải cho một bài toán tối ưu bậc hai với các ràng buộc tuyến tính, phản ánh sự kết hợp giữa học máy thống kê và tối ưu lồi. Chương 4 cũng đề cập đến các biến thể quan trọng của SVM như lề mềm và kỹ thuật nhân hoá, cho phép mở rộng mô hình sang các bài toán phân lớp phi tuyến.

<!-- Page 112 -->

<!-- Page 113 -->
## 4.1 MÔ HÌNH NƠ-RON NHÂN TẠO PERCEPTRON 87 Hình 4.1:

Tập dữ liệu khả tách tuyến tính. 4.1.1 Pha huấn luyện Định nghĩa 4.1 cho thấy phương hướng huấn luyện mô hình Percep- tron là tìm bộ trọng số (w1,...,wm,b) sao cho điểm số s của tất i cả các mẫu dữ liệu trong D đều không âm. Rõ ràng, việc này chỉ khả thi khi D khả tách tuyến tính. Bây giờ, xét một mẫu dữ liệu (x,y) mà Perceptron h đang phân lớp sai, tức là s = yf(x) < 0. Nếu ta cộng thêm vào s một đại lượng dương xTx + 1 > 0 thì có khả năng s sẽ đỡ “sai” hơn hoặc đỡ “âm” hơn. Ta có >0 (cid:122) (cid:125)(cid:124) (cid:123) s + xTx + 1 = y(wTx + b) + xTx + 1 = y(wTx + b) + y2xTx + y2 (do y2 = 1) = y((w + yx)Tx + (b + y)) Nghĩa là, nếu ta làm phép toán cập nhật tham số w w+yx,b ← ← b + y thì điểm số s sẽ được tăng thêm một đại lượng dương. Một cách diễn giải khác là nếu coi s là hàm của bộ trọng số w,b thì thay

<!-- Page 114 (Heavy) -->
đổi các trọng số theo hướng của đạo hàm ∂s ∂ w và ∂s ∂b làm hàm số s tăng lên. Viết lại theo công thức tính đạo hàm từng phần, ta có:

<!-- formula-not-decoded -->

Nhận xét này dẫn đến thuật toán huấn luyện Perceptron (Thuật toán 4.1).

## Thuật toán 4.1 Thuật toán huấn luyện Perceptron

` 1: procedure TrainPerceptron ( D 2: Khởi tạo w ← 0 , b ← 0 3: repeat 4: count ← 0 5: for all ( x i , y i ) ∈ D do 6: s i ← y i · f ( x i ) 7: if s i < 0 then 8: w ← w+ y i · x i 9: b ← b + y i 10: count ← mistake +1 11: end if 12: end for 13: until count = 0 14: return (w , b ) 15: end procedure `

` ) ▷ Phân lớp sai `

## 4.1.2 Tính dừng của thuật toán huấn luyện

Đảm bảo tính dừng của thuật toán huấn luyện Perceptron được trình bày trong Định lý 4.3.

Định lý 4.3 (Tính dừng của thuật toán huấn luyện Percerptron) . Nếu tồn tại bộ trọng số (w ⋆ , b ⋆ ) và δ &gt; 0 sao cho y i (w ⋆T x i + b ) ≥

<!-- Page 115 (Heavy) -->
δ, ∀ i thì số lỗi thuật toán 4.1 mắc phải không vượt quá

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

với R = max i ∥ x i ∥ 2 là chiều dài lớn nhất của các mẫu dữ liệu trong D .

Chứng minh: Gọi w ( t ) , b ( t ) là giá trị trọng số sau lần cập nhật thứ t (hoặc lần mắc lỗi thứ t đối với mẫu dữ liệu ( x , y ) nào đó trong D ). Ta có

<!-- formula-not-decoded -->

Mặt khác, ta lại có

<!-- formula-not-decoded -->

Ta có thể viết lại vế phải (VP) như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Ta thu được, bất đẳng thức cho một lần cập nhật trọng số

<!-- formula-not-decoded -->

Theo bất đẳng thức Bunhiacopxki, ta có

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 116 -->

<!-- Page 117 (Heavy) -->
Như vậy, nếu các điểm dữ liệu có y i = +1 và các điểm dữ liệu có y i = -1 ở hai phía của siêu phẳng phân lớp B thì khoảng cách giữa hai phân lớp trong D sẽ không nhỏ hơn 2 δ ∥ w ∥ . Khoảng cách này được gọi là lề của hàm phân lớp. So với mô hình Perceptron, mô hình SVM đưa thêm tiêu chí cực đại hóa lề khi tìm kiếm bộ trọng số Θ .

Không mất tính tổng quát, ta có thể chọn δ = 1 (nếu không ta có thể nhân w , b, δ với cùng một đại lượng để δ = 1 ). Bài toán huấn luyện SVM trở thành bài toán tối ưu một hàm mục tiêu với ràng buộc:

<!-- formula-not-decoded -->

Biến đổi hàm tối ưu ở công thức (4.2), ta thu được bài toán này tương đương, có dạng tìm giá trị tối ưu hàm mục tiêu bậc hai với ràng buộc tuyến tính.

Định nghĩa 4.4 (Máy véc-tơ hỗ trợ SVM lề cứng) . Cho tập dữ liệu D = { ( x i , y i ) } n i =1 với y i ∈ {-1 , +1 } . Bài toán tối ưu SVM lề cứng là bài toán tối ưu

<!-- formula-not-decoded -->

Bài toán tối ưu được cho bởi (4.3) gọi là bài toán tối ưu SVM với lề cứng do nó đòi hỏi tất cả các mẫu dữ liệu trong D phải được phân lớp đúng. Hiện có nhiều gói phần mềm tối ưu cho phép giải tổng quát dạng tối ưu bậc hai với điều kiện tuyến tính khá tốt. Tuy nhiên, nếu chúng ta chuyển dạng tối ưu bậc hai của SVM lề cứng sang dạng đối ngẫu Lagrange thì sẽ có những cách giải nhanh hơn rất nhiều. Để làm điều này, ta sử dụng hàm Lagrange của bài toán

<!-- Page 118 (Heavy) -->
Hình 4.2: Mô hình Máy véc-tơ hỗ trợ SVM.

<!-- image -->

gốc được định nghĩa ở công thức (4.3)

<!-- formula-not-decoded -->

với α i ≥ 0 , ∀ i là các hệ số Lagrange tương ứng với các ràng buộc. Điều kiện cần của w , b tối ưu bài toán gốc là đạo hàm của L với w và b bị triệt tiêu bằng 0. Dựa trên dữ kiện này, chúng ta tiến hành đạo hàm và giải phương trình đạo hàm bằng 0, ta thu được các giá trị tối ưu của w và b như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Thế các kết quả trên vào công thức (4.4), ta được công thức đối

<!-- Page 119 (Heavy) -->
ngẫu Lagrange của bài toán SVM lề cứng như sau:

<!-- formula-not-decoded -->

Trong đó 1 là véc-tơ n chiều gồm toàn số 1 còn Q là ma trận kích thước n × n đối xứng: Q = [ q ij = y i y j x T i x j ] .

Định nghĩa 4.5 (Bài toán đối ngẫu SVM lề cứng) . Cho bài toán tối ưu SVM lề cứng với hàm mục tiêu và điều kiện ràng buộc theo Định nghĩa 4.4, bài toán đối ngẫu Lagrange SVM lề cứng là bài toán tối ưu:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

với α i là các hệ số Lagrange tương ứng với các ràng buộc của bài toán gốc.

Định lý 4.6 (Tính chất của bài toán đối ngẫu SVM lề cứng) . Bài toán tối ưu đối ngẫu của SVM lề cứng là một bài toán tối ưu lồi với các ràng buộc tuyến tính.

Chứng minh: Từ công thức (4.5), chúng ta thấy được rằng hàm mục tiêu L ( α ) của bài toán đối ngẫu SVM lề cứng là hàm bậc hai với véc-tơ tham số α . Ma trận Hessian của hàm mục tiêu này được tính như sau:

<!-- formula-not-decoded -->

<!-- Page 120 (Heavy) -->
Theo định nghĩa của ma trận Q thì phần tử q ij = y i y j x T i x j . Dễ thấy ∀ v ∈ R n

<!-- formula-not-decoded -->

Đặt a i = y i v i , chúng ta có thể biến đổi tổng trên thành

<!-- formula-not-decoded -->

Do đó, ma trận Q là ma trận nửa xác định dương. Từ công thức (4.6), ta có thể suy ra L ( α ) là hàm lõm. Bài toán đối ngẫu tìm cực đại của hàm lõm L ( α ) với các ràng buộc tuyến tính tương ứng với tìm cực tiểu của một hàm lồi với các ràng buộc tuyến tính. □

Từ định lý trên chúng ta thấy được bài toán đối ngẫu của SVM lề cứng vẫn là bài toán bài toán quy hoạch lồi bậc 2 nhưng có các ràng buộc đơn giản hơn rất nhiều so với ràng buộc của bài toán gốc. Các gói phần mềm như libsvm [6], liblinear [7] được thiết kế và cài đặt chuyên biệt để giải bài toán tối ưu SVM ở dạng đối ngẫu.

Ngoài ra, tại nghiệm tối ưu của bài toán gốc và bài toán đối ngẫu, ta còn có điều kiện bù phần dư trong các điều kiện KarushKuhn-Tucker như sau:

<!-- formula-not-decoded -->

Sử dụng các điều kiện ở công thức (4.7), ta có thể diễn giải như sau:

<!-- Page 121 (Heavy) -->
- Nếu y i (w T x i + b ) &gt; 1 thì α i = 0 , tức là mẫu thứ i không tham gia vào việc tính w . Đây là các mẫu dữ liệu nằm ngoài lề của bài toán phân lớp.
- Nếu α i &gt; 0 thì y i (w T x i + b ) = 1 , tức là nếu mẫu thứ i tham gia vào việc tính w thì mẫu dữ liệu này phải nằm ngay trên lề của bài toán phân lớp. Ta gọi các mẫu dữ liệu này là véc-tơ hỗ trợ vì các véc-tơ này nằm 'đỡ' lấy hai bên lề của bài toán phân lớp.

Sau khi tính toán được α i , ∀ i , ta có thể tính w và b như sau:

<!-- formula-not-decoded -->

## 4.3 Máy véc-tơ hỗ trợ lề mềm

Do không phải lúc nào tập dữ liệu D cũng khả tách tuyến tính, mô hình SVM có thể sửa để cho phép các mẫu dữ liệu vi phạm ràng buộc lề cứng nhưng cố gắng tối thiểu hóa các vi phạm này. Bài toán SVM lề cứng được trình bày ở Định nghĩa 4.4 sẽ được điều chỉnh thành bài toán lề mềm như sau:

Định nghĩa 4.7 (Máy véc-tơ hỗ trợ SVM lề mềm) . Cho tập dữ liệu D = { ( x i , y i ) } n i =1 với y i ∈ {-1 , +1 } . Bài toán tối ưu SVM lề mềm là bài toán tối ưu

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Trong định nghĩa trên, ξ i là vi phạm của mẫu dữ liệu thứ i và C &gt; 0 là trọng số của việc cho phép vi phạm. Giá trị của C là một

<!-- Page 122 (Heavy) -->
tham số điều chỉnh cho bài toán SVM lề mềm. Nếu chúng ta chọn giá trị của C nhỏ đồng nghĩa với việc số lượng các điểm vi phạm điều kiện phân lớp của SVM có thể lớn, và ngược lại giá trị lớn của C sẽ hạn chế lại số lượng điểm vi phạm. Nếu chúng ta tăng C →∞ thì bài toán SVM lề mềm sẽ trở thành bài toán SVM lề cứng.

Các ràng buộc đối với ξ i là ξ i ≥ 0 và ξ i ≥ 1 -y i (w T x i + b ) có thể viết gọn lại thành ξ i ≥ max(0 , 1 -y i (w T x i + b )) . Nhưng nhận thấy ta đang tối thiểu hóa tổng 1 2 ∥ w ∥ 2 + C ∑ n i =1 ξ i nên tại nghiệm tối ưu, ta có thể khai triển

<!-- formula-not-decoded -->

Do đó, có thể viết lại bài toán tối ưu SVM với lề mềm gọn hơn theo công thức (4.8).

<!-- formula-not-decoded -->

Trong công thức (4.8), hàm số

<!-- formula-not-decoded -->

được gọi là hàm lỗi bản lề. Hàm này là một cách khác để đo độ bất hợp lý của hàm phân lớp so với độ hợp lý mà ta thấy trong mô hình Perceptron và mô hình Logistic.

Đề tìm nghiệm tối ưu của Bài toán SVM lề mềm, chúng ta tiếp tục sử dụng khai triển Lagrange dựa trên công thức (4.8):

<!-- formula-not-decoded -->

với α i ≥ 0 , β i ≥ 0 là các hệ số Lagrange của các ràng buộc.

<!-- Page 123 (Heavy) -->
Hình 4.3: Hàm lỗi bản lề (hinge loss).

<!-- image -->

Tiếp tục lấy đạo hàm cho w , b và ξ ta có

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Thế ngược trở lại L , ta thu được

<!-- formula-not-decoded -->

với Q là ma trận Gram của tập dữ liệu D được định nghĩa như trường hợp của hàm đối ngẫu SVM lề cứng. Do β i ≥ 0 , ràng buộc đối với α i bây giờ trở thành 0 ≤ α i ≤ C, ∀ i . Ràng buộc này còn được gọi là ràng buộc dạng hộp do α ∈ [0 , C ] n là một hộp n chiều có kích thước mỗi chiều bằng C .

Điều kiện bù phần dư như sau

<!-- formula-not-decoded -->

<!-- Page 124 -->

<!-- Page 125 (Heavy) -->
số α i &gt; 0 . Kết hợp các điều kiện lại, ta có công thức tính trọng số w và b như sau:

<!-- formula-not-decoded -->

Ngoài cách tiếp cận giải bài toán SVM lề mềm bằng cách tối ưu bài toán đối ngẫu, chúng ta có thể giải trực tiếp bài toán gốc được trình bày ở Định nghĩa 4.7. Dựa vào nhận xét đây là bài toán tối ưu lồi do ∥ w ∥ 2 và hàm lỗi hinge là hai hàm lồi, ta có thể tối ưu hóa với phương pháp xuống đồi bằng đạo hàm. Cụ thể, đặt J (w , b ) là hàm số cần tối ưu, ta có Thuật toán huấn luyện 4.2. Chú ý là bài toán SVM lề mềm tổng quát hơn bài toán SVM lề cứng nên chúng ta chỉ cần xét trường hợp lề mềm là đủ.

<!-- formula-not-decoded -->

Các công thức cập nhật w và b này chỉ làm việc với các mẫu dữ liệu vi phạm lề phân lớp trong tập dữ liệu D (tức là các mẫu có y i (w T x i + b ) &lt; 1 ). Trong khi mô hình Perceptron chỉ cập nhật khi gặp lỗi (tức là y i (w T x i + b ) &lt; 0 ) thì mô hình SVM mở rộng việc

<!-- Page 126 -->

<!-- Page 127 -->
## 4.4 PHƯƠNG PHÁP NHÂN HÓA 101 lặp, ta cần tìm một cặp trọng số α ,α vi phạm các ràng buộc bù i j phần dư như sau: α = 0 y (wTx + b) > 1 i i i ⇒ 0 < α < C y (wTx + b) = 1 i i i ⇒ α = C y (wTx + b) < 1 i i i ⇒ Sau đó, giải bài toán tối ưu nhỏ bằng cách giữ nguyên tất cả các trọng số α ,k = i,k = j và chỉ tối ưu hai trọng số α ,α .

May mắn k i j ̸ ̸ là khi tối ưu chỉ hai trọng số, ta có công thức tính trực tiếp α ,α i j tốt nhất. Thuật toán lại tiếp tục tối ưu hóa cặp trọng số khác cho đến khi tất cả các trọng số đều thỏa mãn các ràng buộc trên trong một ngưỡng cho trước. 4.4 Phương pháp nhân hóa Trong chương này, chúng ta đã tìm hiểu hai mô hình học máy sử dụng hàm phân lớp tuyến tính h(x) = sgn(wTx + b) là mô hình Perceptron và mô hình SVM. Các công thức cập nhật trọng số w của các mô hình này đều có một điểm chung là mỗi lần cập nhật w thay đổi bằng một tổ hợp tuyến tính của các mẫu dữ liệu huấn luyện. Cụ thể, xuất phát từ w = 0, ta có công thức cập nhật như sau: (cid:88) w w + α y x (4.10) i i i ← i với α = I[y f(x ) < 0] cho mô hình Perceptron và α = I[y f(x ) < i i i i i i 1] cho mô hình SVM. Như vậy, khi thuật toán dừng, nghiệm w thu được sẽ là một tổ hợp tuyến tính của các mẫu dữ liệu trong tập D = (x ,y ) ,i = i i { } 1,2,...,n. Nghĩa là, trọng số w có thể được viết dưới dạng: n (cid:88) w = ν x (4.11) i i i=1

<!-- Page 128 -->

<!-- Page 129 -->
## 4.4 PHƯƠNG PHÁP NHÂN HÓA 103 trên không gian Rm′ mà không cần thực sự làm việc trên không gian mới này.

Tức là chỉ cần hàm κ(x,y) là đủ. Các công thức từ (4.13) đến (4.16) ở pha huấn luyện và pha suy luận trở thành n (cid:88) f(x) = ν κ(x ,x) + b i i i=1 h(x) = sgn(f(x)) ν ν + α y i i i i ← α = I[y f(x ) < 0] (cho mô hình Perceptron) i i i α = I[y f(x ) < 1] (cho mô hình SVM). i i i Tiếp tục mở rộng ra cho bài toán đối ngẫu SVM lề mềm, ta thu được dạng bài toán tối ưu theo hàm nhân κ(u,v) như sau: 1 max αT1 αTQα (4.18) α − 2 n (cid:88) với ràng buộc α y = 0, (4.19) i i i=1 0 α C, i i ≤ ≤ ∀ với Q = [q ] và q = y y κ(x ,x ). Tức là bài toán đối ngẫu cũng ij ij i j i j có thể chuyển sang không gian mới sử dụng hàm κ(u,v) mà không tốn thêm nhiều công sức tính toán. Hàm κ(u,v) = ϕ(u)Tϕ(v) với một ánh xạ ϕ bất kì được gọi là hàm nhân. Kỹ thuật sử dụng hàm nhân để chuyển mẫu dữ liệu từ không gian này sang không gian khác đối với các thuật toán tuyến tính được gọi là phương pháp nhân hoá (kernelization). Phương pháp này có nhiều ưu điểm được liệt kê dưới đây: • Phi tuyến hoá các thuật toán tuyến tính: Bằng việc sử dụng hàm nhân dựa trên hàm ϕ là hàm phi tuyến, ta đã phi tuyến hoá thuật toán phân lớp ban đầu. Thuật toán mới vẫn là thuật

<!-- Page 130 -->

<!-- Page 131 -->
## 4.5 TÌNH HUỐNG ÁP DỤNG:

PHÂN LỚP CHỮ SỐ MNIST BẰNG SVM 105 • κ(u,v) = tanh(c+auTv): hàm nhân tan-hyperbol. Sử dụng hàm này tương đương với mô hình mạng nơ-ron có một lớp ẩn với hàm kích hoạt tanh. • κ(u,v) = (cid:80)m min(u ,v ): hàm nhân giao histogram (hay dùng i=1 i i trong phân loại ảnh) • κ(u,v) = (cid:80)m min( u d, v d): hàm nhân giao histogram tổng i=1 | i | | i | quát • κ(u,v) = 1 : hàm nhân student 1+∥u−v∥d • κ(u,v) = (cid:80) κ (u ,v ) với ℓ ℓ ℓ ℓ (cid:88) κ (a,b) = P(Y = y X = a)P(Y = y X = b) ℓ ℓ ℓ | | y∈{0,1} là hàm nhân Bayes hay dùng trong dự đoán tương tác protein. • κ(u,v) = ϕ (u)Tϕ (v) với u,v là các xâu ký tự và ϕ (x) là tần p p p suất các đoạn p ký tự trong x. Hàm nhân này dùng cho bài toán dự đoán trên văn bản. 4.5 Tình huống áp dụng: Phân lớp chữ số MNIST bằng SVM Trong bài toán áp dụng này chúng ta sẽ sử dụng thuật toán SVM lề mềm cho bài toán phân lớp chữ số MNIST sử dụng thư viện scikit-learn. Như đã đề cập trong Chương 3, bộ dữ liệu MNIST là một tập hợp các hình ảnh chữ số viết tay, được sử dụng rộng rãi trong các bài toán phân loại hình ảnh. Bài toán này bao gồm 60,000 hình ảnh huấn luyện và 10,000 hình ảnh kiểm tra, mỗi hình ảnh có kích thước 28 28 điểm ảnh, tương đương với 784 đặc trưng × đầu vào. Các đặc trưng này sẽ đóng vai trò là các véc-tơ trong miền dữ liệu đầu vào. Mục tiêu của chúng ta là xây dựng một mô hình

<!-- Page 132 -->

<!-- Page 133 (Heavy) -->
Bảng 4.1: Dữ luyện huấn luyện

|   x 1 |   x 2 |   y | |-------|-------|-----| |     1 |     0 |  -1 | |     4 |     5 |  +1 | |     1 |     2 |  -1 | |     0 |     1 |  -1 | |     4 |     1 |  +1 | |     2 |     2 |  -1 |

SVM được huấn luyện thông qua việc giải bài toán đối ngẫu, trong đó chỉ các điểm nằm trên biên quyết định (gọi là véc-tơ hỗ trợ) mới ảnh hưởng đến vị trí của siêu phẳng tối ưu. Từ đó, mô hình đạt hiệu quả cao về tính khái quát và độ chính xác.

Một ưu điểm nổi bật của SVM là khả năng mở rộng cho các bài toán phân lớp phi tuyến nhờ kỹ thuật nhân hoá, cho phép ánh xạ dữ liệu sang không gian đặc trưng khác mà không tính toán trực tiếp toạ độ trên không gian đó.

Về mặt lý thuyết, SVM dựa trên nền tảng của tối ưu hóa lồi và chương trình bậc hai. Độc giả quan tâm có thể tham khảo thêm trong các tài liệu về tối ưu như [8] và [9].

## Bài tập

1. Hãy giải thích tại sao Perceptron không thể giải quyết bài toán phân loại phi tuyến tính.
2. Giải thích tác dụng của phép chuẩn hoá về N (0 , 1) đối với véc-tơ đặc trưng đầu vào khi huấn luyện mô hình Perceptron.
3. Cho dữ liệu trong Bảng 4.1 với nhãn y i ∈ {-1 , 1 } như sau Giả sử mô hình Perceptron được khởi tạo với phương trình đường thẳng x 2 = 3 2 .

<!-- Page 134 -->

<!-- Page 135 -->
## 4.6 TỔNG KẾT CHƯƠNG 109 SVM với dữ liệu như vậy.

Nêu sự khác biệt chính giữa SVM tuyến tính và SVM với hàm nhân. 9. [Lập trình] Viết chương trình huấn luyện theo thuật toán SVM lề mềm với dữ liệu trong Bảng 4.1. Tính toán độ rộng đường biên và độ chính xác của mô hình với các giá trị khác nhau của tham số C. 10. [Lập trình] Dựa trên mã nguồn tham khảo của phần trình bày Tình huống áp dụng, thay đổi các tham số của mô hình SVM lề mềm bao gồm: • Thay đổi tham số C trong khoảng [0.01,100]. • Thay đổi tham số γ trong khoảng [0.01,1]. • Thay đổi hàm nhân hoá từ Gaussian sang hàm nhân đa thức. So sánh các mô hình huấn luyện được theo độ chính xác.

<!-- Page 136 -->

<!-- Page 137 -->
Tài liệu tham khảo [1] Cortes, C., and Vapnik, V., Support-vector networks, Machine Learning, vol. 20, no. 3, pp. 273–297, 1995. [2] Boser, B. E., Guyon, I. M., and Vapnik, V. N., A training algorithm for optimal margin classifiers, Proceedings of the 5th Annual ACM Workshop on Computational Learning Theory, pp. 144–152, 1992. [3] Vapnik, V. N., Statistical learning theory, Wiley-Interscience, 1998. [4] Scho¨lkopf, B., and Smola, A. J., Learning with kernels: Sup- port vector machines, regularization, optimization, and beyond, MIT Press, 2001. [5] Joachims, T., Text categorization with support vector ma- chines: Learning with many relevant features, Proceedings of the 10th European Conference on Machine Learning, pp. 137– 142, 1998. [6] Chang, Chih-Chung, and Chih-Jen Lin. "LIBSVM: a library for support vector machines." ACM transactions on intelligent systems and technology (TIST) 2.3 (2011): 1-27.

<!-- Page 138 -->
112 TÀI LIỆU THAM KHẢO [7] Fan, R. E., Chang, K. W., Hsieh, C. J., Wang, X. R., Lin, C. J. (2008). LIBLINEAR: A library for large linear classification. the Journal of machine Learning research, 9, 1871-1874. [8] Boyd, Stephen. "Convex optimization." Cambridge UP (2004). [9] Nocedal, Jorge, and Stephen J. Wright, eds. Numerical opti- mization. New York, NY: Springer New York, 1999.

<!-- Page 139 -->
# Chương 5 Mạng nơ-ron tích chập Thuật toán lan truyền ngược được Paul Werbos đề xuất lần đầu vào năm 1974, và được áp dụng hiệu quả vào mạng nơ-ron năm 1986 bởi Rumelhart, Hinton và Williams.

Thuật toán này mở ra hy vọng mới cho Học máy nhờ khả năng biểu diễn phi tuyến mạnh mẽ của mạng nơ-ron nhiều lớp. Tuy nhiên, mạng nhiều lớp lan truyền tới bộc lộ nhiều hạn chế: số lượng tham số lớn, hiện tượng triệt tiêu đạo hàm, thiếu khả năng tự trích chọn đặc trưng, dễ quá khớp và nhạy cảm với dữ liệu đầu vào. Việc khắc phục các vấn đề này đòi hỏi cải tiến kiến trúc mạng nơ-ron. Chương 5 giới thiệu một mô hình mạng nơ-ron chuyên biệt cho xử lý ảnh và video: mạng nơ-ron tích chập CNN. CNN xuất phát từ nhu cầu nhận dạng ảnh và đã trở thành nền tảng trong thị giác máy tính. CNN sử dụng phép toán tích chập để trích xuất đặc trưng cục bộ từ ảnh, với cơ sở toán học từ tích chập trên tín hiệu hai chiều.

<!-- Page 140 (Heavy) -->
Công thức tích chập liên tục được định nghĩa như sau:

<!-- formula-not-decoded -->

Trong thực tế, ảnh và bộ lọc được biểu diễn dưới dạng ma trận rời rạc. Các đặc trưng như cạnh, góc, khuôn mặt, chữ số hay vật thể được trích xuất qua các lớp tích chập.

Để tăng hiệu quả, CNN hiện đại tích hợp thêm các lớp như liên kết đầy đủ, triệt tiêu ngẫu nhiên và chuẩn hoá loạt. Chương này cũng trình bày các kiến trúc CNN tiêu biểu như VGG, Inception, ResNet và MobileNet.

## 5.1 Mô hình hoá dữ liệu dạng ảnh

Ảnh và các dữ liệu liên quan như video mang nhiều thông tin thị giác nên là một trong những đối tượng nghiên cứu chính của Học máy. Trong máy tính, ảnh có nhiều cách thể hiên. Trong đó cách thể hiên cơ bản nhất là dùng ma trận nhiều chiều.

Định nghĩa 5.1 (Ảnh cấp xám) . Ảnh cấp xám là ma trận hai chiều G ∈ R R × C với R là chiều cao và C là chiều rộng của ảnh. Mỗi phần tử a i,j trong ma trận là cường độ của điểm ảnh tại hàng i và cột j .

Hình 5.1 minh họa ảnh cấp xám với kích thước R × C trong đó phần tử a ij là phần tử ở hàng i, cột j. Giá trị a i,j có thể được hạn chế là số thực trong đoạn [0 , 1] hoặc là số nguyên không âm trong đoạn [0 , 255] .

Ví dụ 5.2 (Ảnh cấp xám các chữ số MNIST) . Một trong các bộ dữ liệu chuẩn về ảnh cấp độ sáng là bộ ảnh MNIST [1] gồm các ảnh có kích thước 28 × 28 thể hiện các chữ số viết tay từ 0 đến 9.

<!-- Page 141 (Heavy) -->
<!-- formula-not-decoded -->

Hình 5.1: Minh họa về ảnh cấp sáng được lưu trữ dưới dạng ma trận hai chiều.

<!-- image -->

Hình 5.2: Ví dụ về ảnh cấp xám 28 × 28 được lấy từ tập MNIST với nhãn cần phải học là tập các chữ số từ 0 đến 9.

Định nghĩa 5.3 (Ảnh đa sắc, ảnh đa kênh) . Ảnh đa kênh là ma trận ba chiều I ∈ R R × C × K với R là chiều cao, C là chiều rộng và K là số kênh màu. Có thể hiểu mỗi kênh màu là một ảnh cấp xám đặc trưng cho một kênh màu nhất định. Mỗi phần tử a i,j,k trong ma trận là cường độ của điểm ảnh tại hàng i , cột j và kênh màu thứ k .

Như vậy ảnh số (ảnh màu RGB) là ảnh có 3 kênh: kênh đỏ (R), kênh xanh lá cây (G) và kênh xanh dương (B). Minh họa ba kênh màu cơ bản của ảnh số được lưu trên máy tính theo ma trận (Hình 5.3).

Đa phần các bài toán học máy trong xử lý ảnh sử dụng ảnh màu

<!-- Page 142 (Heavy) -->
Hình 5.3: Minh họa về ba kênh màu của ảnh RGB.

<!-- image -->

RGB làm dữ liệu đầu vào. Hình 5.4 [12] minh hoạ bài toán phát hiện vật thể trong ảnh là một trong những bài toán trọng tâm của Học máy. Ngoài các ảnh màu RGB thông dụng, dữ liệu ảnh dùng trong Học máy còn có các ảnh được chụp chuyên dụng với các cảm biến khác nhau nhận tín hiệu ở các dải tần số khác nhau cũng và có số lượng các kênh màu lớn (ví dụ: ảnh chụp cắt lớp vi tính, ảnh vệ tinh).

Video được thể hiện là một chuỗi ảnh liên tiếp. Ở mức chung nhất có thể xem ảnh là một cách lưu thông tin mang tính không gian. Các thông số kĩ thuật đi kèm dữ liệu ảnh thường có kích thước về chiều cao, chiều rộng, số kênh màu.

Thư viện dùng để xử lí ảnh thường dùng là Opencv. Ngoài ra còn có các thư viện khác như Pillow hoặc Scikit-image. Một điểm

<!-- Page 143 -->
## 5.2 PHÉP TOÁN TÍCH CHẬP 117 Xe đạp Chó Hình 5.4:

Ví dụ về dữ liệu dùng cho bài toán phát hiện vật thể trong ảnh. lưu ý là các dữ liệu ảnh thường rất lớn và cần lượng tài nguyên tính toán và lưu trữ thích hợp để có thể xử lí. 5.2 Phép toán tích chập Mạng nơ-ron tích chập (CNN) có thể nói là mô hình Học sâu phổ biến nhất hiện nay. Mạng CNN là nguồn cảm hứng và động lực cho nhiều nghiên cứu và ứng dụng của Học máy. Bắt đầu gây chú ý với mạng AlexNet năm 2012 [2], việc nghiên cứu và ứng dụng mạng CNN đã bùng nổ suốt từ đó đến nay. Từ mạng Alexnet có tám lớp, các mạng CNN đã phát triển thành mạng RestNet có 152 lớp và còn nhiều mạng có độ sâu hơn thế. Các cấu trúc mới, chuyên biệt cho từng loại ứng dụng Học máy được phát triển dựa trên các mạng xương sống như ResNet [4], Inception và MobileNet nở rộ và đạt nhiều thành tựu, đặc biệt trong các cuộc thi về khả năng nhận dạng. Cấu trúc mạng CNN còn được ứng dụng trong các hệ thống gợi ý, xử lý ngôn ngữ tự nhiên, xử lý âm thanh, v.v..

<!-- Page 144 (Heavy) -->
Hình 5.6: Ví dụ phép tích chập trên ảnh cấp xám.

<!-- image -->

## 5.2.1 Lớp tích chập

Mạng CNN gồm nhiều loại lớp nơ-ron nối với nhau gồm: lớp tích chập, lớp gộp và lớp liên kết đầy đủ (Hình 5.5). Lớp liên kết đầy đủ chính là lớp nơ-ron của mạng MLP chúng ta đã tìm hiểu ở mục trước, lớp này thường dùng ở phía cuối mạng để cho kết quả dự đoán. Trong mục này, chúng ta tìm hiểu lớp tích chập bao gồm nguyên lý thiết kế và cách cập nhật trọng số theo thuật toán lan truyền ngược.

Ý tưởng của lớp tích chập xuất phát từ kỹ thuật lọc trên tín hiệu hai chiều của xử lý ảnh. Giả sử có một ảnh cấp xám, để tìm một đặc trưng ảnh nhất định, kỹ thuật lọc ảnh trượt một ma trận bé (ví dụ cỡ 3 × 3 , 5 × 5 , 7 × 7 ) - gọi là bộ lọc - trên các vị trí trong ảnh to - gọi là vùng tiếp nhận . - và sử dụng phép tính tích vô hướng của bộ lọc với vùng tiếp nhận. Kết quả của việc trượt bộ lọc trên ảnh to tạo nên một ảnh cấp xám mới gọi là bản đồ đặc trưng . Các kiến thức chuyên sâu hơn về bộ lọc trong xử lí ảnh có thể được tìm hiểu trong các giáo trình về xử lý ảnh [9].

<!-- Page 145 (Heavy) -->
Ví dụ 5.4. Ví dụ phép tích chập Hình 5.6 sử dụng bộ lọc 3 × 3 (ở giữa) để tìm dấu chữ thập trong ảnh 6 × 6 (bên trái) cho kết quả là bản đồ đặc trưng (bên phải).

Định nghĩa 5.5 (Tích chập trên ảnh cấp xám) . Tích chập của ảnh cấp xám I ∈ R H in × W in với bộ lọc W ∈ R k h × k w là một bản đồ đặc trưng O ∈ R H out × W out = Conv( I, W ) được tính như sau:

<!-- formula-not-decoded -->

với h ∈ [1 , H out ] , w ∈ [1 , W out ] . Ở đây H out = H in -k h + 1 và W out = W in -k w +1 là kích thước của ảnh đầu ra.

Chia sẻ trọng số . Nếu nhìn dưới quan điểm của lớp nơ-ron thì mỗi vị trí trong bản đồ đặc trưng O h,w tương ứng với một nơ-ron. Nơ-ron này chỉ 'nhìn' vào một vùng tiếp nhận k h × k w trong ảnh ban đầu bằng cách đặt trọng số cho các vị trí trong vùng này bằng giá trị của bộ lọc còn các vùng ở ngoài nhận trọng số bằng 0. Như vậy các nơ-ron của bản đồ đặc trưng chia sẻ trọng số với nhau. Đây là ý tưởng không mới nhưng có tính đột phá đối với mạng nơ-ron vì (i) số lượng tham số của mô hình giảm đi đáng kể và (ii) trong pha huấn luyện, đạo hàm của các tham số có chia sẻ lớn hơn do được cộng dồn. Trong Hình 5.6 có đến 4 × 4 = 16 nơ-ron nhưng chỉ có tất cả 3 × 3 trọng số được chia sẻ.

Cách cộng dồn đạo hàm trên các trọng số được chia sẻ như sau có thể được minh hoạ qua ví dụ với hai nơ-ron ở công thức (5.3).

<!-- formula-not-decoded -->

Phát hiện đồng thời nhiều đặc trưng . Nếu như mỗi bộ lọc dùng để phát hiện một đặc trưng thì ta có thể thêm nhiều bộ lọc

<!-- Page 146 (Heavy) -->
để phát hiện nhiều đặc trưng ảnh cùng lúc. Kết quả tích chập của ảnh ban đầu với nhiều bộ lọc sẽ cho nhiều bản đồ đặc trưng. Số lượng bản đồ đặc trưng được gọi là số kênh đầu ra , được kí hiệu là C out của lớp tích chập. Ví dụ, nếu áp dụng C out bộ lọc, tức là W ∈ R k h × k w × C out , trên ảnh đầu vào I thì đầu ra là ảnh đa kênh O ∈ R H out × W out × C out , trong đó mỗi kênh là bản đồ đặc trưng tương ứng với một bộ lọc. Tổng quát hóa cho ảnh đa kênh, ta có định nghĩa tích chập tổng quát như sau.

Định nghĩa 5.6 (Tích chập trên ảnh đa kênh) . Tích chập của ảnh đa kênh I ∈ R H in × W in × C in với bộ lọc W ∈ R k h × k w × C in × C out là một bản đồ đặc trưng O ∈ R H out × W out × C out = Conv( I, W ) được tính như sau:

<!-- formula-not-decoded -->

với h ∈ [1 , H out ] , w ∈ [1 , W out ] , c ∈ [1 , C out ] . Ở đây H out = H in -k h +1 và W out = W in -k w +1 là kích thước của ảnh đầu ra.

Ví dụ 5.7 (Tích chập trên ảnh 3 kênh) . Nếu ảnh đầu vào có kích thước 6 × 6 × 3 , lớp tích chập bộ lọc kích thước 3 × 3 × 3 × 2 thì kết quả ta được ảnh 2 kênh kích thước 4 × 4 × 2 (gồm 2 bản đồ đặc trưng) (Hình 5.7).

Bước nhảy (stride) . Để giảm kích thước bản đồ đặc trưng, chúng ta có thể trượt bộ lọc với bước nhảy s lớn hơn 1. Như vậy, ta chỉ tính tích vô hướng giữa bộ lọc và vùng tiếp nhận ở các vị trí cách nhau s theo cả chiều dài và chiều rộng. Công thức tính kích thước khi có bước nhảy được tính như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 147 -->
## 5.2 PHÉP TOÁN TÍCH CHẬP 121 Hình 5.7:

Ví dụ phép tích chập trên ảnh ba chiều. Bù kích thước (padding). Khi dịch chuyển bộ lọc trên ảnh, ở các vị trí cuối cùng bên phải hoặc bên dưới ảnh, một số vùng tiếp nhận bị thiếu so với kích thước bộ lọc. Nếu ta bù một khoảng đệm vào bảng để đủ kích thước ở các vùng tiếp nhận cuối ảnh thì sẽ tận dụng được hết các vùng tiếp nhận này. Thường khi bù, ta thêm các số 0 vào phần bù này. Khi đó công thức tính kích thước sẽ là H = (H + 2p k + 1)/s (5.7) out in h ⌈ − ⌉ W = (W + 2p k + 1)/s (5.8) out in w ⌈ − ⌉ với p là kích thước bù thêm vào ảnh theo các hướng. Hàm kích hoạt. Sau bước tích chập mà bản chất là một hàm tuyến tính của đầu vào, lớp tích chập lại sử dụng các hàm kích hoạt để phi tuyến hoá kết quả tính toán như hàm sigmoid, hàm tanh, hàm relu. O = f(Conv(I,W)). Đặc biệt hàm relu và một số biến thể của nó được sử dụng phổ biến nhất do (i) tính toán cực kì đơn giản và (ii) đạo hàm không bị triệt tiêu khi nơ-ron được kích hoạt (đầu ra lớn hơn 0).

<!-- Page 148 (Heavy) -->
## 5.2.2 Lan truyền ngược qua lớp tích chập

Mục tiêu của thuật toán lan truyền ngược là tính toán δ i = ∂ℓ ( o,y ) ∂o i với ℓ là hàm lỗi, o là đầu ra của mạng, o i là đầu ra của lớp thứ i (đầu vào của lớp thứ i +1 ).

Xét lớp thứ i +1 là lớp tích chập với đầu vào o i có kích thước H in × W in × C in , bộ lọc W i +1 có kích thước k h × k w × C in × C out và đầu ra o i +1 có kích thước H out × W out × C out .

<!-- formula-not-decoded -->

với f là hàm kích hoạt. Giả sử rằng khi lan truyền ngược, ta đã có δ i +1 = ∂ℓ ( o,y ) ∂o i +1 với kích thước H out × W out × C out .

Từ công thức (5.4), chúng ta suy ra được công thức đạo hàm qua từng lớp tích chập như sau:

<!-- formula-not-decoded -->

với net h,w,c i +1 là tổng trọng số của nơ-ron o h,w,c i +1 trước khi áp dụng hàm kích hoạt và p ∈ [ h, h + k h ) , q ∈ [ w, w + k w ) . Trong trường hợp, p và q không thuộc khoảng đề cập thì đạo hàm bằng 0 và chúng ta có thể bỏ qua trường hợp này trong tính toán. Ngoài ra để, đạo hàm theo hàm lỗi phân lớp được cho bởi công thức (5.10):

<!-- formula-not-decoded -->

Trong công thức (5.10), chúng ta sử dụng hàm lb( u, v ) = max(1 , u -v +1) để tính cận dưới các chỉ số h và w .

Để ý thấy công thức (5.10) rất giống với công thức (5.4), chỉ khác là bộ lọc W i +1 bị xoay 180 độ và đảo chỗ hai chỉ số l, c kết

<!-- Page 149 (Heavy) -->
hợp với bù khoảng đệm. Như vậy, công thức truy hồi để tính δ i từ δ i +1 cũng là một phép tích chập.

Sau khi có δ i +1 = ∂ℓ ( o,y ) ∂o +1 , ta sử dụng đạo hàm này để tính ∂ℓ ( o,y ) ∂W i +1 . Từ công thức (5.4), biến đổi tiếp ta thu được công thức tính toán đạo hàm theo trọng số như sau:

<!-- formula-not-decoded -->

Trong cài đặt trên các thiết bị như GPU, các công thức (5.4), (5.10) và (5.11) được thực hiện song song trên nhiều lõi để tăng hiệu suất tính toán.

## 5.3 Các lớp phổ biến được sử dụng trong mạng tích chập

Mặc dù lớp tích chập đóng vai trò cơ bản trong việc học ra các đặc trưng cơ bản của ảnh, việc sử dụng các lớp tích chập sẽ thiếu hiệu quả nếu thiếu các phép lấy mẫu và ổn định quá trình huấn luyện mạng học sâu. Trong phần này, chúng ta sẽ làm quen với những lớp cơ bản khác đóng vai trò quan trọng trong cấu trúc một mạng học sâu hiện đại.

## 5.3.1 Lớp gộp

Sau các lớp tích chập, mạng CNN sử dụng lớp gộp (pooling) để tiếp tục làm giảm kích thước ảnh. Lớp gộp giúp giảm khối lượng tính toán và quan trọng nhất, làm giảm ảnh hưởng của các thay đổi nhỏ từ đầu vào. Lớp gộp hoạt động độc lập trên các bản đồ đặc

<!-- Page 150 (Heavy) -->
Hình 5.8: Ví dụ kết quả của lớp gộp theo giá trị lớn nhất trong vùng tiếp nhận.

<!-- image -->

<!-- image -->

trưng khác nhau nên chỉ làm thay đổi kích thước chiều dài, chiều rộng mà không làm thay đổi số kênh của ảnh.

Lớp gộp tính toán cũng theo các vùng tiếp nhận như lớp tích chập. Tuy nhiên, lớp tích chập không có trọng số mà nó sử dụng các phép toán quen thuộc như MaxPooling (giá trị lớn nhất trong vùng tiếp nhận) hoăc AveragePooling (giá trị trung bình). Lớp gộp MaxPool được dùng phổ biến nhất trong các mạng CNN. Ngoài ra, ta có thể thay đổi kích thước vùng tiếp nhận cũng như trượt nó với một bước nhảy tuỳ ý.

Ví dụ 5.8. Hình 5.8 là kết quả của lớp gộp với vùng tiếp nhận 2 × 2 và bước nhảy 2. Các nơ-ron được tô cùng màu với vùng tiếp nhận của nó. Ta thấy kích thước ảnh giảm hai lần theo cả chiều dài và chiều rộng (giảm bốn lần diện tích) nhưng giữ nguyên số kênh. Nếu sau lớp gộp là lớp liên kết đầy đủ thì số lượng trọng số của lớp liên kết đầy đủ giảm đi 4 lần so với không có lớp gộp. Trong một mạng CNN có hàng chục triệu, trăm triệu tham số, tỉ suất này có tác dụng rất lớn đối với hiệu năng huấn luyện và suy luận của mạng.

<!-- Page 151 -->
## 5.3 CÁC LỚP PHỔ BIẾN ĐƯỢC SỬ DỤNG TRONG MẠNG TÍCH CHẬP 125 5.3.2 Lớp liên kết đầy đủ Lớp liên kết đầy đủ bản chất là lớp nơ-ron của mạng MLP được trình bày ở chương trước.

Trong mạng CNN, sau một loạt các lớp tích chập, lớp gộp, khi độ lớn của ảnh giảm xuống đến kích thước thiết kế, tất cả các nơ-ron này được nối vào một số lớp liên kết đầy đủ nối tiếp nhau để tính đầu ra mong muốn của mô hình. Các tính toán ở các lớp liên kết đầy đủ cuối cùng giống hệt như những gì chúng ta tìm hiểu về mạng MLP ở mục trước. Nhiệm vụ của lớp liên kết đầy đủ trong mạng CNN là kết hợp thông tin từ các bản đồ đặc trưng cuối cùng của mạng CNN để đưa ra dự đoán cuối cùng. Tuỳ vào từng cấu trúc cụ thể mà, một số mô hình CNN sử dụng một hay nhiều lớp liên kết đầy đủ. Một lưu ý nhỏ nữa là, lớp liên kết đầy đủ thường có số tham số nhiều hơn so với các lớp tích chập và gộp. Do đó, việc sử dụng lớp liên kết đầy đủ cần cân nhắc để tránh tình trạng phù hợp quá mức. 5.3.3 Lớp triệt tiêu ngẫu nhiên Một kỹ thuật đặc trưng, rất phổ biến trong mạng CNN là kỹ thuật triệt tiêu ngẫu nhiên. Trong nhiều trường hợp, kể cả các mô hình có hiệu suất cao nhất (ví dụ độ chính xác 95%) có thể nhận thêm được 1-2% độ chính xác khi áp dụng kỹ thuật này. Kỹ thuật triệt tiêu ngẫu nhiên giúp mạng CNN tránh hiện tượng học quá bằng một ý tưởng khá đơn giản. Trong quá trình huấn luyện, các nơ-ron ở lớp trước bị triệt tiêu giá trị thành 0 ở lớp triệt tiêu ngẫu nhiên với một xác suất p cho trước (ví dụ: p =0,5 nghĩa là khoảng 50% số nơ-ron lớp trước sẽ bị triệt tiêu). Khi chúng ta cố tình triệt tiêu giá trị của các nơ-ron trong pha huấn luyện, các nơ-ron khác phải “gánh” trách nhiệm tạo ra đầu ra mong muốn. Do đó, bất cứ nơ-ron nào cũng phải “học” thay vì dựa vào một số nơ-ron nhất định trong mạng. Lớp triệt tiêu ngẫu nhiên có thể đứng sau tất cả các lớp (lớp đầu vào hoặc các lớp ẩn)

<!-- Page 152 (Heavy) -->
ngoại trừ lớp đầu ra. Ngoài ra, lớp triệt tiêu ngẫu nhiên cũng không hoạt động trong pha suy luận mà chúng ta chỉ triệt tiêu giá trị của nơ-ron trong pha huấn luyện. Do đó, trong pha suy luận, đầu ra của lớp triệt tiêu ngẫu nhiên là tích của đầu vào với p để được giá trị có độ lớn phù hợp.

## 5.3.4 Lớp chuẩn hóa loạt

Vai trò của lớp chuẩn hóa loạt là dùng để ổn định giá trị đầu ra và đạo hàm của các lớp mạng. Lớp chuản hóa loạt sử dụng một phép biến đổi tuyến tính để đảm bảo giá trị được cập nhật cho các lớp phía trước tập trung quanh giá trị 0. Một chú ý nhỏ ở đây là giá trị 0 là giá trị đặc biệt của các hàm kích hoạt phổ biến như relu hoặc sigmoid.

Về mặt toán học, lớp chuẩn hóa loạt được đặc trưng bằng hai tham số β, γ . Giả sử tại mỗi lô dữ liệu huấn luyện, ta nhận m điểm dữ liệu x i với i ∈ [1 . . . m ] , chúng ta có thể tính được giá trị trung bình và phương sai trong lớp đó như sau:

1. Tính trung bình thực nghiệm ( µ B ) và phương sai ( σ 2 B ) của gói trong một lượt cập nhật:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

trong đó m là số lượng mẫu của gói.

2. Chuẩn hóa từng đầu vào:

<!-- formula-not-decoded -->

với ϵ là hằng số rất nhỏ dùng để tránh chia cho 0.

<!-- Page 153 -->
## 5.4 KIẾN TRÚC MẠNG CNN XƯƠNG SỐNG 127 3.

Áp dụng phép biến đổi tuyến tính với các tham số huấn luyện γ và β: y = γxˆ + β. (5.15) i i Lớp chuẩn hoá loạt được sử dụng rộng rãi trong các mạng CNN hiện đại như ResNet, MobileNet và InceptionNet. 5.4 Kiến trúc mạng CNN xương sống Quá trình phát triển bùng nổ của mạng CNN có sự đóng góp rất lớn của một số kiến trúc mạng xương sống (backbone). Các kiến trúc mạng này được huấn luyện sẵn với một số bộ dữ liệu cực lớn như bộ dữ liệu ImageNet [10]. Nhờ đó, các mạng xương sống có khả năng phát hiện nhiều đặc trưng ảnh. Các mô hình mới thường sử dụng một trong các mạng xương sống này cùng bộ trọng số đã được huấn luyện sẵn làm cơ sở để thêm các tính năng mới. Trong mục này, chúng ta cùng tìm hiểu một số kiến trúc mạng CNN xương sống và ý tưởng độc đáo của chúng. 5.4.1 Mạng VGG Mạng VGG được Karen Simonyan và Andrew Zisserman phát minh năm 2014. Vào năm đó, mạng VGG xếp thứ hai về độ chính xác (tỉ lệ lỗi 7,3%) trong cuộc thi phân loại ảnh với bộ dữ liệu ImageNet. Mạng VGG là một mạng CNN khá đơn giản với các lớp nối tiếp. Ý tưởng chính của mạng VGG là • Vùng tiếp nhận lớn từ nhiều lớp tích chập liên tiếp: Một khối gồm hai lớp conv 3x3 xếp liền nhau sẽ có vùng tiếp nhận (receptive field) là 5x5. Mạng VGG chỉ dùng các khối nhiều lớp conv3x3 xếp liền nhau.

<!-- Page 154 (Heavy) -->
- Khối nhâp chập phía sau có nhiều bộ lọc hơn khối tích chập phía trước.

Ngoài ra, mạng VGG sử dụng hàm kích hoạt Relu và sử dụng lớp gộp 2x2 ngay sau các khối nhân nhập. Một số cải tiến mạng VGG thêm các lớp triệt tiêu ngay sau các lớp tích chập. Kết thúc mạng VGG là các hai lớp fc có 4096 nơ-ron và một lớp liên kết đầy đủ có 1000 nơ-ron đầu ra của mạng do bài toán phân lớp có 1000 lớp. Hai mạng VGG-16 (16 lớp) và VGG-19 (19 lớp) là hai mạng VGG nổi tiếng và hay được sử dụng làm mạng xương sống nhất (Hình 5.9). Kiến trúc mạng VGG không thích hợp cho việc thêm lớp nơ-ron để

Hình 5.9: Các mạng VGG-16 và VGG-19.

<!-- image -->

mạng sâu hơn do hiện tượng triệt tiêu đạo hàm khi mạng quá sâu. Ngoài ra, số lượng trọng số của mạng VGG cũng rất lớn (VGG-16 có 138 triệu, VGG-19 có 144 triệu trọng số) không thích hợp cho các thiết bị tính toán nhúng hoặc di động.

## 5.4.2 Mạng Inception

Mạng Inception được phát minh để khắc phục các nhược điểm của mạng VGG và các mạng CNN trước đó về khả năng huấn luyện với độ sâu mạng lớn. Điểm yếu của mạng VGG xuất phát từ việc nó có

<!-- Page 155 -->
## 5.4 KIẾN TRÚC MẠNG CNN XƯƠNG SỐNG 129 số kênh quá lớn.

Ví dụ, ở các lớp tích chập cuối, để nhận vào 512 kênh và tính ra 512 kênh đòi hỏi 3 3 512 512 = 2.359.296 tham × × × số cho một lớp tích chập. Các ý tưởng chính của mạng Inception, được mô tả ở Hình 5.10, bao gồm: • Nút thắt: Mạng Inception sử dụng kỹ thuật nút thắt. Cụ thể, để giảm số kênh trước khi thực hiện tích chập 3 3 và 5 5, × × mạng Inception thực hiện phép tích chập với kích thước 1 1 × để đưa số kênh về mức nhỏ, từ đó giảm số tham số cũng như ép các nơ-ron phải “học” do bị thắt chặt khả năng tính toán. • Quét đặc trưng với bộ lọc nhiều kích thước: mạng Inception sử dụng các lớp conv 1 1, 3 3, 5 5 để quét đặc trưng ở các × × × vùng tiếp nhận kích thước khác nhau, từ đó phát hiện các đặc trưng ở các mức độ phân giải khác nhau. • Sử dụng lớp gộp toàn cục: ở cuối mạng thay cho lớp liên kết đầy đủ. Ở lớp tích chập cuối cùng, mạng Inception sử dụng số bộ lọc đúng bằng số lớp cần phân loại. Sau đó, lớp gộp toàn cục tính trung bình cộng từng bản đồ đặc trưng để tính số đầu ra đúng bằng số lớp. Kỹ thuật này cũng làm giảm đáng kể số tham số (Mạng VGG sử dụng khoảng 90% tham số ở 3 lớp liên kết đầy đủ cuối cùng). • Sử dụng thêm hàm lỗi bổ trợ: Để tránh hiện tượng triệt tiêu đạo hàm khi huấn luyện, ở ngay những lớp giữa của mạng Inception có thêm các đầu ra bổ trợ cũng dùng để phân lớp như đầu ra cuối của mạng. Nhờ đó, các lớp phía trước có thêm đạo hàm từ các hàm lỗi đặt tại đây. Khi huấn luyện, hàm lỗi sử dụng là tổng có trọng số của hàm lỗi ở lớp cuối cùng và các hàm lỗi bổ trợ ở các lớp phía trước. Mạng Inception đến nay có bốn phiên bản từ Inception-v1 đến Inception-v4. Ngoài ra có thêm một phiên bản Inception-ResNet

<!-- Page 156 (Heavy) -->
Hình 5.10: Cấu trúc mô-đun inception.

<!-- image -->

(56 triệu tham số) sử dụng thêm ý tưởng của mạng ResNet ở mục tiếp sau đây.

Mạng Inception-v1 sử dụng chín mô-đun inception, tổng cộng có 22 lớp, khoảng 5 triệu tham số, đạt tỉ lệ lỗi 6,67% đứng đầu cuộc thi ILSVRC năm 2014. Mạng Inception-v2 (11 triệu tham số), Inception-v3 (23 triệu tham số), Inception-v4 (43 triệu tham số) có một số cải tiến tăng hiệu suất tính toán như (i) bằng cách thay lớp tích chập 5 × 5 bằng hai lớp tích chập 3 × 3 ; (ii) thay các lớp tích chập 3 × 3 bằng hai lớp tích chập 1 × 3 và 3 × 1 ; (iii) bố trí các lớp tích chập 1 × 3 và 3 × 1 song song thay vì nối tiếp để làm cho mạng rộng thay vì sâu hơn, tránh mất quá nhiều thông tin; (iv) sử dụng lớp tích chập 7 × 7 (cũng tách như 5 × 5 ).

Một kết quả thú vị là khi kết hợp ba mô hình Inception-ResNetv2 và một mô hình Inception-v4 bằng phương pháp học kết hợp thì tỉ lệ lỗi hạ xuống còn 3,08%.

## 5.4.3 Mạng ResNet

Mạng ResNet, là từ viết tắt của thuật ngữ Residual Network, là mạng nơ-ron đầu tiên chiến thắng tại cuộc thi phân loại ảnh ImageNet vào năm 2015. Mạng ResNet có đặc điểm nổi bật là nó có rất nhiều lớp nơ-ron (mạng ResNet chiến thắng năm 2015 có 152

<!-- Page 157 (Heavy) -->
lớp) mà không bị ảnh hưởng của hiện tượng triệt tiêu đạo hàm như kiến trúc VGG. Điểm cải tiến nổi bật của ResNet so với các thế hệ trước là các khối phần dư được thiết lập bởi kết nối dư thừa. Đây được đánh giá là một trong những ý tưởng đột phá nhất về cấu trúc mạng CNN trong những giai đoạn đầu mà nhờ đó ResNet có thể huấn luyện rất dễ dàng, đạt tỉ lệ lỗi 3,57% trên bộ dữ liệu ImageNet năm 2015. So sánh với kiến trúc khác, ý tưởng chính của mạng ResNet bao gồm những điểm chính sau là:

- Khối phần dư . Các khối này khắc phục nhược điểm của mạng CNN gồm các lớp tích chập nối tiếp là các khối phía sau không nhìn thấy đầu vào của các khối phía trước mà chỉ nhìn thấy đầu ra của các khối phía trước. Ở pha huấn luyện cũng vậy, đạo hàm cũng phải lan truyền ngược theo một thứ tự nhất định và ngày càng bị triệt tiêu.

Cụ thể, nếu xét x là đầu ra của một lớp tích chập, ta thêm vào sau x một số lớp conv và cộng đầu ra với x , kết quả của phép cộng là đầu vào của lớp nơ-ron tiếp theo. Trong Hình 5.11, có thể thấy nếu như x là đầu ra đang đạt được của mạng thì F ( x ) chính là phần dư còn thiếu để đầu ra này 'hoàn hảo' (ví dụ, trích chọn được đặc trưng quan trọng). Ta gọi kiểu kết nối này là kết nối phần dư . Kết nối đưa x ra cộng với F ( x ) gọi là kết nối đơn vị hoặc kết nối tắt .

Hình 5.11: Kết nối phần dư.

<!-- image -->

- Chuẩn hoá loạt : mạng ResNet sử dụng các lớp chuẩn hoá loạt sau mỗi lớp tích chập. Các lớp chuẩn hoá loạt giúp pha huấn luyện có thể sử dụng hệ số huấn luyện λ lớn hơn cũng như làm giảm hiện tượng triệt tiêu đạo hàm.

<!-- Page 158 (Heavy) -->
- Nút thắt : mỗi khối kết nối phần dư của mạng ResNet gồm ba lớp nhâp chập với các kích thước lần lượt là: 1 × 1 , 3 × 3 và 1 × 1 nối tiếp nhau. Hai lớp 1 × 1 giúp giảm số kênh của ảnh rồi tăng số kênh trở lại. Lớp conv 3 × 3 đóng vai trò như nút thắt cổ chai đối với thông tin lan truyền, làm việc với số lượng kênh đầu vào và đầu ra nhỏ hơn.

Với các cải tiến kỹ thuật này, mạng ResNet có thể sâu đến 152 lớp mà vẫn có thể huấn luyện một cách dễ dàng. Cấu trúc ResNet ngày nay là cấu trúc xương sống phải tính đến khi xây dựng các mô hình mới.

Hình 5.12: Mạng ResNet-50.

<!-- image -->

Mạng ResNet-50 (Hình 5.12) gồm 50 lớp, bốn khối phần dư, mỗi khối được lặp lại một số lần. Ở lần lặp đầu tiên, ở các khối phần dư có kí hiệu / 2 , các lớp tích chập 3 × 3 ở kết nối phần dư và kết nối đơn vị sử dụng bước nhảy bằng 2 làm giảm kích thước ảnh đi hai lần. Mạng ResNet-152 mở rộng mạng ResNet-50 với số lần lặp các khối phần dư thứ hai và thứ ba lần lượt là tám và 36 để đạt độ sâu 152 lớp.

## 5.4.4 Mạng MobileNet

Mạng MobileNet là mạng CNN được thiết kế với mục đích làm việc trên các thiết bị nhúng, thiết bị di động. Do khả năng tính toán hạn chế, các tính toán trên mạng MobileNet tìm cách mô phỏng

<!-- Page 159 (Heavy) -->
các lớp tích chập thông thường bằng các lớp tích chập nhẹ hơn. Kỹ thuật này gọi là tích chập phân tách theo kênh . Cụ thể, kỹ thuật này gồm hai loại tích chập sau để thay thế tích chập bình thường:

- Tích chập trên từng kênh : toán tử này thực hiện tích chập trên từng kênh của ảnh đầu vào thay vì quét ảnh đầu vào trên tất cả các kênh như lớp tích chập thông thường. Như vậy, số kênh của bộ lọc bằng với số kênh của đầu vào và số kênh của đầu ra ở bước này. Ví dụ: như hình 5.13, ta tính tích chập từng kênh đầu vào ( 6 × 6 × 1 ) với kênh tương ứng của bộ lọc ( 3 × 3 × 1 ) để được một kênh đầu ra ( 4 × 4 × 1 ), sau đó ghép các kênh kết quả lại để được đầu ra ( 4 × 4 × 3 ).
- Tích chập trên từng điểm : toán tử này chính là phép tích chập với vùng tiếp nhận 1 × 1 . Như vậy tác dụng của phép tích chập trên từng điểm là thay đổi số kênh của đầu vào.

Hình 5.13: Tích chập trên từng kênh.

<!-- image -->

Khi kết hợp với phép tích chập trên từng kênh, hai toán tử này mô phỏng cách tính tích chập bình thường nhưng sử dụng số tham số và số lượng tính toán thấp hơn nhiều. Cụ thể, tổng số tham số của cả hai toán tử là

<!-- formula-not-decoded -->

và số lượng tính toán là

<!-- formula-not-decoded -->

<!-- Page 160 (Heavy) -->
So với khối lượng tính toán nếu dùng lớp tích chập thông thường là k h × k w × C in × C out × H in × W in thì số tính toán giảm đi xấp xỉ k h × k w lần khi C out lớn. Nếu dùng bộ lọc 3 × 3 thì tỉ số này khoảng gần chín lần.

Hình 5.14: Kiến trúc mạng MobileNet-v1.

<!-- image -->

Kiến trúc mạng MobileNet-v1 (4,2 triệu tham số) được thể hiện ở Hình 5.14 gồm 27 lớp tích chập, sau lớp tích chập 3x3 đầu tiên là các lớp tích chập trên kênh và tích chập trên điểm xen kẽ nhau, cuối cùng là lớp gộp trung bình và lớp liên kết đầy đủ để phân lớp. Sau mỗi lớp tích chập, mạng MobileNet sử dụng chuẩn hoá loạt và hàm kích hoạt relu6( z ) = min(max(0 , z ) , 6) để chặn trên và chặn dưới đầu ra của các lớp.

Đến nay kiến trúc mạng MobileNet đã có thêm các phiên bản MobileNet-v2 (3,5 triệu tham số) và MobileNet-v3 (2,9 triệu tham số). Các mạng MobileNet đều có khả năng chạy trên các thiết bị di động với tốc độ rất cao (xử lý khoảng 100 hình / giây với iPhone 7, khoảng 200 hình / giây với iPhone X).

## 5.5 Bài toán nhận dạng hình ảnh

Bài toán nhận dạng hình ảnh với mạng học sâu tích chập được giải quyết đầu tiên vào năm 2012 dựa trên kiến trúc mạng AlexNet. Với tập dữ liệu ImageNet, mạng học sâu đã thể hiện khả năng học

<!-- Page 161 (Heavy) -->
vượt trội so với các phương pháp tiếp cận dựa trên đặc trưng được trích chọn của ảnh dựa trên các phương pháp cổ điển.

Dựa trên thành công này, các ứng dụng sử dụng mạng học sâu cho dữ liệu ảnh được áp dụng rộng rãi. Trong đó có hai bài toán chính được đề cập đến như là phép thử đối với các cấu trúc và phương pháp học sâu mới.

## 5.5.1 Bài toán nhận dạng ảnh

Nhận dạng ảnh hay phân loại hình ảnh là một trong những nhiệm vụ cơ bản nhất trong thị giác máy tính. Các tiến bộ của Học sâu trong bài toán này đã tạo ra một cuộc cách mạng và thúc đẩy những tiến bộ về khoa học và công nghệ trong Trí tuệ nhân tạo những năm gần đây.

Bài toán nhận dạng ảnh có đầu vào là một ảnh và gán cho nó một nhãn từ tập hợp các nhãn được xác định trước trong tập huấn luyện. Cụ thể, với x ∈ R H × W × C là một ảnh màu với chiều cao H , chiều rộng W và số kênh màu C (ví dụ, C = 3 cho ảnh màu RGB), bài toán nhận dạng ảnh yêu cầu dự đoán nhãn y ∈ { 1 , 2 , . . . , K } từ tập hợp K nhãn đã biết trước. Tức là, mô hình cần học một hàm f θ sao cho:

<!-- formula-not-decoded -->

Trong đó, θ là tập hợp các tham số của mô hình.

Ví dụ 5.9 (Nhận dạng ảnh chó và mèo) . Một ví dụ về bài toán nhận dạng ảnh là phân loại ảnh chứa chó hoặc mèo. Trong đó, ảnh là đầu vào có kích thước H × W × 3 và nhãn là chó hoặc mèo hay K = 2 .

Ví dụ 5.10 (Nhận dạng chữ số MNIST) . Bài toán nhận dạng chữ số từ ảnh là một bài toán cơ bản trong thị giác máy tính. Dữ liệu đầu vào là ảnh xám có kích thước 28 × 28 × 1 và nhãn là một trong các chữ số từ 0 đến 9 hay K = 10 .

<!-- Page 162 -->

<!-- Page 163 -->
## 5.6 MỘT SỐ CHIẾN LƯỢC HUẤN LUYỆN 137 5.5.3 Bài toán phân vùng ngữ nghĩa ảnh Bài toán phân vùng ngữ nghĩa ảnh là một bài toán quan trọng trong thị giác máy tính.

Mục tiêu của bài toán này là phân loại từng pixel trong ảnh thành các lớp khác nhau. Cụ thể, với ảnh đầu vào x RH×W×C, bài toán phân vùng ngữ nghĩa ảnh yêu cầu dự ∈ đoán một ma trận Y 1,2,...,K H×W, trong đó K là số lớp cần ∈ { } phân loại. Ví dụ 5.14 (Phân vùng ngữ nghĩa ảnh). Một ví dụ về bài toán phân vùng ngữ nghĩa ảnh là phân loại từng pixel trong ảnh thành các lớp khác nhau. Ví dụ, với ảnh đầu vào có kích thước H W 3, × × mục tiêu là phân loại từng pixel thành các lớp như đường, cây, nhà, xe, người, v.v. Ví dụ 5.15 (Phân vùng ngữ nghĩa ảnh Cityscapes). Cityscapes [13] là một tập dữ liệu lớn chứa hơn 5000 ảnh với hơn 20 nhãn khác nhau. Bài toán phân vùng ngữ nghĩa ảnh Cityscapes yêu cầu phân loại từng pixel trong ảnh thành các lớp khác nhau như đường, cây, nhà, xe, người, v.v. Dữ liệu đầu vào là ảnh màu có kích thước 1024 2048 3 và nhãn là một trong 20 nhãn đã biết trước. × × Ví dụ 5.16 (Bài toán nhận dạng khối u trong ảnh CT). Bộ dữ liệu LIDC (Lung Image Database Consortium) chứa hơn 1000 ảnh CT với nhãn khối u. Bài toán nhận dạng khối u trong ảnh CT yêu cầu phân loại từng pixel trong ảnh thành hai lớp: khối u và không phải khối u. Dữ liệu đầu vào là ảnh CT xám có kích thước 512 512 1 × × và nhãn là một trong hai lớp: nốt phổi / bình thường. 5.6 Một số chiến lược huấn luyện Mạng nơ-ron tích chập là một trong những mô hình quan trọng nhất trong học sâu, đặc biệt trong bài toán xử lý ảnh và thị giác máy tính. CNN được huấn luyện thông qua việc tối ưu hàm lỗi trên

<!-- Page 164 -->

<!-- Page 165 -->
## 5.6 MỘT SỐ CHIẾN LƯỢC HUẤN LUYỆN 139 5.6.2 Điều chỉnh hệ số học Trong cách tiếp cận cơ bản, CNN được huấn luyện thông qua việc tối ưu hàm lỗi bằng thuật toán xuống đồi bằng đạo hàm GD.

Công thức tổng quát để cập nhật lại trọng số W theo hàm lỗi được L cho bởi công thức sau: W(t+1) = W(t) η , (5.19) W − ∇ L trong đó, η là hệ số học và là đạo hàm của hàm lỗi. Như được W ∇ L trình bày ở mục 3.3, sau khi tính toán được đạo hàm của tham số W theo hàm lỗi, việc lựa chọn thuật toán tối ưu như SGD hoặc Adam cũng ảnh hưởng đến hiệu suất của mô hình. Bên cạnh đó, hệ số học (η) quyết định tốc độ cập nhật trọng số. Hệ số học quá lớn dẫn đến mất ổn định còn quá nhỏ sẽ làm chậm hội tụ. Một số cách điều chỉnh tốc độ học phổ biến như: • Giảm theo bước: Hệ số học giảm dần theo các bước: η = η γ⌊t/k⌋. (5.20) t 0 · • Giảm khi không cải thiện: Giảm η khi độ chính xác trên tập kiểm thử không cải thiện. • Khởi động hệ số học: Tăng dần η trong các epoch đầu tiên. • Lặp theo chu kì: Hệ số học dao động theo chu kỳ, giúp thoát khỏi cực tiểu cục bộ. 5.6.3 Các chiến lược huấn luyện nâng cao khác Bên cạnh hai phương pháp chính là học chuyển đổi và điều chỉnh hệ số học, một số chiến lược huấn luyện khác cũng được sử dụng để cải thiện hiệu suất của mô hình CNN, bao gồm:

<!-- Page 166 -->

<!-- Page 167 -->
## 5.8 TỔNG KẾT CHƯƠNG 141 • Chuẩn bị dữ liệu:

Dữ liệu CIFAR10 được cung cấp sẵn trong thư viện torchvision. Đối với dữ liệu ảnh, chúng ta có thể khai báo thêm bước chuẩn hoá - biến đổi trước khi đưa ảnh vào tính toán với mạng học sâu. • Khai báo mô hình học sâu tích chập: Để nhận dạng ảnh từ bộ dữ liệu CIFAR10, chúng ta sẽ sử dụng một mô hình học sâu tích chập đơn giản gồm 2 lớp tích chập chính và 2 lớp lấy mẫu. Đặc trưng đầu ra sẽ được học bằng một lớp nơ-ron kết nối đầy đủ có 128 chiều, sau đó sẽ dùng để học ra xác suất tương ứng cho 10 lớp nhãn mục tiêu. Bảng 5.1 mô tả các lớp của mô hình và các tham số được sử dụng tương ứng. • Huấn luyện mô hình: Chúng ta sẽ sử dụng hàm lỗi Entropy chéo và bộ tối ưu hoá Adam. Với mỗi lượt huấn luyện, chúng ta sẽ tính toán hàm lỗi và cập nhật các tham số của mô hình theo các tập mẫu được lấy ngẫu nhiên. Thư viện PyTorch cung cấp các hàm hỗ trợ việc này. Đối với dữ liệu CIFAR10, chúng ta sẽ huấn luyện trong khoảng 10 lượt. Vì dữ liệu CIFAR10 có kích thước lớn, chúng ta sẽ sử dụng thêm bộ tính toán song song (GPU) để tăng tốc độ huấn luyện. • Đánh giá mô hình: Chúng ta sẽ sử dụng tập dữ liệu kiểm tra để đánh giá độ chính xác của mô hình. Với thiết lập cơ bản như trên, mô hình có thể đạt độ chính xác khoảng 70-72% trên tập kiểm thử. Người học có thể tham khảo mã nguồn tại https://gist. github.com/cuongtv312/79a0992dcabaa17df633fc08aa949314 5.8 Tổng kết chương Chương này trình bày nguyên lý tích chập và cách xây dựng mạng nơ-ron tích chập (CNN) cho bài toán nhận dạng ảnh. So với mạng

<!-- Page 168 (Heavy) -->
Bảng 5.1: Cấu trúc mô hình học sâu tích chập cho bài toán nhận dạng ảnh màu ˜ CIFAR10

| Tên lớp   | Loại lớp               | Tham số                                                                                | Kích thước đầu ra   | |-----------|------------------------|----------------------------------------------------------------------------------------|---------------------| | conv1     | Lớp tích chập 2D       | Số kênh vào: 3, Số kênh ra: 32, Kích thước: 3x3, Bước nhảy: 1, Kích hoạt: ReLU         | (32, 32, 32)        | | pool1     | Lớp lấy mẫu cực đại 2D | Kích thước: 2x2, Bước nhảy: 2                                                          | (32, 16, 16)        | | conv2     | Lớp tích chập 2D       | Số kênh vào: 32, Số kênh ra: 64, Kích thước kernel: 3x3, Bước nhảy: 1, Kích hoạt: ReLU | (64, 16, 16)        | | pool2     | Lớp lấy mẫu cực đại 2D | Kích thước: 2x2, Bước nhảy: 2                                                          | (64, 8, 8)          | | flatten   | Làm phẳng              | Chuyển đổi tensor (64, 8, 8) thành véc-tơ                                              | (4096)              | | fc1       | Lớp kết nối đầy đủ     | Số nút vào: 4096, Số nút ra: 128. Kích hoạt: ReLU                                      | (128)               | | fc2       | Lớp kết nối đầy đủ     | Số nút vào: 128, Số nút ra: 10. Kích hoạt: Không (đầu ra logits)                       | (10)                |

<!-- Page 169 -->
## 5.8 TỔNG KẾT CHƯƠNG 143 nơ-ron truyền thống, CNN giúp giảm số lượng tham số và tận dụng cấu trúc không gian của ảnh.

Các thành phần cơ bản của CNN gồm lớp tích chập, lớp gộp và lớp kết nối đầy đủ. Từ đó, các kiến trúc CNN nổi bật như VGG, ResNet, MobileNet được xây dựng và chứng minh hiệu quả trên tập ImageNet. CNN đóng vai trò quan trọng trong sự phát triển của thị giác máy tính và học sâu, nhờ vào khả năng tự động học đặc trưng mà không cần thiết kế thủ công. Các lớp nâng cao như chuẩn hoá loạt và kết nối phần dư đã góp phần quan trọng trong việc mở rộng kiến trúc mạng sâu. Chiến lược huấn luyện như học chuyển đổi và tối ưu hoá hệ số học đã được áp dụng hiệu quả cho CNN và lan rộng sang các mô hình học sâu khác. Một ưu điểm lớn của CNN là khả năng tính toán hiệu quả và dễ song song hoá. Các toán tử tích chập và gộp được cài đặt hiệu quả trên CPU, GPU và cả vi xử lý di động, góp phần nâng cao hiệu năng mô hình. Với khả năng biểu diễn mạnh mẽ, học đặc trưng tự động và khả năng đạt độ chính xác cao, CNN đã giải quyết nhiều vấn đề của mạng MLP và trở thành trụ cột của học sâu trong nhận dạng hình ảnh hiện nay. Bài tập 1. Giả sử ảnh đầu vào có kích thước 6 6 3 (chiều cao chiều × × × rộng số kênh), lớp tích chập có C = 2 bộ lọc với kích thước out × 3 3 3. Tính kích thước bản đồ đặc trưng khi sử dụng bước × × nhảy s = 1 và không có phần bù. 2. Cho ảnh đầu vào có kích thước 28 28 1 (ảnh xám), sử dụng × ×

<!-- Page 170 -->

<!-- Page 171 -->
## 5.8 TỔNG KẾT CHƯƠNG 145 7. [Tìm hiểu] Tính công thức lan truyền ngược của lớp chuẩn hóa loạt.

Công thức tìm được thay đổi thế nào nếu chúng ta có kích thước lấy mẫu là 1. 8. [Tìm hiểu] Trong mạng dư thừa ResNet, khối dư thừa (Residual Block) hoạt động như thế nào? Tại sao nó lại giúp huấn luyện các mạng rất sâu? 9. [Lập trình] Dựa theo tình huống áp dụng đã trình bày, đề xuất một số các kỹ thuật tăng cường dữ liệu như: xoay ảnh, lật ảnh ngang, dịch chuyển ảnh, thay đổi độ sáng để huấn luyện mạng nơ-ron tích chập cho dữ liệu CIFAR-10. So sánh với kết quả mô hình ban đầu.

<!-- Page 172 -->

<!-- Page 173 -->
Tài liệu tham khảo [1] LeCun, Y., Bottou, L., Bengio, Y., and Haffner, P., Gradient- based learning applied to document recognition, Proceedings of the IEEE, vol. 86, no. 11, pp. 2278–2324, 1998. [2] Krizhevsky, A., Sutskever, I., and Hinton, G. E., ImageNet classification with deep convolutional neural networks, Ad- vances in Neural Information Processing Systems, vol. 25, pp. 1097–1105, 2012. [3] Simonyan, K., and Zisserman, A., Very deep convolutional networks for large-scale image recognition, arXiv preprint arXiv:1409.1556, 2014. [4] He, K., Zhang, X., Ren, S., and Sun, J., Deep residual learning for image recognition, Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pp. 770–778, 2016. [5] Szegedy, C., Liu, W., Jia, Y., Sermanet, P., Reed, S., Anguelov, D., Erhan, D., et al., Going deeper with convolutions, Proceed- ings of the IEEE Conference on Computer Vision and Pattern Recognition, pp. 1–9, 2015.

<!-- Page 174 -->
148 TÀI LIỆU THAM KHẢO [6] Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., Andreetto, M., and Adam, H., MobileNets: Efficient convolutional neural networks for mobile vision ap- plications, arXiv preprint arXiv:1704.04861, 2017. [7] LeCun, Y., Bengio, Y., and Hinton, G., Deep learning, Nature, vol. 521, no. 7553, pp. 436–444, 2015. [8] Tan, M. and Le, Q., 2019, May. Efficientnet: Rethinking model scaling for convolutional neural networks. In International con- ference on machine learning (pp. 6105-6114). PMLR. [9] J¨ahne, Bernd. Digital image processing. Springer Science & Business Media, 2005. [10] Deng, Jia, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. "Imagenet: A large-scale hierarchical image database." In 2009 IEEE conference on computer vision and pattern recognition, pp. 248-255. Ieee, 2009. [11] Zhang, Haoran, Tiansheng Chen, Yang Liu, Yuxi Zhang, and Jiong Liu. "Automatic seismic facies interpretation using su- pervised deep learning." Geophysics 86, no. 1 (2021): IM15- IM33. [12] Redmon, Joseph, and Ali Farhadi. "Yolov3: An incremental improvement." arXiv preprint arXiv:1804.02767 (2018). [13] M. Cordts, M. Omran, S. Ramos, T. Rehfeld, M. Enzweiler, R. Benenson, U. Franke, S. Roth, and B. Schiele, “The Cityscapes Dataset for Semantic Urban Scene Understanding,” in Proc. of the IEEE Conference on Computer Vision and Pattern Recog- nition (CVPR), 2016

<!-- Page 175 -->
# Chương 6 Mạng nơ-ron cho dữ liệu dạng chuỗi Dữ liệu chuỗi như văn bản, âm thanh và chuỗi thời gian đòi hỏi mô hình có khả năng ghi nhớ ngữ cảnh trong quá khứ.

Mạng nơ-ron hồi quy (Recurrent Neural Networks - RNN) là cách tiếp cận cơ bản để xử lý loại dữ liệu này thông qua trạng thái ẩn h tại mỗi t thời điểm t, được cập nhật theo công thức: h = f (W h + W x ) (6.1) t h h t−1 x t Trạng thái ẩn h đóng vai trò là bộ nhớ động, tích lũy thông t tin từ các bước thời gian trước đó, giúp mô hình có khả năng xử lý ngữ cảnh và quan hệ phụ thuộc trong chuỗi. Chương 6 trình bày các kiến trúc mạng nơ-ron cho dữ liệu dạng chuỗi, bao gồm RNN, LSTM, GRU và mô hình mạng chuyển đổi (Transformer). Đây là các kiến trúc quan trọng đã đạt hiệu quả cao trong các bài toán như xử lý ngôn ngữ tự nhiên, dịch máy, nhận

<!-- Page 176 -->

<!-- Page 177 -->
## 6.1 MÔ HÌNH HOÁ DỮ LIỆU DẠNG CHUỖI 151 Bảng 6.1:

Ví dụ về dữ liệu dạng văn bản được thu thập trên mạng internet về các thông tin bất động sản. Mô tả DT 70 m2 (tầng 1) + tầng hai 35 m2 với 1 phòng 1 phòng ngủ, mặt tiền 4 m Khu đô thị Văn Khê, Hà Nội, khu đông dân cư, nhiều văn phòng Chạy xe 2p tới đường Thanh Niên, Hồ Tây. Trước nhà 2 ô tô tránh, mặt tiền 5m cực đẹp, ô tô vô nhà. Nhà xây mới, thiết kế hiện đại, mỗi tầng đều có ban công. DT 45m2, 6 tầng, 5m mặt tiền Nhà cách mặt phố chỉ khoảng 100m. Diện tích là 50m2 rộng rãi và thoáng mát, mặt tiền rộng 5,6m có thể kinh doanh tạp hóa. Rất thuận tiện di chuyển các tuyến đường chính nhau, nhưng phổ biến nhất là f = 44.1kHz với mỗi mẫu là 16 bit dữ liệu. Đầu ra của quá trình này là một chuỗi theo thời gian: s = (s ,s ,...,s ,...,s ) (6.2) 0 1 t N−1 trong đó, t là chỉ số thời gian, N là độ dài của dãy. Dữ liệu âm thanh được dùng chủ yếu trong các bài toán liên quan đến giọng nói con người và âm nhạc. Ví dụ, chúng ta có thể gặp trong bài toán nhận diện giọng nói hoặc bài toán xây dựng văn bản từ tiếng nói. Định nghĩa 6.3 (Chuỗi thời gian). Chuỗi thời gian là một ánh xạ từ tập chỉ số 1,2,... đến không gian đặc trưng . { } X x = (x ,x ,...,x ,...,x ),x (6.3) 1 2 t T t ∈ X trong đó T là độ dài của chuỗi thời gian, x là giá trị của chuỗi tại t thời điểm t. Bên cạnh dữ liệu văn bản và dữ liệu âm thanh, có rất nhiều loại dữ liệu dạng chuỗi thời gian khác cũng được ứng dụng rộng rãi

<!-- Page 178 -->

<!-- Page 179 -->
## 6.2 MẠNG NƠ-RON HỒI QUY 153 6.2 Mạng nơ-ron hồi quy Điểm yếu cố hữu của mạng nơ-ron MLP nói chung và mạng nơ-ron CNN nói riêng là phải hoạt động trên đầu vào có kích thước cố định.

Đặc tính này khiến chúng gặp khó khăn khi làm việc với đầu vào có kích thước biến động như chuỗi thời gian. Ví dụ như khi xử lý một đoạn văn bản, một đoạn sóng âm thanh, các mô hình này cần bước tiền xử lý để chuyển hoá đầu vào về một kích thước cố định cho trước. Khi đó, thứ tự giữa các từ cũng như ngữ cảnh của đoạn văn bị mất rất nhiều thông tin. Khi làm việc với chuỗi thời gian, có một giả thuyết thường xuyên được các mô hình sử dụng là “các dữ liệu quan sát được x là các t biến ngẫu nhiên phụ thuộc vào trạng thái ẩn h nhất định”. Ví dụ, t khi viết một câu văn, các từ trong câu là các biến ngẫu nhiên quan sát được, nhưng các từ trong câu lại phụ thuộc vào trạng thái ẩn là ngữ cảnh của câu văn, trạng thái cảm xúc của người viết. Mạng nơ-ron hồi quy RNN (Recurrent Neural Network), được thiết kế để làm việc với dữ liệu có kích thước biến động. Mạng RNN cố gắng biểu diễn được (i) ngữ cảnh (trạng thái ẩn) của dữ liệu đầu vào và (ii) quan hệ giữa các từ, các đoạn trong đó, từ đó đưa ra các dự đoán chính xác hơn mạng nơ-ron thông thường. Cụ thể, trong pha suy luận, mạng RNN có phần bộ nhớ mô tả nén thông tin ngữ cảnh của chuỗi quá khứ, kết hợp với dữ liệu hiện tại để cập nhật bộ nhớ cũng như đưa ra dự đoán. Ta gọi phần bộ nhớ này là trạng thái ẩn. Cụ thể, thuật toán lan truyền tiến trong mạng RNN được mô tả trong Thuật toán 6.1 và Hình 6.2. Trong đó, x là dữ liệu đầu vào tại bước t = 1,2,...T, h là t t trạng thái ẩn tại bước t được tính từ x và trạng thái ẩn ở bước t trước h và y là đầu ra của mạng tại bước t được tính từ trạng t−1 t thái ẩn h . Các hàm kích hoạt f ,f được chọn từ các hàm kích t h y hoạt như sigmoid, tanh, relu.

<!-- Page 180 (Heavy) -->
## Thuật toán 6.1 Lan truyền tới trong mạng RNN

<!-- formula-not-decoded -->

5: Tính đầu ra:

<!-- formula-not-decoded -->

6: end for

7: return { y t } T t =1

8: end procedure

Hình 6.2: Tính toán của RNN trên chuỗi dữ liệu.

<!-- image -->

Hình 6.2 cho thấy h t hoạt động giống như một bộ nhớ lưu trữ trạng thái của chuỗi dữ liệu đầu vào đến thới điểm t . Trạng thái h t mô tả mối quan hệ giữa các đầu vào x u , u = 1 , 2 , . . . , t . Từ trạng thái h t ta đưa ra dự đoán y t như một lớp nơ-ron bình thường. Hàm lỗi của RNN tính trên các đầu ra y t . Các thuật toán lan truyền ngược vẫn hoạt động như bình thường với lưu ý cộng dồn đạo hàm của hàm lỗi đối với W x , W h và W y do chúng xuất hiện nhiều lần

<!-- Page 181 (Heavy) -->
Hình 6.3: Biểu diễn rút gọn của mạng RNN.

<!-- image -->

như trong hình. Một cách hiểu khác là mạng RNN đã chia sẻ trọng số trong việc tính toán đầu ra tại các bước khác nhau nên số lượng đầu ra không bị hạn chế. Cách tiếp cận này rất giống cách mạng CNN chia sẻ trọng số tại lớp tích chập. Về mặt thiết kế tổng quát, việc chia sẻ trọng số giúp cho mạng RNN học được các đặc trưng chung của dữ liệu đầu vào mà không cần phải sử dụng quá nhiều tham số.

## 6.2.1 Mạng nơ-ron hồi quy sâu

Dựa trên các công thức cơ sở (6.4) và (6.5), có bốn cách để làm mạng nơ-ron RNN sâu hơn, trích rút được các đặc trưng trừu tượng hơn:

- Xếp chồng các trạng thái ẩn lên trên nhau, đầu ra của trạng thái ẩn này là đầu vào của trạng thái ẩn kế tiếp như mạng nơ-ron MLP. Đây là cách làm thông dụng nhất.
- Tăng số lớp mạng giữa kết nối các trạng thái ẩn. Ví dụ mạng hai lớp h t = f 2 ( W 2 h f 1 ( W 1 h h t -1 + W x x t )) .

<!-- Page 182 (Heavy) -->
Hình 6.4: Mạng nơ-ron RNN hai chiều.

<!-- image -->

- Tăng số lớp mạng giữa kết nối đầu vào và trạng thái ẩn
- Tăng số lớp mạng giữa kết nối trạng thái ẩn và đầu ra.

Nói chung, mạng RNN sâu có hiệu suất dự đoán cao hơn các mạng RNN nông.

## 6.2.2 Mạng nơ-ron hồi quy hai chiều

Ngữ cảnh của đầu vào tại bước t nhất định không những phụ thuộc vào đầu vào ở các bước trước (trong quá khứ) mà còn phụ thuộc vào đầu vào ở các bước sau (trong tương lai). Dự đoán dựa trên cả thông tin trong quá khứ và trong tương lai sẽ chính xác hơn dự đoán dựa trên thông tin từ một phía. Mạng nơ-ron hồi quy hai chiều bao gồm hai mạng RNN đi ngược chiều nhau, dự đoán y t được tính từ trạng thái quá khứ h t và trạng thái tương lai g t (Hình 6.4).

## 6.2.3 Kiến trúc Mã hoá - Giải mã

Kiến trúc này dùng trong bài toán biến đổi chuỗi sang chuỗi . Kiến trúc gồm hai RNN hoạt động nối tiếp, trong đó: (i) RNN thứ nhất

<!-- Page 183 (Heavy) -->
Hình 6.5: Kiến trúc Mã hoá - Giải mã.

<!-- image -->

sử dụng chuỗi đầu vào để tính ra C là ngữ cảnh đầu vào từ trạng thái ẩn cuối cùng h T và (ii) RNN thứ hai sử dụng ngữ cảnh C để sinh ra chuỗi đầu ra mong muốn (Hình 6.5). Điểm đặc biệt của kiến trúc Mã hoá - Giải mã là chuỗi đầu vào và chuỗi đầu ra không cần có cùng độ dài. Do đó kiến trúc này thường được dùng trong các bài toán dịch máy giữa hai ngôn ngữ, bài toán nhận dạng và tổng hợp tiếng nói.

## 6.2.4 Những vấn đề trong mạng RNN

Trong cách tiếp cận cơ bản, mạng RNN được thiết kế để làm việc với các dữ liệu có độ dài khác nhau, chẳng hạn như văn bản hay tín hiệu âm thanh mà không cần phải tiền xử lý để đưa về kích thước cố định. Việc chia sẻ các trọng số W h , W x , W y ở mỗi bước thời gian không chỉ giúp giảm số lượng tham số cần học mà còn giúp mô hình học được các đặc trưng chung của dữ liệu chuỗi, tương tự như việc kiến trúc CNN chia sẻ trọng số trong lớp tích chập Nhờ vào

<!-- Page 184 -->

<!-- Page 185 (Heavy) -->
giữa các phần tử trong chuỗi đầu vào. Mạng RNN như mô tả ở trên rất khó học các mối quan hệ dài quá 5 - 10 bước do hiện tượng triệt tiêu đạo hàm. Trong khi đó, mạng LSTM có thể học mối quan hệ cách xa hơn nhờ các cải tiến sau

- Trạng thái ô được tính toán tại mỗi bước sao cho đạo hàm có thêm một đường lan truyền ngược ngắn hơn, trực tiếp hơn từ hàm lỗi.
- Cổng nhân có tác dụng tránh nhiễu, biến thiên ngẫu nhiên ảnh hưởng đến tính toán trạng thái ẩn và trạng thái ô.

Hình 6.6 mô tả tính toán trạng thái ẩn và trạng thái ô trong một bước của mạng LSTM có sử dụng các cổng kích hoạt sigmoid ( σ ) và cổng kích hoạt tanh (3.1). Cụ thể, cổng σ 1 (cổng quên) tính

Hình 6.6: Một bước tính toán trong mạng LSTM.

<!-- image -->

toán trọng số của trạng thái ô phía trước c t -1 . Cổng này 'linh hoạt' lựa chọn có cần trạng thái ô phía trước không. Cổng σ 2 (cổng vào) tính toán tác động (trọng số) của trạng thái ẩn h t -1 và đầu vào

<!-- Page 186 (Heavy) -->
x t trong việc tính trạng thái ô hiện tại c t . Cổng σ 3 (cổng ra) tính trọng số cho việc tính toán trạng thái ẩn hiện tại h t từ trạng thái ô c t . Kết quả tính toán thông tin đầu ra ở mỗi cổng và trạng thái ẩn mô tả bởi Thuật toán 6.2.

## Thuật toán 6.2 Lan truyền tới trong mạng LSTM

- 1: procedure LSTMForward ( { x t } T t =1 , Θ ) ▷ Θ gồm các trọng số: W x ∗ , W h ∗ , W c ∗ , W y
- 2: Khởi tạo h 0 ← 0 , c 0 ← 0
- 3: for t = 1 to T do

4:

<!-- formula-not-decoded -->

- 5: end for
- 6: return { h t , y t } T t =1
- 7: end procedure

Do công thức (6.6), mạng LSTM có thể nhớ dài hạn hơn mạng RNN thuần tuý. Mạng LSTM có thể mở rộng thành mạng LSTM sâu có nhiều lớp trạng thái ẩn hoặc mạng LSTM hai chiều như đã mô tả ở trên. So sánh với mạng RNN, mạng LSTM có thể học được ngữ cảnh dài hơn, phù hợp với các bài toán xử lý chuỗi dữ liệu như dịch máy, nhận diện giọng nói, nhận diện văn bản. Tuy nhiên, mạng LSTM cũng có cùng nhược điểm với mạng RNN là không thể tối ưu hoá được hiệu quả tính toán do việc tính toán trạng thái ẩn và trạng thái ô phức tạp và có tính tuần tự. Trong trường hợp độ dài chuỗi lớn, mạng LSTM cũng gặp khó khăn trong việc liên kết thông tin giữa các phần tử trong chuỗi dữ liệu một cách hiệu quả nếu khoảng cách giữa chúng quá xa.

<!-- Page 187 -->
## 6.4 MẠNG NƠ-RON BIẾN ĐỔI TRANSFORMER 161 6.4 Mạng nơ-ron biến đổi Transformer Để khắc phục các nhược điểm của mạng hồi quy RNN và mạng LSTM, ý tưởng của Transformer là sử dụng cơ chế chú ý để nắm bắt quan hệ giữa các phần tử trong chuỗi một cách song song, giúp mô hình học được các tương quan xa và cũng tăng tốc quá trình xử lý.

Mô tả đầu ra y bằng các đầu vào x và đầu ra trước đó t 1:t y được cho bởi công thức xác suất có điều kiện như sau: 1:t−1 P(y x ,y ) (6.7) t 1:t 1:t−1 | Để có thể ánh xạ một chuỗi thông tin bất kì về miền ngữ nghĩa, mô hình Transformer sử dụng kiến trúc mã hoá - giải mã. Đầu tiên, ta mã hoá chuỗi đầu vào bằng cách nhúng (embedding) vào miền biểu diễn ẩn. Ở chiều giải mã ngược lại, véc-tơ trong biểu diễn ẩn được sử dụng để ánh xạ từ miền biển diễn ẩn thành chuỗi đầu ra. Hình 6.7 mô tả cấu trúc này. Trong ứng dụng thực tế, các phần tử chuỗi đầu vào này được lấy từ một tập từ vựng và được mã hoá thành các chỉ số số nguyên. Số lượng phần tử trong tập tự vựng được lựa chọn phù hợp với dữ liệu cần được học. Trong phép toán tự chú ý, các phần tử trong chuỗi được xử lí song song và bỏ qua các thông tin vị trí trong chuỗi thứ tự đầu vào. Đây là ưu điểm chính giúp cho mạng Transformer có thể tính toán nhanh trên GPU tuy nhiên nó cũng làm mất đi thông tin về vị trí trong dữ liệu đầu vào cũng như là sắp xếp lại thông tin cho dữ liệu đầu ra. Để giải quyết vấn đề này về mặt kỹ thuật, các tác giả của mạng Transformer mã hoá thông tin vị trí (Positional Encoding) thành một đặc trưng trong biểu diễn ẩn của dữ liệu bằng cách tạo ra các véc-tơ có cùng số chiều với không gian của miền nhúng như sau: (cid:0) (cid:1) PE = sin pos/100002i/d (6.8) pos,2i (cid:0) (cid:1) PE = cos pos/100002i/d (6.9) pos,2i+1

<!-- Page 188 -->

<!-- Page 189 -->
## 6.4 MẠNG NƠ-RON BIẾN ĐỔI TRANSFORMER 163 phức tạp như Transformer, nơi sự nhất quán của chuẩn hóa cho từng mẫu là rất quan trọng.

Các khối mã hoá có thể xếp chồng lên nhau để mô tả các mối quan hệ phức tạp giữa các phần tử đầu vào. Khối Giải mã: gồm một mô-đun Chú ý chạy trên các đầu ra phía trước (y ), một mô-đun Chú ý chạy trên cả đầu ra của 1:t−1 khối mã hoá và một mạng kết nối đầy đủ. Các mô-đun này cũng sử dụng kết nối phần dư và chuẩn hoá, tương tự như khối mã hoá. Điểm khác biệt chính của Khối Mã hoá và Giải mã vừa trình bày là hai mô-đun này chỉ sử dụng cơ chế Chú ý (Attention) để lan truyền thông tin giữa các phần tử trong chuỗi, cho phép mạng Transformer có bộ nhớ rất dài. Cụ thể hơn, mỗi phần tử trong chuỗi đầu vào có thể truy cập tới tất cả các phần tử khác trong chuỗi, không giống như mạng RNN hay LSTM chỉ có thể truy cập tới phần tử trước đó. Các bước tính toán chính trong cơ chế Chú ý được mô tả trong Thuật toán 6.3. Mô-đun Chú ý trong mạng Transformer mở rộng cơ chế Chú ý thành nhiều đầu bằng cách chia các ma trận Q,K,V làm nhiều phần, mỗi phần đi qua một cấu trúc Chú ý đơn lẻ rồi tổng hợp lại. Trong bước tổng hợp lại, một hàm tuyến tính được sử dụng để kết hợp các kết quả từ các đầu ra Chú ý đơn lẻ. Trên đây là những mô-đun cơ bản trong kiến trúc về mạng Transformer được đề xuất trong bài báo "Attention is All You Need" [5]. Kể từ khi được đề xuất, mạng Transformer đã thể hiện được khả năng mô hình hoá ngữ cảnh vượt trội so với thế hệ các mô hình học sâu trước đó như RNN và LSTM. Mạng Transformer đã được ứng dụng rộng rãi trong nhiều bài toán xử lý ngôn ngữ tự nhiên, dịch máy, nhận dạng giọng nói và phân tích chuỗi thời gian.

<!-- Page 190 -->

<!-- Page 191 -->
## 6.5 MỘT SỐ BÀI TOÁN NHẬN THỨC KIỂU CHUỖI 165 6.5 Một số bài toán nhận thức kiểu chuỗi 6.5.1 Bài toán dịch máy thống kê Bài toán dịch máy thống kê có thể được mô hình hoá như sau y = y ,y ,...y với y V là các từ trong ngôn ngữ đích.

Ở đây 1 2 T′ t ∈ độ dài câu đích T′ = T (độ dài câu nguồn). Trong ứng dụng thực ̸ tế, các phần tử đầu vào x và phần tử đầu ra là y là các từ. Tuy i i nhiên, các mô hình tính toán không thể tính toán trực tiếp trên kí tự nên cần phải có một bước trung gian là nhúng các phần tử đầu vào x về miền biểu diễn. Giả sử tập từ vựng của chuỗi đầu vào x i là V , ánh xạ nhúng g được định nghĩa như Công thức (6.10). x x g : V Rdx (6.10) x x → với d là số chiều của không gian nhúng cho chuỗi đầu vào. x Ở chiều ngược lại, với V là tập từ vựng ứng với chuỗi đầu ra y y thì ánh xạ nhúng g phải tồn tại một ánh xạ ngược từ không gian y nhúng về tập từ vựng. Công thức ánh xạ ngược được định nghĩa như sau: g−1 : Rdy V (6.11) y → y với d là số chiều của không gian nhúng đầu ra. y Từ các dữ liệu thực tế, chúng ta có hai cách chính để khởi tạo ánh xạ nhúng, bao gồm: 1. Khởi tạo ngẫu nhiên: mỗi một từ vựng trong tập từ điển V được x khởi tạo bằng một véc-tơ ngẫu nhiên có d chiều. x 2. Huấn luyện trước: các từ vựng thường có tính ngữ nghĩa nhất định. Dựa trên cách này, các mô hình nhúng phổ biến có thể được học bằng cách tiền huấn luyện trên ngữ cảnh là câu hoặc các cụm từ có độ dài xác định. Dữ liệu để huấn luyện mô hình nhúng sẽ sử dụng toàn bộ các tập dữ liệu được thu thập. Trong

<!-- Page 192 (Heavy) -->
Bảng 6.2: Ví dụ về các chủ đề và dữ liệu chuỗi cần phân loại chủ đề

| Chủ đề                     | Dữ liệu chuỗi đầu vào                                                                                                  | |----------------------------|------------------------------------------------------------------------------------------------------------------------| | Thời sự Thời tiết Giáo dục | Tình hình mưa lớn gây ngập lụt trên diện rộng. Bộ phim mới được khán giả đón nhận nồng nhiệt. Kì thi THPT sắp diễn ra. |

bài toán dịch máy tổng quát, thì mô hình nhúng được huấn luyện trên tập tất cả văn bản tương ứng với ngôn ngữ nhất định. Trong ứng dụng thực tế thì những mô hình này được huấn luyện trước và có thể được sử dụng luôn giống như các cấu trúc mạng xương sống VGG và ResNet trong bài toán nhận dạng hình ảnh. Điểm khác biệt chính giữa mô hình nhúng trên các từ vựng và mô hình nhúng trên các ảnh là mô hình nhúng trên từ vựng thường được huấn luyện trên một tập dữ liệu lớn hơn và có thể học được bằng cách huấn luyện không giám sát.

## 6.5.2 Bài toán phát hiện chủ đề

Bài toán phát hiện chủ đề có thể mô hình hoá như một bài toán phân loại chuỗi với đầu vào là dãy x = { x 1 , x 2 , ..., x N } và đầu ra nhãn y tương tự với bài toán phân lớp y = y ∈ { 1 , 2 , . . . , C } . Bảng 6.2 mô tả một số ví dụ về các chủ đề và dữ liệu chuỗi cần phân loại chủ đề.

Tuỳ vào cách tiếp cận cụ thể của bài toàn mà các phần tử x i có thể là kí tự, từ hoặc cụm từ. Và tương tự như bài toán dịch máy, mô hình mạng nơ-ron học trên chuỗi cần phải có một bước mã hoá để chuyển các phần tử x i về miền nhúng.

Để triển khai bài toán theo mô hình này, ứng với chuỗi đầu vào x , chúng ta không cần thiết phải học hàm ánh xạ về chuỗi đầu ra y như trong các kiến trúc mô hình mạng hồi quy hoặc mạng bộ nhớ dài ngắn hạn thông thường. Thay vào đó, một ánh xạ từ miền

<!-- Page 193 -->
## 6.6 TÌNH HUỐNG ÁP DỤNG:

HỌC PHÉP TOÁN CỘNG 167 không gian ẩn của chuỗi hồi quy có thể được sử dụng kết hợp với một mạng nơ-ron lan truyền tới để học qua hàm Softmax. Công thức tổng quát được có thể được định nghĩa như sau: h = AGG(h ,h ,...,h ) (6.12) out 0 1 T o = Softmax(FC(h )) (6.13) out với T là số trạng thái ẩn và AGG là hàm tổng hợp như lấy giá trị lớn nhất hoặc lấy giá trị trung bình. Ngoài ra, trong các kiến trúc mới hơn như máy biến đổi Transformer, phần tử đầu hoặc phần tử cuối có thể được lấy để đại diện cho không gian ẩn. 6.6 Tình huống áp dụng: học phép toán cộng 6.6.1 Mô tả bài toán Trong phần Tình huống áp dụng của chương này, chúng ta sẽ thực hiện một bài toán về dự đoán chuỗi trong đó dữ liệu sẽ được sinh ra theo một qui trình đã được định trước. Nhiệm vụ của mô hình là tìm cách dự đoán kết quả mà không cần biết cụ thể qui trình sinh ra dữ liệu. Để minh hoạ cho cách tiếp cận này, chúng ta sẽ thực hiện một bài toán đơn giản là dự đoán phép cộng của hai số tự nhiên có độ dài cho trước. Dữ liệu minh hoạ sẽ là có dạng chuỗi thể hiện các phép toán dưới dạng: A + B = C Trong đó A, B và C là các chuỗi kí tự thể hiện các số tự nhiên có độ dài L xác định. Ví dụ: 1. Với A = 123, B = 100 thì C = 223, ta có phép toán được biểu diễn bằng một xâu kí tự: 123 + 100 = 223

<!-- Page 194 (Heavy) -->
2. Với A = 500 , B = 500 thì C = 1000 , ta có phép toán được biểu diễn bằng một xâu kí tự:

<!-- formula-not-decoded -->

Độ dài của các số tự nhiên A và B được quy định trước, ví dụ như L=3 trong trường hợp này. Độ dài của C thì không được quy định trước, và dựa trên kết quả của phép cộng tương ứng.

Dựa trên cách thiết lập này, chúng ta sẽ có tập dữ liệu minh hoạ D = ( X i , Y i )) N i =1 với N = 3 được minh hoạ ở Bảng 6.3.

Bảng 6.3: Ví dụ về bộ dữ liệu D

|   N | X       |    Y | |-----|---------|------| |   1 | 123+100 |  223 | |   2 | 500+500 | 1000 | |   3 | 999+111 | 1110 |

Chúng ta sẽ sử dụng mô hình hồi quy RNN để dự đoán kết quả của phép cộng dựa trên dữ liệu tập dữ liệu D .

## 6.6.2 Các bước triển khai

Để thực hiện bài toán này, chúng ta vẫn dựa trên các thư viện đã được giới thiệu trong các phần trước. Ngoài ra, chúng ta cần phải có thêm một số thư viện hỗ trợ cho việc sinh dữ liệu D . Các bước triển khai cụ thể bao gồm:

- Chuẩn bị dữ liệu: Chúng ta sẽ tự sinh dữ liệu D với các phép cộng đơn giản. Độ dài của các số tự nhiên A và B sẽ được quy định trước. Trong phần trình bày này, chúng ta sẽ sử dụng L = 3 . Dựa trên qui trình sinh dữ liệu được cài đặt, chúng ta sẽ lần lượt được sinh ra tập dữ liệu huấn luyện và kiểm thử.

<!-- Page 195 -->
## 6.7 TỔNG KẾT CHƯƠNG 169 • Xây dựng mô hình hồi quy RNN:

Chúng ta sẽ xây dựng một mô hình hồi quy RNN đơn giản có một lớp và sau đó là một lớp kết nối đầy đủ để dự đoán kết quả. Tham số nơ-ron ẩn của lớp RNN là 256. • Huấn luyện mô hình: Chúng ta sẽ sử dụng bộ dữ liệu D đã được sinh ra để huấn luyện mô hình hồi quy RNN. Trong phần áp dụng này, chúng ta vẫn sử dụng bộ tối ưu Adam với tốc độ học là 0.001. Chúng ta sẽ huấn luyện mô hình trong 10 vòng lặp. • Đánh giá mô hình: Chúng ta sẽ sử dụng mô hình hồi quy RNN đã được huấn luyện để dự đoán kết quả trên tập kiểm thử. Trong trường hợp này có nhiều cách để đánh giá độ chính xác mô hình. Chúng ta sẽ sử dụng độ đo về các kí tự chính xác và khoảng cách tuyệt đối giữa hai kết quả trên miền số tự nhiên. Người học có thể tham khảo phần mã nguồn minh hoạ được trình bày ở đường dẫn https://gist.github.com/cuongtv312/ 13bf5ef46cbbae0dc0d0e2e03b667df5 6.7 Tổng kết chương Chương này tập trung vào các kiến trúc mạng hồi quy cho dữ liệu chuỗi, làm rõ cách khai thác thông tin theo thứ tự thời gian để giải quyết các nhiệm vụ phức tạp. Các mô hình như RNN và LSTM duy trì trạng thái ẩn, cho phép ghi nhớ ngữ cảnh và học các phụ thuộc trong dữ liệu tuần tự. Nhờ đó, chúng thể hiện hiệu quả trong các tác vụ như biểu diễn ngôn ngữ và dự đoán. Việc lựa chọn kiến trúc phù hợp đóng vai trò quan trọng trong hiệu năng mô hình. Trong nhiều bài toán, LSTM và GRU cho kết quả tốt hơn RNN nhờ khả năng kiểm soát dòng thông tin và khắc phục hiện tượng triệt tiêu đạo hàm. Các mô hình hiện đại như Transformer mang lại bước tiến lớn nhờ khả năng xử lý song song và cơ chế tự chú

<!-- Page 196 -->

<!-- Page 197 -->
Tài liệu tham khảo [1] Rumelhart, D. E., Hinton, G. E., and Williams, R. J., Learning representations by back-propagating errors, Nature, vol. 323, no. 6088, pp. 533–536, 1986. [2] Elman, J. L., Finding structure in time, Cognitive Science, vol. 14, no. 2, pp. 179–211, 1990. [3] Hochreiter, S., and Schmidhuber, J., Long short-term memory, Neural Computation, vol. 9, no. 8, pp. 1735–1780, 1997. [4] Cho, K., Van Merri¨enboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., and Bengio, Y., Learning phrase representations using RNN encoder-decoder for statistical ma- chine translation, arXiv preprint arXiv:1406.1078, 2014. [5] Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., and Polosukhin, I., Attention is all you need, Advances in Neural Information Processing Systems, vol. 30, pp. 5998–6008, 2017. [6] Devlin, J., Chang, M. W., Lee, K., and Toutanova, K., BERT: Pre-training of deep bidirectional transformers for language understanding, arXiv preprint arXiv:1810.04805, 2018.

<!-- Page 198 -->
172 TÀI LIỆU THAM KHẢO [7] Graves, A., Mohamed, A. R., and Hinton, G., Speech recogni- tion with deep recurrent neural networks, Proceedings of the IEEE International Conference on Acoustics, Speech, and Sig- nal Processing, pp. 6645–6649, 2013. [8] Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.

<!-- Page 199 -->
# Chương 7 Mô hình hồi quy Trong Chương 2, chúng ta đã tìm hiểu về khả năng phân lớp của các mô hình Học máy – mô phỏng cách con người học và phân biệt các khái niệm.

Ngoài việc học khái niệm, con người còn có khả năng học mối quan hệ định lượng giữa các đại lượng, nhằm dự đoán giá trị của một biến dựa trên các biến khác, như giá nhà, nhiệt độ, hay độ ẩm. Trong Học máy, bài toán này được gọi là bài toán hồi quy. Về lý thuyết, hồi quy chỉ khác phân lớp ở hàm mất mát. Ta thay hàm lỗi phân lớp bằng hàm lỗi bình phương sai số như sau: n 1 (cid:88)(cid:0) (cid:1)2 L(w) = y f(x ;w) . i i n − i=1 Chương 7 trình bày các khái niệm cơ bản về hồi quy tuyến tính, phân tích sự đánh đổi giữa độ lệch và phương sai, cùng các mô hình hồi quy phi tuyến như mạng nơ-ron. Các kỹ thuật này đóng vai trò nền tảng trong việc xây dựng mô hình dự báo và ước lượng trong nhiều bối cảnh ứng dụng thực tế.

<!-- Page 200 -->

<!-- Page 201 -->
## 7.1 BÀI TOÁN HỒI QUY 175 mẫu theo phân bố , trung bình bình phương sai số MSE (mean P squared error) của mô hình hồi quy h được định nghĩa là: n 1 (cid:88) err (h) = (y h(x ))2 D i i n − i=1 = E [(y h (x))2] D D − Nếu có đủ dữ liệu huấn luyện, theo luật số lớn, chúng ta kì vọng lỗi thực nghiệm sẽ hội tụ về lỗi của mô hình hồi quy P err (h) err (h).

D P −→ 7.1.1 Hàm hồi quy tối ưu Chúng ta có thể xây dựng hàm hồi quy tối ưu dựa trên phân phối có điều kiện của y khi biết x theo định lý sau: Định lý 7.4 (Hàm hồi quy tối ưu). Giả sử dữ liệu (x,y) ∈ X × Y và được lấy mẫu theo phân bố với hàm lỗi ở Định nghĩa 7.1. Hàm P hồi quy tối ưu thoả mãn err (h⋆) = minerr (h) P P h là hàm hồi quy h⋆ được định nghĩa như sau: (cid:90) h⋆(x) = E [y x] = yp(y x)dy. P | | y Chứng minh: Ta có err (h) = E [(y h(x))2] P P − = E [(y h⋆(x) + h⋆(x) h(x))2] P − − = E [(y h⋆(x))2] + E [(h⋆(x) h(x))2] P P − − + E [2(y h⋆(x))(h⋆(x) h(x))] P − − = err (h⋆) + E [(h⋆(x) h(x))2] P P − + 2E [(y h⋆(x))(h⋆(x) h(x))] P − −

<!-- Page 202 -->

<!-- Page 203 -->
## 7.1 BÀI TOÁN HỒI QUY 177 do y E [h (x)] là hằng số đối với D, tiếp tục khai triển thu được D D − = Bias2 [y,h (x)] + Var [h (x)] D D D D + 2(y E [h (x)])E [E [h (x)] h (x)] D D D D D D − − (cid:124) (cid:123)(cid:122) (cid:125) 0 = Bias2 [y,h (x)] + Var [h (x)].

D D D D Trong đó, ta có Bias [y,h (x)] = y E [h (x)] (7.1) D D D D − là độ lệch giữa giá trị mong muốn y và giá trị kì vọng của h (x) D khi ta chạy thuật toán nhiều lần trên các tập dữ liệu D ngẫu nhiên. Còn Var [h (x)] = E [(E [h (x)] h (x))2] (7.2) D D D D D D − là phương sai của h (x) khi ta chạy thuật toán nhiều lần trên các D tập dữ liệu D ngẫu nhiên. Bây giờ cho (x,y) lấy mẫu từ phân bố , ta có công thức đưa P ra mối liên hệ giữa độ lệch và phương sai của một hàm hồi quy h D như sau: E [E [(y h (x))2]] = E (cid:2) Bias2 [y,h (x)] + Var [h (x)] (cid:3) . P D − D P D D D D Đây là khai triển kì vọng về lỗi mô hình hồi quy bất kì, còn gọi là sự tráo đổi giữa độ lệch và phương sai (bias-variance tradeoff). Lưu ý h là kết quả của thuật toán Học máy khi chạy trên dữ liệu D D ngẫu nhiên. Do vế trái bị chặn dưới bởi err (h⋆), nếu ta tìm được P cách giảm độ lệch (ví dụ: sử dụng mô hình mạnh, có thể nhớ được toàn bộ tập dữ liệu D) thì đến một lúc nào đó phương sai của hàm h sẽ phải tăng. Nghĩa là, thuật toán cho kết quả là một hàm dự D đoán rất không ổn định, học quá trên tập dữ liệu D.

<!-- Page 204 -->

<!-- Page 205 (Heavy) -->
của hàm hồi quy với các giá trị mục tiêu. Lỗi của mô hình hồi quy tuyến tính trên tập dữ liệu huấn luyện D là

<!-- formula-not-decoded -->

Trong trường hợp đơn giản, với x ∈ R 1 , chúng ta có thể minh hoạ mô hình hồi quy tuyến tính là một đường thẳng và lỗi của mô hình hồi quy tuyến tính là khoảng cách từ các điểm trên tập huấn luyện đến đường thẳng như trong Hình 7.2.

Hình 7.2: Minh hoạ lỗi của mô hình hồi quy tuyến tính

<!-- image -->

Chúng ta thấy rằng có sự tương đồng giữa các mô hình hồi quy tuyến tính, hồi quy Logistic và perceptron. Các mô hình đều là tổng các trọng số nhân với các thuộc tính đầu vào cộng với một hệ số tự do. Điểm khác biệt chỉ nằm ở hàm kích hoạt và cách tham số được cập nhật để tối ưu hóa hàm lỗi. Bảng 7.1 đưa ra so sánh các khác biệt cơ bản giữa ba mô hình này.

Mô hình hồi quy tuyến tính được quan tâm nhiều trong thực tế và hướng đến việc trả lời được các câu hỏi về mối quan hệ giữa các biến đầu vào và biến đầu ra, cụ thể là:

<!-- Page 206 (Heavy) -->
Bảng 7.1: So sánh ba mô hình hồi quy tuyến tính, hồi quy Logistic và perceptron

| Mô hình            | Hàm kích hoạt   | Hàm lỗi                       | |--------------------|-----------------|-------------------------------| | Hồi quy Logistic   | sigmoid( x )    | Entropy chéo                  | | Perceptron         | sgn( x )        | So sánh                       | | Hồi quy tuyến tính | id( x ) = x     | Trung bình bình phương sai số |

- Liệu giữa thuộc tính x k và y có mối liên hệ nào không?
- Mức độ chặt chẽ của mối liên hệ giữa x k và y như thế nào?
- Trong các thuộc tính x 1 , x 2 , . . . , x m , cái nào tác động nhiều đến y ?
- Dự đoán trên dữ liệu chưa biết chính xác đến mức nào?
- Có thực sự mối quan hệ giữa x và y là tuyến tính?

Ví dụ 7.6 (Dự báo doanh số từ quảng cáo) . Ví dụ, xét mô hình tuyến tính dự báo doanh số từng tháng dựa trên các loại hình quảng cáo:

Doanh số = w 1 × Tivi + w 2 × Đài phát thanh + w 3 × Báo chí + b (7.4)

Từ hàm hồi quy tuyến tính ở công thức (7.4), chúng ta có thể đưa ra được các nhận xét sau:

- Nếu thêm 1 đồng vào quảng cáo trên Tivi thì tăng được w 1 đơn vị doanh số
- Nếu thêm 1 đồng vào quảng cáo trên Đài phát thanh thì tăng được w 2 đơn vị doanh số
- Nếu thêm 1 đồng vào quảng cáo trên Báo chí thì tăng được w 3 đơn vị doanh số

<!-- Page 207 -->
## 7.2 MÔ HÌNH HỒI QUY TUYẾN TÍNH 181 • Nếu không quảng cáo gì cả thì được b đơn vị doanh số.

Nhiệm vụ của thuật toán huấn luyện mô hình là từ dữ liệu về quảng cáo và doanh số, tìm ra bộ trọng số (w1,w2,w3,b) phù hợp nhất và sau đó dùng bộ trọng số này để dự đoán doanh số tương lai. Chúng ta thấy trong bài toán này, thiết lập tương tự như bài toán học máy có giám sát phân lớp mà chúng ta đã làm quen ở các chương trước. Điểm khác biệt duy nhất là giá trị doanh số là một giá trị thực, không phải là một khái niệm. 7.2.1 Huấn luyện mô hình Trong huấn luyện mô hình hồi quy tuyến tính, dựa theo công thức (7.3), chúng ta cần tìm β = (w,b) dự đoán tốt trên . Giả sử ta P có tập dữ liệu huấn luyện D = (x ,y ) n , thì bộ tham số của { i i }i=1 mô hình hồi quy tuyến tính được xác định bằng cách tối thiểu hóa hàm lỗi thực nghiệm β∗ = arg minerr (h) D β n 1 (cid:88) = arg min (y h(x ))2. i i n − β i=1 Chúng ta nhận thấy bài toán huấn luyện mô hình hồi quy tuyến tính có thể được xem như bài toán tối ưu hoá hàm bậc hai theo tham số β. Xét mỗi mẫu huấn luyện, ta có sai số dự đoán ε = y h(x ) = y (w⊤x + b). i i i i i − − Hàm mục tiệu ở trên là tương đương với tổng bình phương sai số ε , viết tắt là RSS, được định nghĩa là i n (cid:88) L = RSS = ε2. i i=1

<!-- Page 208 (Heavy) -->
Để cực tiểu của hàm lỗi L , chúng ta lấy đạo hàm theo w và b rồi giải hệ phương trình để hai đại lượng này triệt tiêu:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Để cho dễ trình bày và cài đặt, ta có thể viết lại dưới dạng ma trận:

<!-- formula-not-decoded -->

khi đó hàm lỗi L là

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Lấy đạo hàm theo β và tìm nghiệm để đạo hàm bằng 0, ta thu được

<!-- formula-not-decoded -->

Công thức (7.6) có thể dùng để tính trực tiếp bộ tham số tối ưu β ∗ , còn gọi là phương trình chuẩn tắc (normal equation). Tuy nhiên, cách tiếp cận này yêu cầu phải tính phải tính ma trận nghịch đảo ( X ⊤ X ) -1 . Dễ thấy ma trận X ⊤ X là ma trận vuông có kích thước m × m . Nếu số chiều m lớn, việc tính toán ma trận nghịch đảo này là tốn kém và có nhiều sai số.

Ngoài cách tiếp cận trên, chúng ta có thể sử dụng phương pháp xuống đồi bằng đạo hàm như được trình bày ở Chương 3. Sử dụng công thức (7.5), ta có công thức cập nhật tham số β t +1 tại bước cập nhật thứ t +1 thông qua bước thứ t như sau:

<!-- formula-not-decoded -->

<!-- Page 209 -->
## 7.3 CÁC PHƯƠNG PHÁP ĐÁNH GIÁ MÔ HÌNH 183 với λ là tốc độ học.

Xuất phát từ điểm bắt đầu β ngẫu nhiên, 0 thuật toán sẽ lặp lại bước cập nhật này cho đến khi hội tụ. Gọi L(β ) là hàm lỗi tại bước t, chúng ta cũng có được tính chất hội t tụ tương tự như trong Chương 3, tức là hàm lỗi L(β ) sẽ giảm dần t theo thời gian và tiến về giá trị cực tiểu L(β∗) với β∗ là bộ tham số tối ưu. Định lý 7.7 (Tính hội tụ của xuống đồi bằng đạo hàm cho hồi quy tuyến tính). Xét hàm lỗi L = y Xβ 2 ∥ − ∥ với ma trận đặc trưng X Rn×m và Y Rn. Thuật toán xuống ∈ ∈ đồi bằng đạo hàm β β + λX⊤(y Xβ ) t+1 t t ← − hội tụ tới nghiệm tối ưu β∗ khi hệ số học 2 0 < λ < , λ (X⊤X) max với λ (X⊤X) là giá trị riêng lớn nhất của ma trận X⊤X. max Để chứng minh Định lý trên, chúng ta chỉ cần chỉ ra hàm lỗi L thoả mãn các điều kiện tương tự của hàm lỗi trong Đinh lý 3.6 ở Chương 3. Phần chứng minh chi tiết được xem như là bài tập ở cuối chương. 7.3 Các phương pháp đánh giá mô hình Một trong những bước quan trọng trong quá trình xây dựng mô hình hồi quy là đánh giá chất lượng của mô hình. Đánh giá mô hình giúp chúng ta hiểu rõ hơn về khả năng dự đoán của mô hình, từ đó có thể cải thiện mô hình hoặc chọn mô hình phù hợp với bài toán. Trong phần này, chúng ta sẽ tìm hiểu về hai phương pháp đánh giá mô hình hồi quy phổ biến.

<!-- Page 210 -->

<!-- Page 211 -->
## 7.3 CÁC PHƯƠNG PHÁP ĐÁNH GIÁ MÔ HÌNH 185 Hình 7.3:

Hệ số R cho các trường hợp khác nhau. Đại lượng SD trong công thức (7.11) thể hiện tính ổn định của dự đoán và thường được sử dụng cho từng khoảng [a,b] của đầu ra y . i • Độ tương quan: Phương pháp này đo lường mối quan hệ tuyến tính giữa dự đoán y và nhãn y bằng hệ số tương quan R, được (cid:98)i i cho bởi công thức: (cid:80)n (y y)(y µ) R = i=1 i − (cid:98)i − (7.12) (cid:112)(cid:80)n (y y)2 + (cid:80)n (y µ)2 i=1 i − i=1 (cid:98)i − Hệ số R cho thấy tính xu thế mối quan hệ giữa hai đại lượng y (cid:98)i và y . Khi R = 1 nghĩa là hai đại lượng cùng tăng, cùng giảm i với mối quan hệ tuyến tính. Khi R = 1 nghĩa là hai đại lượng − tăng giảm ngược chiều với mối quan hệ tuyến tính. Khi R = 0, hai đại lượng không có tương quan gì (Hình 7.3). • Hệ số R2: Bên cạnh Hệ số R, chúng ta có thể sử dụng hệ số R2 là tỉ lệ giữa phần phương sai đầu ra được diễn giải bởi mô hình so với phương sai của đầu ra đích. (cid:80)n (y y )2 R2 = 1 i=1 i − (cid:98)i . (7.13) − (cid:80)n (y y)2 i=1 i −

<!-- Page 212 -->

<!-- Page 213 (Heavy) -->
- Phương pháp dựa trên giả thiết độc lập và hiệp phương sai dạng đường chéo của sai số: Nếu ta giả sử tồn tại β ⋆ = ( w ∗ , b* ) sao cho Đẳng thức (7.16) sau được thoả mãn:

<!-- formula-not-decoded -->

với ϵ i là biến ngẫu nhiên thoả mãn E [ ϵ i ] = 0 , E [ ϵ i ] = σ 2 , E [ ϵ i ϵ j ] = 0 , ∀ i = j . Khi đó ta có,

̸

<!-- formula-not-decoded -->

Ta có thể ước lượng σ 2 bằng ước lượng không chệch như sau:

<!-- formula-not-decoded -->

Từ đó, ta có thể tính khoảng tin cậy 95% của w k theo công thức:

<!-- formula-not-decoded -->

Trong đó, v k +1 ,k +1 là phương sai của w k . Tương tự như phương pháp bootstrap, nếu khoảng tin cậy này chứa số 0, ta nói có thể bỏ qua thuộc tính x k khi ước lượng y .

## 7.4 Mạng nơ-ron hồi quy

## 7.4.1 Hồi quy với hệ cơ sở phi tuyến

Với mô hình hồi quy tuyến tính, các hệ số tuyến tính w 1 , w 2 , . . . , w d tác động trực tiếp lên các biến đầu vào x 1 , x 2 , . . . , x d . Mô hình tuyến

<!-- Page 214 -->

<!-- Page 215 -->
## 7.4 MẠNG NƠ-RON HỒI QUY 189 Sử dụng hàm lỗi sai số bình phương trên tập dữ liệu D = (x ,y ) n , ta có công thức tính lỗi ℓ là: { i i }i=1 n (cid:88) ℓ = (y wTf )2, với f = f(x ;W). (7.23) i i i i − i=1 Để huấn luyện mạng nơ-ron hồi quy, ta tính đạo hàm ℓ đối với các tham số W và b theo quy tắc lan truyền ngược.

Đạo hàm của hàm lỗi đối với w là: n ∂ℓ (cid:88) = 2 e f , (7.24) i i ∂w − i=1 trong đó e = y wTf là sai số. Đạo hàm của hàm lỗi đối với W i i i − được tính bằng cách lan truyền ngược đạo hàm δ = 2e w về các f i − lớp phía trước của mạng nơ-ron và cộng dồn qua tất cả các mẫu. Một số ví dụ về mạng nơ-ron hồi quy ứng dụng trong thực tế bao gồm: • Bài toán phát hiện vật thể trong ảnh: Cần tính vị trí và kích thước của vật thể trong ảnh. Một phương pháp phổ biến là sử dụng các hình chữ nhật bao vật thể. Toạ độ của các hình chữ nhật có thể được dự đoán bằng cách kết hợp đặc trưng trích xuất từ các tầng tích chập của mạng nơ-ron CNN và áp dụng hồi quy để dự đoán tọa độ. • Dự đoán nồng độ ô nhiễm không khí: Sử dụng mạng nơ-ron hồi quy để dự báo mức độ bụi mịn và các chất ô nhiễm khác dựa trên dữ liệu từ các cảm biến thời tiết và môi trường. • Dự báo giá bất động sản: Mô hình có thể ước tính giá trị thị trường của nhà ở dựa trên các đặc trưng như diện tích, vị trí, số phòng ngủ, tiện ích xung quanh, v.v.

<!-- Page 216 -->

<!-- Page 217 -->
## 7.6 HỒI QUY BẰNG K LÁNG GIỀNG GẦN NHẤT 191 • Ω(W) = 1 W 2:

Hàm điều chỉnh theo chuẩn hoá L2 hay còn 2∥ ∥2 gọi là hồi quy Ridge nếu mô hình là tuyến tính. Đạo hàm của hàm điều chỉnh L2 so với W cho ta Ω(W) = W, giúp việc W ∇ tính toán đạo hàm trở nên trực quan và hiệu quả. Sự khả vi của đạo hàm với hàm điều chỉnh L2 đảm bảo rằng các thuật toán xuống đồi bằng đạo hàm có thể hội tụ ổn định tới nghiệm tối ưu. Việc sử dụng hàm điều chỉnh L2 giúp tăng tính ổn định của mô hình với dữ liệu mới bằng cách làm giảm độ lệch và giảm thiểu vấn đề hay gặp trong trường hợp các dữ liệu đầu vào phụ thuộc tuyến tính. • Ω(W) = W : Hàm điều chỉnh theo chuẩn hoá L1, còn được 1 ∥ ∥ gọi là hồi quy Lasso, hay được dùng trong bài toán lựa chọn đặc trưng với hồi quy tuyến tính. Nó có khả năng thiết lập một số trọng số thành 0, qua đó loại bỏ các đặc trưng không quan trọng. Tuy nhiên, hàm điều chỉnh L1 không khả vi tại điểm 0, đòi hỏi áp dụng các kỹ thuật tối ưu đặc biệt. Các thuật toán như đạo hàm dưới có thể được sử dụng để xử lý tính không khả vi của hàm này. 7.6 Hồi quy bằng K láng giềng gần nhất Tương tự như KNN trong bài toán phân lớp, ta có thể sử dụng lân cận là các mẫu dữ liệu gần với đầu vào x để ước lượng giá trị của hàm hồi quy. Giả sử, trong tập dữ liệu D = (x ,y ) ,i = i i { } 1,2,...,n, ta lấy ra k điểm gần với x nhất là x ,x ,...,x theo i1 i2 i k hàm khoảng cách d(u,v) (thường chọn d(u,v) = u v là khoảng 2 ∥ − ∥ cách Euclid). Khi đó, ta có thể dùng trung bình cộng nhãn của k láng giềng này để ước lượng kì vọng E[y x] theo công thức (7.27). | k 1 (cid:88) h(x) = y (7.27) k ij j=1

<!-- Page 218 -->

<!-- Page 219 (Heavy) -->
Hình 7.4: Cây quyết định hồi quy tập đầu vào X .

<!-- image -->

## 7.7 Mô hình Cây quyết định trong hồi quy

Giống như cây quyết định để phân lớp, ta cũng dùng cây quyết định để phân vùng không gian đầu vào X và ước lượng E [ y | x ] thông qua trị số trung bình trong từng phân vùng.

Cụ thể, trong pha suy luận, với mỗi dữ liệu đầu vào x , ta tìm phân vùng ở các nút lá leaf( x ) của cây ứng với x , dự đoán bằng giá trị h ( x ) được định nghĩa theo công thức sau:

<!-- formula-not-decoded -->

là giá trị trung bình các nhãn y i của các mẫu dữ liệu trong D được phân vào lá đó (Hình 7.4).

Trong pha huấn luyện, thay vì tìm kiếm các quyết định phân chia cây sao cho khả năng phân lớp tăng lên, ở cây quyết định hồi quy, chúng ta tìm kiếm quyết định làm giảm phương sai của các nút, làm nhãn của các nút đồng nhất hơn. Cụ thể, phương sai của một nút chứa tập dữ liệu được định nghĩa là: D = { ( x i , y i ) } , i = 1 , 2 , . . . , n là

<!-- formula-not-decoded -->

Khi phân chia tập dữ liệu D thành các tập dữ liệu D 1 , D 2 , . . .

<!-- Page 220 -->

<!-- Page 221 -->
## 7.9 TỔNG KẾT CHƯƠNG 195 Chúng ta sẽ sử dụng mô hình hồi quy tuyến tính để dự đoán giá nhà dựa trên các đặc trưng đầu vào.

Các bước triển khai cơ bản bao gồm: • Chuẩn bị dữ liệu: Chúng ta sử dụng trực tiếp dữ liệu được cung cấp bởi thư viện scikit-learn. Số lượng đặc trưng đầu vào là 8 và 1 nhãn đầu ra. Các đặc trưng bao gồm một số thông số cơ bản như diện tích nhà, số phòng, tuổi nhà cũng như vị trí nhà và các thông tin liên quan. Chúng ta tiếp tục tiền xử lý và chia dữ liệu thành tập huấn luyện và tập kiểm thử. • Huấn luyện mô hình: Sử dụng thư viện scikit-learn để huấn luyện mô hình hồi quy tuyến tính. Trong thư viện được sử dụng, mô hình hồi quy tuyến tính khá đơn giản. Chỉ cần lựa chọn các tham số mặc định là ta có thể thu được mô hình cần huấn luyện • Đánh giá mô hình: Sử dụng các chỉ số đánh giá như sai số trung bình bình phương và hàm R2 để đánh giá mô hình hồi quy tuyến tính. Người học có thể tham khảo mã nguồn tại đường dẫn https:// gist.github.com/cuongtv312/2bb428d9ed4ab25371978d48b11575cc 7.9 Tổng kết chương Chương 7 cung cấp tổng quan khá toàn diện về các mô hình hồi quy – phương pháp dự đoán giá trị liên tục trong Học máy. Hồi quy tuyến tính giả định quan hệ tuyến tính giữa biến đầu vào và đầu ra, được huấn luyện qua hàm mất mát bình phương sai số. Phương pháp này đơn giản, hiệu quả với dữ liệu ít chiều và ít nhiễu. Hồi quy phi tuyến mở rộng khả năng biểu diễn bằng cách sử dụng các hàm kích hoạt phi tuyến và tầng ẩn, giúp mô hình học được quan hệ phức tạp hơn giữa các biến. Mạng nơ-ron hồi quy kế thừa cấu

<!-- Page 222 -->

<!-- Page 223 (Heavy) -->
Bảng 7.2: Dữ luyện huấn luyện

|   N |   x |    y |   N |   x |   y | |-----|-----|------|-----|-----|-----| |   1 | 1.0 |  0.0 |   6 | 0.7 | 0.5 | |   2 | 1.0 |  1.0 |   7 | 1.5 | 0.8 | |   3 | 0.1 | -0.4 |   8 | 2.0 | 2.0 | |   4 | 0.0 |  1.0 |   9 | 1.4 | 1.2 | |   5 | 0.3 |  0.8 |  10 | 2.0 | 1.0 |

ưu không duy nhất. Đề xuất phương pháp để tìm được nghiệm tối ưu duy nhất trong trường hợp này.

4. [Lập trình] Cho dữ liệu D = { ( x i , y i ) } 1 0 i =1 trong Bảng 7.2 với như sau:
- a) Viết chương trình huấn luyện theo thuật toán hồi quy tuyến tính với dữ liệu trong Bảng 7.2 có cấu trúc 2 lớp ẩn, mỗi lớp có 5 nơ-ron.
- b) Thay đổi số lớp ẩn và số nơ-ron trong mỗi lớp ẩn, so sánh kết quả của các mô hình tìm được.
5. [Tìm hiểu] Phân tích độ lệch và độ nhiễu mô hình hồi quy K-láng giềng gần nhất
6. [Tìm hiểu] Nêu các phương pháp để tăng độ tổng quát hoá của mô hình hồi quy sử dụng cây quyết định.
7. [Tìm hiểu] So sánh ưu nhược điểm của mô hình hồi quy tuyến tính, mô hình học sâu và cây quyết định trong việc dự đoán giá trị liên tục.
8. Trình bày các phương pháp đánh giá hiệu năng của mô hình hồi quy, bao gồm: trung bình sai số bình phương, trung bình sai số tuyệt đối và hệ số xác định R 2 .

<!-- Page 224 -->

<!-- Page 225 -->
Tài liệu tham khảo [1] Legendre, A. M., Nouvelles méthodes pour la détermination des orbites des comètes, F. Didot, Paris, 1805. [2] Fisher, R. A., The goodness of fit of regression formulae, and the distribution of regression coefficients, Journal of the Royal Statistical Society, vol. 85, no. 1, pp. 597–612, 1922. [3] Breiman, L., Friedman, J. H., Olshen, R. A., and Stone, C. J., Classification and regression trees, Wadsworth International Group, 1984. [4] Altman, N. S., An introduction to kernel and nearest-neighbor nonparametric regression, The American Statistician, vol. 46, no. 3, pp. 175–185, 1992. [5] Bishop, C. M., Neural networks for pattern recognition, Oxford University Press, 1995. [6] Hastie, T., Tibshirani, R., and Friedman, J., The elements of statistical learning, Springer, 2001.

<!-- Page 226 -->

<!-- Page 227 -->
# Chương 8 Học tăng cường Khác với học có giám sát, học tăng cường tập trung vào bài toán ra quyết định tuần tự thông qua tương tác giữa tác nhân và môi trường.

Mục tiêu chính của học tăng cường là cực đại hóa kỳ vọng tổng phần thưởng nhận được trong tương lai. Tác nhân chọn hành động theo chính sách π, nhằm tối ưu hàm mục tiêu: (cid:34) (cid:35) ∞ (cid:88) J(π) = E γtr τ∼π t t=0 Trong đó, γ (0,1) là hệ số chiết khấu, r là phần thưởng tại t ∈ thời điểm t, và τ là một quỹ đạo các trạng thái và hành động theo chính sách π. Chương này sẽ giới thiệu các khái niệm nền tảng trong học tăng cường, bao gồm môi trường, trạng thái, hành động, chính sách, hàm giá trị và phần thưởng.

<!-- Page 228 -->

<!-- Page 229 -->
## 8.1 GIỚI THIỆU VỀ QUÁ TRÌNH QUYẾT ĐỊNH MARKOV 203 Hình 8.1:

Mô hình đơn giản minh hoạ về tác tử thông minh học cách tương tác với môi trường khái niệm dữ liệu trong học có giám sát. Điểm khác biệt là thông tin về mô hình tối ưu được cho dưới dạng phần thưởng. Đây là thông tin gián tiếp, không phải thông tin trực tiếp từ hàm lỗi trong học có giám sát. 8.1.1 Mô hình toán học của học tăng cường Bài toán học tăng cường được xây dựng dựa trên cơ sở của một quá trình quyết định Markov, viết tắt là MDP (Markov Decision Process). Tính chất cơ bản của quá trình quyết định Markov đến từ dãy các trạng thái Markov . Xét một chuỗi các trạng thái s ,s ,s ,...,s 0 1 2 t trong miền thời gian rời rạc. Tính chất Markov yêu cầu giới hạn lại sự phụ thuộc lẫn nhau giữa trạng thái ở tương lai s sẽ độc lập t+1 với các trạng thái quá khứ s , s , ..., s theo Định nghĩa 8.1. t−1 t−2 0 Định nghĩa 8.1 (Tính chất Markov). Dãy s , s , ..., s có tính 0 1 T chất Markov nếu với mọi t 0, ≥ P(s s ) = P(s s ,s ,...,s ). t+1 t t+1 t t−1 0 | |

<!-- Page 230 -->

<!-- Page 231 -->
## 8.1 GIỚI THIỆU VỀ QUÁ TRÌNH QUYẾT ĐỊNH MARKOV 205 Định nghĩa 8.3 (Chính sách đơn định).

Cho một quá trình Markov được đặc trưng bởi S,A,T,R,γ , chính sách π là ánh xạ từ tập ⟨ ⟩ trạng thái S vào tập hành động A đại diện cho cách chọn hành động cho tác tử trong môi trường này, π : S A, (8.1) (cid:55)→ với π(s) A là hành động được chọn tại trạng thái s. ∈ Chính sách được đề cập trong Công thức (8.1) là chính sách đơn định, trong đó tác tử sẽ chỉ được phép chọn một hành động duy nhất tại mỗi trạng thái. Chúng ta có thể mở rộng định nghĩa này cho trường hợp chính sách ngẫu nhiên. Định nghĩa 8.4 (Chính sách ngẫu nhiên). Cho một quá trình Markov được đặc trưng bởi S,A,T,R,γ , chính sách π là phân ⟨ ⟩ phối xác suất lựa chọn hành động tại mỗi trạng thái, π(a s) = P(a s), (8.2) | | với π(a s) là xác suất chọn hành động a A tại trạng thái s S. | ∈ ∈ Để diễn tả tính ngẫu nhiên của chính sách, chúng ta có thể viết tắt a π(. s) với ý nghĩa hành động a được lấy mẫu dựa theo phân ∼ | phối của chính sách π tại trạng thái s. Nhiệm vụ của mô hình là tìm cách tối ưu hoá phần thưởng từ khi xuất phát từ trạng thái bắt đầu đến khi kết thúc (hoặc vô hạn). Ta thấy, R(s,a,s′) chỉ đánh giá được phần thưởng tại một bước riêng biệt. Để đánh giá tổng phần thường trên một dãy các trạng thái, còn gọi là quỹ đạo (trajectory), có L bước: xuất phát từ s , thực hiện hành động a đến s ; thực hiện a đến s ; ...; và 0 0 1 1 2 kết thúc tại trạng thái s , có dạng: L τ = s ,a ,s ,a ,...,s ,a ,s . 0 0 1 1 L−1 L−1 L { }

<!-- Page 232 -->

<!-- Page 233 -->
## 8.1 GIỚI THIỆU VỀ QUÁ TRÌNH QUYẾT ĐỊNH MARKOV 207 sau có độ quan trọng thấp hơn phần thưởng nhận được ở các bước thời gian trước đó.

Giá trị của γ được lựa chọn trong khoảng [0,1) để đảm bảo rằng tổng phần thưởng U(τ) hội tụ về một giá trị hữu hạn. Trong trường hợp γ = 1, tổng phần thưởng U(τ) có thể vô hạn khi L tiến về vô cùng. Việc này sẽ gây khó khăn cho việc tối ưu hoá hàm mục tiêu. Mục tiêu chính của Học tăng cường là tìm ra chính sách π cực đại hoá giá trị U(τ). Định nghĩa 8.6 (Chính sách tối ưu). Cho một quá trình quyết định Markov S,A,T,R,γ , chính sách π∗ là chính sách tối ưu nếu ⟨ ⟩ π∗ = arg maxE U(τ), τ∼π π trong đó, E U(τ) là kì vọng tổng điểm thưởng của quỹ đạo τ τ∼π được sinh ra từ chính sách π. Điểm khác biệt cơ bản giữa học tăng cường và học có giám sát là học tăng cường không cần phải biết giá trị của hàm mục tiêu tại mỗi bước thời gian nên không thể trực tiếp huấn luyện mô hình như trong học có giám sát. Thêm vào đó, các quyết định của mô hình học tăng cường có thể ảnh hưởng đến phân phối các trạng thái dọc theo quỹ đạo. 8.1.2 Một số loại môi trường cơ bản của học tăng cường Dựa vào tính chất riêng của các tập trạng thái S, tập hành động A và hàm chuyển T mà ta có một số loại phân biệt môi trường cơ bản sau: • Môi trường tất định và môi trường ngẫu nhiên: trong môi trường tất định, hàm chuyển P(s′ s,a) = 1 với duy nhất giá trị của | trạng thái đến s′ nào đó. Với các giá trị khác, của trạng thái đến

<!-- Page 234 -->

<!-- Page 235 -->
## 8.2 THUẬT TOÁN TỐI ƯU QUY HOẠCH ĐỘNG 209 8.2 Thuật toán tối ưu quy hoạch động Học tăng cường có thể xem như là một bài toán tối ưu hóa trên quá trình Markov, thông qua việc đưa ra các hành động tối ưu tại mỗi trạng thái.

Trong phần này chúng ta sẽ tìm hiểu về các phương pháp quy hoạch động cổ điển trong học tăng cường. 8.2.1 Giá trị tối ưu Chúng ta bắt đầu bằng các định nghĩa về giá trị trạng thái, từ đó giải quyết bài toán học tăng cường bằng phương pháp lặp giá trị. Định nghĩa 8.7 (Giá trị trạng thái trong chính sách). Giá trị của một trạng thái s trong chính sách π là kì vọng của giá trị quỹ đạo τ bắt đầu từ trạng thái s được sinh ra từ chính sách π: V π(s) = E [U(τ) s = s] τ∼π 0 |  (cid:12)  ∞ (cid:12) = E τ∼π  (cid:88) γtR(s t ,a t ,s t+1 ) (cid:12) (cid:12)s 0 = s, (cid:12) t=0,at∼π(st) (cid:12) trong đó, a π(s ) là hành động được chọn theo chính sách π tại t t ∼ thời điểm t, s là trạng thái tại thời điểm t. t Ta có  (cid:12)  ∞ (cid:12) V π(s) = E τ∼π  (cid:88) γtR(s t ,a t ,s t+1 ) (cid:12) (cid:12)s 0 = s (cid:12) t=0,at∼π(st) (cid:12) (cid:88) (cid:88) = π(a s) T(s,a,s′)(R(s,a,s′) + γV π(s′)). (8.3) | a s′ Đây là phương trình Bellman cho giá trị trạng thái V π(s). Định nghĩa 8.8 (Giá trị tối ưu của một trạng thái). Giá trị tối ưu của trạng thái s là giá trị lớn nhất có thể đạt được của V π(s)

<!-- Page 236 -->

<!-- Page 237 -->
## 8.2 THUẬT TOÁN TỐI ƯU QUY HOẠCH ĐỘNG 211 Như vậy, phương trình Bellman của Qπ(s,a) có thể được viết lại như sau: (cid:32) (cid:33) (cid:88) (cid:88) Qπ(s,a) = T(s,a,s′) R(s,a,s′) + γ π(a′ s′)Qπ(s′,a′) . | s′ a′ (8.6) Tương tự với hàm giá trị V ∗, dựa trên ta có hàm tối ưu Q∗(s,a) có thể được tính qua V ∗(s′) (cid:88) Q∗(s,a) = T(s,a,s′)(R(s,a,s′) + γV ∗(s′)). s′ Để ý rằng giá trị tối ưu V ∗(s′) = arg max Q∗(s′,a), ta thu được a công thức truy hồi của Q∗ như sau: (cid:88) (cid:16) (cid:17) Q∗(s,a) = T(s,a,s′) R(s,a,s′) + γ maxQ∗(s′,a′) (8.7) a′ s′ Các hàm Qπ và Q∗ được gọi là hàm giá trị trạng thái - hành động hay hàm giá trị Q.

Các hàm giá trị Q đánh giá giá trị của hành động a tại mỗi trạng thái s. Trong thực hành, các hàm giá trị Q thường được sử dụng để dễ dàng tìm chính sách tối ưu π∗. π∗(s) = arg maxQ∗(s,a) (8.8) a 8.2.3 Thuật toán lặp giá trị Trong bài toán tối ưu quyết định Markov với tập tham số cho trước, mục tiêu là tìm chính sách tối ưu π∗, tương đương với việc xác định giá trị tối ưu V ∗(s) cho mọi trạng thái s. Theo Định nghĩa 8.8, việc tính V ∗(s) yêu cầu xét toàn bộ không gian chính sách π, điều này không khả thi trong thực tế. Thay vào đó, ta dùng công thức (8.4), cho phép tính V ∗(s) dựa trên giá trị V ∗(s′) của các trạng thái kề s′ mà s có thể chuyển đến.

<!-- Page 238 -->

<!-- Page 239 -->
## 8.2 THUẬT TOÁN TỐI ƯU QUY HOẠCH ĐỘNG 213 Hình 8.3:

Mô hình tính toán giá trị V sử dụng giá trị V t+1 t bước theo một chính sách π: (cid:34) (cid:35) t−1 (cid:88) V (s) = maxE γiR(s ,a = π(s ),s ) s = s . t τ∼π i i i i+1 0 π | i=0 Tương tự định nghĩa đệ quy của V ∗, ta có công thức đệ quy cho V dựa trên V : t+1 t (cid:88) V (s) = max T(s,a,s′)(R(s,a,s′) + γV (s′)). (8.9) t+1 t a s′ Công thức này gọi là “nhìn về phía trước một bước” vì giá trị V (s) được tính từ V (s′) của các trạng thái s′ có thể đạt được từ t+1 t s. Mô hình tính toán minh họa trong Hình 8.3. Từ Hình 8.3, ta thấy V (s) được tính mà không cần biết trước t+1 giá trị V (s′), nhờ vậy loại bỏ được sự phụ thuộc lẫn nhau giữa t+1 các trạng thái. Việc chia bài toán tối ưu tổng thể thành các bài toán con đơn giản là nguyên lý cốt lõi của quy hoạch động. Dựa trên công thức (8.9), ta xây dựng được mã giả như trình bày trong Thuật toán 8.1.

<!-- Page 240 (Heavy) -->
` Thuật toán 8.1 Thuật toán lặp giá trị 1: procedure ValueIteration ( S, A, T, R, γ ) 2: for all s ∈ S do 3: V 0 ( s ) ← 0 4: end for 5: repeat 6: for all s ∈ S do 7: V t +1 ( s ) ← max a ∈ A ∑ s ′ T ( s, a, s ′ ) · ( R ( s, a, s ′ ) + γ · V t ( s ′ )) 8: end for 9: until V t +1 ( s ) hội tụ với mọi s ∈ S 10: return V ∗ ( s ) ← V t +1 ( s ) 11: end procedure `

Điều kiện dừng của vòng lặp tại Bước 5 có thể là số vòng lặp t đủ lớn hoặc khi chênh lệch giữa hai lần cập nhật nhỏ hơn một ngưỡng ϵ , tức là ∀ s : | V t +1 ( s ) -V t ( s ) | &lt; ϵ . Để đảm bảo tính tối ưu, cần bảo đảm rằng V t ( s ) hội tụ về V ∗ ( s ) khi t → ∞ . Định lý sau trình bày điều kiện hội tụ của thuật toán lặp giá trị.

Định lý 8.11 (Tính hội tụ của thuật toán lặp giá trị) . Xét một quá trình quyết định Markov với tập trạng thái hữu hạn S và tập hành động rời rạc hữu hạn A . Giả sử tồn tại giá trị tối ưu V ∗ ( s ) hữu hạn với mọi s ∈ S . Khi đó, dãy giá trị V t ( s ) sinh ra từ thuật toán lặp giá trị hội tụ về V ∗ ( s ) khi t →∞ .

Chứng minh: Xét trường hợp đơn giản với tập trạng thái S và hành động A là rời rạc và hữu hạn. Giả sử hệ số chiết khấu γ thoả mãn 0 &lt; γ &lt; 1 để đảm bảo tổng phần thưởng hữu hạn. Sắp xếp các trạng thái s ∈ S theo thứ tự bất kỳ, khi đó V ∗ ∈ R | S | là véc-tơ giá trị tối ưu và tương tự V 0 , V 1 , . . . , V t ∈ R | S | là dãy véc-tơ giá trị trong quá trình lặp.

Thuật toán lặp giá trị có thể viết dưới dạng toán tử Bellman

<!-- Page 241 (Heavy) -->
T : R | S | → R | S | như sau:

<!-- formula-not-decoded -->

Véc-tơ giá trị tối ưu V ∗ là điểm cố định của T , tức là T V ∗ = V ∗ . Thuật toán lặp giá trị được định nghĩa đệ quy bởi:

<!-- formula-not-decoded -->

Để chứng minh hội tụ, ta chứng minh T là toán tử co với hệ số γ theo chuẩn ∞ :

<!-- formula-not-decoded -->

Xét V, V ′ ∈ R | S | bất kỳ và s ∈ S , ta có:

<!-- formula-not-decoded -->

Dòng (8.13) dùng tính chất: | max f ( a ) -max g ( a ) | ≤ max | f ( a ) -g ( a ) | . Dòng (8.14) áp dụng bất đẳng thức tam giác. Dòng (8.15) dùng bất đẳng thức Jensen với T ( s, a, s ′ ) là phân phối xác suất. Suy ra:

<!-- formula-not-decoded -->

Vậy T là toán tử co với hệ số γ &lt; 1 trên không gian metric ( R | S | , ∥· ∥ ∞ ) . Theo định lý điểm cố định Banach, tồn tại duy nhất điểm cố

<!-- Page 242 -->

<!-- Page 243 -->
## 8.2 THUẬT TOÁN TỐI ƯU QUY HOẠCH ĐỘNG 217 Hình 8.4:

Mô hình tính toán giá trị V π(s) với chính sách π Ta định nghĩa V π(s) là giá trị tại trạng thái s sau t bước theo t chính sách π và cập nhật theo công thức đệ quy: (cid:88) V π (s) = T(s,π(s),s′)[R(s,π(s),s′) + γV π(s′)]. (8.18) t+1 t s′ Tương tự như thuật toán lặp giá trị, công thức trên cho phép V π(s) t hội tụ về V π(s) khi t , bắt đầu từ giá trị khởi tạo V bất kỳ. 0 → ∞ Sau khi đã tính được V π(s), ta có thể cập nhật lại chính sách π theo: (cid:88) π(s) = arg max T(s,a,s′)[R(s,a,s′) + γV π(s′)]. (8.19) a s′ Kết hợp hai công thức (8.18) và (8.19), ta thu được thuật toán lặp theo chính sách (Thuật toán 8.2). Thuật toán dừng khi chính sách π không thay đổi sau vòng lặp cập nhật V π. Trong các điều kiện tương tự Định lý 8.11, thuật toán hội tụ về chính sách tối ưu π∗ và giá trị tối ưu V ∗(s). Phần chứng minh chi tiết được để lại như một bài tập ở cuối chương. Thuật toán lặp theo giá trị và lặp theo chính sách là hai phương pháp nền tảng cho các thuật toán tối ưu trong học tăng cường. Dựa

<!-- Page 244 (Heavy) -->
## Thuật toán 8.2 Thuật toán lặp chính sách

̸

` 1: procedure PolicyIteration ( S, A, T, R, γ ) 2: Khởi tạo chính sách π ( s ) ngẫu nhiên với mọi s ∈ S 3: repeat ▷ Đánh giá chính sách 4: repeat 5: for all s ∈ S do 6: V t +1 ( s ) ← ∑ a ∼ π ( . | s ) ∑ s ′ T ( s, a, s ′ )( R ( s, a, s ′ ) + γ · V t ( s ′ )) 7: end for 8: until V t +1 ( s ) hội tụ với mọi s ▷ Cải thiện chính sách 9: check ← true 10: for all s ∈ S do 11: π old ← π ( s ) 12: π ( s ) ← arg max a ∈ A ∑ s ′ T ( s, a, s ′ )( R ( s, a, s ′ ) + γ · V ( s ′ )) 13: if π ( s ) = π old then 14: check ← false 15: end if 16: end for 17: until check = true 18: return π 19: end procedure `

trên quy hoạch động, ta có thể loại bỏ sự phụ thuộc lẫn nhau trong mô hình và xác định thứ tự tính toán hợp lý để xấp xỉ giá trị tối ưu.

Khi số vòng lặp đủ lớn, Định lý 8.11 đảm bảo thuật toán hội tụ về giá trị V ∗ cần tìm. Các trình bày trong phần này chỉ áp dụng cho bài toán tối ưu quá trình Markov với miền trạng thái S và hành động A là hữu hạn, rời rạc. Với các miền hành động liên tục, cần áp dụng kỹ thuật rời rạc hoá hoặc xấp xỉ để chuyển bài toán về dạng có thể xử lý bằng các thuật toán trên.

<!-- Page 245 -->
## 8.3 HỌC TĂNG CƯỜNG VÀ PHƯƠNG PHÁP HỌC HÀM Q 219 Hình 8.5:

Mô hình tương tác giữa tác tử và môi trường trong học tăng cường 8.3 Học tăng cường và phương pháp học hàm Q Trong mục 8.2, ta đã xây dựng hai thuật toán: lặp giá trị và lặp theo chính sách dựa trên phương pháp quy hoạch động để giải bài toán tối ưu quyết định trên quá trình Markov. Tuy nhiên, trong thực tế, hàm chuyển trạng thái T(s,a,s′) và hàm phần thưởng R(s,a,s′) thường không được biết trước hoặc không gian trạng thái quá lớn để lưu trữ đầy đủ các giá trị này. Phần này giới thiệu thiết lập tổng quát hơn (Hình 8.5), trong đó tác tử không biết trước T và R, mà phải học thông qua tương tác với môi trường. Cụ thể, tác tử thực hiện hành động a, sau đó nhận được trạng thái mới s′ và phần thưởng riêng lẻ r = r(s,a,s′). Kể từ đây, ta dùng r để chỉ phần thưởng thay vì hàm R(s,a,s′) tổng quát. Nếu tập hành động là rời rạc, tác tử biết trước số lượng hành động và hành động được biểu diễn bởi số nguyên từ 0 đến A 1. | | − Nếu hành động là liên tục, tác tử biết số chiều d của hành động và mỗi hành động là một véc-tơ trong Rd. Vì thông tin môi trường—bao gồm hàm chuyển trạng thái T và hàm phần thưởng R—không được cung cấp cho tác tử, nên hai Thuật toán 8.1 và 8.2 không thể áp dụng được. Trong thiết lập này, mô hình học tăng cường phải đồng thời thực hiện hai nhiệm vụ: khám phá môi trường và khai thác thông tin thu được để ước

<!-- Page 246 -->

<!-- Page 247 -->
## 8.3 HỌC TĂNG CƯỜNG VÀ PHƯƠNG PHÁP HỌC HÀM Q 221 Tuy nhiên, phương pháp này có hai nhược điểm chính: • Sai lệch giữa giá trị thật và xấp xỉ có thể gây sai số lớn trong việc tìm chính sách tối ưu. • Để xấp xỉ chính xác, cần thu thập tập mẫu lớn.

Điều này khó đạt được, đặc biệt trong môi trường không quan sát được toàn phần hoặc có miền hành động liên tục. 8.3.2 Học hàm Q thông qua kinh nghiệm Thay vì phải trải qua bước trung gian là ước lượng hàm chuyển trạng thái T(s,a,s′) và hàm phần thưởng R(s,a,s′), chúng ta có thể cập nhật trực tiếp giá trị V hoặc π dựa trên các mẫu kinh nghiệm (s,a,s′,r). Để làm được điều này, chúng ta tiến hành xấp xỉ giá trị V π(s) mỗi khi nhận được một mẫu kinh nghiệm (s,a,s′,r). Chúng ta có thể viết lại công thức cập nhật giá trị V π(s) từ công thức (8.17) theo cách diễn đạt kì vọng theo các mẫu kinh nghiệm như sau: V π(s) = E [r + γV π(s′)] (8.24) (s,a,s′,r)∼π Hay nói theo một cách khác, giá trị ước lượng x = r +γV π(s′) trên là một ước lượng không lệch của V π(s). Trong trường hợp chúng ta cố định s, và thực hiện hành động a π(. s) để thu được dãy ∼ | kinh nghiệm D = (s,a ,s′ ,r ),(s,a ,s′ ,r ),...,(s,a ,s′ ,r ) . s { 1 1 1 2 2 2 N N N } Với giả thiết là các giá trị V π(s′) đã được biết trước, ta có thể tính i được các giá trị mục tiêu x với i = 1,...,N như sau: i x = r + γV π(s′) i i i

<!-- Page 248 -->

<!-- Page 249 -->
## 8.3 HỌC TĂNG CƯỜNG VÀ PHƯƠNG PHÁP HỌC HÀM Q 223 biết với trạng thái s S.

Tại thời điểm t + 1 ta nhận được kinh ∈ nghiệm (s,a,s′,r) bằng cách thực hiện hành động a = π(. s), giá | trị V π (s) có thể được cập nhật theo công thức: t+1 v = r + γV π(s′) t V π (s) = V π(s) + α(v V π(s)) t+1 t − t Trong đó, giá trị cập nhật v được xem như là giá trị mục tiêu của V π(s). Tham số α là tốc độ học, xác định mức độ điều chỉnh của giá trị ước lượng V π(s) dựa trên sai số giữa dự đoán V π(s) và giá t t trị mới v. Cách tiếp cận này tuy có thể xấp xỉ được giá trị V (s) theo các π mẫu kinh nghiệm nhận được nếu số lượng các mẫu kinh nghiệm đủ nhiều. Tuy nhiên, nếu ta dựa theo Thuật toán lặp giá trị 8.2 thì việc trích ra chính sách cập nhật từ V theo công thức (8.19) còn thiếu dữ kiện là hàm chuyển trạng thái T(s,a,s′) và hàm phần thưởng R(s,a,s′) của môi trường. Do đó, để thực hiên được bước lựa chọn hành động tối ưu tại trạng thái s chúng ta cần cách học thông tin tổng quát hơn. Thay vì xấp xỉ giá trị V π(s), chúng ta sẽ xấp xỉ hàm Qπ(s,a). Theo định nghĩa, hàm Q làm việc trên tập trạng thái và hành động, do đó từ giá trị hiện tại của Qπ(s,a) chúng ta có thể dễ t dàng xác định được giá trị hành động ứng với chính sách hiện tại cũng như cập nhật chính sách mới, tương tự với thuật toán lặp giá trị. Bằng việc sử dụng hàm Qπ(s,a), tại thời điểm t bất kì, chúng t ta có thể lấy ra được giá trị tối ưu và hành động tối ưu nhất tại trạng thái s theo công thức: V π(s) = maxQπ(s,a′) (8.28) t t a′ π (s) = arg maxQπ(s,a′) (8.29) t t a′ Chính sách π được tính theo công thức (8.29) hay được gọi là chính sách tham lam theo hàm Q hoặc gọi tắt là chính sách tham lam.

<!-- Page 250 -->

<!-- Page 251 -->
## 8.3 HỌC TĂNG CƯỜNG VÀ PHƯƠNG PHÁP HỌC HÀM Q 225 tử sẽ luôn có một xác suất nhất định ε > 0 để lựa chọn hành động ngẫu nhiên.

Thuật toán 8.3 Thuật toán SARSA dựa trên chính sách tham lam ε 1: procedure SARSA(α,γ,ε) 2: for all (s,a) S A do ∈ × 3: Khởi tạo Q(s,a) tùy ý 4: end for 5: while chưa đạt điều kiện dừng do 6: Khởi tạo trạng thái ban đầu s 7: Chọn a ε Q(s, ) ∼ − · 8: while s không phải trạng thái kết thúc do 9: Thực hiện hành động a, nhận được phần thưởng r và trạng thái mới s′ 10: Chọn a′ ε Q(s′, ) ∼ − · 11: Ước lượng giá trị mục tiêu: q = r + γQ(s′,a′) 12: Cập nhật: Q(s,a) Q(s,a) + α (q Q(s,a)) ← − 13: s s′, a a′ ← ← 14: end while 15: end while 16: end procedure Kết hợp các công thức (8.30), (8.31), và (8.32), chúng ta có thể xây dựng Thuật toán 8.3. Thuật toán thường có có tên gọi là SARSA vì hàm mục tiêu Q được cập nhật theo bộ giá trị (s,a,r,s′,a′) bao gồm trạng thái hiện tại, hành động hiện tại, phần thưởng nhận được, trạng thái kế tiếp và hành động kế tiếp. Trong phần trình bày ở Thuật toán 8.3, chúng ta bỏ qua tham số t và chỉ sử dụng ký hiệu Q(s,a). Cách tiếp cận này trực tiếp cập nhật hàm Q theo mỗi mẫu kinh nghiệm (s,a,r,s′,a′). Công thức (8.30) có thể được hiểu như là ước lượng giá trị q là giá trị mục tiêu hiện

<!-- Page 252 -->

<!-- Page 253 -->
## 8.4 CÁC THUẬT TOÁN HỌC XẤP XỈ 227 Với đầu vào là cặp giá trị (s,a), giả sử ϕ(s,a) = [x ,x ,...,x ] 1 2 d với x ,x ,...,x là các đặc trưng được lựa chọn phù hợp.

Ở bước 1 2 d học theo thuật toán lặp giá trị, ta có thể mô hình hoá hàm giá trị Q(s,a) bằng một hàm hồi quy tuyến tính Q (s,a) = (f ϕ)(s,a) = w + w x + + w x (8.34) w w 0 1 1 d d ◦ ··· được đặc trưng bởi véc-tơ trọng số w Rd+1 như sau: ∈ w = [w ,w ,w ,...,w ] (8.35) 0 1 2 d trong đó, w ,w ,...,w là các trọng số tuyến tính và w là hệ số 1 2 d 0 tự do. Để cập nhật hàm Q (s,a), chúng ta sẽ định nghĩa hàm mục w tiêu (w) và sử dụng phương pháp Xuống đồi bằng đạo hàm để L cập nhật trọng số w. Dựa trên công thức (8.30), ta có thể viết lại hàm mục tiêu theo mẫu kinh nghiệm (s,a,r,s′,a′) như sau: y = r + γ maxQ (s′,a′) (8.36) w a′ 1 L(w) = [y Q (s,a)]2 (8.37) w 2 − Xem giá trị mục tiêu y là hằng số đối với tham số w, ta có đạo hàm của hàm mục tiêu L(w) theo trọng số w như sau: L(w) = [y Q (s,a)] Q (s,a) (8.38) w w w w ∇ − − ∇ Dựa trên kết quả này, chúng ta có thể áp dụng phương pháp Xuống đồi bằng đạo hàm để cập nhật w. Kết hợp công thức (8.38) với Thuật toán 8.3, ta có được thuật toán SARSA với xấp xỉ hàm giá trị (Thuật toán 8.4). Phương pháp xấp xỉ giá trị được trình bày có thể áp dụng chung cho các phương pháp lặp giá trị và lặp chính sách. Có một chú ý nhỏ là việc sử dụng giá trị mục tiêu để cập nhật trọng số w trong

<!-- Page 254 -->

<!-- Page 255 (Heavy) -->
trong công thức (8.34) bằng một mạng học sâu Q θ . Mạng học sâu Q θ có đầu vào là trạng thái s và có | A | đầu ra tương ứng với các giá trị Q θ ( s, a ) với θ là bộ tham số của mạng học sâu.

Mạng học sâu cho hàm giá trị Q hay thường được viết tắt là DQN (Deep Q-Network). Hình 8.6 mô tả cấu trúc đơn giản của mạng DQN. Trong Hình minh hoạ 8.6, chúng ta có o 0 sẽ là giá trị của mạng Q θ ứng với hành động a 0 và o 1 ứng với hành động a 1 . Không mất tính tổng quát, chúng ta có thể viết gọn lại o a = Q θ ( s, a ) và dựa trên giá trị cụ thể của a để lấy ra o a tương ứng. Ở mỗi bước tương tác với môi trường, khi nhận được trạng thái s , hành động a được chọn theo chính sách ϵ -tham lam dựa trên giá trị o như sau:

<!-- formula-not-decoded -->

Hình 8.6: Cấu trúc cơ bản của DQN

<!-- image -->

Ở bước cập nhật, thay vì chỉ cập nhật trọng số w của hàm hồi quy tuyến tính, chúng ta sẽ cập nhật trọng số θ của toàn bộ mạng học sâu DQN. Về mặt mô hình tính toán, mạng DQN khá gần với

<!-- Page 256 (Heavy) -->
một mạng học sâu hồi quy. Tuy nhiên, việc học hồi quy giá trị Q θ ( s, a ) gặp hai khó khăn chính: sự thiếu ổn định có giá trị mục tiêu và các mẫu dữ liệu có sự tương quan với nhau. Để giải quyết vấn đề này, DQN đưa vào hai kỹ thuật chính là: Hàm mục tiêu cố định và Bộ nhớ đệm :

- Hàm mục tiêu cố định ˆ Q : Hàm mục tiêu ˆ Q θ -( s, a ; ) dùng để tính toán giá trị mục tiêu y trong quá trình huấn luyện mạng Q θ . Ở đây, chúng ta cũng sử dụng mạng học sâu có cấu trúc giống như mạng Q θ . Giả sử tại thời điểm t , tác tử ở trạng thái s , dựa theo công thức (8.39) chọn hành động a và nhận được phần thưởng r và trạng thái tiếp theo s ′ . Giá trị mục tiêu y đối với được tính toán dựa trên giá trị của hàm mục tiêu ˆ Q θ -theo công thức

<!-- formula-not-decoded -->

Dựa trên giá trị mục tiêu y , chúng ta xây dựng được hàm lỗi ứng với tập mẫu kinh nghiệm ( s, a, r, s ′ ) như sau:

<!-- formula-not-decoded -->

Trong quá trình huấn luyện mạng Q θ , trọng số θ -của hàm mục tiêu ˆ Q θ -được giữ cố định trong một khoảng thời gian nhất định và sau đó sẽ được cập nhật lại bằng trọng số θ của mạng Q θ .

- Bộ nhớ đệm B : Để huấn luyện mạng Q θ , chúng ta sử dụng bộ nhớ đệm B được sử dụng để lưu trữ các mẫu kinh nghiệm ( s, a, r, s ′ ) trong quá trình tương tác với môi trường. Tác dụng của bộ nhớ đệm B là để lấy mẫu ngẫu nhiên các mẫu kinh nghiệm ( s, a, r, s ′ ) để huấn luyện mạng Q θ . Kết hợp công thức (8.41) và bộ nhớ đệm B , ta có công thức hàm lỗi tổng quát là

<!-- formula-not-decoded -->

<!-- Page 257 (Heavy) -->
Từ công thức hàm lỗi này, chúng ta có thể sử dụng thuật toán tối ưu hoá theo đạo hàm ngẫu nhiên để cập nhật trọng số θ bằng việc lấy mẫu các kinh nghiệm ( s, a, r, s ′ ) từ bộ nhớ đệm B .

Dựa trên các thành phần chính của mạng DQN, chúng ta có thể xây dựng được thuật toán huấn luyện mạng DQN như sau:

` Thuật toán 8.5 Thuật toán huấn luyện DQN (Huấn luyện mạng DQN với chính sách tham lam ϵ ) 1: Khởi tạo θ và θ -với các trọng số ngẫu nhiên 2: Khởi tạo bộ nhớ đệm B ←∅ 3: for k = 1 , 2 , . . . , do 4: Khởi tạo trạng thái ban đầu s 5: for t = 1 , 2 , . . . , T do 6: Chọn hành động a ∼ ε -Q θ ( s, a ) 7: Thực hiện hành động a , 8: Nhận về phần thưởng r và trạng thái tiếp theo s ′ 9: Lưu trữ ( s, a, r, s ′ ) vào bộ nhớ đệm B 10: end for 11: Lấy mẫu ngẫu nhiên một ( s, a, r, s ′ ) từ bộ nhớ đệm B 12: Tính toán giá trị mục tiêu y theo công thức (8.40) 13: Tính toán hàm lỗi L ( θ ) theo công thức (8.42) 14: Cập nhật θ ← θ -α ∇ θ L ( θ ) 15: Sau K bước, cập nhật θ -← θ 16: end for `

Trong thuật toán trên, việc lựa chọn giá trị của tham số T và K đóng vai trò quan trọng với hiệu suất huấn luyện và độ ổn định của mạng DQN. Trong cấu trúc được mô tả ở Hình 8.6, chúng ta có thể thấy rằng mạng DQN có dạng một mạng học sâu nhiều lớp. Với các môi trường khác nhau, chúng ta có thể tích hợp thêm các lớp học sâu tích chập nếu cần trích chọn đặc trưng theo không gian của trạng thái đầu vào hoặc là lớp học sâu hồi quy nếu chúng ta muốn tích hợp thêm các đặc trưng theo thời gian. Mặc dù đã có

<!-- Page 258 (Heavy) -->
thể giải nhiều bài toán giả lập phức tạp như chơi game Atari, mạng DQN còn một số hạn chế, bao gồm:

- Mạng DQN không thể làm việc với không gian hành động liên tục, mà chỉ có thể làm việc với không gian hành động rời rạc.
- Việc huấn luyện mạng DQN có thể không ổn định nếu lựa chọn được các tham số phù hợp.
- Khó khăn trong việc cân bằng giữa quá trình tìm hiểu môi trường và tối ưu.

## 8.5.2 Phương pháp Xuống đồi bằng đạo hàm của chính sách

Trong phần này, chúng ta tiếp tục mở rộng các tiếp cận trong học tăng cường bằng cách tối ưu trực tiếp trên chính sách hiện tại thay vì dùng qua giá trị trung gian như hàm V hay hàm Q . Chúng ta đã biết rằng, trong học tăng cường, chính sách là một hàm ánh xạ từ trạng thái s về tập hành động A . Hàm ánh xạ này có thể đặc trưng cho một chính sách tất định theo công thức (8.1) hoặc là chính sách ngẫu nhiên theo công thức (8.2). Để có thể thu thập thông tin hiệu quả từ môi trường, chính sách ngẫu nhiên thường được sử dụng. Giả sử, tập các hành động A là hữu hạn, chính sách ngẫu nhiên có thể được biểu diễn dưới dạng một hàm xác suất π ( a | s ) được mô hình hoá bằng mạng học sâu như sau:

<!-- formula-not-decoded -->

trong đó o = π θ ( s ) là véc-tơ xác suất với | A | chiều. Chúng ta để ý là cách mô hình hoá này tương tự với việc học một mô hình học sâu phân lớp có số lớp bằng với số hành động có thể trong tập A . Để thể hiện tính ngẫu nhiên, hành động a được chọn theo xác suất π ( a | s ) , được kí hiệu là

<!-- formula-not-decoded -->

<!-- Page 259 (Heavy) -->
trong đó xác suất tương ứng với hành động a được kí hiệu là π θ ( a | s ) . Sử dụng Định nghĩa 8.7 về giá trị của trạng thái theo chính sách, chúng ta có định nghĩa về hàm mục tiêu của chính sách π θ như sau:

Định nghĩa 8.13 (Hàm mục tiêu của chính sách π θ ) . Hàm mục tiêu của chính sách π θ theo tham số θ được định nghĩa như sau:

<!-- formula-not-decoded -->

với τ ∼ π θ ( s ) là một chuỗi các trạng thái và hành động được sinh ra từ chính sách π θ khi bắt đầu từ trạng thái s .

Với định nghĩa này, chúng ta cần tìm θ ∗ để J ( θ ∗ ) đạt giá trị cực đại. Điểm khác biệt so với các phương pháp lặp chính sách đã trình bày là chúng ta trực tiếp tối ưu hoá trên chính sách π θ thay vì tối ưu hoá qua một hàm trung gian thể hiện giá trị V hay Q . Tuy nhiên, việc sử dụng trực tiếp Định nghĩa 8.13 trên để tối ưu hoá tham số θ là không khả thi vì rất khó để ước lượng ∇ θ J ( θ ) . Thay vào đó, chúng ta có thể viết lại định nghĩa trên thông qua giá hàm Q π θ như sau. Chúng ta bắt đầu bằng việc đưa ra định nghĩa về phân bố dừng d π θ ( s ) của các trạng thái trong quá trình đi theo chính sách π θ .

Định nghĩa 8.14 (Phân bố dừng của các trạng thái) . Phân bố dừng d π θ của các trạng thái trong quá trình đi theo chính sách π θ được định nghĩa là phân bố thoã mãn điều kiện:

<!-- formula-not-decoded -->

Trong phần trình bày này, chúng ta xét trường hợp đơn giản là tập trạng thái S và tập hành động A là rời rạc. Thêm vào đó, với

<!-- Page 260 (Heavy) -->
một chiến thuật π θ tuỳ ý, thì phân bố dừng d π θ luôn tồn tại và duy nhất. Sử dụng Định nghĩa 8.14, chúng ta có thể viết lại giá trị hàm mục tiêu V π θ ứng với một chính sách π θ như sau:

Định nghĩa 8.15 (Hàm mục tiêu của chính sách theo tham số θ ) . Giả sử d π θ là phân bố dừng của các trạng thái trong quá trình đi theo chính sách π θ , hàm mục tiêu J ( θ ) của chính sách π θ được định nghĩa như sau:

<!-- formula-not-decoded -->

Để ý rằng, hàm mục tiêu J ( θ ) được định nghĩa như một giá trị kì vọng của hàm Q π θ ( s, a ) và xác suất π θ ( a | s ) . Chúng ta có thể sử dụng biểu diễn này để tính toán giá trị đạo hàm của hàm mục tiêu J ( θ ) theo tham số θ theo Định lý đạo hàm chính sách.

Định lý 8.16 (Định lý đạo hàm chính sách) . Giả sử hàm mục tiệu J ( θ ) được định nghĩa như ở Định nghĩa 8.15, thì đạo hàm của J ( θ ) theo tham số θ có thể được xấp xỉ như sau:

<!-- formula-not-decoded -->

Chứng minh: Sử dụng định nghĩa hàm mục tiêu J ( θ ) theo Định nghĩa 8.15, lấy đạo hàm theo θ ở hai vế ta có:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 261 (Heavy) -->
## Thuật toán 8.6 Thuật toán tối ưu chính sách (Policy Gradient)

1: procedure PolicyGradient ( α, γ )

2: Khởi tạo tham số θ ngẫu nhiên cho chính sách π θ

3: while chưa đạt điều kiện dừng do

4: Lấy một quỹ đạo theo π θ :

<!-- formula-not-decoded -->

5: for t = 1 to T do

6: Tính tổng phần thưởng trả về từ bước t

<!-- formula-not-decoded -->

7: Cập nhật tham số:

<!-- formula-not-decoded -->

8: end for

9: end while

10: end procedure

## 8.5.3 Phương pháp tối ưu chính sách

Dựa trên Định lý 8.16 ta có thể tính gần đúng ∇ θ J ( θ ) theo mẫu các kinh nghiệm thu được bằng thuật toán xấp xỉ Monte-Carlo.

<!-- formula-not-decoded -->

trong đó, G t = ∑ T k = t γ k -t r k là giá trị trả về tính theo các trạng thái ở tương lai đối với mỗi mẫu kinh nghiệm thu được theo một đường đi τ nào đó. Sử dụng quỹ đạo được lựa chọn theo phương pháp lấy mẫu Monte-Carlo, ta có ước lượng không chệch của đạo hàm theo θ . Ta có mô tả thuật toán tối ưu chính sách với phương pháp lấy mẫu Monte-Carlo như trong Thuật toán 8.6.

:

<!-- Page 262 -->

<!-- Page 263 -->
## 8.6 TÌNH HUỐNG ÁP DỤNG:

SỬ DỤNG MẠNG DQN ĐỂ ĐIỀU KHIỂN THĂNG BẰNG 237 8.6.2 Các bước triển khai Để giải quyết bài toán này, chúng ta sẽ sử dụng mạng DQN để học chính sách tối ưu cho bài toán điều khiển thăng bằng. Các bước triển khai chính bao gồm: • Khởi tạo môi trường mô phỏng: Trong các bài toán học tăng cường, dữ liệu không được cung cấp sẵn mà được thu thập trong quá trình tác tử tương tác với môi trường. Trong trường hợp này, tác tử sẽ điều khiển thông qua hành động và nhận về các tập dữ liệu dưới dạng (s,a,s′,r). Dữ liệu thu thập được sẽ được lưu trữ trong bộ đệm để huấn luyện mạng DQN. • Khai báo cấu trúc mạng DQN: Trong bài toán này chúng ta sẽ huấn luyện mạng học sâu DQN có đầu vào là 4 giá trị ứng với trạng thái hiện tại và đầu ra là hai giá trị ứng với phần thưởng nhận được khi thực hiện một trong hai hành động di chuyển sang trái/phải. Chính sách tối ưu được học một cách gián tiếp thông qua hàm học sâu DQN với cấu trúc có 3 lớp. Trong đó, hai lớp ẩn được sử dụng hàm kích hoạt ReLU để ánh xạ trạng thái đầu vào thành các giá trị miền ẩn. Lớp thứ 3 là lớp đầu ra với kích thước bằng số lượng hành động có thể thực hiện tương tự như mô tả ở Hình 8.6. Để có thể khám phá môi trường một cách hiệu quả, hành động sẽ được lấy theo thuật toán tham lam của mạng Q. Chúng ta cũng có khai báo tương tự cho mạng mục ˆ tiêu Q. • Huấn luyện mạng Q: Để huấn luyện mạng Q, trước tiên ta cần khởi tạo các tham số cần thiết cho quá trình tương tác với môi trường và quá trình huấn luyện. Ngoài các tham số tương tự như huấn luyện các mạng học sâu cơ bản, chúng ta có thêm một số tham số như: tham số ε, tham số K. Để cải thiện tính khám phá của mạng, chúng ta sẽ sử dụng phương pháp giảm dần tham số ε thông qua giá trị lớn nhất, ứng với các vòng lặp khởi động, và

<!-- Page 264 -->

<!-- Page 265 -->
## 8.7 TỔNG KẾT CHƯƠNG 239 thể tìm hiểu sâu hơn các khía cạnh lý thuyết và ứng dụng của học tăng cường qua các tài liệu liên quan [8].

Bài tập 1. Nêu các điểm khác biệt chính của học tăng cường và học giám sát. Dưới những điều kiện nào thì nên mô hình bài toán thực tế dưới dạng học tăng cường? 2. Dựa theo chứng minh tính hội tụ của thuật toán lặp theo giá trị, chứng minh tính hội tụ của thuật toán lặp theo chính sách trong trường hợp tập trạng thái và tập hành động là hữu hạn và chính sách π là chính sách xác định. 3. [Tìm hiểu] Nếu chúng ta sử dụng chính sách π là chính sách ngẫu nhiên, thì tính hội tụ của thuật toán lặp theo chính sách có còn đúng không? 4. Dựa trên các bước cơ bản của thuật toán quy hoạch động lặp theo giá trị, đề xuất phương pháp quy hoạch động để tính giá trị tối ưu của hàm Q. Đánh giá độ phức tạp của thuật toán tìm được. 5. [Tìm hiểu] Trong thuật toán DQN, chính sách khai phá đóng vai trò quan trọng để thu thập thông tin từ môi trường thông qua kinh nghiệm. Nêu một số chính sách khai phá cho thuật toán học theo mạng học sâu DQN. 6. [Lập trình] Dựa trên phần trình bày trong mục Tình huống áp dụng, sử dụng thuật toán đạo hàm theo chính sách giải bài toán CartPole với mạng học sâu có 2 lớp, số lớp ẩn là 128 ở mỗi lớp. So sánh về độ tốt và số lượng mẫu kinh nghiệm cần thiết để học được chính sách tối ưu giữa thuật toán đạo hàm theo chính sách và thuật toán huấn luyện mạng DQN.

<!-- Page 266 -->

<!-- Page 267 -->
Tài liệu tham khảo [1] Bellman, R. E., Dynamic programming, Princeton University Press, 1957. [2] Howard, R. A., Dynamic programming and Markov processes, MIT Press, 1960. [3] Sutton, R. S., Learning to predict by the methods of temporal differences, Machine Learning, vol. 3, no. 1, pp. 9–44, 1988. [4] Mnih, V., Kavukcuoglu, K., Silver, D., Rusu, A. A., Veness, J., Bellemare, M. G., Graves, A., et al., Human-level control through deep reinforcement learning, Nature, vol. 518, no. 7540, pp. 529–533, 2015. [5] Lillicrap, T. P., Hunt, J. J., Pritzel, A., Heess, N., Erez, T., Tassa, Y., Silver, D., and Wierstra, D., Continuous control with deep reinforcement learning, arXiv preprint arXiv:1509.02971, 2015. [6] Schulman, J., Wolski, F., Dhariwal, P., Radford, A., and Klimov, O., Proximal policy optimization algorithms, arXiv preprint arXiv:1707.06347, 2017.

<!-- Page 268 -->
242 TÀI LIỆU THAM KHẢO [7] Silver, D., Huang, A., Maddison, C. J., Guez, A., Sifre, L., Van Den Driessche, G., Schrittwieser, J., et al., Mastering the game of Go with deep neural networks and tree search, Nature, vol. 529, no. 7587, pp. 484–489, 2016. [8] Sutton, Richard S. and Barto, Andrew G., Reinforcement learning: An introduction, MIT Press, 2018.

<!-- Page 269 -->
# Chương 9 Học kết hợp Chương 9 giới thiệu Học kết hợp (Ensemble Learning) – một hướng tiếp cận mạnh mẽ trong Học máy nhằm nâng cao độ chính xác, khả năng tổng quát hóa và tính ổn định của mô hình.

Học kết hợp xây dựng một tập các mô hình con và sử dụng một hàm kết hợp để đưa ra quyết định cuối cùng F H(x) = M (x),M (x),...,M (x) . (9.1) 1 2 K F{ } Trong đó, M (x) là các mô hình con được huấn luyện độc lập hoặc k theo thứ tự. Hai kỹ thuật học kết hợp phổ biến là Bagging và Tăng cường (Boosting). Bagging sử dụng lấy mẫu ngẫu nhiên có hoàn lại để tạo các mô hình con, điển hình là Rừng ngẫu nhiên (Random Forest). Boosting tạo mô hình con theo trình tự, trong đó mỗi mô hình kế tiếp tập trung vào các mẫu bị dự đoán sai trước đó. Các thuật toán nổi bật gồm AdaBoost, Tăng cường bằng đạo hàm (Gradient Boosting) và XGBoost.

<!-- Page 270 -->

<!-- Page 271 (Heavy) -->
Hình 9.1: Học kết hợp

<!-- image -->

- Bài toán phân lớp C lớp: M k ( x ) ∈ { 1 , . . . , C } .

<!-- formula-not-decoded -->

- Bài toán hồi quy: M k ( x ) ∈ R .

<!-- formula-not-decoded -->

Một trường hợp đặc biệt của các công thức trên là khi α k = 1 với mọi k , tức là, các mô hình quan trọng như nhau. Khi đó, mô hình kết hợp đưa ra quyết định giống như bỏ phiếu theo đa số đối với bài toán phân lớp và lấy trung bình cộng đối với bài toán hồi quy.

## 9.2 Phương pháp Bagging

## 9.2.1 Tổng quan phương pháp

Phương pháp tổng hợp mô hình qua lấy mẫu ngẫu nhiên, còn gọi là Bootstrap Aggregating hay Bagging , là kỹ thuật kết hợp nhiều mô hình cơ sở, được huấn luyện bằng cùng một thuật toán học máy A nhưng trên các tập dữ liệu khác nhau. Các tập dữ liệu này được

<!-- Page 272 (Heavy) -->
tạo ra bằng cách lấy mẫu ngẫu nhiên có hoàn lại từ tập dữ liệu gốc, theo phương pháp bootstrap .

Phương pháp lấy mẫu ngẫu nhiên có hoàn lại ( bootstrap ) là một kỹ thuật thống kê dùng để ước lượng các đặc trưng của phân phối dữ liệu bằng cách lấy mẫu ngẫu nhiên có hoàn lại từ tập dữ liệu gốc. Ưu điểm nổi bật của phương pháp này là có thể ước lượng khoảng tin cậy cho các tham số mô hình mà không cần giả định phân phối xác suất cụ thể của dữ liệu. Lược đồ bootstrap được mô tả trong Thuật toán 9.1, với ̂ θ = ̂ θ ( D ) là một thống kê bất kỳ được tính từ dữ liệu D .

| Thuật toán 9.1 Phương pháp Bootstrap   | Thuật toán 9.1 Phương pháp Bootstrap                                              | |----------------------------------------|-----------------------------------------------------------------------------------| | 1:                                     | procedure Boostrap ( D = { x 1 , . . . ,x n } ,S,B )                              | | 2:                                     | for b = 1 to B do                                                                 | | 3:                                     | Lấy mẫu ngẫu nhiên có hoàn lại D b = { x b 1 , . . . ,x bn } từ tập dữ liệu gốc D | | 4:                                     | Tính thống kê ̂ θ b = ̂ θ ( D b )                                                 | | 5:                                     | end for                                                                           | | 6:                                     | Ước lượng điểm θ = 1 B ∑ B b =1 ̂ θ b                                             | | 7:                                     | Tính độ lệch chuẩn σ = √ 1 B - 1 ∑ B b =1 ( ̂ θ b - θ ) 2                         | | 8:                                     | Tính khoảng tin cậy 95% CI = [ θ - 1 . 96 · σ, θ +1 . 96 · σ ]                    | | 9:                                     | end procedure                                                                     |

Người ta chứng minh được rằng, dưới đây cho thấy khi kích thước mẫu đủ lớn và thống kê ̂ θ ( · ) khả vi thì phân phối của ước lượng bootstrap hội tụ về phân phối của ước lượng thống kê gốc.

Phương pháp Bagging (Hình 9.2) sử dụng phương pháp Bootstrap để tạo ra các bộ dữ liệu huấn luyện khác nhau D k từ bộ dữ liệu gốc D = { ( x i , y i ) } , i = 1 , 2 , . . . , n bằng cách lấy mẫu ngẫu nhiên có hoàn lại. Sau đó, mỗi bộ dữ liệu D k được sử dụng để huấn luyện một mô hình con M k ( x ) = A ( D k ) bằng cách sử dụng thuật toán học máy A . Cuối cùng, các mô hình con phối hợp với nhau

<!-- Page 273 (Heavy) -->
Hình 9.2: Phương pháp Bagging

<!-- image -->

để đưa ra quyết định cuối cùng. Lược đồ chung của phương pháp Bagging được mô tả trong Thuật toán 9.2.

` Thuật toán 9.2 Phương pháp Bagging 1: procedure TrainBagging ( A , D, K ) 2: for k = 1 to K do 3: Lấy mẫu bootstrap D k từ tập dữ liệu gốc D 4: Huấn luyện mô hình con: M k ( x ) ←A ( D k ) 5: Gán trọng số: α k ← 1 6: end for 7: return M k ( x ) , α k , k = 1 , . . . , K 8: end procedure `

Như vậy phương pháp Bagging sử dụng trọng số α k = 1 cho mọi mô hình huấn luyện được.

Các phương pháp bagging tuân thủ lược đồ 9.2 nhưng có thể khác nhau ở các bước

- Phép lấy mẫu ngẫu nhiên: việc lấy mẫu có thể tiến hành với cả

<!-- Page 274 -->

<!-- Page 275 (Heavy) -->
## Thuật toán 9.3 Huấn luyện mô hình Rừng ngẫu nhiên

- 1: procedure TrainRF ( D,K,m )
- 2: for k = 1 to K do
- 3: Lấy mẫu ngẫu nhiên có hoàn lại từ D để tạo tập dữ liệu con D k , với | D k | = n
- 4: Huấn luyện cây quyết định M k ( x ) trên D k , sử dụng thuật toán cây quyết định (ví dụ: ID3, C4.5 hoặc CART), với mỗi nút phân chia chọn ngẫu nhiên m đặc trưng từ tổng số đặc trưng
- 5: Gán trọng số α k ← 1
- 6: end for
- 7: return M k ( x ) , α k , k = 1 , . . . , K
- 8: end procedure

## Thuật toán 9.4 Dự đoán với Rừng ngẫu nhiên

- 1: procedure EvalRF ( M k , α k , x )
- 2: for all y ∈ Y do
- 4: end for
- 3: score [ y ] ← ∑ K k =1 α k · I [ M k ( x ) = y ]
- 5: return H ( x ) ← arg max y score [ y ]
- 6: end procedure

định đúng thì mô hình kết hợp vẫn cho kết quả đúng. Trên thực tế, để mô hình Rừng ngẫu nhiên cho kết quả tốt ta cần có (i) các đặc trưng có liên quan đến nhiệm vụ cần giải quyết và (ii) các cây quyết định được xây dựng một cách ngẫu nhiên và có tương quan yếu.

Định lý 9.1. Nếu mỗi cây M k ( x ) có phương sai Var ( M k ( x )) = σ 2 và độ tương quan trung bình giữa các cây là ρ , thì phương sai của mô hình kết hợp H ( x ) = 1 K ∑ K k =1 M k ( x ) (trong bài toán hồi quy) được cho bởi:

<!-- formula-not-decoded -->

Khi K →∞ , nếu ρ nhỏ (do tính đa dạng của các cây), thì Var ( H ( x )) → ρσ 2 , nhỏ hơn σ 2 .

<!-- Page 276 (Heavy) -->
Chứng minh: Gọi H ( x ) = 1 K ∑ K k =1 M k ( x ) là mô hình kết hợp trung bình từ K mô hình cơ sở M k ( x ) . Ta cần tính phương sai của H ( x ) :

<!-- formula-not-decoded -->

Chia tổng trên thành hai phần:

- Trường hợp i = j : Có K số hạng Var ( M k ) = σ 2 .
- ·
- Trường hợp i = j : Có K ( K -1) số hạng Cov ( M i , M j ) = ρσ 2 .

Suy ra

khi K →∞ .

Nếu ρ ≪ 1 , tức các mô hình cơ sở có tính đa dạng cao, thì phương sai của mô hình kết hợp sẽ nhỏ hơn nhiều so với phương sai của từng mô hình đơn lẻ. □

Một điểm thú vị của mô hình Rừng ngẫu nhiên là nó có thể được sử dụng để ước lượng lỗi tổng quát hóa mà không cần một tập kiểm tra riêng biệt. Điều này được thực hiện thông qua lỗi ngoài túi (Out-of-Bag hay OOB). Cụ thể, lỗi OOB được tính như sau:

- Gọi F i ⊂ { 1 , 2 , . . . , K } là tập hợp các chỉ số k mà mẫu ( x i , y i ) / ∈ D k .

̸

<!-- formula-not-decoded -->

<!-- Page 277 -->
## 9.3 PHƯƠNG PHÁP BOOSTING 251 • Với mỗi mẫu (x ,y ) trong tập huấn luyện D, ta tính i i 1 (cid:88) H (x ) = M (x ). (9.5) OOB i k i i |F | k∈Fi Tức là kết hợp các mô hình M không được huấn luyện bằng k mẫu (x ,y ). i i • Cuối cùng, ta tính lỗi OOB bằng cách n 1 (cid:88) err = L(H (x ),y ), (9.6) OOB OOB i i n i=1 Mỗi mẫu trong tập huấn luyện D có xác suất khoảng (1 − 1/n)n 1/e 0.368 không được chọn vào một tập dữ liệu Boot- ≈ ≈ strap D .

Do đó sẽ có khoảng 36,8% mẫu không được chọn vào D . k k Tận dụng điều này, mô hình Rừng ngẫu nhiên có thể ước lượng lỗi tổng quát hóa mà không cần một tập kiểm tra riêng biệt. Có thể chứng minh được lỗi err là một ước lượng không OOB chệch của kì vọng lỗi err (H(x)). P 9.3 Phương pháp Boosting Khác với Bagging coi các mô hình con độ quan trọng như nhau, phương pháp Tăng cường (Boosting) kết hợp các mô hình học máy bằng cách lần lượt huấn luyện các mô hình dựa trên điểm yếu của các mô hình được huấn luyện trước đó. Có hai lược đồ Tăng cường hay được sử dụng nhất là AdaBoost và Tăng cường bằng đạo hàm (Gradient Boosting). Trong mục này, chúng ta cùng tìm hiểu phương pháp AdaBoost. Đầu tiên, xét bài toán phân lớp nhị phân = 1 . Ý tưởng Y {± } chính của phương pháp AdaBoost là lần lượt xây dựng các mô hình phân lớp M (x),k = 1,2,... dựa trên bộ dữ liệu D gồm các mẫu k k

<!-- Page 278 (Heavy) -->
Hình 9.3: Phương pháp AdaBoost

<!-- image -->

dữ liệu trong D = { ( x i , y i ) } , i = 1 , 2 , . . . , n nhưng mỗi mẫu ( x i , y i ) có độ quan trọng w k ( i ) được xác định từ điểm yếu của các mô hình học máy trước đó (Hình 9.3).

Ở bước khởi tạo, trọng số các mẫu dữ liệu bằng nhau và bằng 1 n với n là số lượng mẫu dữ liệu trong tập huấn luyện:

<!-- formula-not-decoded -->

Ta dùng bộ trọng số này để huấn luyện mô hình M 1 ( x ) sao cho tỉ lệ lỗi sau khi huấn luyện là nhỏ nhất có thể được, được mô tả bằng công thức tính ϵ 1 :

̸

<!-- formula-not-decoded -->

Phương pháp AdaBoost sau đó cập nhật lại trọng số w 2 ( i ) bằng cách tăng trọng số cho các mẫu dữ liệu bị M 1 ( x ) dự đoán sai và giảm trọng số cho các mẫu dữ liệu được M 1 ( x ) đoán đúng rồi chuẩn

<!-- Page 279 -->
## 9.3 PHƯƠNG PHÁP BOOSTING 253 hoá để tổng trọng số bằng 1. w (i) = w (i)e−α1yiM1(xi) (9.9) (cid:101)2 1 w (i) (cid:101)2 w (i) = (9.10) 2 (cid:80)n w (i′) i′=1 (cid:101)2 với hệ số α được xác định bởi công thức 1 1 1 ϵ 1 α = ln − (9.11) 1 2 ϵ 1 Công thức (9.11) trên cho thấy, khi M (x) tốt hơn hàm phân lớp 1 ngẫu nhiên một chút (tức là 1 ϵ > 0,5) thì α sẽ là một số dương. 1 1 − Như vậy, trọng số của các mẫu dữ liệu mà M (x) đoán sai sẽ được 1 nhân với một đại lượng eα1 > 1 còn trọng số các mẫu dữ liệu được đoán đúng sẽ được nhân với một đại lượng e−α1 < 1.

Ta lại huấn luyện mô hình phân lớp tiếp theo M (x) để tối thiểu hoá tỉ lệ lỗi 2 n (cid:88) ϵ = w (i)I[M (x ) = y ] (9.12) 2 2 2 i i ̸ i=1 và phương pháp AdaBoost tiếp tục cho đến khi đạt số lượng mô hình phân lớp K cho trước hoặc khi một hệ số α < 0 (Thuật toán 9.5). k Ta có Định lý 9.2 sau đây về cận trên tỉ lệ lỗi huấn luyện của AdaBoost. Định lý 9.2 (Cận trên tỉ lệ lỗi huấn luyện của AdaBoost). Thuật toán 9.5 cho mô hình phân lớp H(x) với tỉ lệ lỗi huấn luyện thoả mãn K K (cid:113) (cid:89) (cid:112) (cid:89) err (H) 4ϵ (1 ϵ ) = 1 4γ2. D ≤ k − k − k k=1 k=1 Trong đó ϵ = (cid:80)n w (i)I[M (x ) = y ] < 1 là tỉ lệ lỗi của mô k i=1 k k i ̸ i 2 hình cơ sở thứ k và γ = 1 ϵ . k 2 − k

<!-- Page 280 -->

<!-- Page 281 -->
## 9.3 PHƯƠNG PHÁP BOOSTING 255 Chứng minh:

Đầu tiên, xuất phát từ công thức ước lượng trọng số của mẫu dữ liệu tại bước k + 1 w (i)e−α k yiM k (xi) K w (i) = K+1 Z k 1 (cid:89) K e−α k yiM k (xi) = n Z k k=1 (cid:32) (cid:33)−1 (cid:40) (cid:41) K K 1 (cid:89) (cid:88) = Z exp y α M (x ) k i k k i n − k=1 k=1 Nếu H(x ) = y , tức là H(x) phân lớp sai trên mẫu dữ liệu i i ̸ (x ,y ) thì theo định nghĩa của H(x), ta có i i K (cid:88) y α M (x ) < 0 i k k i k=1 Như vậy ta luôn có cận trên của lỗi là (cid:40) (cid:41) K (cid:88) I[H(x ) = y ] exp y α M (x ) i i i k k i ̸ ≤ − k=1 (cid:40) (cid:41) n n K 1 (cid:88) 1 (cid:88) (cid:88) err (H) = I[H(x ) = y ] exp y α M (x ) D i i i k k i n ̸ ≤ n − i=1 i=1 k=1 K n (cid:89) (cid:88) = Z w (i) k K+1 k=1 i=1 K (cid:89) = Z k k=1 Dễ thấy Z = ϵ eα k + (1 ϵ )e−α k k k k − Chọn α để tối thiểu hoá Z , lấy đạo hàm của Z đặt bằng 0 để k k k tìm cực trị ϵ eα k (1 ϵ )e−α k = 0. k k − −

<!-- Page 282 -->

<!-- Page 283 -->
## 9.4 TĂNG CƯỜNG BẰNG ĐẠO HÀM 257 Thuật toán 9.7 Phương pháp SAMME cho phân lớp C lớp 1: procedure TrainAdaBoostSAMME( ,D,K,C) A 2: for i = 1 to n do 3: w (i) 1 1 ← n 4: end for 5: for k = 1 to K do 6:

Huấn luyện mô hình M (D,w ) k k 7: Tính lỗi: ϵ (cid:80)n w (i) ←IA [M (x ) = y ] k ← i=1 k · k i ̸ i 8: Tính trọng số mô hình: (cid:18) (cid:19) (C 1)(1 ϵ ) k α ln − − k ← ϵ k 9: if α < 0 then k 10: K k 1; break ← − 11: end if 12: for i = 1 to n do 13: w (cid:101)k (i) w k (i) eα k ·I[yi̸=M k (xi)] ← · 14: end for 15: Z (cid:80)n w (i) k ← i=1 (cid:101)k 16: for i = 1 to n do 17: w (i) w (cid:101)k (i) k+1 ← Z k 18: end for 19: end for 20: return M ,α với k = 1,...,K k k 21: end procedure Thuật toán 9.8 Dự đoán với SAMME (AdaBoost đa lớp) 1: procedure EvalAdaBoostSAMME(M ,α ,x,C) k k 2: for y = 1 to C do 3: score[y] (cid:80)K α I[y = M (x)] ← k=1 k · k 4: end for 5: return H(x) arg maxC score[y] ← y=1 6: end procedure

<!-- Page 284 (Heavy) -->
<!-- image -->

Huấn luyện

xấp xỉ lỗi

Hình 9.4: Phương pháp Tăng cường bằng đạo hàm

mãn bài toán tối ưu, được mô tả như sau:

<!-- formula-not-decoded -->

Sau đó, lần lượt tìm các mô hình H 1 ( x ) , H 2 ( x ) , . . . , H K ( x ) có hiệu suất tăng dần bằng bài toán tối ưu theo công thức (9.14)

<!-- formula-not-decoded -->

Tức là tại bước thứ k , ta tìm mô hình M k trong không gian các mô hình cơ sở H sao cho khi cộng thêm M k vào mô hình H k -1 ở bước trước thì tổng số lỗi là nhỏ nhất.

## 9.4.1 Tăng cường bằng đạo hàm bậc 1

Đặt u i = H k -1 ( x i ) , i = 1 , . . . , n và v i = M k ( x i ) rồi xấp xỉ hàm lỗi L ( u i + v i , y i ) bằng khai triển Taylor bậc nhất quanh u i , bài toán tối ưu trên trở thành

<!-- formula-not-decoded -->

Do đó, ta chọn M k theo hướng ngược hướng đạo hàm của hàm lỗi trên. Tức là chọn M k sao cho điều kiện sau được thỏa mãn:

<!-- formula-not-decoded -->

Tính lỗi

<!-- Page 285 -->
## 9.4 TĂNG CƯỜNG BẰNG ĐẠO HÀM 259 Đại lượng r được gọi là phần dư của mẫu dữ liệu thứ i tại bước ki k.

Đây chính là bài toán hồi quy với đầu vào là các mẫu dữ liệu x i và đầu ra là các phần dư r . ki Sau đó ta tìm kiếm hằng số α để tối ưu tổng số lỗi sau k (cid:40) (cid:41) n (cid:88) α = arg min L(H (x ) + αM (x ),y ) . (9.17) k k−1 i k i i α i=1 Đây là bài toán tối ưu một biến nên dễ dàng giải hơn. Lược đồ tổng quát của phương pháp Tăng cường bằng đạo hàm bậc 1 như liệt kê trong Thuật toán 9.9. Thuật toán 9.9 Phương pháp Tăng cường bằng đạo hàm bậc 1 (Gradient Boosting) 1: procedure TrainGradientBoost( ,D = (x ,y ) n ,K) A { i i }i=1 2: Đặt M (x) 1 0 3: Tìm α a ← rg min (cid:80)n L(α,y ) 0 ← α i=1 i 4: H (x) α 0 0 ← 5: for k = 1 to K do 6: for i = 1 to n do (cid:12) 7: r ∂L(y (cid:98) ,yi)(cid:12) ki ← − ∂y (cid:98) (cid:12) y (cid:98) =H k−1 (xi) 8: end for 9: Tạo tập dữ liệu huấn luyện mới: D = (x ,r ) n k { i ki }i=1 10: Huấn luyện mô hình hồi quy: M (D ) k k 11: Tìm α arg min (cid:80)n L(H (x ← ) A + αM (x ),y ) k ← α i=1 k−1 i k i i 12: Cập nhật mô hình tổng: H (x) H (x) + α M (x) k k−1 k k ← 13: end for 14: return M ,α với k = 0,...,K k k 15: end procedure 9.4.2 Tăng cường bằng đạo hàm bậc 2 Bên cạnh việc sử dụng đạo hàm bậc một như trình bày ở công thức (9.14), chúng ta có thể sử dụng đạo hàm bậc hai của hàm lỗi để cải

<!-- Page 286 (Heavy) -->
## Thuật toán 9.10 Dự đoán với Tăng cường bằng đạo hàm bậc 1

1: procedure EvalGradientBoost ( M k , α k , x )

3: return H ( x )

2: H ( x ) ← ∑ K k =0 α k M k ( x )

4: end procedure

thiện mô hình kết hợp. Phương pháp này được gọi là Tăng cường bằng đạo hàm bậc 2 (Newton boosting).

Cụ thể, ta khai triển hàm lỗi L ( ̂ y, y ) theo khai triển Taylor bậc hai quanh u i như sau:

<!-- formula-not-decoded -->

với

<!-- formula-not-decoded -->

Để cực tiểu hàm lỗi này, ta cần chọn v i sao cho

<!-- formula-not-decoded -->

và trọng số của mẫu dữ liệu thứ i này chính là w ki .

Tăng cường bằng đạo hàm bậc 2 cải tiến Boosting bằng đạo hàm bậc 1 bằng cách tìm mô hình M k ( x ) cho bài toán hồi quy với bộ dữ liệu có trọng số D k = { ( x i , r ki / w ki ) } , trong đó mẫu dữ liệu thứ i có trọng số là w ki , chính là đạo hàm bậc 2 của hàm lỗi theo công thức (9.18). Tăng cường bằng đạo hàm bậc 2 tận dụng cả đạo hàm bậc hai để xác định trọng số của từng mẫu, do đó, thường hội tụ nhanh hơn nhưng chi phí tính toán cao hơn vì phải ước lượng

<!-- Page 287 (Heavy) -->
đạo hàm bậc hai. Tăng cường bằng đạo hàm bậc 1 đơn giản hơn và phổ biến hơn trong thực tế vì dễ triển khai và mở rộng.

` Thuật toán 9.11 Tăng cường bằng đạo hàm bậc 2 1: procedure TrainNewtonBoost ( A , D = { ( x i , y i ) } n i =1 , K ) 2: Đặt M 0 ( x ) ← 1 3: Tìm α 0 ← arg min α ∑ n i =1 L ( α, y i ) 4: H 0 ( x ) ← α 0 5: for k = 1 to K do 6: for i = 1 to n do 7: r ki ←-∂L ( ̂ y,y i ) ∂ ̂ y ∣ ∣ ∣ ̂ y = H k -1 ( x i ) 8: w ki ← ∂ 2 L ( ̂ y,y i ) ∂ ̂ y 2 ∣ ∣ ∣ ̂ y = H k -1 ( x i ) 9: end for 10: Tạo tập dữ liệu huấn luyện mới: D k = { ( x i , r ki / w ki ) } n i =1 11: Huấn luyện mô hình hồi quy: M k ←A ( D k , w k ) 12: Tìm α k ← arg min α ∑ n i =1 L ( H k -1 ( x i ) + αM k ( x i ) , y i ) 13: Cập nhật mô hình tổng: H k ( x ) ← H k -1 ( x ) + α k M k ( x ) 14: end for 15: return M k , α k với k = 0 , . . . , K 16: end procedure `

## 9.5 Tình huống áp dụng:

XGBoost

XGBoost xây dựng mô hình bằng cách kết hợp nhiều cây quyết định, mỗi cây mới được xây dựng để sửa các sai số của cây trước đó. XGBoost sử dụng một hàm lỗi tổng quát để tối ưu hóa mô hình, có thể được hiểu như một dạng tổng quát của các mô hình cây quyết định. Giả sử ở bước thứ t , mô hình đã học được một hàm dự đoán ˆ y ( t -1) i = ∑ t -1 k =1 f k ( x i ) từ các cây quyết định trước đó

<!-- formula-not-decoded -->

<!-- Page 288 (Heavy) -->
Để huấn luyện cây quyết định thứ t , ta cần tìm cây f t sao cho hàm lỗi sau khi thêm cây f t vào mô hình là nhỏ nhất.

Giả sử hàm lỗi L ( y i , ˆ y ( t -1) i ) , với g i và h i lần lượt là đạo hàm bậc nhất và bậc hai của hàm lỗi tại điểm ˆ y ( t -1) i :

<!-- formula-not-decoded -->

Chúng ta có thể xấp xỉ hàm lỗi khi thêm vào cây mới f t là:

<!-- formula-not-decoded -->

với Ω là hàm điều chỉnh trên cây mới f t . Trong XGBoost, hàm điều chỉnh cho một cây với T lá và trọng số lá w j được định nghĩa là:

<!-- formula-not-decoded -->

Tổng hợp lại, ta thu được hàm lỗi xấp xỉ khi thêm cây f t vào mô hình là:

<!-- formula-not-decoded -->

Cây mới f t được lựa chọn để cực tiểu hoá hàm lỗi ˜ L ( t ) . Việc sử dụng hàm lỗi ˜ L ( t ) để huấn luyện cây f t có ý nghĩa là cây mới có thể sửa chữa các lỗi do kết hợp t -1 các cây trước.

Trong ứng dụng, XGBoost cung cấp một API để huấn luyện mô hình và dự đoán trên dữ liệu. Người học có thể xem ví dụ về việc sử dụng XGBoost trên dữ liệu IRIS tại https://gist.github.com/ tqlong/de320d89aab422a0bf0978f84e5d75ae

<!-- Page 289 -->
## 9.6 TỔNG KẾT CHƯƠNG 263 9.6 Tổng kết chương Chương này trình bày các phương pháp học kết hợp nhằm nâng cao hiệu suất dự đoán của mô hình Học máy thông qua việc phối hợp nhiều mô hình con.

Bagging giảm phương sai bằng cách huấn luyện song song nhiều mô hình trên các tập dữ liệu con được lấy mẫu ngẫu nhiên có lặp, và kết hợp đầu ra bằng trung bình hoặc bỏ phiếu đa số. Boosting cải thiện dần hiệu suất qua từng vòng lặp bằng cách tập trung vào các mẫu dữ liệu khó, nhờ cơ chế gán trọng số thích nghi cho lỗi của mô hình trước. XGBoost là một cải tiến mạnh mẽ của Boosting với khả năng tối ưu hóa hiệu quả và hỗ trợ xử lý dữ liệu lớn nhờ cơ chế tính toán phân tán. Học kết hợp cho phép kết hợp linh hoạt nhiều mô hình con khác nhau, tận dụng thế mạnh riêng của từng mô hình nhằm đạt hiệu suất tổng thể vượt trội. Tuy nhiên, việc sử dụng nhiều mô hình cũng làm tăng chi phí tính toán và gây khó khăn trong việc diễn giải kết quả, đặc biệt trong các hệ thống đòi hỏi minh bạch. Nhìn chung, học kết hợp là một trong những kỹ thuật quan trọng và hiệu quả trong xây dựng mô hình Học máy hiện đại, và vẫn đang là chủ đề thu hút nhiều nghiên cứu trong cộng đồng khoa học dữ liệu. Bài tập 1. Cho một tập dữ liệu nhỏ gồm 10 mẫu: 1,2,3,4,5,6,7,8,9,10 . { } Thực hiện phương pháp Bootstrap để tạo ra 5 tập dữ liệu con (mỗi tập có 10 phần tử, lấy mẫu ngẫu nhiên có hoàn lại). Tính giá trị trung bình của từng tập dữ liệu con và ước lượng điểm trung bình cùng khoảng tin cậy 95% cho giá trị trung bình của tập dữ liệu gốc.

<!-- Page 290 -->

<!-- Page 291 -->
## 9.6 TỔNG KẾT CHƯƠNG 265 8. [Lập trình] Sử dụng thư viện xgboost trong Python để giải quyết bài toán phân loại trên tập dữ liệu IRIS.

Thực hiện các bước sau: • Chuẩn bị dữ liệu (tải và chia tập huấn luyện/kiểm tra). • Huấn luyện mô hình XGBoost với các siêu tham số mặc định. • Tinh chỉnh ít nhất hai siêu tham số (ví dụ: độ sâu lớn nhất, tốc độ học) để cải thiện hiệu suất. • Đánh giá mô hình bằng độ chính xác và trực quan hóa tầm quan trọng của các đặc trưng.

<!-- Page 292 -->

<!-- Page 293 -->
Tài liệu tham khảo [1] Breiman, L., Bagging predictors, Machine Learning, vol. 24, no. 2, pp. 123–140, 1996. [2] Freund, Y., and Schapire, R. E., A decision-theoretic gener- alization of on-line learning and an application to boosting, Journal of Computer and System Sciences, vol. 55, no. 1, pp. 119–139, 1997. [3] Breiman, L., Random forests, Machine Learning, vol. 45, no. 1, pp. 5–32, 2001. [4] Friedman, J. H., Greedy function approximation: A gradient boosting machine, Annals of Statistics, vol. 29, no. 5, pp. 1189– 1232, 2001. [5] Chen, T., and Guestrin, C., XGBoost: A scalable tree boost- ing system, Proceedings of the 22nd ACM SIGKDD Interna- tional Conference on Knowledge Discovery and Data Mining, pp. 785–794, 2016.

<!-- Page 294 -->

<!-- Page 295 -->
# Chương 10 Bài toán trích xuất đặc trưng Bên cạnh việc thiết kế mô hình, cách trích xuất và biểu diễn đặc trưng là yếu tố then chốt ảnh hưởng đến hiệu suất và tốc độ học của hệ thống Học máy.

Chương 10 tập trung vào các kỹ thuật giảm chiều và trích chọn đặc trưng, bao gồm Phân tích thành phần chính (PCA), các biến thể của bộ tự mã hóa (autoencoder) và các phương pháp học có giám sát như trích chọn dựa trên độ quan trọng của đặc trưng. Các phương pháp này nhằm loại bỏ nhiễu, giảm độ phức tạp mô hình và làm nổi bật các đặc trưng có giá trị thống kê hoặc ý nghĩa phân biệt cao trong dữ liệu. Nội dung chương có mối liên hệ chặt chẽ với các mô hình học sâu như MLP (Chương 3), CNN (Chương 5) và các mạng cho dữ liệu chuỗi (Chương 6), nơi đặc trưng có thể được học tự động thông qua các tầng biểu diễn trừu tượng. Chương này cung cấp giúp người học hiểu và cải thiện khả năng biểu diễn dữ liệu trong các mô hình Học máy hiện đại.

<!-- Page 296 -->

<!-- Page 297 -->
## 10.2 PHƯƠNG PHÁP PHÂN TÍCH THÀNH PHẦN CHÍNH 271 Hình 10.1:

Quá trình trích xuất đặc trưng và khôi phục lại dữ liệu thô Có nhiều cách tiếp cận khác nhau để trích xuất đặc trưng từ dữ liệu, bao gồm: xây dựng đặc trưng thủ công dựa trên tri thức chuyên gia, học đặc trưng thông qua các phương pháp học không giám sát và học đặc trưng tự động bằng các mô hình học sâu. Các đặc trưng thủ công thường dễ hiểu nhưng phụ thuộc nhiều vào kinh nghiệm; học không giám sát có thể khai thác cấu trúc ẩn trong dữ liệu nhưng đôi khi thiếu định hướng cụ thể; học sâu cho phép mô hình hóa các đặc trưng phức tạp nhưng chi phí tính toán cao. Trong thực tiễn, việc lựa chọn phương pháp trích xuất đặc trưng thường phải trải qua quá trình thử nghiệm và hiệu chỉnh dựa trên bản chất của tập dữ liệu cũng như yêu cầu cụ thể của bài toán đặt ra. 10.2 Phương pháp phân tích thành phần chính Phương pháp phân tích thành phần chính PCA (Principal Compo- nent Analysis) là một trong các phương pháp trích xuất đặc trưng kinh điển trong lĩnh vực học máy. PCA thường được sử dụng để giảm chiều dữ liệu, nén dữ liệu và để trực quan hóa dữ liệu. PCA làm việc với dữ liệu dạng số, đặc biệt là dữ liệu dạng ma trận. Cụ thể, giả sử ta có một tập dữ liệu X Rn×d, ta có dạng ∈

<!-- Page 298 (Heavy) -->
véc-tơ của X

là:

<!-- formula-not-decoded -->

với các mẫu dữ liệu x i ∈ R d nằm trên các dòng của X . Mục tiêu của PCA là tìm một ma trận W ∈ R d × d ′ để biến đổi dữ liệu ban đầu X thành dữ liệu mới Z = XW ∈ R n × d ′ với d ′ ≤ d . Trong đó, các cột của Z là các thành phần chính của dữ liệu X . Các dòng của Z là các biểu diễn mới của các mẫu dữ liệu x i .

Đặc điểm của phương pháp PCA là các thành phần chính của được sắp xếp theo thứ tự giảm dần của phương sai. Trong đó, phương sai được hiểu là sự biến thiên hay thông tin của dữ liệu. Hình 10.2 minh hoạ cho độ phân tán của dữ liệu trong không gian 2 chiều, được minh hoạ qua hai véc-tơ đặc trưng cho hai thành phần chính. Độ dài của các véc-tơ thành phần chính này đặc trưng cho độ phân bố của dữ liệu theo các chiều khác nhau.

Khi sắp xếp theo thứ tự giảm dần của phương sai, thành phần chính đầu tiên sẽ là thành phần chính có phương sai lớn nhất, tức là thành phần chứa nhiều thông tin của dữ liệu nhất. Thành phần chính thứ hai sẽ là thành phần chứa nhiều thông tin thứ hai và cứ tiếp tục như vậy. Do đó, ta có thể giảm chiều dữ liệu bằng cách chỉ giữ lại một số thành phần chính đầu tiên. Các thành phần chính còn lại có thể bị loại bỏ hoặc có thể được giữ lại để tăng độ chính xác của mô hình.

## 10.2.1 Thành phần chính đầu tiên

Giả sử dữ liệu huấn luyện gồm n mẫu dữ liệu x 1 , . . . , x n trong không gian R d . Chúng ta có công thức tính phương sai của dữ liệu

<!-- Page 299 (Heavy) -->
Hình 10.2: Minh hoạ phương pháp phân tích thành phần chính PCA trên dữ liệu 2 chiều

<!-- image -->

ban đầu là:

<!-- formula-not-decoded -->

trong đó µ = 1 n ∑ n i =1 x i là trung bình của bộ dữ liệu.

Gọi véc-tơ đơn vị w 1 ( ∥ w 1 ∥ = 1 ) là cột đầu tiên của ma trận W . Giá trị này cũng đặc trưng cho thành phần chính đầu tiên. Trọng số của thành phần này của dữ liệu X được cho bởi công thức (10.4):

<!-- formula-not-decoded -->

Nếu ta chiếu x i -µ lên w 1 , ta sẽ được véc-tơ khôi phục ̂ x i = z i w 1 + µ . Khi đó phương sai của bộ dữ liệu mới ̂ X được định nghĩa như sau:

<!-- formula-not-decoded -->

<!-- Page 300 (Heavy) -->
Lưu ý, là trung bình của các véc-tơ trong bộ dữ liệu mới cũng bằng µ . Theo định lý Pythagoras, ta có đẳng thức sau:

<!-- formula-not-decoded -->

Kết hợp công thức (10.5) và (10.6), ta thu được:

<!-- formula-not-decoded -->

Như vậy, ta vừa chứng minh sự tương đương giữa cực đại hoá phương sai và cực tiểu hoá lỗi khôi phục khi chiếu dữ liệu lên thành phần chính đầu tiên.

Định lý 10.2 (Phương sai và lỗi khôi phục) . Cực đại hoá phương sai của thành phần chính đầu tiên tương đương với cực tiểu hoá lỗi khôi phục của dữ liệu khi chiếu dữ liệu lên thành phần chính đầu tiên.

Hơn nữa, kết hợp đẳng thức ∥ w 1 ∥ = 1 và ∥ ̂ x i -µ ∥ 2 = ∥ z i w 1 ∥ 2 = | z i | 2 ta thu được công thức (10.7).

<!-- formula-not-decoded -->

Nghĩa là phương sai của dữ liệu mới bằng phương sai của các hệ số tương ứng với thành phần chính đầu tiên.

Để cực đại phương sai này, ta cần tìm w 1 là véc-tơ đơn vị, ∥ w 1 ∥ = 1 , sao cho w T 1 Σw 1 đạt cực đại. Trong đó Σ là ma trận hiệp phương sai của dữ liệu X . Để tìm w 1 thỏa mãn điều kiện trên, ta có thể giải bài toán tối ưu

<!-- formula-not-decoded -->

<!-- Page 301 (Heavy) -->
Để tìm nghiệm cực đại được cho bởi hàm mục tiêu ở công thức (10.8), ta sử dụng phương pháp nhân thử Lagrange như sau. Đầu tiên, ta xây dựng hàm Lagrange như sau:

<!-- formula-not-decoded -->

Sử dụng điều kiện triệt tiêu của đạo hạm tại cực trị, ta tính được đạo hàm của hàm Lagrange theo w 1 và λ như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

tức là w 1 là véc-tơ riêng của Σ với trị riêng λ . Thế ngược lại, phương sai của thành phần chính đầu tiên là

<!-- formula-not-decoded -->

Do đó, ta có thể tìm được w 1 bằng cách tìm véc-tơ riêng w 1 ứng với giá trị riêng lớn nhất của Σ . Do ma trận Σ là ma trận đối xứng và toàn phương xác định dương, nên ta có thể tìm được d giá trị riêng là số thực không âm và sắp xếp chúng giảm dần

<!-- formula-not-decoded -->

Như vậy, w 1 là véc-tơ riêng tương ứng với giá trị riêng lớn nhất λ 1 .

Theo lập luận ở trên, véc-tơ w 1 này cũng tối thiểu lỗi khôi phục dữ liệu khi chiếu lên nó.

## 10.2.2 Các thành phần chính tiếp theo

Để thành phần chính thứ hai không có tương quan với thành phần đầu tiên, ta cần tìm w 2 sao cho trực giao với w 1 , hay w T 2 w 1 = 0 . Hay w 2 thuộc vào không gian con của R d trực giao với w 1 . Vì tính trực giao của các véc-tơ riêng, lập luận tương tự như với thành phần đầu tiên, ta có thể tìm được w 2 bằng cách tìm véc-tơ riêng

<!-- Page 302 (Heavy) -->
w 2 ứng với giá trị riêng lớn thứ hai của Σ , tức là λ 2 . Tiếp tục như vậy, ta có thể tìm được các thành phần chính thứ k bằng cách tìm véc-tơ riêng w k ứng với giá trị riêng lớn thứ k , tức là λ k , của Σ .

Do các thành phần chính không tương quan, thông tin (phương sai) của dữ liệu ban đầu được lưu trữ trong các đặc trưng mới là

<!-- formula-not-decoded -->

Do đó, ta có thể chọn d ′ sao cho tỉ lệ phương sai được lưu trữ trong các đặc trưng mới vượt qua một ngưỡng cho trước. Ví dụ, ta có thể chọn d ′ sao cho tỉ lệ

<!-- formula-not-decoded -->

với θ ∈ (0 , 1) . Ví dụ, có thể chọn θ = 0 . 95 là tỉ lệ phương sai giữ lại được ít nhất 95%. Tỉ lệ 95% này thường được sử dụng trong thực hành PCA.

## Thuật toán 10.1 Thuật toán Phân tích thành phần chính (PCA)

1: procedure PCA ( X ∈ R n × d , θ )

3: Tính ma trận hiệp phương sai: Σ ← 1 n -1 X T X

2: Tâm hoá dữ liệu: X ← X -1 n 1 n 1 T n X

4: Phân tích trị riêng:

Tính các véc-tơ riêng w 1 , . . . , w d và giá trị riêng λ 1 ≥ . . . ≥ λ d

- 5: Tìm d ′ sao cho: ∑ d ′ i =1 λ i ∑ d i =1 λ i ≥ θ

7: Tính các thành phần chính: Z ← XW

6: Tạo ma trận: W ← [ w 1 , . . . , w d ′ ] ∈ R d × d ′

8: return W , Z

- 9: end procedure

Việc tính các véc-tơ riêng và các giá trị riêng của ma trận Σ có thể được thực hiện thông qua các phân tích trị riêng hoặc phân tích

<!-- Page 303 -->
## 10.2 PHƯƠNG PHÁP PHÂN TÍCH THÀNH PHẦN CHÍNH 277 trị đơn (Singular Value Decomposition - SVD).

Các phương pháp này thường được cài đặt sẵn trong các thư viện lập trình của các ngôn ngữ Matlab, Python, R, C/C++. 10.2.3 Giảm chiều dữ liệu Ghép các cột w ,w ,...,w lại thành ma trận W có d′ cột. Ta có 1 2 d′ đẳng thức sau: Z = XW. (10.16) Các cột của ma trận Z bao gồm z ,z ,...,z là biểu diễn mới của 1 2 d′ của dữ liệu ban đầu X. Lưu ý rằng, nếu ta chọn d′ = d, thì ma trận W sẽ là ma trận vuông và trực chuẩn (ma trận của d véc-tơ riêng). Ta có thể khôi phục chính xác dữ liệu X từ dữ liệu đã giảm chiều Z bằng cách biến đổi như sau: d (cid:88) X = XWWT = ZWT = z wT. (10.17) k k (cid:124) (cid:123)(cid:122) (cid:125) I k=1 Công thức (10.17) cho thấy rằng, dữ liệu ban đầu X có thể được khôi phục bằng tổng có trọng số các thành phần chính w (trọng k số Z là biểu diễn mới của dữ liệu). Khi d′ < d, ta có thể khôi phục một cách xấp xỉ dữ liệu X từ dữ liệu đã giảm chiều Z bằng đại lượng d′ (cid:88) X(cid:101) = ZWT = z wT. (10.18) k k k=1 Công thức (10.18) cho thấy rằng, dữ liệu ban đầu X có thể được xấp xỉ bằng việc loại bỏ các thành phần chính w có ít thông tin k (λ nhỏ) của dữ liệu ban đầu. k

<!-- Page 304 (Heavy) -->
Ví dụ: Giả sử ta có dữ liệu X gồm n = 1 . 000 . 000 ảnh có độ phân giải 64 × 64 = 4096 điểm ảnh. Bộ dữ liệu gốc có kích thước 1 . 000 . 000 × 4 . 096 byte ≈ 3 . 096 MB . Nếu ta chọn d ′ = 128 , thì ma trận W có kích thước 4 . 096 × 128 byte = 512 KB . Ta có thể nén dữ liệu gốc thành dữ liệu đã giảm chiều Z có kích thước 1 . 000 . 000 × 128 byte ≈ 122 MB , giảm kích thước xuống còn 122 / 3 . 096 ≈ 3 . 9% so với kích thước gốc.

Ở dưới góc độ tối thiểu hoá lỗi khôi phục dữ liệu, thuật toán PCA tìm ra các thành phần chính W có lỗi khôi phục nhỏ nhất theo Định lý 10.3 sau.

Định lý 10.3 (PCA tối ưu lỗi khôi phục) . Phương pháp PCA tìm được nghiệm tối ưu của bài toán sau

<!-- formula-not-decoded -->

Trong đó, phép biến đổi tuyến tính XW là một phép chiếu dữ liệu X lên không gian con có d ′ chiều. Phép biến đổi tuyến tính ZW T là một phép khôi phục dữ liệu từ không gian con về không gian gốc. Chuẩn Frobenius của lỗi khôi phục ∥ X -XWW T ∥ 2 F đo mức độ sai khác giữa dữ liệu gốc X và dữ liệu khôi phục XWW T .

## 10.3 Bộ tự mã hóa sâu

## 10.3.1 Giới thiệu

Trong phân tích thành phần chính, chúng ta đã thấy rằng, việc trích xuất đặc trưng (nén dữ liệu) được thực hiện bởi một hàm tuyến tính

<!-- formula-not-decoded -->

<!-- Page 305 (Heavy) -->
trong đó, W ∈ R d × d ′ là ma trận các thành phần chính. Hơn nữa, việc khôi phục dữ liệu từ z cũng được thực hiện bởi hàm tuyến tính

<!-- formula-not-decoded -->

Như vậy, PCA là một phương pháp trích xuất đặc trưng tuyến tính. Tuy nhiên, nó không thể trích xuất được các đặc trưng phi tuyến. Để giải quyết vấn đề này, chúng ta có thể sử dụng các mô hình học sâu để trích xuất đặc trưng phi tuyến và khôi phục dữ liệu từ các đặc trưng này. Trong phần này, chúng ta sẽ giới thiệu một mô hình học sâu được sử dụng phổ biến để trích xuất đặc trưng gọi là bộ tự mã hóa sâu DAE (Deep Auto-encoder).

Gọi một mạng nơ-ron sâu f θ : x ↦→ z với tham số θ là bộ mã hoá và một mạng nơ-ron sâu khác g θ : z ↦→ ˆ x là bộ giải mã. Mô hình tổng quát của DAE được mô tả như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## 10.3.2 Huấn luyện bộ tự mã hóa sâu

Để huấn luyện một bộ tự mã hóa sâu, chúng ta cần xác định hàm lỗi L đối với bộ tham số θ của mô hình. Giống như phương pháp PCA, chúng ta cũng muốn tối thiểu hóa sai số khôi phục dữ liệu ˆ x = g θ ( z ) từ z = f θ ( x ) . Do đó, chúng ta có thể sử dụng hàm lỗi trung bình tổng bình phương sai số khôi phục được cho bởi công thức (10.24).

<!-- formula-not-decoded -->

trong đó, x i là mẫu dữ liệu thứ i và ˆ x i là kết quả khôi phục dữ liệu của mô hình. Hình 10.3 mô tả quá trình huấn luyện mô hình DAE, gồm hai bước: bước mã hoá và bước giải mã.

<!-- Page 306 -->

<!-- Page 307 (Heavy) -->
Khi huấn luyện xong, mạng DAE có khả năng khử nhiễu ở đầu vào của mạng. Ngoài ra, mạng DAE huấn luyện với nhiễu có khả năng trích xuất số đặc trưng nhiều hơn số đầu vào ban đầu ( d ′ &gt; d ).

## 10.3.4 Bộ tự mã hoá biến phân

Điểm yếu của bộ tự mã hoá sâu DAE truyền thống và bộ tự mã hoá khử nhiễu là:

- Chúng không đảm bảo tính liên tục của không gian mã hoá . Nghĩa chúng không đảm bảo g θ ( f θ ( x ) + ϵ ) ≈ x .
- Chúng không đảm bảo tính đầy đủ của không gian mã hoá. Nghĩa là không đảm bảo g θ ( z ) là một dữ liệu có nghĩa đối với mã hoá z bất kì.

Để đảm bảo tính liên tục và đầy đủ của không gian mã hoá, chúng ta có thể sử dụng bộ tự mã hoá biến phân VAE (Variational Auto-encoder). Mô hình VAE được mô tả qua hai công thức (10.25) và (10.26).

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Trong đó, z là một biến ngẫu nhiên được lấy từ phân phối chuẩn với kì vọng µ θ ( x ) ∈ R d ′ và độ lệch chuẩn σ θ ( x ) ∈ R d ′ . Thường z được lấy mẫu bằng phương pháp tham số hoá lại như sau. Trước tiên, chúng ta tham số hoá z bằng µ θ ( x ) và σ θ ( x ) như sau:

<!-- formula-not-decoded -->

với ϵ ∼ N (0 , I ) .

Hình 10.4 mô tả quá trình tính toán cơ bản của bộ tự mã hoá biến phân, sử dụng phương pháp tham số hoá theo phân phối Gauss

<!-- Page 308 (Heavy) -->
Hình 10.4: Minh hoạ quá trình mã hoá và giải mã trong bước huấn luyện của bộ tự mã hoá biến phân

<!-- image -->

nhiều chiều lại để lấy mẫu biến ngẫu nhiên z trong miền biểu diễn ẩn. Hàm lỗi của mô hình VAE được tính gồm hai thành phần

<!-- formula-not-decoded -->

Trong đó, hàm lỗi L 1 đặc trưng cho tính khôi phục dữ liệu của mô hình

<!-- formula-not-decoded -->

được tính như bình thường. Hàm lỗi L 2 được dùng để chuẩn hóa phân phối trên miền không gian ẩn của z

<!-- formula-not-decoded -->

<!-- Page 309 (Heavy) -->
được sử dụng để đảm bảo tính liên tục và tính đầy đủ của không gian mã hoá. Trong đó, µ θ ( x i ) và σ θ ( x i ) là kết quả mã hoá của mô hình VAE trên dữ liệu x i . Ở đây, hàm lỗi chuẩn hóa L 2 ( θ ) được tính bằng khoảng cách Kullback-Leibler giữa phân phối N ( µ θ ( x ) , σ 2 θ ( x )) và phân phối chuẩn. Nhờ đó, các phân phối N ( µ θ ( x ) , σ 2 θ ( x )) được đưa về gần phân phối chuẩn N (0 , I ) . Điều này ngăn mô hình mã hóa dữ liệu cách xa nhau trong không gian mã hoá và khuyến khích các phân phối 'chồng lấp' lên nhau, từ đó đáp ứng các điều kiện về tính liên tục và tính đầy đủ của không gian mã hoá.

## 10.4 Trích chọn đặc trưng trong bài toán học có giám sát

Các phương pháp đã giới thiệu trong chương này không sử dụng thông tin về nhãn của dữ liệu. Các thuật toán PCA, bộ tự mã hoá sâu là các phương pháp không giám sát. Chúng tìm cách nén dữ liệu và giữ các thông tin quan trọng nhất với mục tiêu khôi phục lại dữ liệu ban đầu. Tuy nhiên, trong một số trường hợp, nếu ta muốn tìm ra các đặc trưng quan trọng nhất với mục tiêu dự đoán nhãn của dữ liệu, ta có thể sử dụng các phương pháp trích chọn đặc trưng trong bài toán học có giám sát. Cụ thể, bài toán trích chọn đặc trưng như sau: Cho dữ liệu D = { ( x i , y i ) } , i = 1 , 2 , . . . , n thuật toán học máy A và hàm lỗi L ( f ) = E [ ℓ ( f ( x ) , y )] , tìm đặc trưng z = E ( x ) sao cho lỗi trên tập dữ liệu đã trích chọn đặc trưng

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Có ba hướng tiếp cận chính để trích xuất đặc trưng trong trường hợp này: phương pháp lọc, phương pháp gói, phương pháp nhúng.

là nhỏ nhất

<!-- Page 310 -->

<!-- Page 311 -->
## 10.4 TRÍCH CHỌN ĐẶC TRƯNG TRONG BÀI TOÁN HỌC CÓ GIÁM SÁT 285 Cách dùng độ đo Spearman để đánh giá mức độ tương quan giữa đặc trưng và nhãn tương tự, từ đó loại bỏ hoặc giữ lại đặc trưng tương tự như độ tương quan Pearson.

Phân tích phương sai ANOVA là phương pháp sử dụng phép kiểm tra giả thuyết thống kê để đánh giá mối quan hệ về phương sai giữa các nhóm dữ liệu. Ý tưởng chính ở phương pháp này là khi biến x có phương sai thấp (ít biến thiên) thì nó sẽ có ít ảnh hưởng đến nhãn y. Thông tin tương hỗ là phép tính định lượng thông tin của một biến thay đổi khi biết thông tin của một biến khác. Ta đã biết đến khái niệm này trong phương pháp Cây quyết định. Tương tự như vậy ta định nghĩa thông tin tương hỗ của hai biến x,y là lượng thông tin thêm được về x khi biết y. Định nghĩa 10.4 (Thông tin tương hỗ). Thông tin tương hỗ giữa hai biến x và y được định nghĩa như sau: I(x,y) = H(x) H(x y) − | trong đó, H(x) là entropy của x và H(x y) là entropy của x khi | biết y. Trong trường hợp đặc trưng x và nhãn mục tiêu y là biến rời rạc, chúng ta có thể tính thông tin tương hỗ giữa x và y theo H(x) và H(x y) bằng cách sử dụng các tần suất xuất hiện của các giá trị | của x và y trong tập dữ liệu. Cụ thể, ta có (cid:88) H(x) = P(x )log P(x ) i i − xi (cid:88) (cid:88) H(x y) = P(y ) P(x y )log P(x y ) j i j i j | − | | yj xi

<!-- Page 312 -->

<!-- Page 313 -->
## 10.4 TRÍCH CHỌN ĐẶC TRƯNG TRONG BÀI TOÁN HỌC CÓ GIÁM SÁT 287 • Loại bỏ đặc trưng là phương pháp gói trong đó đặc trưng được bỏ ra khỏi tập đặc trưng đang xét sao cho tập đặc trưng mới đem lại hiệu suất tốt nhất. 10.4.3 Phương pháp nhúng Phương pháp nhúng là phương pháp tìm kiếm các đặc trưng tốt nhất bằng cách tận dụng khả năng đánh giá các đặc trưng của chính thuật toán học máy có giám sát đang quan tâm.

Lược đồ của phương pháp này gần giống với lược đồ Phương pháp gói ở Hình 10.5. Tuy nhiên, trong phương pháp nhúng, chúng ta có thể trực tiếp đánh giá được độ quan trọng của các đặc trưng. Dựa trên đánh giá này, việc lựa chọn thêm đặc trưng hoặc bỏ đặc trưng sẽ dễ dàng hơn. Có nhiều thuật toán học máy cho phép đánh giá trực tiếp độ quan trọng của đặc trưng như thuật toán học máy sử dụng mô hình cây quyết định hoặc mô hình hồi quy tuyến tính. Cây quyết định: Khi sử dụng mô hình cây quyết định để huấn luyện trên tập dữ liệu, mỗi lần phân chia tại một nút sử dụng đặc trưng f , thuật toán sẽ cộng thêm vào độ quan trọng của đặc trưng i f đại lượng bằng đúng tiêu chí phân chia tại nút đó. Độ quan trọng i của đặc trưng f được tính bằng tổng các tiêu chí tại các nút của i cây sử dụng đặc trưng đó. Hồi quy: Trong hồi quy, độ quan trọng của đặc trưng f được i tính bằng trọng số tương ứng với đặc trưng. Các trọng số này được điều chỉnh bởi thuật toán hồi quy kết hợp với các hàm điều chỉnh như. Ví dụ, mô hình LASSO, được cho bởi công thức (10.31) n min (cid:88)(cid:0) y wTx (cid:1)2 + λ w . (10.31) i i 1 w − ∥ ∥ i=1 Hàm l được điều chỉnh có tác dụng ép các trọng số tương ứng với các đặc trưng không quan trọng tiến về 0. Có thể dùng các hàm

<!-- Page 314 -->

<!-- Page 315 -->
## 10.6 TỔNG KẾT CHƯƠNG 289 Việc sử dụng dữ liệu đã giảm chiều giúp giảm thời gian huấn luyện và yêu cầu bộ nhớ, so với việc sử dụng dữ liệu gốc 3072 chiều.

Mã ví dụ có thể xem tại https://gist.github.com/tqlong/ 88c494e70cee0ac0c22b0e08d48d9c48 10.6 Tổng kết chương Chương 10 giới thiệu các phương pháp trích xuất đặc trưng hiệu quả, góp phần nâng cao hiệu suất huấn luyện và giảm nguy cơ quá khớp trong mô hình Học máy. Phân tích thành phần chính PCA là một công cụ ổn định để giảm chiều, giúp làm nổi bật cấu trúc ẩn trong dữ liệu và hỗ trợ trực quan hóa hoặc tiền xử lý. Bộ mã hoá - giải mã AE (autoencoder) ứng dụng học sâu để học các biểu diễn nén của dữ liệu, từ đó tái tạo lại thông tin đầu vào một cách hiệu quả. Đây là phương pháp mạnh mẽ để học đặc trưng không giám sát. Một phiên bản của AE là bộ mã hoá biến phân VAE, cho phép học phân bố ẩn của dữ liệu và sinh mẫu mới từ không gian đặc trưng đã học, mở rộng khả năng biểu diễn và tổng quát hóa của mô hình. Những phương pháp này có vai trò quan trọng trong thiết kế mô hình, đặc biệt trong các bài toán với số chiều lớn và dữ liệu thực tế có số chiều ẩn thấp hoặc có nhiễu. Bài tập 1. Chứng minh Định lý 10.3. 2. Cho tập dữ liệu trong R2 như Hình 10.6. Hãy tính (i) ma trận hiệp phương sai Σ, (ii) các véc-tơ riêng v và v , (iii) các thành 1 2 phần chính z và z của các điểm dữ liệu trong tập huấn luyện. 1 2

<!-- Page 316 (Heavy) -->
<!-- image -->

-

-

-

Hình 10.6: Tập dữ liệu trong R 2

3. [Lập trình] Sử dụng thư viện scikit-learn trong Python, áp dụng PCA để giảm chiều dữ liệu tập IRIS từ 4 chiều xuống 2 chiều. Trực quan hóa dữ liệu đã giảm chiều bằng biểu đồ phân tán và so sánh với dữ liệu gốc.
4. [Tìm hiểu] Giải thích sự khác biệt giữa PCA và bộ tự mã hóa sâu trong trích xuất đặc trưng. Tại sao bộ tự mã hóa sâu có khả năng trích xuất đặc trưng phi tuyến?
5. Cho một bộ tự mã hóa sâu đơn giản với hàm kích hoạt tuyến tính và hàm lỗi là trung bình bình phương sai số

<!-- formula-not-decoded -->

Tính đạo hàm của hàm lỗi đối với các tham số θ, ϕ của bộ tự mã hóa sâu.

6. [Lập trình] Sử dụng thư viện Keras hoặc Pytorch , triển khai một bộ tự mã hóa khử nhiễu sử dụng bộ dữ liệu MNIST. Đánh giá khả năng khôi phục ảnh của bộ tự mã hóa.

<!-- Page 317 -->
## 10.6 TỔNG KẾT CHƯƠNG 291 7. [Tìm hiểu] Giải thích vai trò của hàm lỗi Kullback-Leibler (KL) trong bộ tự mã hóa biến phân (VAE).

Tại sao nó đảm bảo tính liên tục và đầy đủ của không gian mã hóa? 8. [Lập trình] Sử dụng thư viện scikit-learn, triển khai áp dụng PCA trên tập dữ liệu CIFAR-10. • Giảm chiều dữ liệu xuống còn θ = 95% tổng phương sai, • Huấn luyện một mô hình Logistic Regression trên dữ liệu đã giảm chiều. • So sánh hiệu suất với mô hình trên dữ liệu gốc. • Trực quan hóa hiệu suất của mô hình và tỉ lệ phương sai θ được sử dụng. Hãy thử với nhiều giá trị khác nhau của θ.

<!-- Page 318 -->

<!-- Page 319 -->
Tài liệu tham khảo [1] Pearson, K., On lines and planes of closest fit to systems of points in space, Philosophical Magazine, vol. 2, no. 11, pp. 559–572, 1901. [2] Hotelling, H., Analysis of a complex of statistical variables into principal components, Journal of Educational Psychology, vol. 24, no. 6, pp. 417–441, 1933. [3] Hinton, G. E., and Salakhutdinov, R. R., Reducing the dimen- sionality of data with neural networks, Science, vol. 313, no. 5786, pp. 504–507, 2006. [4] Kingma, D. P., and Welling, M., Auto-encoding variational Bayes, arXiv preprint arXiv:1312.6114, 2013. [5] Guyon, I., and Elisseeff, A., An introduction to variable and feature selection, Journal of Machine Learning Research, vol. 3, pp. 1157–1182, 2003. [6] Hall, M. A., Correlation-based feature selection for machine learning, Proceedings of the 17th International Conference on Machine Learning, pp. 359–366, 1999.

<!-- Page 320 -->
294 TÀI LIỆU THAM KHẢO [7] Tibshirani, R., Regression shrinkage and selection via the Lasso, Journal of the Royal Statistical Society: Series B, vol. 58, no. 1, pp. 267–288, 1996. [8] Fisher, R. A., The correlation between relatives on the sup- position of Mendelian inheritance, Transactions of the Royal Society of Edinburgh, vol. 52, no. 2, pp. 399–433, 1919.

<!-- Page 321 -->
# Chương 11 Mô hình sinh Chương 11 giới thiệu các mô hình sinh (Generative Models) – một nhánh quan trọng và đặc biệt của Học máy, tập trung vào việc tạo ra dữ liệu mới dựa trên phân phối thống kê tiềm ẩn của dữ liệu quan sát.

Khác với các mô hình phân biệt chỉ học ranh giới giữa các lớp, mô hình sinh tìm cách học toàn bộ cấu trúc phân phối xác suất của dữ liệu, cho phép sinh mẫu mới tương tự như dữ liệu huấn luyện. Chương sẽ trình bày các phương pháp ước lượng phân phối như cực đại độ hợp lý MLE (Maximum Likelihood Estimation), thuật toán cực đại kỳ vọng EM (Expectation Maximization) và các tiếp cận học phân phối sử dụng mạng nơ-ron sâu. Các phương pháp được giới thiệu không chỉ mang giá trị lý thuyết mà còn đóng vai trò nền tảng trong các ứng dụng hiện đại như tạo dữ liệu tổng hợp, phục hồi ảnh, dịch phong cách và sáng tạo nội dung.

<!-- Page 322 -->

<!-- Page 323 (Heavy) -->
Hình 11.1: Minh hoạ phương pháp ước lượng mật độ tham số

<!-- image -->

## 11.2 Ước lượng mật độ bằng mô hình tham số

Sử dụng mô hình tham số để mô tả phân bố hoặc mật độ phân bố là phương pháp cổ điển trong thống kê. Trong cách tiếp cận này, ta giả định rằng có thể mô tả phân bố thật sự p ⋆ ( x ) của dữ liệu bằng một mô hình phân bố có tham số p θ ( x ) . Sau đó, ta tìm các tham số của hàm số đó sao cho phân phối có tham số đó phù hợp nhất với phân phối thực nghiệm của dữ liệu. Cụ thể bài toán ước lượng mật độ bằng mô hình tham số như sau

Định nghĩa 11.1 (Ước lượng mật độ bằng mô hình tham số) . Cho tập dữ liệu D = { x 1 , . . . , x n } với x i ∼ p ⋆ ( x ) và lớp mô hình phân bố có tham số { p θ ( x ) : θ ∈ Θ } . Tìm tham số θ để mô hình p θ ( x ) 'xấp xỉ' p ⋆ ( x ) .

Hình 11.1 là một ví dụ về ước lượng mật độ bằng mô hình tham số. Trong đó, ta giả định rằng dữ liệu D được sinh ra từ một phân bố chuẩn. Đường liền nét là kết quả thuật toán ước lượng và đường

<!-- Page 324 (Heavy) -->
đứt nét là phân phối thực tế cần ước lượng. Tuy nhiên, dữ liệu chỉ có các điểm rời rạc được lấy mẫu và được thể hiện bằng các cột hít-tô-gram trong hình.

Như vậy để tìm được tham số θ , ta phải chỉ ra thế nào là phù hợp. Trong lý thuyết xác suất, có nhiều cách để so sánh hai phân bố, ở đây là mô hình p θ và phân bố p ⋆ của các mẫu dữ liệu trong D .

## 11.2.1 Ước lượng hợp lý cực đại

Nếu sử dụng khoảng cách Kullback-Leibler (KL) để so sánh p ⋆ và p θ , ta có công thức khoảng cách sau:

<!-- formula-not-decoded -->

Dựa trên công thức (11.1), nếu D KL ( p ⋆ ∥ p θ ) = 0 , ta có thể suy ra được p ⋆ = p θ . Tuy nhiên, khoảng cách KL không tính được do không biết p ⋆ . Sử dụng Luật số lớn, xấp xỉ khoảng cách KL bằng giá trị trung bình (thực nghiệm) trên tập dữ liệu D được lấy mẫu từ phân bố p ⋆ , ta có biến đổi sau:

<!-- formula-not-decoded -->

<!-- Page 325 (Heavy) -->
trong đó, C là hằng số không phụ thuộc vào θ , p ( D | θ ) là xác suất của dữ liệu trong mô hình p θ ( x ) . Như vậy ta có thể tối thiểu khoảng cách KL bằng cách tối đa hóa hàm mật độ xác suất của dữ liệu p ( D | θ ) , còn gọi là độ hợp lý (likelihood).

Định nghĩa 11.2 (Ước lượng hợp lý cực đại) . Gọi

<!-- formula-not-decoded -->

là độ hợp lý của θ đối với tập dữ liệu D . Ước lượng hợp lý cực đại (MLE) của θ là nghiệm tối ưu của bài toán cực đại hóa L ( θ )

<!-- formula-not-decoded -->

Ví dụ 11.3 (Ước lượng mô hình Bernoulli) . Mô tả một đồng xu không cân bằng với xác suất mặt ngửa là θ . Giả sử ta quan sát được n lần tung đồng xu và thu được k lần mặt ngửa. Hỏi θ hợp lý nhất là bao nhiêu?

Ta đặt X i = 1 nếu mặt ngửa xuất hiện và X i = 0 nếu mặt sấp xuất hiện ở lần tung thứ i . Có thể mô tả phân bố của X i bằng một biến ngẫu nhiên nhị thức X i Bernoulli ( x θ ) = θ x (1 θ ) 1 -x

∼ | -

Giả sử n lần tung độc lập với nhau thì xác suất của dữ liệu trong mô hình có thể được tính theo công thức

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

do các biến x i ∈ { 0 , 1 } .

Do log là hàm đồng biến, cực trị của L ( θ ) là cực trị của log L ( θ ) . Do đó, ta có thể tìm θ MLE bằng cách giải bài toán tối ưu

<!-- formula-not-decoded -->

<!-- Page 326 (Heavy) -->
Lấy đạo hàm và đặt bằng 0 để tìm cực trị ta được

<!-- formula-not-decoded -->

Như vậy, tỉ số giữa số lần mặt ngửa và tổng số lần tung là ước lượng hợp lý cực đại của mô hình đồng xu nói trên.

Ví dụ 11.4 (Ước lượng mô hình Gauss) . Các bạn nam trong lớp có chiều cao là x 1 , x 2 , . . . , x n . Hỏi phân bố chiều cao của các bạn nam trong lớp như thế nào ?

Nếu ta giả định rằng chiều cao của các bạn nam trong lớp tuân theo phân bố Gauss thì ta có thể mô tả chiều cao của một bạn nam bất kì bằng một biến ngẫu nhiên Gauss có phân phối như sau:

<!-- formula-not-decoded -->

với µ là trung bình và σ 2 là phương sai.

Giả sử các biến X i là độc lập với nhau thì xác suất của dữ liệu trong mô hình là

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Tương tự như Ví dụ 11.3, ta lấy đạo hàm ℓ ( µ, σ 2 ) theo µ và σ 2 và đặt bằng 0 được

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 327 (Heavy) -->
## 11.2.2 Ước lượng hậu nghiệm cực đại

Trong thực tế, ước lượng hợp lý cực đại có thể dẫn đến các ước lượng vô lý do nhiễu và khả năng học quá. Ví dụ, nếu ta tung đồng xu năm lần mà không ra mặt ngửa lần nào thì ước lượng hợp lý cực đại của θ là 0. Tuy nhiên, ta có thể thấy rằng đây là một ước lượng vô lý vì đồng xu bình thường không thể không bao giờ tung ra mặt ngửa. Hoặc ngược lại, nếu cả 5 lần đều ra mặt ngửa thì ước lượng của θ là 1, đây cũng là một ước lượng vô lý.

Một ước lượng thay thế phổ biến là ước lượng hậu nghiệm cực đại (Maximum a Posteriori - MAP). Ước lượng này được tính bằng cách tối đa hóa hàm hậu nghiệm p ( θ | D ) , còn gọi là hàm hậu nghiệm.

Định nghĩa 11.5 (Ước lượng hậu nghiệm cực đại) . Giả sử p ( θ ) là xác suất tiên nghiệm của tham số θ . Ước lượng hậu nghiệm cực đại của θ là nghiệm tối ưu của bài toán cực đại hóa hàm p ( θ | D )

<!-- formula-not-decoded -->

Theo công thức Bayes, ta có biến đổi sau để tối đa xác suất hậu nghiệm

<!-- formula-not-decoded -->

trong đó, log p ( D ) là hằng số không phụ thuộc vào θ , p ( D | θ ) là hàm hợp lý (likelihood) còn p ( θ ) là xác suất tiên nghiệm của tham số θ .

Như vậy, ước lượng hậu nghiệm cực đại là sự điều chỉnh của ước lượng hợp lý cực đại bằng cách thêm vào hàm mục tiêu hàm xác suất tiên nghiệm p ( θ ) . Xác suất tiên nghiệm là 'niềm tin' của

<!-- Page 328 (Heavy) -->
ta về giá trị của tham số khi chưa biết dữ liệu. Khi có dữ liệu, ta điều chỉnh 'niềm tin' này bằng giá trị ước lượng hậu nghiệm cực đại. Đây là một cách để tránh hiện tượng học quá do các ước lượng được điều chỉnh bởi xác suất tiên nghiệm.

Để tính toán đơn giản và dễ hiểu, ta thường giả định xác suất tiên nghiệm có một dạng hàm số phù hợp với xác suất hậu nghiệm theo định nghĩa sau

Định nghĩa 11.6 (Xác suất tiên nghiệm liên hợp) . Xác suất tiên nghiệm liên hợp là xác suất tiên nghiệm có cùng dạng hàm số với xác suất hậu nghiệm.

Dưới đây là một số ví dụ về xác suất tiên nghiệm liên hợp của một số phân phối phổ biến.

Ví dụ 11.7 (Phân phối nhị phân) . Xét thí nghiệm sau, tung đồng xu N lần và đếm số lần tung ra mặt ngửa. Thực hiện n thí nghiệm như vậy ta thu được các dữ liệu X i , i = 1 , 2 , . . . , n là số lần ra mặt ngửa trong n lần thí nghiệm.

Sử dụng tính chất của phân phối nhị phân ta có thể ước lượng được xác suất p ( X i | θ ) theo công thức sau:

<!-- formula-not-decoded -->

Từ đó, ta có thể tính được hàm hợp lý trên toàn bộ dữ liệu D là

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 329 (Heavy) -->
Phân phối hậu nghiệm của θ có thể được tính bằng công thức Bayes như sau:

<!-- formula-not-decoded -->

với p ( θ ) = Beta( θ | α, β ) ∝ θ α -1 (1 -θ ) β -1 và C 1 , C 2 là hằng số không phụ thuộc vào θ . Do đó, p ( θ | D ) cũng là phân phối Beta với tham số Beta( θ | α n , β n ) được cho bởi công thức sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Từ đó ta có thể dễ dàng tính được, phân bố p ( θ | D ) này đạt cực đại với giá trị θ = ∑ n i =1 X i + α -1 nN + α + β -2 . Hình 11.2 là một ví dụ về phân phối Beta với N = 20 và số lần thí nghiệm n = 10 . Đường liền nét là phân phối hậu nghiệm của θ = 0 . 5 . Do việc lấy mẫu là ngẫu nhiên nên giá trị trung bình thực nghiệm đạt 10 . 08 , sẽ bị lệch so với giá trị lý thuyết. Khi số lần thí nghiệm n tăng lên, giá trị trung bình thực nghiệm sẽ tiến gần hơn đến giá trị lý thuyết.

Ví dụ 11.8 (Phân phối đa thức (multinomial)) . Xét thí nghiệm sau, tung xúc xắc K mặt tất cả N lần và đếm số lần ra từng mặt X 1 , X 2 , . . . , X K . Thực hiện n thí nghiệm như vậy ta thu được các dữ liệu

<!-- formula-not-decoded -->

là số lần ra từng mặt xúc xắc trong n lần thí nghiệm.

<!-- Page 330 (Heavy) -->
Hình 11.2: Phân phối Nhị phân với θ = 0 . 5 , N = 20 và n = 10

<!-- image -->

Nếu dữ liệu tuân theo phân phối đa thức

<!-- formula-not-decoded -->

thì hàm hợp lý của dữ liệu là

<!-- formula-not-decoded -->

Phân phối liên hợp của phân phối đa thức là phân phối Dirichlet.

<!-- formula-not-decoded -->

Phân phối này đạt cực đại tại θ k = α k -1 ∑ K k =1 α k -K .

<!-- Page 331 (Heavy) -->
Phân phối hậu nghiệm của θ là phân phối Dirichlet với tham số

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Phân bố này đạt cực đại tại θ k = ∑ n i =1 ( X k i + α k ) -1 ∑ n i =1 ∑ K k =1 ( X k i + α k ) -K .

Trên đây là một số ví dụ về ước lượng hậu nghiệm cực đại của một số phân phối phổ biến. Chúng ta có thể áp dụng phương pháp này để ước lượng tham số cho các phân phối phổ biến khác ví dụ như Phân phối Poisson, Phân phối Đa thức, Phân phối chuẩn, v.v..

## 11.3 Thuật toán EM - Cực đại hoá kì vọng

Ước lượng tham số của mô hình phân bố có tham số như ở mục trên chỉ thực hiện được khi ta có mô hình phân bố tường minh của dữ liệu được quan sát. Tuy nhiên, trong thực tế, ta thường không có mô hình phân bố tường minh của dữ liệu được quan sát mà chỉ có mô hình phân bố liên hợp của cả dữ liệu được quan sát và phần dữ liệu ẩn. Khi đó việc ước lượng tham số của mô hình trở nên khó khăn hơn nhiều vì ta không thể tìm được chính xác phân phối xác suất của dữ liệu được quan sát.

Cụ thể như sau, giả sử có biến ngẫu nhiên X và Z với mô hình phân phối liên hợp, được cho bởi công thức sau:

<!-- formula-not-decoded -->

Giả sử ta quan sát được X và muốn ước lượng tham số θ của mô hình phân bố p θ ( X,Z ) . Giả sử ta tuân theo nguyên tắc ước lượng hợp lý cực đại

<!-- formula-not-decoded -->

<!-- Page 332 (Heavy) -->
trong đó, tổng trên Z được tính theo mọi khả năng có thể có của biến ẩn Z (do ta không biết Z ). Tính toán này cực kì khó khăn vì phải duyệt qua mọi khả năng của Z cũng như do hàm log-tổng.

Ví dụ 11.9 (Hai đồng xu) . Giả sử có 2 đồng xu với xác suất ra mặt ngửa lần lượt là θ 1 và θ 2 . Xét thí nghiệm sau: Với xác suất p ta chọn đồng xu thứ nhất và với xác suất 1 -p ta chọn đồng xu thứ hai để tung. Thực hiện n thí nghiệm như vậy thu được x 1 , . . . , x n ∈ { 0 , 1 } , trong đó x i = 1 nếu được mặt ngửa, x i = 0 nếu được mặt sấp. Hãy ước lượng bộ tham số θ = ( p, θ 1 , θ 2 ) .

Ở đây biến ẩn là biến Z i ∈ { 0 , 1 } , biến Z i chỉ ra đồng xu được chọn trong thí nghiệm ( Z i = 1 nếu chọn đồng xu thứ nhất, Z i = 0 nếu chọn đồng xu thứ hai). Biến quan sát là biến X i ∈ { 0 , 1 } . Ta có mô hình phân bố liên hợp như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Như vậy, ta có dạng tường minh (công thức) của xác suất dữ liệu đầy đủ (cả biến quan sát được và biến ẩn). Tuy nhiên, do biến ẩn không được biết (không biết chọn đồng xu nào để tung), ta phải tính tổng trên tất cả các khả năng có thể có của biến ẩn để tính hàm hợp lý (likelihood) của dữ liệu D = { X 1 , . . . , X n } :

<!-- formula-not-decoded -->

Cực đại hoá đại lượng trên không hề dễ dàng mà thường chúng ta phải sử dụng một đại lượng thay thế (cận dưới) dễ tính hơn để cực đại hoá.

<!-- Page 333 (Heavy) -->
## 11.3.1 Cận dưới bằng chứng

Cận dưới bằng chứng (evidence lower bound - ELBO) là một đại lượng thay thế cho hàm hợp lý dễ tính toán hơn và tối ưu hơn. Trong trường hợp biến quan sát được là X và biến ẩn là Z có mô hình xác suất liên hợp p θ ( X,Z ) . Cận dưới bằng chứng được xác định như sau: Theo nguyên lý ước lượng hợp lý cực đại, ta cần tìm θ ⋆ cực đại hàm log-hợp lý

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Xét một phân bố bất kì của biến ẩn q ( Z ) , ta có

<!-- formula-not-decoded -->

Do hàm ln là hàm lõm, ln E [ · ] ≥ E [ln( · )] nên

<!-- formula-not-decoded -->

Trong đó kì vọng được tính trên phân bố q ( Z ) , H ( q ) là entropy của q ( Z ) , KL[ q ∥ p θ ( Z | X )] là khoảng cách Kullback-Leibler giữa phân bố q ( Z ) và phân bố hậu nghiệm p θ ( Z | X ) .

Bất đẳng thức tại công thức (11.6) đúng với mọi phân bố q ( Z ) , cho thấy cận dưới ELBO của ℓ (Θ) gồm hai phần:

<!-- Page 334 (Heavy) -->
- Kì vọng của log-hợp-lý đầy đủ E q ( Z ) [ln p θ ( X,Z )] : nếu lựa chọn q ( Z ) hợp lý, ta có thể tính toán được đại lượng này vì ta đã biết dạng hàm số tường minh của p θ ( X,Z ) .
- Entropy của H ( q ) = E q ( Z ) [ -ln q ( Z )] : đại lượng này là hằng số đối với θ nếu ta cố định q ( Z )

Công thức (11.7) cho thấy cận dưới ELBO là chặt nếu ta chọn q ( Z ) chính là xác suất hậu nghiệm p θ ( Z | X ) . Với phân bố này thì KL[ q ∥ p θ ( Z | X )] triệt tiêu bằng 0 .

## 11.3.2 Thuật toán cực đại hoá kì vọng

Kết hợp lại ta có hai bước E và bước M trong thuật toán cực đại hoá kì vọng EM (Expectation-Maximization) (Thuật toán 11.1)

- Bước E: Chọn phân bố q ( Z ) = p θ ( Z | X ) để tính kì vọng

<!-- formula-not-decoded -->

- Bước M: Cực đại hóa ELBO ( θ ) để cập nhật tham số θ . Bước này đảm bảo rằng log-hợp lý sẽ tăng lên.

Ví dụ 11.10. Áp dụng cho bài toán ở ví dụ 11.9, ta có X = X 1 , . . . , X n và Z = Z 1 , . . . , Z n là các biến ngẫu nhiên thuộc { 0 , 1 } với xác suất liên hợp

<!-- formula-not-decoded -->

Bước E : Tính xác suất hậu nghiệm

<!-- formula-not-decoded -->

<!-- Page 335 (Heavy) -->
Thuật toán 11.1 Thuật toán Cực đại hoá Kỳ vọng (EM Algorithm)

1: procedure TrainEM ( X )

2: Khởi tạo tham số θ (0) ngẫu nhiên

3: for t = 1 , 2 , . . . cho đến khi hội tụ do

4: Tính phân phối hậu nghiệm:

<!-- formula-not-decoded -->

5: Thiết lập hàm mục tiêu:

<!-- formula-not-decoded -->

6: Cập nhật tham số:

<!-- formula-not-decoded -->

7: end for

8: return θ ( t )

9: end procedure

Các đại lượng này tính được do ta biết xác suất liên hợp p θ ( X i , Z i ) . Đại lượng r i còn được gọi là trách nhiệm của đồng xu thứ nhất đối với kết quả tung X i . Đồng xu thứ hai có trách nhiệm là 1 -r i .

Bước M : Cập nhật tham số θ bằng cách tối ưu hoá hàm mục tiêu

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

▷ Bước E

▷ Bước M

<!-- Page 336 (Heavy) -->
Lấy kì vọng theo phân bố q ( Z ) = p θ ( Z | X ) ta được

<!-- formula-not-decoded -->

Áp dụng phương pháp tìm cực trị như trong Ví dụ 11.3, ta có cập nhật

<!-- formula-not-decoded -->

## 11.3.3 Thuật toán EM trên phân bố xác suất họ mũ

Phân bố xác suất họ mũ là một lớp các phân bố thường dùng trong xác suất thống kê cũng như Học máy. Hầu hết các phân bố xác suất ta thường dùng như phân bố nhị phân, phân bố nhị thức, phân bố chuẩn, v.v. . . đều thuộc họ phân bố này. Phân bố họ mũ cho biến ngẫu nhiên X là

<!-- formula-not-decoded -->

Trong đó F ( X ) gọi là thống kê đầy đủ của phân bố, Z ( θ ) là hằng số chuẩn hoá để công thức trên tạo thành một xác suất. Đặc điểm của hằng số Z ( θ ) là:

<!-- formula-not-decoded -->

<!-- Page 337 (Heavy) -->
Nếu áp dụng nguyên lý Ước lượng hợp lý cực đại lên phân bố xác suất họ mũ, ta có công thức sau:

<!-- formula-not-decoded -->

Do đó, cực trị của ℓ ( θ ) chỉ phụ thuộc vào thống kê đầy đủ F ( X )

<!-- formula-not-decoded -->

Trong đó, A là thuật toán ước lượng hợp lý cực đại dựa trên thống kê đầy đủ F ( X ) .

Thuật toán EM trên xác suất họ mũ . Nếu xác suất liên hợp p θ ( X,Z ) thuộc họ mũ thì thuật toán EM hoạt động thế nào? Ta sẽ cực đại hoá kì vọng

<!-- formula-not-decoded -->

Dễ thấy công thức (11.9) trên không khác gì công thức (11.8) ngoài việc thay thống kê đầy đủ F ( X ) bằng kì vọng E q [ F ( X,Z )] . Do đó, để có được thuật toán EM, ở bước M, ta chỉ cần áp dụng thuật toán ước lượng hợp lý cực đại A với đầu vào là kì vọng E q [ F ( X,Z )] là cập nhật được tham số θ ( t ) = A ( E q [ F ( X,Z )]) .

Ví dụ 11.11 (Phân bố trộn Gauss) . Phân bố Gauss có dạng

<!-- formula-not-decoded -->

với µ , Σ lần lượt là kì vọng và ma trận hiệp phương sai.

<!-- Page 338 (Heavy) -->
Theo nguyên tắc ước lượng hợp lý cực đại, với dữ liệu x 1 , x 2 , . . . , x n , ta có

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Ta có thể trộn K phân bố Gauss lại với nhau để được phân bố trộn Gauss có dạng

<!-- formula-not-decoded -->

trong đó, bộ tham số θ = ( π 1: K , µ 1: K , Σ 1: K ) với điều kiện π k ≥ 0 và ∑ k π k = 1 . Tức là mẫu dữ liệu x được lấy mẫu bằng cách chọn ngẫu nhiên một phân bố trong K phân bố Gauss với xác suất π 1: K .

Để ước lượng bằng thuật toán EM, gọi z ik ∈ { 0 , 1 } là biến ngẫu nhiên (biến ẩn - hidden variable) chỉ ra x i (biến quan sát được - observed variable) được lấy mẫu từ phân bố thứ k . Đặt e k = 0 , . . . , 0 , 1 , 0 , . . . , 0 là véc-tơ cơ sở chuẩn tắc thứ k . Ta có

<!-- formula-not-decoded -->

<!-- Page 339 (Heavy) -->
Xác suất cuối cùng trong các công thức trên được gọi là trách nhiệm của phân bố thứ k với mẫu dữ liệu x i .

Hàm hợp lý của dữ liệu đầy đủ X = ( x 1 , x 2 , . . . , x n ) , Z = ( z ik ) là

<!-- formula-not-decoded -->

với log-hợp lý

<!-- formula-not-decoded -->

Lấy kì vọng theo phân bố hậu nghiệm được (Bước E)

<!-- formula-not-decoded -->

Giải cực trị của hàm trên ta được cập nhật (Bước M)

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Ví dụ 11.12 (Thuật toán K-means) . Thuật toán K-means (Thuật toán 11.2) là một thuật toán phân cụm dựa trên phân bố trộn Gauss với hai điểm riêng sau:

- Cố định các ma trận hiệp phương sai Σ k là ma trận đơn vị.
- Xác định trách nhiệm của các cụm bằng cách tính khoảng cách và chọn cụm gần nhất với dữ liệu.

<!-- Page 340 (Heavy) -->
` Thuật toán 11.2 Thuật toán K-means 1: procedure TrainKMeans ( X , K ) 2: Khởi tạo các tâm cụm µ (0) 1 , . . . , µ (0) K ngẫu nhiên 3: for t = 1 , 2 , . . . cho đến khi hội tụ do 4: for all x i ∈ X do 5: Gán cụm gần nhất: ▷ Bước E: Gán cụm r ik ← { 1 nếu k = arg min j ∥ x i -µ ( t -1) j ∥ 0 ngược lại 6: end for 7: for k = 1 to K do 8: Cập nhật: ▷ Bước M: Cập nhật tâm cụm µ ( t ) k ← ∑ n i =1 r ik · x i ∑ n i =1 r ik 9: end for 10: end for 11: return θ = ( µ 1 , . . . , µ K ) 12: end procedure `

## 11.4 Ước lượng mật độ phi tham số

Ước lượng mật độ phi tham số là phương pháp xây dựng mô hình dựa trên dữ liệu huấn luyện nhưng không có số lượng tham số cố định. Có hai phương pháp ước lượng mật độ cơ bản là: phương pháp ước lượng mật độ bằng cách đếm và phương pháp ước lượng mật độ bằng hàm nhân. Phương pháp ước lượng bằng cách đếm được sử dụng phổ biến đối với dữ liệu đơn giản, số chiều đặc trưng ít. Do đó trong phần này, chúng tôi xin trình bày về phương pháp sử dụng hàm nhân.

Phương pháp ước lượng mật độ bằng hàm nhân (kernel density estimation - KDE) dựa trên ý tưởng cửa sổ Parzen. Theo đó, mỗi

<!-- Page 341 (Heavy) -->
điểm dữ liệu huấn luyện có "ảnh hưởng" đến vùng không gian xung quanh nó (cửa sổ) thông qua một hàm nhân.

Xét một lân cận V x quanh điểm dữ liệu x . Mật độ xác suất trung bình của lân cận V x là

<!-- formula-not-decoded -->

với v ( V x ) là thể tích của lân cận V x còn P ( V x ) là tổng xác suất của V x . Xác suất P ( V x ) có thể ước lượng bằng tỉ lệ số điểm dữ liệu rơi vào lân cận V x

<!-- formula-not-decoded -->

Xét trường hợp đơn giản trong không gian R d , ta chọn lân cận V x là hình hộp (cửa sổ Parzen) có kích thước s và có tâm tại x , ta có

<!-- formula-not-decoded -->

với κ ( u ) là hàm nhân có các tính chất sau:

- ·
- κ ( u ) thể hiện hình hộp có kích thước bằng 1 có tâm ở gốc toạ độ.
- ·
- κ ( u /s ) hình hộp có kích thước s có tâm ở gốc toạ độ
- κ (( u -x ) /s ) hình hộp có kích thước s có tâm ở x

Dựa trên các tính chất trên, chúng ta có thể chọn hàm nhân κ ( u ) sao cho

<!-- formula-not-decoded -->

<!-- Page 342 -->

<!-- Page 343 (Heavy) -->
- Hàm nhân Gauss (Gaussian kernel):

<!-- formula-not-decoded -->

- Hàm nhân Epanechnikov (Epanechnikov kernel):

<!-- formula-not-decoded -->

với c d = ∫ ∥ u ∥≤ 1 1 d u là thể tích của vòng tròn đơn vị trong R d .

## 11.5 Biểu diễn phân bố bằng mạng nơ-ron

## 11.5.1 Biểu diễn mật độ bằng hàm năng lượng

Các mô hình biểu diễn phân bố bằng hàm năng lượng là một lớp mô hình sinh tổng quát hoá xác suất họ mũ như sau:

<!-- formula-not-decoded -->

trong đó

- x là một điểm dữ liệu.
- E θ ( x ) là hàm năng lượng (thế năng) của điểm dữ liệu x .
- Z ( θ ) là hàm chia.
- f θ ( x ) = -E θ ( x ) là mô hình cần huấn luyện.
- θ là tham số của mô hình cần huấn luyện.

Về bản chất, hàm p θ ( x ) có công thức rất giống với hàm softmax dùng trong các mô hình phân lớp: mỗi điểm dữ liệu x được gán một điểm số f θ ( x ) và sử dụng softmax để tính mật độ xác suất của x .

<!-- Page 344 (Heavy) -->
Ví dụ 11.13. Giả sử x là một ảnh màu x ∈ [0 , 1] H × W × 3 , f θ ( x ) là một mạng nơ-ron (ví dụ: mạng CNN) có một đầu ra là số thực. Khi đó, ta có thể huấn luyện mạng này để biểu diễn được phân bố của ảnh màu từ bộ dữ liệu D = { x 1 , x 2 , . . . , x n } .

Lấy mẫu. Việc lấy mẫu x ∼ p θ ( x ) có thể thực hiện bằng phương pháp Langevin Monte Carlo như sau:

<!-- formula-not-decoded -->

Bước lấy mẫu được lặp lại T lần để đảm bảo phân phối của x ( T ) gần với phân phối p θ ( x ) .

Huấn luyện mô hình biểu diễn mật độ bằng hàm năng lượng. Để huấn luyện mô hình biểu diễn mật độ bằng hàm năng lượng, sử dụng nguyên tắc ước lượng hợp lý cực đại MLE, ta cần cực đại hóa hàm hợp lý theo tham số θ như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Định lý 11.14 (Đạo hàm hàm chia) . Đạo hàm của hàm chia log Z ( θ ) là

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 345 (Heavy) -->
Chứng minh:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

□

Sử dụng phương pháp leo đồi bằng đạo hàm thì cần tính đạo hàm

như sau:

<!-- formula-not-decoded -->

Số hạng đầu tiên trong công thức trên có thể tính bằng phương pháp lan truyền ngược và số hạng thứ hai có thể tính bằng phương pháp Monte Carlo thông qua việc lấy mẫu x ∼ p θ ( x ) . Do đó, ta có thể huấn luyện mô hình biểu diễn mật độ bằng hàm năng lượng bằng cách sử dụng phương pháp lan truyền ngược và phương pháp lấy mẫu Monte Carlo.

Một cách nhìn khác của thuật toán huấn luyện mô hình năng lượng ở trên là bài toán cực tiểu hoá một hàm lỗi V ( Z, θ ) như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

trong đó, Z = ( z 1 , . . . z n s ) cần cực tiểu V ( z, θ ) hay cực đại

<!-- formula-not-decoded -->

<!-- Page 346 (Heavy) -->
## Thuật toán 11.4 Huấn luyện mô hình năng lượng (EBM Training)

- 1: procedure TrainEBM ( { x 1 , . . . , x n } , η )
- 2: Khởi tạo tham số θ (0)
- 3: for t = 1 , 2 , . . . cho đến khi hội tụ do ▷ Lấy mẫu từ mô hình hiện tại
- 4: for i = 1 to n s do
- 5: Lấy mẫu z i ∼ p θ ( t -1) ( x )

6: end for ▷ Cập nhật tham số theo chênh lệch đạo hàm 7: Tính đạo hàm:

<!-- formula-not-decoded -->

8: end for

9: return θ

10: end procedure

còn θ cần cực đại V ( z, θ ) hay cực đại điểm số của dữ liệu

<!-- formula-not-decoded -->

## 11.5.2 Biểu diễn phân bố bằng hàm sinh

Một cách tiếp cận khác để biểu diễn phân bố (một cách gián tiếp) là sử dụng hàm sinh. Phương pháp này mô tả cách sinh ra dữ liệu một cách ngẫu nhiên từ một phân bố. Cụ thể, để sinh ra một điểm dữ liệu x thuộc phân bố p ( x ) , ta xây dựng một mạng nơ-ron có đầu vào là một biến ngẫu nhiên z và đầu ra là một điểm dữ liệu x như sau:

<!-- formula-not-decoded -->

trong đó, z là véc-tơ ngẫu nhiên có phân phối chuẩn, G θ ( z ) là một mạng nơ-ron biến đổi không gian ngẫu nhiên của z thành

<!-- Page 347 (Heavy) -->
không gian dữ liệu x có phân bố p ( x ) . Mạng nơ-ron G θ ( z ) được gọi là mô hình sinh dữ liệu (generator). Gọi p g là phân bố của X = G θ ( Z ) , Z ∼ N (0 , I ) .

Lấy mẫu. Mạng G θ ( z ) được huấn luyện sao cho đầu ra của nó tuân theo phân bố mong muốn p ( x ) khi z ∼ N (0 , I ) . Do đó, việc lấy mẫu từ mô hình sinh dữ liệu rất đơn giản, theo công thức sau:

<!-- formula-not-decoded -->

Khoảng cách Kullback-Leibler và Jensen-Shannon. Bản chất của ước lượng hợp lý cực đại là tối thiểu khoảng cách Kullback-Leibler (KL) giữa mô hình phân bố q ( x ) = p θ ( x ) (phân bố của G θ ( Z ) ) và phân bố của dữ liệu p ( x ) (không biết nhưng biết bộ dữ liệu D = { x 1 , x 2 , . . . , x n } .

<!-- formula-not-decoded -->

Khoảng cách KL bằng không khi và chỉ khi p ( x ) = q ( x ) , ∀ x . Tuy nhiên, việc sử dụng khoảng cách KL trong tính toán gặp một số khó khăn sau

- Khoảng cách KL không đối xứng D KL ( p ∥ q ) = D KL ( q ∥ p ) .

̸

- Khi tính trên các vùng có xác suất p ( x ) thấp (ít dữ liệu) nhưng xác suất q ( x ) lại lớn, đặc biệt trong giai đoạn đầu của quá trình huấn luyện.

Khoảng cách Jensen-Shannon có thể được sử dụng để giảm khó khăn tính toán trên bằng việc đối xứng hoá tính toán khoảng cách như sau:

<!-- formula-not-decoded -->

<!-- Page 348 (Heavy) -->
Hình 11.3: Minh hoạ mô hình GAN

<!-- image -->

Khoảng cách Jensen-Shannon có tính chất đối xứng và trơn hơn so với khoảng cách Kullback-Leibler.

Huấn luyện hàm sinh. Để hướng dẫn việc huấn luyện hàm sinh G θ ( z ) , ta sử dụng một mô hình phân biệt D ϕ ( x ) có đầu ra là đánh giá xác suất x thuộc vào phân bố p ( x ) . Mô hình D ϕ ( x ) đóng vai trò của một 'nhà phê bình' phân biệt các mẫu dữ liệu 'thật' (real) khỏi những mẫu dữ liệu 'giả'. Mô hình G θ ( z ) đóng vai trò là kẻ tấn công tìm cách đánh lừa 'nhà phê bình' D ϕ ( x ) . Hai mô hình cạnh tranh nhau nên mô hình này còn được gọi là mô hình sinh đối nghịch GAN (Generative Adversarial Networks). Quá trình này được minh hoạ ở Hình 11.3.

Xác suất của một mẫu dữ liệu x thuộc vào phân bố p ( x ) là D ϕ ( x ) . Ta muốn xác suất này cực đại khi x ∼ p ( x ) tức là cực đại E X ∼ p ( x ) [log D ϕ ( X )] . Ta muốn xác suất này cực tiểu khi x = G θ ( z ) , z ∼ p z tức là cực đại E Z ∼ p z [log(1 -D ϕ ( G θ ( Z )))] .

Ngược lại, ta lại muốn hàm sinh G θ ( z ) 'đánh lừa' được mô hình phân biệt D ϕ ( x ) , tức là cực tiểu E Z ∼ p z [log(1 -D ϕ ( G θ ( Z )))] . Kết hợp lại, việc huấn luyện G θ , D ϕ là bài toán cực tiểu hoá một cực

<!-- Page 349 (Heavy) -->
đại sau:

<!-- formula-not-decoded -->

## Thuật toán 11.5 Thuật toán huấn luyện mô hình GAN

## 1: procedure TrainGAN ( D,n s )

- 2: Khởi tạo tham số cho mô hình sinh G θ và mô hình phân biệt D ϕ
- 3: while chưa hội tụ do

<!-- formula-not-decoded -->

- 6: Cập nhật tham số D ϕ theo:
- 5: Lấy mẫu x 1 , . . . , x n s ∼ D (dữ liệu thật)

<!-- formula-not-decoded -->

7: Cập nhật tham số của G θ để giảm xác suất bị phân biệt:

<!-- formula-not-decoded -->

8: end while

- 9: return G θ , D ϕ
- 10: end procedure

Gọi p g là phân bố của đầu ra của mạng G θ , ta có

<!-- formula-not-decoded -->

Để tìm D ϕ ( x ) cực đại L ( G,D ) , xét tổng bên trong tích phân. Đặt A = p ( x ) , B = p g ( x ) , y = D ϕ ( x ) , ta có

<!-- formula-not-decoded -->

<!-- Page 350 (Heavy) -->
suy ra cực đại của hàm này đạt tại y = A A + B , tức là D ∗ ϕ ( x ) = p ( x ) p ( x )+ p g ( x ) . Khi D ∗ ϕ ( x ) tối ưu như trên thì

<!-- formula-not-decoded -->

Khi hàm sinh G ∗ θ ( x ) cho phân bố p g ( x ) ≈ p ( x ) thì D ϕ ( x ) sẽ bị 'lừa', tức là D ∗ ϕ ( x ) ≈ 1 / 2 . Khi đó ta có

<!-- formula-not-decoded -->

Như vậy, hàm mục tiêu L ( G,D ∗ ) của G θ bản chất là khoảng cách Jensen-Shannon giữa hai phân bố p và p g . Khi G ∗ θ tối ưu thì L ( G ∗ , D ∗ ) tối ưu và bằng -2 log 2 .

## Các yếu điểm của mô hình GAN cổ điển

- Dữ liệu nằm trong không gian có số chiều thấp: Các dữ liệu x về mặt biểu diễn có thể có số chiều rất lớn. Do đó, khi khởi tạo, phân bố p g có thể nằm ở vùng không gian khác hoàn toàn so với p . Do đó rất dễ để mô hình phân biệt D ϕ học được cách phân biệt hoàn hảo hai phân bố này (phân biệt thật - giả).
- ·
- Đạo hàm dùng để huấn luyện bị triệt tiêu: Khi D ϕ ( x ) hoàn hảo thì D ( x ) ≈ 1 với x ∼ p ( x ) và D ( x ) ≈ 0 khi x ∼ p g . Khi đó L ( G,D ) ≈ 0 và đạo hàm bị triệt tiêu gần bằng 0, khiến cho việc huấn luyện rất khó khăn.

<!-- Page 351 (Heavy) -->
Mô hình Wasserstein GAN (WGAN) tìm cách giải quyết khó khăn của mô hình GAN cổ điển bằng cách đánh giá khoảng cách giữa hai phân bố p và p g 'trơn' hơn. Khoảng cách Wasserstein giữa hai phân bố p và p g được định nghĩa như sau

<!-- formula-not-decoded -->

trong đó f là hàm số liên tục K-Lipschitz. Tiếp tục nới lỏng điều kiện đối với hàm f bằng cách biểu diễn hàm f bằng một mạng nơ-ron với bộ trọng số w ∈ W . Ta có hàm mục tiêu

<!-- formula-not-decoded -->

Tương tự như huấn luyện mô hình GAN, để huấn luyện mô hình Wasserstein GAN, ta huấn luyện f w để cực đại E X ∼ p ( x ) [ f w ( X )] -E Z ∼ p z [ f w ( G θ ( Z ))] nhằm phân biệt p và p g . Còn để huấn luyện G θ , ta cực tiểu đại lượng -E Z ∼ p z [ f w ( G θ ( Z ))] nhằm đánh lừa 'nhà phê bình' f w (Thuật toán 11.6).

## 11.6 Tình huống áp dụng:

Generative Adversarial Networks (GAN)

Trong hướng dẫn này, chúng ta sẽ triển khai một mô hình GAN đơn giản để sinh ra hình ảnh giống như tập dữ liệu MNIST, một tập dữ liệu phổ biến gồm 60.000 hình ảnh số viết tay kích thước 28x28.

1. Sử dụng các thư viện như torch , torchvision và matplotlib để tải và hiển thị hình ảnh từ tập dữ liệu MNIST.
2. Xây dựng một mạng sinh (Generator) có đầu vào là một véc-tơ ngẫu nhiên (100 chiều) và đầu ra là một hình ảnh 28x28 (Bảng 11.1).

<!-- Page 352 (Heavy) -->
## Thuật toán 11.6 Thuật toán huấn luyện mô hình WGAN

- 1: procedure TrainWGAN ( D,n s , n critic , α, c )
- 2: Khởi tạo tham số mô hình sinh θ (0) , mô hình phê bình w (0)
- 3: while chưa hội tụ do
- 4: for j = 1 to n critic do
- 5: Lấy mẫu z 1 , . . . , z n s ∼ N (0 , I )

7: Tính đạo hàm:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

8: Cập nhật tham số mô hình phê bình:

<!-- formula-not-decoded -->

9: Chặt giá trị:

<!-- formula-not-decoded -->

10: end for

- 11: Lấy mẫu z 1 , . . . , z n s ∼ N (0 , I )

12: Tính đạo hàm:

<!-- formula-not-decoded -->

13: Cập nhật tham số mô hình sinh:

<!-- formula-not-decoded -->

- 14: end while

- 15: return G θ , f w

16: end procedure

<!-- Page 353 -->
## 11.6 TÌNH HUỐNG ÁP DỤNG:

GENERATIVE ADVERSARIAL NETWORKS (GAN) 327 Bảng 11.1: Các lớp trong kiến trúc của Generator trong mô hình GAN Lớp Đầu vào Đầu ra Hàm kích hoạt/Xử lý Linear 1 100 128 LeakyReLU (0.2) Linear 2 128 256 LeakyReLU (0.2) Linear 3 256 784 Tanh 3. Xây dựng một mạng phân loại (Discriminator) có đầu vào là một hình ảnh 28x28 và đầu ra là một giá trị xác suất (0-1) cho biết hình ảnh đó có phải là hình ảnh thật hay không (Bảng 11.2). Bảng 11.2: Các lớp trong kiến trúc của Discriminator trong mô hình GAN Lớp Đầu vào Đầu ra Hàm kích hoạt Linear 1 784 512 LeakyReLU (0.2) Linear 2 512 256 LeakyReLU (0.2) Linear 3 256 1 Sigmoid 4. Để huấn luyện GAN, ta chọn hàm lỗi entropy chéo nhị phân nn.BCELoss() để phân biệt ảnh thật, giả và thuật toán tối ưu hóa Adam với các tham số lr = 0.0002 và betas = (0.5,0.999) cho cả hai mạng sinh và phân loại. 5. Vòng lặp huấn luyện là phần cốt lõi của mô hình GAN, trong đó huấn luyện mạng sinh và mạng phân biệt xen kẽ nhau. • [Chuẩn bị dữ liệu]: Sử dụng tập dữ liệu MNIST với kích thước lô là 64 (batch_size). Dữ liệu được chuẩn hóa về khoảng [ 1,1] để phù hợp với đầu ra của hàm sinh (hàm kích hoạt − Tanh). • [Huấn luyện mạng phân biệt]:

<!-- Page 354 -->

<!-- Page 355 -->
## 11.7 TỔNG KẾT CHƯƠNG 329 Mô hình sinh thể hiện bước chuyển từ nhận thức sang sáng tạo trong Học máy, khi hệ thống không chỉ phân loại hay dự đoán mà còn có thể tạo ra dữ liệu mới có độ chân thực cao.

Chương 12 tiếp theo sẽ mở rộng góc nhìn bằng cách kết nối các mô hình Học máy đã học với các mạng đồ thị xác suất, nhằm giới thiệu một hướng tiếp cận tổng quát và có tính thống kê cao hơn cho việc mô hình hóa và suy luận. Bài tập (cid:80) 1. Chứng minh rằng độ hợp lý của L(θ) = p (X) = p (X,Z) θ Z θ không giảm khi thực hiện thuật toán EM. 2. [Tìm hiểu] So sánh giữa ước lượng hợp lý cực đại (MLE) và ước lượng hậu nghiệm cực đại (MAP). Đưa ra một ví dụ cụ thể minh họa ưu điểm của MAP so với MLE khi dữ liệu ít hoặc có nhiễu. 3. [Tìm hiểu] Giải thích sự khác biệt giữa biểu diễn xác suất bằng hàm năng lượng và hàm sinh. So sánh cách hàm sinh được sử dụng trong mô hình GAN và cách lấy mẫu từ biểu diễn xác suất bằng hàm năng lượng để tạo dữ liệu mới. 4. [Lập trình] Triển khai thuật toán EM cho Gaussian Mixture Model (GMM) trên dữ liệu hai chiều. Người đọc có thể họn 2 chiều trong dữ liệu IRIS. • Trực quan hóa quá trình phân cụm và so sánh với K-means. • Thử nghiệm với số lượng cụm khác nhau và so sánh kết quả. 5. [Lập trình] Nghiên cứu và triển khai biến thể Wasserstein GAN (WGAN). So sánh hiệu suất của WGAN với GAN cơ bản trên tập dữ liệu MNIST bằng cách đánh giá chất lượng ảnh sinh ra và độ ổn định của quá trình huấn luyện.

<!-- Page 356 -->

<!-- Page 357 -->
Tài liệu tham khảo [1] Dempster, A. P., Laird, N. M., and Rubin, D. B., Maximum likelihood from incomplete data via the EM algorithm, Journal of the Royal Statistical Society: Series B, vol. 39, no. 1, pp. 1–22, 1977. [2] Silverman, B. W., Density estimation for statistics and data analysis, Chapman and Hall, 1986. [3] LeCun, Y., Chopra, S., Hadsell, R., Ranzato, M., and Huang, F. J., A tutorial on energy-based learning, Proceedings of the IEEE International Joint Conference on Neural Networks, pp. 1–6, 2006. [4] Goodfellow, I., Pouget-Abadie, J., Mirza, M., Xu, B., Warde- Farley, D., Ozair, S., Courville, A., and Bengio, Y., Generative adversarial nets, Advances in Neural Information Processing Systems, vol. 27, pp. 2672–2680, 2014. [5] Kingma, D. P., and Welling, M., Auto-encoding variational Bayes, arXiv preprint arXiv:1312.6114, 2013. [6] Bishop, C. M., Mixture density networks, Technical Report NCRG/94/004, Aston University, 1994.

<!-- Page 358 -->
332 TÀI LIỆU THAM KHẢO [7] Neal, R. M., Probabilistic inference using Markov chain Monte Carlo methods, Technical Report CRG-TR-93-1, University of Toronto, 1993.

<!-- Page 359 -->
# Chương 12 Mô hình đồ thị xác suất Chương 12 trình bày về mô hình đồ thị xác suất, một công cụ mạnh mẽ để biểu diễn tri thức và suy luận trong các tình huống bất định hoặc ngẫu nhiên.

Mô hình đồ thị kết hợp lý thuyết xác suất với cấu trúc đồ thị, cho phép mô hình hóa các mối quan hệ phụ thuộc giữa các biến ngẫu nhiên một cách trực quan và hiệu quả. Từ các mô hình đơn giản như mạng Bayes ngây thơ đến mạng Bayes tổng quát và trường ngẫu nhiên Markov, chương này cho thấy khả năng mô tả cấu trúc thống kê tiềm ẩn trong dữ liệu một cách rõ ràng. Các bài toán thực tế như gán nhãn từ loại hay nhận dạng chuỗi minh họa vai trò của mô hình đồ thị trong việc khai thác phụ thuộc ngữ cảnh và mối quan hệ giữa các quan sát lân cận. Nội dung chương giúp hoàn thiện bức tranh tổng thể về các mô hình Học máy, từ phân loại, hồi quy, học sâu đến biểu diễn xác suất, hướng tới những hệ thống thông minh có khả năng suy luận và ra quyết định.

<!-- Page 360 -->

<!-- Page 361 (Heavy) -->
toán học và suy luận. Đồng thời, chương cũng sẽ giới thiệu một số ứng dụng thực tế để minh họa sức mạnh của mô hình này trong việc giải quyết các bài toán phức tạp.

## 12.2 Mô hình Bayes ngây thơ

Mô hình Bayes ngây thơ (NB - Naive Bayes) là mô hình Học máy tuân theo hướng tiếp cận mô hình sinh. Mô hình NB tìm cách mô tả xác suất p ( x, y ) dưới một giả thuyết độc lập xác suất. Ở đây, giả sử dữ liệu vào x = ( x 1 , . . . , x m ) gồm m thuộc tính. Theo định lý Bayes, ta có

<!-- formula-not-decoded -->

Để biểu diễn P ( y ) , y = 1 , . . . C , ta cần C tham số (thật ra là C -1 tham số độc lập do tổng của chúng bằng 1). Để biểu diễn p ( x | y ) thì với mỗi giá trị của y , ta phải mô tả xác suất p ( x | y ) với mọi x ∈ X . Nếu không có gì đặc biệt, trong trường hợp đơn giản nhất mỗi thuộc tính x k nhận 2 giá trị thì số lượng tham số cần thiết để mô tả p ( x | y ) sẽ là 2 m -1 tham số độc lập. Như vậy, nếu sử dụng mô hình xác suất tổng quát, chúng ta không thể lưu trữ, tính toán gì khi số thuộc tính lớn (hàng tỉ tham số khi m ≥ 32 ).

Vì vậy, theo hướng tiếp cận mô hình sinh, chắc chắn chúng ta phải giả sử một đặc tính nào đó của xác suất p ( x | y ) để có thể làm việc, cài đặt thuật toán trên thực tế. Với mô hình NB, chúng ta sử dụng giả thuyết độc lập xác suất có điều kiện theo công thức (12.1).

<!-- formula-not-decoded -->

Trong đó, ta nói, các thuộc tính x k là độc lập có điều kiện với nhau khi biết nhãn y (nói một cách dễ hiểu, các thuộc tính x k chỉ phụ thuộc vào nhãn y ). Mối quan hệ này được mô tả trong

<!-- Page 362 (Heavy) -->
Hình 12.1: Mô hình Bayes ngây thơ.

<!-- image -->

hình 12.1. Giả thuyết này có thể không đúng trong thực tế, nhưng nó giúp đơn giản hóa rất nhiều các phép toán xác suất. Công thức (12.1) làm giảm số lượng tham số dùng để mô tả xác suất p ( x | y ) đáng kể do xác suất này bị tách thành m phân bố độc lập p ( x k | y ) , k = 1 , . . . , m . Đặc biệt, các phân bố độc lập p ( x k | y ) là phân bố trên một biến x k , dễ dàng thao tác, ước lượng và cài đặt.

## 12.2.1 Pha huấn luyện

Đầu tiên, để huấn luyện mô hình NB, chúng ta cần ước lượng các xác suất p ( x k | y ) và P ( y ) với mọi k = 1 , . . . , m và y = 1 , . . . , C từ dữ liệu D = { ( x i , y i ) } , i = 1 , 2 , . . . , n .

- Ước lượng P ( y ) : Chúng ta ước lượng P ( y ) bằng tần suất xuất hiện của nhãn y trong dữ liệu D .

<!-- formula-not-decoded -->

với c y là số lần nhãn y xuất hiện trong D .

- Ước lượng P ( x k | y ) khi x k ∈ A k là thuộc tính rời rạc : Chúng ta ước lượng P ( x k | y ) bằng tần suất xuất hiện x k khi nhãn của dữ liệu bằng y theo ước lượng tần suất ở (12.3).

<!-- formula-not-decoded -->

<!-- Page 363 (Heavy) -->
trong đó c k ya = |{ ( x i , y i ) ∈ D : x k i = a, y i = y }| với a ∈ A k là số mẫu dữ liệu trong D thuộc phân lớp y và có thuộc tính thứ k là a .

- Ước lượng P ( x k | y ) khi x k ∈ A k ⊆ R là thuộc tính liên tục : Thường chúng ta chọn một phân bố quen thuộc để mô tả phân bố có điều kiện của x k . Ví dụ nếu giả sử P ( x k | y ) là phân bố chuẩn (Gauss) có kì vọng µ k y và phương sai ( σ k y ) 2 thì có thể ước lượng các tham số này bằng công thức

<!-- formula-not-decoded -->

Đây là các ước lượng hợp lý cực đại của các tham số cúa phân bố thuộc tính thứ k cho các mẫu dữ liệu thuộc phân lớp y .

## 12.2.2 Pha suy luận

Sau khi huấn luyện, có thể dùng mô hình NB để dự đoán phân lớp của một mẫu dữ liệu x ∈ X bất kì. Cụ thể, ta cần tìm nhãn y ⋆ cực đại hóa xác suất hậu nghiệm ̂ P ( y | x ) .

<!-- formula-not-decoded -->

Trong đó, ta đã lợi dụng tính đồng biến của hàm log . Như vậy, để suy luận trên mẫu dữ liệu x , chỉ cần tìm nhãn y cực đại hóa tổng của các giá trị của hàm log các xác suất đã được tính trong pha huấn luyện. Việc sử dụng hàm log thay vì giá trị trực tiếp khi làm việc với xác suất, giúp chúng ta tránh được hiện tượng tràn số vì kết quả tính toán quá nhỏ.

<!-- Page 364 (Heavy) -->
## Thuật toán 12.1 Thuật toán huấn luyện mô hình Bayes ngây thơ

<!-- formula-not-decoded -->

- 2: Đếm số lượng mẫu theo lớp:

<!-- formula-not-decoded -->

3: for all thuộc tính k do

4: if A k là rời rạc then

5:

for all

6:

a

A

k

, y

Đếm số mẫu:

∈

<!-- formula-not-decoded -->

7:

end for

8: else

9:

10:

<!-- formula-not-decoded -->

Tính trung bình và phương sai:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

11: end for

12: end if

13: end for

14: Tính các phân bố xác suất:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

15: return các ước lượng xác suất ̂ P ( y ) , ̂ P ( x k = a | y ) 16: end procedure

= 1

, . . . , C

do

<!-- Page 365 -->
## 12.2 MÔ HÌNH BAYES NGÂY THƠ 339 Thuật toán 12.2 Thuật toán suy luận bằng mô hình Bayes ngây thơ 1: procedure TestNB(x = (x1,...,xm)) 2: for y = 1 to C do 3:

Tính điểm số: m (cid:88) s log P(cid:98)(y) + log P(cid:98)(xk y) y ← | k=1 4: end for 5: Dự đoán nhãn: y⋆ arg maxs y ← y 6: return y⋆ 7: end procedure 12.2.3 Lưu ý khi ước lượng xác suất Nhược điểm của cách ước lượng xác suất trong các công thức (12.2) và (12.3) là chúng đếm số lần xuất hiện của các giá trị a Ak và ∈ nhãn y. Nếu các số đếm này bằng 0 thì chúng ta sẽ nhận được các xác suất bằng 0 trong pha huấn luyện. Đến pha suy luận, xác suất bằng 0 nhân với các xác suất khác trong công thức tính P(x,y) cũng sẽ cho kết quả bằng 0. Như vậy, các mẫu dữ liệu x có giá trị thuộc tính không xuất hiện trong tập huấn luyện D sẽ được ước lượng có xác suất bằng 0 (hiện tượng học quá). Để khắc phục hiện tượng này, sử dụng phương pháp làm trơn của Laplace, chúng ta có thể thêm các số đếm giả vào cả tử số và mẫu số của các công thức (12.2) và (12.3). Cụ thể, chúng ta thêm một hằng số C vào số đếm của cả tử số và mẫu số như công thức (12.5) c + 1 ck + 1 P(cid:98)(y) = y ,P(cid:98)(xk = a y) = ya (12.5) n + C | c + Ak y | |

<!-- Page 366 -->

<!-- Page 367 (Heavy) -->
<!-- image -->

Hình 12.2: Ví dụ minh hoạ về mạng Bayes mô tả quan hệ giữa các thuộc tính.

## 12.3.1 D-chia cắt

Để nói về quan hệ độc lập xác suất toàn cục, trước tiên ta nói về tính chất D-chia cắt (D-separation) của hai tập thuộc tính trong V . Hình 12.3 mô tả ba tình huống D-chia cắt: hình trái - đầu nối với đuôi, hình giữa - đuôi nối với đuôi, hình phải - đầu nối với đầu. Các thuộc tính tô màu là thuộc tính trong tập Z .

Hình 12.3: Các tình huống D-chia cắt.

<!-- image -->

Định nghĩa 12.2 (D-chia cắt) . Tập thuộc tính Z D-chia cắt hai tập thuộc tính X và Y nếu mọi đường đi p = v 1 , v 2 , . . . , v ℓ từ X đến Y ( v 1 ∈ X,v ℓ ∈ Y ) có một trong các tính chất sau (Hình 12.3):

<!-- Page 368 (Heavy) -->
1. Có một đỉnh v i ∈ Z và ( v i -1 , v i ) ∈ E, ( v i , v i +1 ) ∈ E (đầu-nốivới-đuôi).
2. Có một đỉnh v i ∈ Z và ( v i , v i -1 ) ∈ E, ( v i , v i +1 ) ∈ E (đuôi nối với đuôi).
3. Nếu ( v i -1 , v i ) ∈ E, ( v i +1 , v i ) ∈ E (đầu-nối-với-đầu) thì v i / ∈ Z và tất cả con cháu của v i không thuộc Z .

Bổ đề 12.3. Cho y là một nút lá trong mạng Bayes N , nếu loại bỏ nút y khỏi N được mạng mới N ′ có tập đỉnh là X thì

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

do y là nút lá nên y / ∈ pa x , ∀ x

<!-- formula-not-decoded -->

Chứng minh:

□

Bổ đề 12.4. Cho X là một tập nút gốc, nếu loại bỏ tất cả các nút khác khỏi N được mạng mới N ′ (cũng có tập đỉnh là X ) thì

<!-- formula-not-decoded -->

Chứng minh: Sử dụng bổ đề 12.3 lần lượt với từng nút lá không thuộc X ta được điều phải chứng minh. □

<!-- Page 369 (Heavy) -->
Bổ đề 12.5. Nếu P ( X,Y.Z ) = g ( X,Z ) h ( Y, Z ) thì X độc lập với Y khi biết Z , tức là P ( X,Y | Z ) = P ( X | Z ) P ( Y | Z ) .

Bổ đề 12.6. Nếu X,Y,Z phân hoạch V và Z D-chia cắt X và Y thì X độc lập với Y khi biết Z . Khi đó ta viết X ⊥ Y | Z .

Chứng minh: Vì Z D-chia cắt X và Y nên

- ∀ x ∈ X, pa x ∩ Y = ∅ hay pa x ⊂ X ∪ Z
- ∀ y ∈ Y, pa y ∩ X = ∅ hay pa y ⊂ Y ∪ Z

Nếu tách Z thành hai tập Z 1 và Z 2 sao cho

- Z 1 = { z 1 ∈ Z : pa z 1 ∩ X = ∅}
- Z 2 = Z \ Z 1 .

Do Z D-chia cắt X và Y nên ∀ z 1 ∈ Z 1 , pa z 1 ∩ Y = ∅ (nếu không sẽ tạo thành tình huống đầu-nối-với-đầu). Và theo cách xây dựng Z 2 ta cũng có ∀ z 2 ∈ Z 2 , pa z 2 ∩ X = ∅ .

Vậy ta có

<!-- formula-not-decoded -->

Như vậy P ( X,Y,Z ) được phân tích thành hai nhân tử g ( X,Z ) và h ( Y, Z ) , suy ra X ⊥ Y | Z theo Bổ đề 12.5. □

̸

<!-- Page 370 (Heavy) -->
## 12.3.2

## Quan hệ độc lập xác suất có điều kiện

Định lý 12.7 (Độc lập xác suất toàn cục) . Nếu Z D-chia cắt X và Y thì X và Y độc lập xác suất khi biết giá trị của Z .

<!-- formula-not-decoded -->

Chứng minh:

Theo bổ đề 12.4, ta chỉ cần xét trường hợp

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Gọi U là tập các đỉnh không bị D-chia cắt với X bởi Z . Ta có X ⊂ U .

\ ⊥ |

Gọi W = V \ U \ Z là tập các đỉnh còn lại ngoài U ∪ Z hay W là tập các đỉnh bị chia cắt với X bới Z . Ta có Y ⊂ W . Đặt X ′ = U \ X và Y ′ = W Y . Do bổ đề 12.6, ta có U W Z hay

<!-- formula-not-decoded -->

Suy ra X Y Z

<!-- formula-not-decoded -->

Từ định lý 12.7, ta có thể xác định tất cả các mối quan hệ độc lập xác suất được biểu diễn bởi mạng Bayes bằng cách kiểm tra

tính chất D-chia cắt.

Mệnh đề 12.8. Nếu gọi bao trùm Markov của một đỉnh x ∈ V là tập các đỉnh thoã mãn một trong các điều kiện cha của x , con của x hoặc cha của các con của x thì x độc lập xác suất với tất cả các đỉnh còn lại nếu biết bao trùm Markov của x .

<!-- Page 371 -->
## 12.4 TRƯỜNG NGẪU NHIÊN MARKOV 345 Mệnh đề 12.9.

Mỗi thuộc tính xk độc lập xác suất với tất cả các thuộc tính không phải con cháu của nó nếu biết các thuộc tính pa k (độc lập xác suất cục bộ). Pha huấn luyện của mạng Bayes giống như pha huấn luyện của mô hình Bayes ngây thơ. Theo đó, ta cần xác định tất cả các phân bố p(xk pa ) trong Định nghĩa 12.1. Lưu ý rằng phân bố này là k | phân bố của một thuộc tính xk nên rất dễ ước lượng (xem Mục 12.2). 12.4 Trường ngẫu nhiên Markov Trường ngẫu nhiên Markov là một dạng mô hình đồ thị xác suất dựa trên đồ thị vô hướng. Trước khi định nghĩa trường ngẫu nhiên Markov, ta cần một số khái niệm trong đồ thị G = V,E . ⟨ ⟩ • Đồ thị con đầy đủ (clique) là một đồ thị con C của G có cạnh nối tất cả các cặp đỉnh. • Đồ thị con đầy đủ lớn nhất là đồ thị con đầy đủ mà nếu thêm bất cứ đỉnh nào sẽ không còn là đồ thị con đầy đủ. • Tập tất cả các đồ thị con đầy đủ lớn nhất đặt tên là . C Định nghĩa 12.10 (Trường ngẫu nhiên Markov). Trường ngẫu nhiên Markov được biểu diễn bằng đồ thị vô hướng G = V,E thể ⟨ ⟩ hiện phân bố xác suất có khai triển xác suất liên hợp thành nhân tử 1 (cid:89) p(x1,x2,...,xm) = ψ (x ). C C Z C∈C Trong đó nhân tử ψ (x ) 0 gọi là hàm thế năng của đồ thị con C C ≥ đầy đủ C còn Z là hằng số, còn gọi là hàm phân hoạch, để biểu thức vế phải là một xác suất (có tổng xác suất bằng 1).

<!-- Page 372 (Heavy) -->
Nếu đặt ψ C ( x C ) = e -E C ( x C ) , ta gọi E C ( x C ) là hàm năng lượng của C . Khi đó

<!-- formula-not-decoded -->

Định nghĩa 12.11 (Chia cắt) . Xét ba tập đỉnh X,Y,Z rời nhau. Tập đỉnh Z chia cắt tập đỉnh X và tập đỉnh Y nếu mọi đường đi từ X đến Y đều phải đi qua một đỉnh trong Z .

Định lý 12.12 (Hammersley-Clifford) . Nếu các nhân tử ψ C ( x C ) là các hàm số dương thì Z chia cắt X và Y khi và chỉ khi X và Y độc lập xác suất khi biết giá trị của Z .

## 12.4.1 Đồ thị nhân tử

Cả hai mô hình đồ thị xác suất mạng Bayes và trường ngẫu nhiên Markov đều có thể biểu diễn dưới dạng đồ thị nhân tử do xác suất liên hợp p ( x 1 , . . . , x m ) đều được phân tích thành nhiều nhân tử, mỗi nhân tử là một hàm trên một tập con các thuộc tính

Hình 12.4: Một đồ thị nhân tử có 3 nhân tử.

<!-- image -->

Trong đó, S là một tập con các thuộc tính, x S là giá trị các thuộc tính trong S . Khi vẽ đồ thị nhân tử, ta dùng biểu diễn đồ thị hai

<!-- Page 373 -->
## 12.5 SUY LUẬN CHÍNH XÁC TRÊN ĐỒ THỊ DẠNG CÂY 347 phía: một bên là tập thuộc tính, một bên là các nhân tử.

Có cạnh nối giữa một nhân tử f và một thuộc tính xk nếu thuộc tính đó nằm S trong tập đầu vào của nhân tử, xk S (Hình 12.4) mô tả một đồ thị ∈ nhân tử có ba nhân tử p(x1,...,x4) = f (x1,x2) f (x2,x3,x4) 1 2 × × f (x1,x3,x4). 3 12.5 Suy luận chính xác trên đồ thị dạng cây Khi mạng Bayes và trường ngẫu nhiên Markov dựa trên đồ thị là cây (đồ thị không có chu trình), đồ thị nhân tử cũng sẽ là cây. Khi đó tồn tại thuật toán suy luận chính xác rất hiệu quả trên mô hình đồ thị. Suy luận trên mô hình đồ thị cho phép trả lời các câu hỏi phong phú hơn nhiều các mô hình phân lớp hoặc hồi quy mà chúng ta đã tìm hiểu. Có thể kể đến một số câu hỏi quan trọng của phép suy luận như: • Tính p(y X) trong đó y là một đỉnh còn X là tập con các đỉnh | mà ta biết giá trị. • Tính y⋆ = arg max p(y X), tìm nhãn y có xác suất cao nhất khi y | biết X. Đây là câu hỏi thường thấy trong các bài toán phân lớp, hồi quy. • Tính p(Y X) trong đó X,Y là các tập đỉnh rời nhau. | • Tính Y ⋆ = arg max p(Y X), tìm tập các nhãn Y có xác suất Y | cao nhất khi biết X. Đây là câu hỏi thường thấy trong bài toán tìm kiếm nhãn cho một cấu trúc dữ liệu phức tạp như chuỗi văn bản, âm thanh, hình ảnh. Thuật toán suy luận trên đồ thị nhân tử dạng cây gồm thuật toán tổng-tích và thuật toán max-tổng.

<!-- Page 374 (Heavy) -->
## 12.5.1 Tính xác suất biên của một đỉnh

Đầu tiên, ta tìm hiểu thuật toán tính xác suất biên của một đỉnh p ( x ) . Ta có công thức xác suất liên hợp:

<!-- formula-not-decoded -->

Hình 12.5: Cây con trong đồ thị nhân tử.

<!-- image -->

Để tính p ( x ) , chúng ta xét các nhân tử f S có nối với x tạo thành một cây con có gốc là f S (xem Hình 12.5). Nếu ta nhóm tất cả các nhân tử trong cây con này lại thành một đại lượng F S ( x, X s ) trong đó F S là tích các nhân tử trong cây con, X S là tất cả các đỉnh thuộc tính trong cây con đó, Công thức (12.7) trên trở thành

<!-- formula-not-decoded -->

<!-- Page 375 (Heavy) -->
Sử dụng tính chất X S là các tập rời nhau nên có thể tráo đổi tổng và tích, tiếp tục biến đổi ta thu được công thức sau:

<!-- formula-not-decoded -->

với ne( x ) là tập các nhân tử f S có nối với x . Ta gọi đại lượng

<!-- formula-not-decoded -->

là thông điệp từ nút nhân tử f S tới nút thuộc tính x .

Để tính được thông điệp trên, nhận thấy rằng, mỗi đỉnh thuộc tính u nối với f S lại tương ứng với một cây con gốc u . Ta lại nhóm tất cả các nhân tử của từng cây con lại để thu được công thức như sau:

<!-- formula-not-decoded -->

trong đó, x S = { x, u 1 , . . . u k } là các đỉnh thuộc tính của nhân tử f S , G ( u i , X u i ) là tích các nhân tử trong cây con gốc u i , X u i là tất cả các đỉnh còn lại của cây con này. Tiếp tục khai triển từ các đỉnh u ∈ ne( f S ) \ { x } , với ne kí hiệu là lân cận của một đỉnh, ta thu được:

<!-- formula-not-decoded -->

Ta gọi đại lượng

<!-- formula-not-decoded -->

<!-- Page 376 (Heavy) -->
là thông điệp từ nút thuộc tính u đến nút nhân tử f S .

Tiếp tục, khai triển bằng cách sử dụng đẳng thức G u ( u, X u ) = ∏ f ℓ ∈ ne( u ) \ f S F ℓ ( u, X uℓ ) để thay vào công thức trên ta được

<!-- formula-not-decoded -->

Hai công thức (12.11) và (12.12) được dùng để lan truyền các thông điệp trên đồ thị nhân tử giữa các nút thuộc tính và các nút nhân tử của chúng. Riêng các trường hợp ở các nút lá ta xét hai trường hợp sau:

- Nếu f S là nút lá thì µ f S → x ( x ) = f S ( x ) .
- Nếu u là nút lá thì µ u → f S ( u ) = 1 .

Thuật toán 12.3 Thuật toán tính p ( x ) cho mọi thuộc tính x trên cây

- 1: procedure TreeInference ( G )
- 2: Chọn một nút gốc r và xây dựng cây với r là gốc
- 3: (Truyền đi lên) : Từ các lá, tính thông điệp µ f → x truyền dần lên đến r
- 4: (Truyền đi xuống) : Khi r nhận đủ thông điệp, truyền ngược các thông điệp từ r về các lá
- 5: (Tổng hợp) : Với mỗi nút x , tính xác suất:

<!-- formula-not-decoded -->

- 6: return p ( x ) cho mọi x
- 7: end procedure

<!-- Page 377 (Heavy) -->
Tính p ( x S ) khi x S là các thuộc tính của nhân tử f S . Bằng các luận giải như trên ta có

<!-- formula-not-decoded -->

## 12.5.2 Tính xác suất cực đại

Trong mục này, ta tìm hiểu thuật toán tổng lớn nhất để tính giá trị cực đại của xác suất liên hợp

<!-- formula-not-decoded -->

với max là hàm lấy giá trị lớn nhất.

Nếu ta lấy logarit cả hai vế và sử dụng tính chất đồng biến của logarit thì ta thu được phương trình sau

<!-- formula-not-decoded -->

Ngoài ra, nhận thấy tính chất phân phối của phép cộng với phép max (giống như tính chất phân phối của phép nhân với phép cộng)

<!-- formula-not-decoded -->

Nên thuật toán để tính max x V ∑ S ln f S ( x S ) sẽ giống hệt như thuật toán tính ∑ V \{ x } ∏ S f S ( x S ) , chỉ cần thay phép nhân bằng phép cộng, phép cộng bằng phép max . Cụ thể ta có biến đổi công thức như sau:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- Page 378 (Heavy) -->
nếu u là nút lá

<!-- formula-not-decoded -->

nếu f S là nút lá

<!-- formula-not-decoded -->

xác suất cực đại là

<!-- formula-not-decoded -->

Các công thức trên được áp dụng để tính p max bằng cách lan truyền các thông điệp từ lá đến một nút thuộc tính bất kì được chọn làm gốc. Để lần ngược lại cấu hình các thuộc tính x k , ta phải lưu lại bộ giá trị u 1 , . . . , u K là cực trị ứng với mỗi giá trị của x trong công thức (12.17).

## 12.6 Mô hình Markov ẩn HMM

Trong các mục trước của chương, chúng ta đã tìm hiểu mô hình đồ thị xác suất tổng quát bao gồm mạng Bayes (đồ thị có hướng) và trường ngẫu nhiên Markov (đồ thị vô hướng). Trong mục này, chúng ta tìm hiểu mô hình Markov ẩn (HMM - Hidden Markov Model) là một mô hình mạng Bayes chuyên dùng để mô hình hoá dữ liệu dạng chuỗi. Mô hình HMM có ứng dụng trong xử lý ngôn ngữ tự nhiên, xử lý tiếng nói, tin sinh học. Đây là những lĩnh vực có dữ liệu dạng chuỗi rất lớn. Mô hình HMM mô tả quá trình sinh ra dữ liệu chuỗi gồm các bước sau:

- Tại thời điểm 0, hệ thống ở một trạng thái q 0 ∈ S là tập các trạng thái.

<!-- Page 379 -->
## 12.6 MÔ HÌNH MARKOV ẨN HMM 353 • Hệ thống trải qua các trạng thái theo thời gian, trạng thái q ở t thời điểm t chỉ phụ thuộc vào trạng thái q ở thời điểm t 1. t−1 − • Tại mỗi thời điểm, tuỳ thuộc vào trạng thái hiện tại q , hệ thống t sinh ra dữ liệu quan sát được o V . t ∈ Ví dụ 12.13 (Mô hình âm thanh).

Mô hình HMM sử dụng một tập rời rạc các trạng thái S = s ,s ,...,s . 1 2 N { } Tập V các dữ liệu có thể quan sát được tuỳ thuộc vào từng nhiệm vụ. • V = v ,v ,...,v rời rạc: dành cho nhiệm vụ xử lý ngôn ngữ 1 2 M { } (tập từ vựng), tin sinh học (DNA, protein) hoặc khi dữ liệu đã được phân cụm, rời rạc hoá. • V = Rm liên tục: dành cho nhiệm vụ có dữ liệu liên tục như mô hình hoá âm thanh (acoustic models). Để tiện trình bày, chúng ta sẽ bắt đầu với tập V rời rạc. Mô hình HMM sử dụng các tham số π = P(q = s ) : xác suất để s là trạng thái đầu tiên i 0 i i a = P(q = s q = s ) : xác suất chuyển từ s sang s ij t+1 j t i i j | b (v ) = P(o = v q = s ) : xác suất sinh v từ trạng thái s i k t k t i k i | Ta gộp cả ba bộ tham số lại thành một bộ Θ = (A,B,π). Như vậy, quá trình lấy mẫu một chuỗi dữ liệu có O = o o ...o 1 2 T có độ dài T gồm các bước sau: 1. Lấy mẫu trạng thái đầu tiên q từ phân bố π 0

<!-- Page 380 (Heavy) -->
Hình 12.6: Mạng Bayes cho mô hình HMM.

<!-- image -->

2. Lần lượt lấy mẫu các trạng thái q 1 , q 2 , . . . , q T từ trạng thái trước đó theo phân bố A = [ a ij ]
3. Lấy mẫu dữ liệu o t từ trạng thái q t theo phân bố b i ( v k )

Biễu diễn mạng Bayes của mô hình HMM sinh dữ liệu dạng chuỗi ở Hình 12.6. Trong đó, các nút tròn thể hiện các trạng thái ẩn (hidden) còn các nút vuông là dữ liệu quan sát được.

Xác suất liên hợp của mô hình HMM gồm nhiều nhân tử tương ứng với các cạnh của đồ thị và trạng thái ban đầu

<!-- formula-not-decoded -->

Với mô hình HMM, có ba bài toán chính:

1. B1 (suy luận): Cho Θ và chuỗi dữ liệu O , hỏi xác suất P ( O ) là bao nhiêu?
2. B2 (suy luận): Cho Θ và chuỗi dữ liệu O , hỏi chuỗi trạng thái Q = q 1 q 2 . . . q T nào có xác suất cực đại?

<!-- formula-not-decoded -->

3. B3 (huấn luyện): Cho bộ dữ liệu là tập các chuỗi O 1 , O 2 , . . . , , hãy tìm bộ tham số Θ hợp lý nhất với bộ dữ liệu này.

<!-- Page 381 -->
## 12.6 MÔ HÌNH MARKOV ẨN HMM 355 12.6.1 Bài toán suy luận xác suất Ta sẽ sử dụng thuật toán suy luận trên mạng Bayes lan truyền các thông điệp trên các nút của đồ thị nhân tử tương ứng của mô hình (cid:80) HMM để tính P(O Θ) = P(Q,O Θ). | Q | Nếu chọn cách truyền thông điệp từ trái qua phải, ta có thủ tục lan truyền tới.

Sau khi đơn giản hoá các công thức lan truyền thông điệp, chúng ta đặt α (i) = µ (s ) = P(q = s ,o o ...o Θ) t →qt i t i 1 2 t | thì ta có công thức truy hồi sau: α (j) = π 0 j (cid:34) (cid:35) N (cid:88) α (j) = α (i)a b (o ) t+1 t ij j t+1 i=1 Xác suất của chuỗi được tính bởi công thức n (cid:88) P(O Θ) = α (i) T | i=1 Nếu chọn cách truyền thông điệp ngược lại từ phải qua trái, ta có thủ tục lan truyền ngược. Tương tự biến đổi ở trên, ta đặt β (i) = µ (s ) = P(o o ...o q = s ,Θ) t qt← i t+1 t+2 t | t i thì ta thu công thức truy hồi sau β (i) = 1 T N (cid:88) β (i) = β (j)a b (o ). t t+1 ij j t+1 i=1 Xác suất của chuỗi được tính bởi công thức n (cid:88) P(O Θ) = β (i)π . 0 i | i=1

<!-- Page 382 -->

<!-- Page 383 -->
## 12.6 MÔ HÌNH MARKOV ẨN HMM 357 ξ (i,j) = P(q = s ,q = s O,Θ) t t i t+1 j | P(q = s ,q = s ,O Θ) t i t+1 j = | P(O Θ) | α (i)a b (o )β (j) t ij j t+1 t+1 = (12.31) P(O Θ) | γ (i) = P(q = s O,Θ) t t i | N (cid:88) = ξ (i,j) (12.32) t j=1 Đại lượng ξ (i,j) là xác suất để ở hai thời điểm t,t + 1, hệ thống t lần lượt ở các trạng thái s và s .

Đại lượng γ (i) là xác suất để hệ i j t thống ở trạng thái s tại thời điểm t. i Việc ước lượng lại bộ tham số được thực hiện như sau π γ (i) (12.33) i 0 ← (cid:80)T−1 ξ (i,j) a t=0 t (12.34) ij ← (cid:80)T−1 γ (i) t=0 t (cid:80)T γ (i) b (v ) t=1,ot=v k t (12.35) i k ← (cid:80)T γ (i) t=1 t Thuật toán 12.4 cho phép huấn luyện mô hình HMM từ một chuỗi dữ liệu O. Nếu tập dữ liệu huấn luyện có nhiều xâu O(1),O(2),..., O(n), ta chỉ cần sửa các công thức ước lượng tham số như sau: n 1 (cid:88) π γ(ℓ)(i) (12.36) i ← n 0 ℓ=1 (cid:80)n (cid:80)T(ℓ)−1 ξ(ℓ)(i,j) a ℓ=1 t=0 t (12.37) ij ← (cid:80)n (cid:80)T(ℓ)−1 γ(ℓ)(i) ℓ=1 t=0 t (cid:80)n (cid:80)T(ℓ) γ(ℓ)(i) ℓ=1 t=1,o(ℓ)=v t b (v ) t k (12.38) i k ← (cid:80)n (cid:80)T(ℓ) γ(ℓ)(i) ℓ=1 t=1 t

<!-- Page 384 -->

<!-- Page 385 -->
## 12.7 TRƯỜNG NGẪU NHIÊN CÓ ĐIỀU KIỆN 359 Trong đó, ℓ là chỉ số của chuỗi dữ liệu O(ℓ) và các đại lượng ξ(ℓ),γ(ℓ) t t là ξ,γ tính cho chuỗi dữ liệu này. 12.7 Trường ngẫu nhiên có điều kiện Trường ngẫu nhiên có điều kiện (CRF - Conditional Random Field) là một trường ngẫu nhiên Markov dựa trên đồ thị vô hướng.

Mô hình CRF mô tả xác suất hậu nghiệm p(y x), trong đó, y = y y ...y 1 2 T | là các nhãn cần dự đoán, x là tất cả các đặc trưng đầu vào. Trường hợp dự đoán trên một chuỗi, có thể x được chia thành x x ...x là 1 2 T đặc trưng của các vị trí trong chuỗi. Lý do mô hình CRF không mô tả xác suất liên hợp p(x,y) là do x có thể có tới hàng chục nghìn đặc trưng. Trong khi đó, chỉ cần p(y x) là đủ để giải bài toán phân | lớp y⋆ = arg max p(y x). y | Định nghĩa 12.14 (Trường ngẫu nhiên có điều kiện). Xét một đồ thị nhân tử G trên cả x và y. Nếu với mọi x ta có p(y x) phân tích | thành nhân tử dựa trên các nút nhân tử trong G, ta nói x,y là một trường ngẫu nhiên có điều kiện. Gọi ψ A là tập các nhân tử trong G. Ta có công thức phân { a }a=1 tích A 1 (cid:89) p(y x) = ψ (y ,x ), (12.39) a a a | Z(x) a=1 trong đó, x ,y là các thuộc tính đầu vào của nhân tử ψ . Trong a a a công thức trên, ta coi x là các hằng số chứ không phải biến ngẫu a nhiên. Để bài toán huấn luyện và suy luận có thể giải dễ dàng hơn, người ta thường chọn các nhân tử có logarit là một tổ hợp tuyến

<!-- Page 386 (Heavy) -->
tính của các hàm đặc trưng sau:

<!-- formula-not-decoded -->

Công thức (12.40) mỗi nhân tử ψ a được tính nhờ K a đặc trưng. Các trọng số θ ak thể hiện sự quan trọng của từng đặc trưng. Thường trong đồ thị G có sự lặp đi lặp lại của các cấu trúc nhân tử thì các cấu trúc này sẽ sử dụng các trọng số và hàm đặc trưng giống nhau. Ví dụ, trong một cấu trúc chuỗi thì nhân tử ψ ( y t , y t -1 , x t ) sẽ giống nhân tử ψ ( y t +1 , y t , x t +1 ) , sử dụng chung trọng số θ và tập hàm đặc trưng.

Ví dụ 12.15 (Mô hình HMM là một CRF) .

Kết hợp các công thức trên ta được

<!-- formula-not-decoded -->

với Θ = { θ ak } là tập tất cả các trọng số và F ( y, x ) = { f ak ( y a , x a ) } là tập tất cả các hàm đặc trưng.

## 12.7.1 Pha huấn luyện

Giả sử ta có tập huấn luyện D = { ( x i , y i ) } , i = 1 , 2 , . . . , n . Theo nguyên lý ước lượng hợp lý cực đại, ta sẽ tìm tham số Θ ⋆ cực đại hoá xác suất của dữ liệu tức là ta cần tìm Θ ⋆ theo công thức sau:

<!-- formula-not-decoded -->

<!-- Page 387 (Heavy) -->
Cũng giống như thuật toán huấn luyện mô hình hồi quy Logistic, xuất phát từ một nghiệm Θ , ta cập nhật nghiệm này theo hướng của đạo hàm

<!-- formula-not-decoded -->

Ta có khai triển của đạo hàm của hàm phân phối Z (Θ) như sau:

<!-- formula-not-decoded -->

Trong đó kì vọng được tính từ phân bố p ( y | x ) dựa trên bộ tham số Θ . Như vậy, bài toán huấn luyện được quy về bài toán suy luận, ta phải tính được kỳ vọng của các hàm đặc trưng trong véc-tơ

<!-- formula-not-decoded -->

Ta có công thức tính

<!-- formula-not-decoded -->

Trong đó, p ( y a | x ) được tính từ công thức (12.13) vì p ( y | x ) có khai triển theo đồ thị nhân tử như trong công thức (12.39).

## 12.7.2 Pha suy luận

Bước (b) và (c) trong Thuật toán (12.5) chính là một pha suy luận của mô hình CRF. Tổng quát hơn, các suy luận trên mạng CRF bao gồm một số tác vụ cơ bản sau:

<!-- Page 388 (Heavy) -->
## Thuật toán 12.5 Thuật toán huấn luyện mô hình CRF cho đồ thị nhân tử dạng cây

- 1: procedure TrainCRF ( D,λ )
- 2: Khởi tạo ngẫu nhiên các tham số Θ
- 3: while chưa hội tụ do ▷ Thực hiện cho mỗi mẫu ( x, y ) trong D
- 4: for all ( x, y ) ∈ D do
- 5: Chọn một nút gốc trong đồ thị nhân tử
- 6: Thực hiện lan truyền thông điệp hai chiều trên cây:

<!-- formula-not-decoded -->

Tính xác suất biên gần đúng:

<!-- formula-not-decoded -->

Tính kỳ vọng đặc trưng:

7:

8:

<!-- formula-not-decoded -->

- 9: Cập nhật tham số:

<!-- formula-not-decoded -->

10: end for

11: end while

12: return Θ

13: end procedure

<!-- Page 389 (Heavy) -->
- Tính xác suất p ( y a | x ) cho từng nhân tử.
- Tính kì vọng E y a [ f a ( y a , x a )] cho từng nhân tử.
- Tìm arg max y a p ( y a | x ) cho từng nhân tử
- Tìm kiếm toàn bộ bộ nhãn y ⋆ = arg max y p ( y | x ) .

Hai bài toán đầu đơn giản, chúng ta đã thấy ở bước (b) và (c) của Thuật toán (12.5). Hai bài toán cuối là bài toán tối ưu tổ hợp NP-khó, tức là không thể giải một cách hiệu quả trong thời gian chấp nhận được với mọi trường hợp. Thay vào đó, người ta dùng các thuật toán tìm kiếm xấp xỉ để tìm một nghiệm chấp nhận được. Cụ thể chúng ta cần tìm giá trị y ⋆ sao cho

<!-- formula-not-decoded -->

Riêng đối với một số cấu trúc mạng, ta có thuật toán tìm kiếm hiệu quả

- Đồ thị nhân tử dạng cây: sử dụng thuật toán Viterbi (giống mô hình HMM). Chọn một nút y ∗ làm gốc, ta sử dụng các công thức (12.17) và (12.18), áp dụng vào mạng CRF được

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

nếu u là nút lá

<!-- formula-not-decoded -->

<!-- Page 390 (Heavy) -->
nếu ψ a là nút lá

<!-- formula-not-decoded -->

xác suất cực đại là

<!-- formula-not-decoded -->

Để lần ngược lại kết quả y ⋆ , ta cần lưu trữ nghiệm của max trong công thức (12.44).

- Đồ thị nhân tử chỉ gồm các nhân tử của cặp thuộc tính

<!-- formula-not-decoded -->

và hàm ϕ ij là hàm sub-modular: sử dụng thuật toán luồng cực đại.

## 12.8 Tình huống áp dụng:

Bài toán gán nhãn từ loại

Trong mục này, chúng ta cùng tìm hiểu cách áp dụng Trường ngẫu nhiên có điều kiện (CRF) cho bài toán gán nhãn từ loại (POS Tagging). Chúng ta sẽ sử dụng tập dữ liệu sẵn có từ thư viện NLTK, giúp dễ dàng thực hành mà không cần thu thập dữ liệu phức tạp.

- Chuẩn bị dữ liệu: sử dụng thư viện NLTK để tải tập dữ liệu (treebank) gán nhãn từ loại và chia thành tập huấn luyện (80%) và tập kiểm tra (20%). Bộ dữ liệu treebank trong NLTK được trích xuất từ các bài viết của Tạp chí phố Wall, là một phần của bộ dữ liệu Penn Treebank.

<!-- Page 391 -->
## 12.8 TÌNH HUỐNG ÁP DỤNG:

BÀI TOÁN GÁN NHÃN TỪ LOẠI 365 – Nguồn dữ liệu: các bài báo theo các chủ đề về kinh tế, tài chính và tin tức chung. – Kích thước: 3914 câu với tổng cộng hơn 100.000 từ đã được gán nhãn từ loại. – Nhãn từ loại: gồm 45 nhãn khác nhau (ví dụ: NN cho danh từ số ít, VB cho động từ nguyên thể, JJ cho tính từ, . cho dấu chấm, v.v.). • Tiền xử lý dữ liệu: Tiếp theo, ta trích xuất các đặc trưng từ mỗi từ trong câu gồm từ hiện tại, từ trước đó, từ sau đó và các thuộc tính như từ có viết hoa hay không. Các đặc trưng này sẽ là đầu vào cho mô hình CRF. – Trích xuất đặc trưng: Mỗi từ được gán các đặc trưng như dạng chữ thường (word.lower), viết hoa (isupper), viết hoa chữ cái đầu (istitle) và là số (isdigit). – Ngữ cảnh: Bao gồm từ trước (-1:word.lower) và từ sau (+1:word.lower) để mô hình hóa mối quan hệ chuỗi. – Đánh dấu ranh giới: Thêm đặc trưng BOS (bắt đầu câu) và EOS (kết thúc câu) để xác định vị trí trong câu. – Tách nhãn: Tách nhãn từ loại (ví dụ: NN, VB) từ mỗi từ để tạo đầu ra cho mô hình. – Định dạng đầu vào: chuyển thành cặp đặc trưng (X) và nhãn (y) cho tập huấn luyện và kiểm tra. • Xây dựng mô hình CRF: Mô hình CRF được xây dựng bằng thư viện sklearn-crfsuite. Thư viện cho phép thiết lập các tham số như thuật toán huấn luyện (lbfgs), hệ số điều chuẩn (c1, c2), số lần lặp tối đa và bật tính năng tạo tất cả các chuyển tiếp có thể để mô hình hóa tốt hơn. • Huấn luyện mô hình: sử dụng hàm fit để huấn luyện. trên tập dữ liệu huấn luyện đã tiền xử lý.

<!-- Page 392 -->

<!-- Page 393 -->
## 12.9 TỔNG KẾT CHƯƠNG 367 • Tính P(cid:98)(y) và P(cid:98)(xk y) cho mỗi y và k, sử dụng làm trơn | Laplace với hằng số 1. • Sử dụng các xác suất này để ra quyết định xem mẫu x1 = 1,x2 = 0,x3 = 1 thuộc lớp nào. 2.

Chứng minh rằng trong mô hình Bayes ngây thơ, việc chọn lớp y∗ = arg max P(y x) tương đương với tối ưu hóa hàm log- y | likelihood (cid:88) y∗ = arg maxlog P(y) + log P(xk y). y | k 3. Cho mạng Bayes với đồ thị A B C và A D. Chứng → → → minh rằng B D-chia cắt A và C và A độc lập với C khi biết B. Hơn nữa, hãy kiểm tra xem C có độc lập với D khi biết A hay không. 4. [Tìm hiểu] Hãy tìm hiểu chứng minh định lý Hammersley-Clifford cho trường ngẫu nhiên Markov. 5. Cho đồ thị nhân tử dạng cây với các nhân tử trong bảng 12.1. Bảng 12.1: Giá trị của các nhân tử trong đồ thị nhân tử dạng cây Nhân tử Biến x x Giá trị 1 2 (0,0) 0 0 0.6 (0,1) 0 1 0.4 ψ (x ,x ) 12 1 2 (1,0) 1 0 0.3 (1,1) 1 1 0.7 (0,0) 0 0 0.5 (0,1) 0 1 0.5 ψ (x ,x ) 23 2 3 (1,0) 1 0 0.8 (1,1) 1 1 0.2

<!-- Page 394 -->

<!-- Page 395 -->
Tài liệu tham khảo [1] McCallum, A., and Nigam, K., A comparison of event models for Naive Bayes text classification, Proceedings of the AAAI Workshop on Learning for Text Categorization, pp. 41–48, 1998. [2] Pearl, J., Reverend Bayes on inference engines: A distributed hierarchical approach, Proceedings of the National Conference on Artificial Intelligence, pp. 133–136, 1982. [3] Lauritzen, S. L., and Spiegelhalter, D. J., Local computations with probabilities on graphical structures and their application to expert systems, Journal of the Royal Statistical Society: Se- ries B, vol. 50, no. 2, pp. 157–224, 1988. [4] Geman, S., and Geman, D., Stochastic relaxation, Gibbs distri- butions, and the Bayesian restoration of images, IEEE Trans- actions on Pattern Analysis and Machine Intelligence, vol. 6, no. 6, pp. 721–741, 1984. [5] Rabiner, L. R., A tutorial on hidden Markov models and se- lected applications in speech recognition, Proceedings of the IEEE, vol. 77, no. 2, pp. 257–286, 1989.

<!-- Page 396 -->
370 TÀI LIỆU THAM KHẢO [6] Lafferty, J. D., McCallum, A., and Pereira, F. C. N., Condi- tional random fields: Probabilistic models for segmenting and labeling sequence data, Proceedings of the 18th International Conference on Machine Learning, pp. 282–289, 2001.

<!-- Page 397 -->
# Chương 13 Triển khai mô hình học máy Xây dựng mô hình chỉ là bước khởi đầu trong chuỗi giá trị của Học máy.

Chương 13 trình bày cách đưa mô hình học máy vào vận hành trong môi trường thực tế, giúp người học nắm bắt toàn bộ vòng đời triển khai mô hình. Nội dung chương bao gồm các bước quan trọng như tiền xử lý dữ liệu, đóng gói mô hình, triển khai dịch vụ, giám sát hiệu suất và tối ưu hoá sau triển khai. Chương cũng giới thiệu các công cụ và nền tảng phổ biến trong triển khai hệ thống Học máy hiện đại, như Docker để tạo môi trường độc lập, FastAPI để xây dựng dịch vụ RESTful và CI/CD để tự động hóa quy trình triển khai liên tục. Thông qua các ví dụ thực tiễn, chương cung cấp kiến thức thiết yếu để chuyển đổi một mô hình từ môi trường nghiên cứu sang hệ thống hoạt động ổn định và có thể mở rộng trong thực tế.

<!-- Page 398 (Heavy) -->
Hình 13.1: Quá trình phát triển, triển khai mô hình Học máy.

<!-- image -->

## 13.1 Vòng đời phát triển mô hình học máy

Quá trình phát triển và triển khai mô hình học máy bắt đầu từ nhu cầu sản xuất, kinh doanh của tổ chức. Nhà lãnh đạo đặt ra các mục tiêu cần đạt đối với phần mềm. Nhóm phát triển sẽ phân tích xem bài toán có phù hợp với cách tiếp cận học máy hay không, tức là có xác định được nhiệm vụ, độ đo hiệu năng và có sẵn dữ liệu kinh nghiệm hay không. Nếu câu trả lời là có , nhóm phát triển sẽ khởi động vòng đời phát triển mô hình học máy (Hình 13.1).

1. Thu thập và chuẩn bị : Dữ liệu được thu thập từ lịch sử hoạt động, sau đó được chuẩn hoá, làm sạch và chuyển thành định dạng mô hình có thể xử lý. Dữ liệu được chia thành tập huấn luyện , tập kiểm thử (dành cho phát triển) và tập kiểm tra (dành cho đánh giá độc lập, không dùng để tinh chỉnh mô hình).
2. Trích chọn đặc trưng dữ liệu : Người phát triển phân tích dữ liệu để chọn đặc trưng phù hợp, loại bỏ đặc trưng nhiễu hoặc dư thừa. Có thể tạo thêm đặc trưng mới từ các đặc trưng có sẵn. Việc này giúp mô hình học hiệu quả hơn và phản ánh đúng nhiệm vụ.
3. Huấn luyện mô hình : Chọn và huấn luyện mô hình học máy phù

<!-- Page 399 -->
## 13.2 THU THẬP VÀ TIỀN XỬ LÝ DỮ LIỆU 373 hợp bằng dữ liệu huấn luyện.

Mô hình được tinh chỉnh dần để hiệu suất P cải thiện theo thời gian và số lượng mẫu huấn luyện. 4. Đánh giá mô hình: Đánh giá mô hình bằng dữ liệu kiểm thử để đảm bảo mô hình đạt yêu cầu và hoạt động tốt trên dữ liệu chưa từng thấy. Không dùng dữ liệu huấn luyện để đánh giá để tránh thiên lệch. 5. Triển khai mô hình: Sau khi đánh giá, mô hình được đóng gói và chuyển sang định dạng thích hợp (ví dụ: tối ưu bằng TensorRT, ONNX). Sau đó được tích hợp vào hệ thống thực (máy chủ, ứng dụng web, v.v.). 6. Sử dụng mô hình: Mô hình được kết nối qua API để hệ thống dễ dàng gửi dữ liệu đầu vào và nhận kết quả. Mô hình thường được nạp sẵn vào bộ nhớ để giảm độ trễ và chia sẻ tài nguyên hiệu quả. 7. Giám sát mô hình: Khi mô hình vận hành, ta giám sát các chỉ số như thời gian xử lý, độ chính xác, lỗi và mức độ hài lòng. Có thể triển khai song song mô hình cũ–mới để so sánh (A/B testing). 8. Bảo trì mô hình: Dựa trên giám sát và yêu cầu mới, mô hình có thể cần cập nhật để cải thiện hiệu suất, mở rộng API, điều chỉnh đầu vào–đầu ra hoặc tái huấn luyện với dữ liệu mới thu thập. 13.2 Thu thập và tiền xử lý dữ liệu Dữ liệu đóng vai trò cốt lõi trong học máy, vì mô hình không thể hoạt động nếu không có dữ liệu đầu vào. Dữ liệu cung cấp thông tin để thuật toán học, nhận diện mẫu, dự đoán và tự động hóa quyết định. Tuy nhiên, không phải mọi dữ liệu đều có giá trị như nhau.

<!-- Page 400 -->

<!-- Page 401 -->
## 13.2 THU THẬP VÀ TIỀN XỬ LÝ DỮ LIỆU 375 • Dữ liệu thu thập theo thời gian thực:

Từ API, cảm biến, thiết bị IoT hoặc web scraping. Các phương pháp này cho phép cập nhật liên tục, mở rộng linh hoạt. Bất kể nguồn dữ liệu nào, quá trình thu thập cần đảm bảo tính đầy đủ, toàn vẹn và phù hợp với mục tiêu phân tích. Định dạng dữ liệu. Dữ liệu học máy có thể tồn tại dưới ba định dạng chính: • Cấu trúc: Dữ liệu bảng (CSV, SQL), dễ phân tích bằng các công cụ truyền thống, thích hợp với mô hình tuyến tính hoặc cây quyết định. • Phi cấu trúc: Văn bản tự nhiên, hình ảnh, âm thanh, video. Yêu cầu kỹ thuật đặc thù như NLP, xử lý ảnh, nhận dạng giọng nói. • Bán cấu trúc: Dữ liệu có tổ chức nhưng không cứng nhắc, ví dụ JSON, XML. Phù hợp cho các ứng dụng web, dữ liệu phân cấp hoặc linh hoạt. Việc hiểu rõ định dạng giúp lựa chọn đúng kỹ thuật xử lý và mô hình phù hợp. Lưu trữ và quản lý dữ liệu. Hệ thống học máy hiện đại yêu cầu lưu trữ hiệu quả và dễ dàng mở rộng: • Cơ sở dữ liệu quan hệ (RDBMS): Phù hợp dữ liệu có cấu trúc; sử dụng SQL để truy vấn; ví dụ: MySQL, PostgreSQL. • Cơ sở dữ liệu phi quan hệ (NoSQL): Dữ liệu bán cấu trúc hoặc phi cấu trúc; linh hoạt hơn RDBMS; ví dụ: MongoDB, Cassan- dra, DynamoDB.

<!-- Page 402 -->

<!-- Page 403 -->
## 13.2 THU THẬP VÀ TIỀN XỬ LÝ DỮ LIỆU 377 • Điền giá trị:

Sử dụng trung bình, trung vị, mode hoặc mô hình dự đoán (như hồi quy). Xử lý dữ liệu ngoại lai: • IQR: Loại các giá trị nằm ngoài [Q 1.5 IQR,Q +1.5 IQR]. 1 3 − × × • Z-score: Loại giá trị có điểm Z vượt quá ngưỡng (thường là Z > 3). | | Xử lý lỗi định dạng và chính tả : • Lỗi chính tả: Phát hiện và sửa bằng so khớp gần đúng, ví dụ với thư viện fuzzywuzzy. • Định dạng không đồng nhất: Chuẩn hóa ngày tháng, chữ viết hoa/thường, hoặc đơn vị đo lường. Làm sạch dữ liệu đúng cách giúp cải thiện chất lượng dữ liệu và hiệu năng mô hình. 13.2.3 Trích chọn đặc trưng Chúng ta đã đề cập đến một số kỹ thuật trích chọn đặc trưng trong Chương 10. Chuyển đổi dữ liệu. Đây là bước quan trọng trong tiền xử lý, giúp biến đổi dữ liệu thô thành dạng phù hợp với mô hình học máy. Chuyển đổi đúng cách giúp tăng độ chính xác, giảm độ lệch phân phối, đẩy nhanh tốc độ huấn luyện và cải thiện khả năng tổng quát hóa. Có một số kỹ thuật phổ biến như sau: • Chuẩn hoá Min-Max: Đưa dữ liệu về một khoảng cố định, thường là [0,1]. Phù hợp với dữ liệu có đơn vị đo khác nhau,

<!-- Page 404 -->

<!-- Page 405 -->
## 13.2 THU THẬP VÀ TIỀN XỬ LÝ DỮ LIỆU 379 • Dựa trên mô hình:

Dùng trọng số của mô hình tuyến tính (như Lasso), cây quyết định hoặc Random Forest để đánh giá tầm quan trọng của đặc trưng. • Rút trích tuần tự: Phương pháp gói thử nghiệm từng tổ hợp đặc trưng với mô hình thực tế để chọn tổ hợp tốt nhất. Việc chọn đúng đặc trưng giúp giảm độ nhiễu, rút ngắn thời gian huấn luyện và cải thiện khả năng tổng quát. Tạo đặc trưng. Là quá trình xây dựng đặc trưng mới từ dữ liệu gốc để mô hình học tốt hơn. Đây là công việc quan trọng nhưng thường mang tính sáng tạo và phụ thuộc vào kiến thức lĩnh vực. Một số ví dụ điển hình: • Tổ hợp đặc trưng: Kết hợp nhiều thuộc tính để tạo đặc trưng mới. Ví dụ: tỷ lệ giá/số phòng trong bài toán bất động sản. • Phân loại thời gian: Tách ngày thành các phần như ngày trong tuần, tháng, mùa, v.v. để phát hiện quy luật theo chu kỳ. • Làm rời: Phân nhóm giá trị liên tục thành các khoảng rời rạc. • Đếm và tần suất: Tạo đặc trưng thống kê như số lần xuất hiện của từ trong văn bản hoặc số giao dịch của khách hàng. • Embedding: Với dữ liệu dạng văn bản, danh mục hoặc đồ thị, có thể dùng kỹ thuật học sâu để tạo ra véc-tơ đặc trưng có tính ngữ nghĩa cao. Việc tạo và chọn đặc trưng tốt có thể ảnh hưởng mạnh mẽ đến hiệu suất mô hình, trong nhiều trường hợp, có tác động lớn hơn cả việc lựa chọn thuật toán, mô hình Học máy.

<!-- Page 406 -->

<!-- Page 407 -->
## 13.3 TRIỂN KHAI MÔ HÌNH HỌC MÁY 381 13.3.2 Chuẩn bị mô hình trước khi triển khai Lưu trữ và quản lý mô hình Lưu trữ mô hình là bước quan trọng nhằm đảm bảo mô hình có thể tái sử dụng, theo dõi và cải thiện.

Việc sử dụng định dạng lưu trữ phù hợp giúp tích hợp dễ dàng vào hệ thống triển khai. Một số công cụ phổ biến: • Pickle/Joblib: Dùng trong Python để lưu mô hình cơ bản. Joblib tối ưu hơn với mô hình có kích thước lớn. • TensorFlow SavedModel: Lưu trữ cấu trúc, trọng số và siêu tham số của mô hình TensorFlow, thuận tiện triển khai trên nhiều nền tảng. • ONNX: Định dạng mở hỗ trợ chuyển đổi mô hình giữa các framework như PyTorch và TensorFlow, phù hợp cho môi trường triển khai không đồng nhất. Để quản lý vòng đời mô hình, có thể dùng MLflow, công cụ mã nguồn mở hỗ trợ lưu trữ, so sánh, theo dõi hiệu suất và phiên bản mô hình. Việc theo dõi mô hình giúp đảm bảo mô hình triển khai là bản tốt nhất và có thể truy vết khi có sự cố. Kiểm thử và tối ưu mô hình Trước khi triển khai, cần đánh giá mô hình về độ chính xác, tốc độ phản hồi và mức sử dụng tài nguyên: • Độ chính xác: Kiểm tra chất lượng dự đoán trên tập kiểm tra để xác nhận mô hình đạt tiêu chuẩn chất lượng. • Thời gian phản hồi: Đo thời gian xử lý một yêu cầu, đặc biệt quan trọng với hệ thống thời gian thực.

<!-- Page 408 -->

<!-- Page 409 -->
## 13.3 TRIỂN KHAI MÔ HÌNH HỌC MÁY 383 • Kubernetes:

Quản lý và điều phối nhiều container ở quy mô lớn, hỗ trợ tự động mở rộng, cân bằng tải và đảm bảo tính khả dụng cao. Một số định dạng API phổ biến là: • REST API: Phổ biến và dễ triển khai; truyền dữ liệu qua HTTP với định dạng JSON/XML; phù hợp với ứng dụng web và di động. • gRPC: Hiệu suất cao hơn, truyền dữ liệu nhị phân, phù hợp với hệ thống phân tán hoặc thời gian thực yêu cầu độ trễ thấp. Việc đóng gói hiệu quả giúp mô hình dễ triển khai, bảo trì và tích hợp vào các dịch vụ hoặc hạ tầng hiện tại. 13.3.4 Các phương pháp triển khai mô hình Tùy vào yêu cầu hệ thống, có thể triển khai mô hình theo ba hướng chính: • Triển khai tại chỗ: Chạy mô hình trên máy chủ nội bộ của tổ chức. Ưu điểm: bảo mật cao, kiểm soát hoàn toàn. Nhược điểm: chi phí hạ tầng lớn, khó mở rộng. • Triển khai trên đám mây: Sử dụng nền tảng như AWS Sage- Maker, Google AI Platform. Ưu điểm: mở rộng linh hoạt, tích hợp tốt. Nhược điểm: chi phí phụ thuộc vào tài nguyên sử dụng. • Triển khai trên thiết bị biên: Mô hình chạy trực tiếp trên thiết bị IoT, điện thoại hoặc hệ nhúng. Ưu điểm: phản hồi nhanh, giảm tải hệ thống trung tâm. Nhược điểm: hạn chế về tài nguyên.

<!-- Page 410 -->

<!-- Page 411 -->
## 13.4 CÁC NỀN TẢNG HỖ TRỢ TRIỂN KHAI MÔ HÌNH 385 hợp công cụ giám sát và CI/CD giúp hệ thống luôn đạt hiệu suất tối ưu. 13.4 Các nền tảng hỗ trợ triển khai mô hình Triển khai mô hình học máy là quá trình phức tạp gồm đóng gói, quản lý, giám sát và tối ưu.

Việc sử dụng các công cụ hỗ trợ giúp đơn giản hoá quy trình và đảm bảo mô hình hoạt động hiệu quả trong môi trường sản xuất. 13.4.1 Công cụ đóng gói và triển khai Docker: Công cụ phổ biến để đóng gói mô hình cùng môi trường vào container độc lập, đảm bảo tính di động và nhất quán khi triển khai trên các hệ thống khác nhau. Kubernetes: Nền tảng mã nguồn mở quản lý và điều phối nhiều container. Hỗ trợ cân bằng tải, mở rộng tự động và đảm bảo tính sẵn sàng cao cho hệ thống. TensorFlow Serving: Giải pháp triển khai mô hình Tensor- Flow nhanh chóng, hỗ trợ phục vụ nhiều phiên bản mô hình, tối ưu cho ứng dụng web và API. TorchServe: Dịch vụ triển khai mô hình PyTorch, hỗ trợ cấu hình API REST, logging, batch inference và quản lý tài nguyên. 13.4.2 Công cụ quản lý và giám sát mô hình MLflow: Nền tảng mã nguồn mở hỗ trợ quản lý vòng đời mô hình (tracking, packaging, deployment). Giúp theo dõi, lưu trữ và tái sử dụng mô hình trong nhiều môi trường. Prometheus + Grafana: Prometheus thu thập chỉ số hệ thống và mô hình (latency, throughput, CPU/GPU); Grafana hiển thị trực quan bằng biểu đồ, hỗ trợ phát hiện và cảnh báo sự cố.

<!-- Page 412 -->

<!-- Page 413 -->
## 13.5 TÌNH HUỐNG ÁP DỤNG:

TRIỂN KHAI MÔ HÌNH QUA GIAO THỨC LẬP TRÌNH ỨNG DỤNG REST 387 xây dựng hệ thống triển khai học máy hiệu quả, linh hoạt và có thể mở rộng. 13.5 Tình huống áp dụng: Triển khai mô hình qua giao thức lập trình ứng dụng REST Trong thực tế, việc triển khai mô hình học máy thông qua giao thức lập trình ứng dụng REST giúp tích hợp vào các hệ thống dễ dàng và linh hoạt. Hướng dẫn này sử dụng thư viện FastAPI để triển khai một mô hình học máy đơn giản cho bài toán phân loại hoa IRIS. Mô hình này sẽ nhận dữ liệu đầu vào từ người dùng thông qua API và trả về kết quả dự đoán. Chúng ta sẽ dựa trên mô hình Random Forest đã được huấn luyện trên tập dữ liệu IRIS, sử dụng thư viện scikit-learn để thực hiện các bước huấn luyện và lưu trữ mô hình. Các bước triển khai chính bao gồm: • Chuẩn bị thư viện: Trong bước này, chúng ta sẽ cài đặt các thư viện cần thiết để triển khai mô hình học máy, bao gồm FastAPI cho việc xây dựng API, scikit-learn cho việc huấn luyện mô hình và joblib để lưu trữ mô hình và các thư viện liên quan. Các thư viện được lưu trữ thông qua tệp requirements.txt để dễ dàng quản lý và cài đặt. • Huấn luyện mô hình: Trong bước này, chúng ta sẽ sử dụng tập dữ liệu IRIS để huấn luyện mô hình Random Forest và lưu trữ mô hình đã huấn luyện. Các bước triển khai chính người học có thể tham khảo các Chương 2 và 9 để hiểu rõ hơn về cách sử dụng thư viện sklearn để huấn luyện mô hình Random Forest trên tập IRIS. • Lưu trữ mô hình: Mô hình sau khi huấn luyện sẽ được lưu trữ dưới dạng tệp để có thể sử dụng lại trong các lần triển khai sau. Chú ý rằng việc lưu trữ này bao gồm toàn bộ tham số và quá

<!-- Page 414 -->

<!-- Page 415 -->
## 13.6 TỔNG KẾT CHƯƠNG 389 Đoạn mã 13.3:

Kết quả dự đoán nhận được { "prediction": 0 } Người đọc có thể tham khảo mã nguồn tại: https://gist.github. com/cuongtv312/cd68e6989b11cf48e8d8b5ed0d306e5c 13.6 Tổng kết chương Chương 13 nhấn mạnh tầm quan trọng của việc triển khai và quản lý mô hình Học máy một cách chuyên nghiệp và toàn diện. Từ khâu thu thập và làm sạch dữ liệu, đóng gói mô hình, xây dựng API đến giám sát hiệu suất sau triển khai, mỗi bước trong vòng đời mô hình đều đòi hỏi quy trình bài bản và sự phối hợp hiệu quả giữa các nhóm phát triển, vận hành và hạ tầng. Các công cụ như Docker, FastAPI và hệ thống CI/CD không chỉ hỗ trợ tự động hóa mà còn giúp đảm bảo tính ổn định, khả năng mở rộng và duy trì chất lượng của hệ thống Học máy trong môi trường thực tế. Nội dung chương trang bị cho người học kiến thức và kỹ năng thiết yếu để đưa mô hình từ nghiên cứu vào ứng dụng, đóng vai trò quan trọng trong việc xây dựng các hệ thống Học máy vận hành thực tế. Bài tập Dưới đây là các bài tập giúp sinh viên tìm hiểu và thực hành các công cụ phổ biến trong việc triển khai mô hình học máy. Sinh viên cần nghiên cứu, cài đặt và thực hành để nắm vững cách sử dụng từng công cụ.

<!-- Page 416 -->

<!-- Page 417 -->
Tài liệu tham khảo [1] Breck, E., Cai, S., Nielsen, E., Salib, M., and Sculley, D., The ML test score: A rubric for ML production readiness and tech- nical debt reduction, Proceedings of the IEEE International Conference on Big Data, pp. 1123–1132, 2017. [2] Polyzotis, N., Roy, S., Whang, S. E., and Zinkevich, M., Data management challenges in production machine learning, Pro- ceedings of the 2018 ACM International Conference on Man- agement of Data, pp. 1723–1726, 2018. [3] Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., et al., Hidden technical debt in ma- chine learning systems, Advances in Neural Information Pro- cessing Systems, vol. 28, pp. 2503–2511, 2015. [4] Abadi, M., Agarwal, A., Barham, P., Brevdo, E., Chen, Z., Citro, C., Corrado, G. S., et al., TensorFlow: Large-scale machine learning on heterogeneous systems, arXiv preprint arXiv:1603.04467, 2015. [5] Bergstra, J., and Bengio, Y., Random search for hyper- parameter optimization, Journal of Machine Learning Re- search, vol. 13, pp. 281–305, 2012.

<!-- Page 418 -->
392 TÀI LIỆU THAM KHẢO [6] M¨akinen, S., Skogstro¨m, E., Laaksonen, J., and Ja¨rvinen, H., Who needs MLOps: What data scientists seek to accomplish and how can MLOps help?, arXiv preprint arXiv:2010.13335, 2020. [7] Hazelwood, K., Bird, S., Brooks, D., Chintala, S., Diril, U., Dzhulgakov, D., Fawzy, M., et al., Applied machine learning at Facebook: A datacenter infrastructure perspective, Proceedings of the IEEE International Symposium on High-Performance Computer Architecture, pp. 620–629, 2018.

<!-- Page 419 -->
Chỉ mục Adam, 74 cường độ, 114 ANOVA, 285 cận dưới bằng chứng, 307 Bayes ngây thơ, 335 DQN, 229 bài toán hồi quy, 173 dữ liệu, 28 bài toán phân lớp, 26, 29 dữ liệu dạng chuỗi, 150 bản đồ đặc trưng, 118 dữ liệu ảnh, 114 bộ lọc, 118 bộ nhớ ngắn hạn dài, 158 entropy chéo, 60 Bộ nhớ đệm, 230 GAN, 322 bộ tự mã hoá biến phân, 281 GD, 75 bộ tự mã hóa sâu, 279 giá trị riêng, 183 C4.5, 48 CART, 194 HMM, 352 chiến lược huấn luyện, 137 hàm hợp lý, 301 chuỗi thời gian, 151 hàm kích hoạt, 58 chính sách tham lam, 224 hàm Lagrange, 91, 275 CIFAR10, 140 hàm lỗi, 174 CNN, 113, 123 hàm lỗi entropy chéo, 60 CRf, 359 Hàm mục tiêu, 230 Cây quyết định, 44 hàm nhân hoá, 101 cây quyết định, 44, 193 hàm phân hoạch, 345

<!-- Page 420 -->
394 CHỈ MỤC hàm phân lớp tối ưu, 35 lặp theo chính sách, 216 hàm sigmoid, 36 lặp theo giá trị, 209 hàm tuyến tính, 36 lớp chuẩn hoá loạt, 126 hệ số chiết khấu, 206 lớp gộp, 123 học bán giám sát, 15 lớp nơ-ron, 59 học chuyển đổi, 17 lớp triệt tiêu ngẫu nhiên, 125 học chủ động, 16 lớp tích chập, 117 học có giám sát, 11 MAP, 301 học hàm Q, 219 MDP, 204 học không giám sát, 13 MLE, 38, 318 học kết hợp, 18, 244 MLP, 61, 125 học máy, 1, 4 MNIST, 135 học trực tuyến, 17 MobileNet, 132 học tăng cường, 14 mô hình sinh, 296 học tự giám sát, 15 mô hình đồ thị xác suất, 334 học đa nhiệm vụ, 16 Mạng Bayes, 334, 340 hồi quy Logistic, 36 mạng nơ-ron nhiều lớp, 58, 61 hồi quy tuyến tính, 178 mạng xương sống, 127 hội tụ, 68 nhiệm vụ, 8 ID3, 47 ImageNet, 136 PCA, 271 Inception, 128 perceptron, 86 phân lớp tuyến tính, 86 khoảng cách KL, 298, 321 phân tích thành phần chính, kinh nghiệm, 3 271 KNN, 42 phép toán tự chú ý, 161 lan truyền ngược, 64 phương pháp bagging, 245 LASSO, 287 phương pháp nhân hoá, 101, likelihood, 37 103 LSTM, 158 phương sai, 176 lấy mẫu, 296 phương trình Bellman, 209

<!-- Page 421 -->
CHỈ MỤC 395 phương trình chuẩn tắc, 182 trung bình bình phương sai số, Pytorch, 77 13, 175 trích chọn đặc trưng, 283 quy hoạch động, 209 trường ngẫu nhiên Markov, 334, quỹ đạo, 205 345 relu, 59 tính chất Markov, 203 ResNet, 130 Tăng cường bằng đạo hàm, 256 RNN, 153 tỉ lệ lỗi, 30 RSS, 181 tỉ lệ lỗi trung bình, 28 rủi ro kì vọng, 30 Tối thiểu hóa rủi ro thực nghiệm, rủi ro thực nghiệm, 30 31 rừng ngẫu nhiên, 248 tự giám sát, 280 SGD, 72 VGG, 127 SMO, 100 vòng đời mô hình, 18 softmax, 60 vòng đời phát triển, 372 Spearman, 284 vùng tiếp nhận, 118 suy luận, 347 XGBoost, 261 SVM, 85, 90 xác suất lỗi, 29 SVM lề cứng, 91 SVM lề mềm, 95 điểm số, 36 sự tráo đổi giữa độ lệch và phương đánh giá mô hình, 183 sai, 177 đặc trưng ẩn, 63 định lý PAC, 31 thu thập dữ liệu, 373 độ hợp lý, 37, 299 thuật toán học máy, 3 độ lệch, 176 thuật toán lan truyền ngược, 64 ước lượng hợp lý cực đại, 38, thông tin tương hỗ, 285 299 Transformer, 161 ước lượng mật độ, 297 triển khai, 380 triển khai mô hình, 18 triệt tiêu đạo hàm, 131

<!-- Page 422 -->
396 CHỈ MỤC