lương nơ-ron đầu lón. Trong thực tế của bài toán học máy thông kê, ham số cân học không được biét trước, mà chỉ được uóc luông tù dữ liệu. Vì thế, việc xây dựng một mạng nơ-ron nhiều lóp với số luông nơ-ron và số lóp lón hôn được kì vòng là sẽ có kết quả xáp xì tôt hôn.

## 3.2 Huân luyên mô hình mạng nơ-ron nhiều lóp

Pha huân luyên của mạng nơ-ron MLP sử dụng một thuurat toán nội tiếng có tên thuurat toán lan truyến nguồn (back propagation). Thuật toán có mục tiêu tính đạo ham của lối $\ell(o,y)$ với tát các trông số $W_i$ tài các lopcode hàm tù lóp cuối về lopcode tiện (nguồn huóng tính toán đầu ra của mạng). Đâu tiện, ta khai triên tù dạng tông quant của ham lối theo công thức là:

$$\delta_i = \underbrace{\frac{\partial \ell(o,y)}{\partial o_i}}_{\in \mathbb{R}^{p_i}} = \underbrace{\left[ \frac{\partial o_{i+1}}{\partial o_i} \right]^T}_{\substack{J_{i+1}^T \in \mathbb{R}^{p_i} \times p_{i+1}}} \underbrace{\left[ \frac{\partial \ell(o,y)}{\partial o_{i+1}} \right]}_{\delta_{i+1} \in \mathbb{R}^{p_{i+1}}} = J_{i+1}^T \delta_{i+1}$$

Trong đó, ma trần Jacobian $J_{i+1} = \left[ \frac{\partial o_{i+1}}{\partial o_i} \right] \in \mathbb{R}^{p_{i+1} \times p_i}$ là ma trầnDao hàm của $o_{i+1}$ với $o_i$. Vì $o_{i+1} = f_{i+1}(W_{t+1}o_i)$ nên xét phàn tù dòng $j$, có k của ma trần $J_{i+1}$, ta có công thứcDao hàm của $o_{i+1}^j$ với $o_i^k$ như sau:

$$\frac{\partial o_{i+1}^j}{\partial o_i^k} = \frac{\partial f_{i+1}([w_{i+1}^j]^T o_i)}{\partial o_i^k}$$

$$= f'_{i+1} (\text{net}_{i+1}^j) w_{i+1}^{jk}$$