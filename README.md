# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).


# 创建Vue项目(optional)
npm create vite@latest onedrive-pkce-front -- --template vue
cd onedrive-pkce-front
npm install

# 安装axios（可选，也可用fetch）
npm install axios

# 启动前端服务（监听内网IP）
npm run dev -- --host 0.0.0.0 --port 5173

# 安装后端依赖
pip install -r requirements.txt

# 启动后端服务
env CLIENT_SECRET=<your_client_secret_here> python main.py --debug
