lương nο-ron đầu lón. Trong thực tế của bài toán học máy thông kê, ham số can học không được biét trước, mà chỉ được uóc luông tù dữ liệu. Vì thế, việc xây dựng một mang nο-ron nhiều lóp với số luông nο-ron và số lóp lón hơn được kì vòng là sẽ có kết quả xáp xì tôt hơn.

## 3.2 Huân luyên mô hình mạng nο-ron nhiều lóp

Pha huân luyên của mạng nο-ron MLP sử dụng một thuật toán nội tiếng có tên thuur toán lan truyến nguồn (back propagation). Thuật toán có mục tiêu tính đạo ham của lối $\ell(o,y)$ với tát các trONG số $W_i$ tại các lộ nο-ron. Y tuồng chính của thuật toán này là sử dụng công thức đạo ham hàm hợp để lan truyến nguồnDao ham tù lộ cuối về lộ dâu tiện (nguồn huóng tính toán dâu ra của mạng). Đâu tiện, ta khai triên tù dạng tông quát của ham lối theo công thức là:

$$\delta_i = \underbrace{\frac{\partial \ell(o,y)}{\partial o_i}}_{\in \mathbb{R}^{p_i}} = \underbrace{\left[ \frac{\partial o_{i+1}}{\partial o_i} \right]^T}_{J_{i+1}^T \in \mathbb{R}^{p_i \times p_i+1}} \underbrace{\left[ \frac{\partial \ell(o,y)}{\partial o_{i+1}} \right]}_{\delta_{i+1} \in \mathbb{R}^{p_i+1}} = J_{i+1}^T \delta_{i+1}$$

Trong đó, ma trần Jacobian $J_{i+1} = \left[ \frac{\partial o_{i+1}}{\partial o_i} \right] \in \mathbb{R}^{p_{i+1} \times p_i}$ là ma trầnDao ham của $o_{i+1}$ đối với $o_i$. Vì $o_{i+1} = f_{i+1}(W_{t+1}o_i)$ nên xét phàn tù dòng $j$, có k của ma trần $J_{i+1}$, ta có công thứcDao ham của $o_{i+1}^j$ đối với $o_i^k$ như sau:

$$\frac{\partial o_{i+1}^j}{\partial o_i^k} = \frac{\partial f_{i+1}([w_{i+1}^j]^T o_i)}{\partial o_i^k}$$

$$= f'_{i+1}(\text{net}_{i+1}^j)w_{i+1}^{jk}$$