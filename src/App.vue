<template>
  <div style="padding: 20px;">
    <h1>OneDrive PKCE授权（内网私有部署）</h1>
    <button @click="startAuth" :disabled="loading">
      {{ loading ? '授权中...' : '点击授权OneDrive' }}
    </button>
    <div style="margin-top: 20px; white-space: pre-wrap;">
      {{ result }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

// 配置（替换为你的实际配置）
const CONFIG = {
  clientId: '5846bd51-d602-4afa-9d54-8d0f3ddaad2e', // 替换为Entra ID的客户端ID
  redirectUri: 'http://localhost:5173/callback', // 前端内网地址（与Entra ID一致）
  scope: 'Files.ReadWrite.All User.Read',
  backendBaseUrl: 'http://localhost:18080' // 后端内网地址
};

const loading = ref(false);
const result = ref('');

// 1. 生成PKCE挑战码
const generatePKCECodes = async () => {
  // 生成code_verifier（64位随机字符串）
  const codeVerifier = Array.from(crypto.getRandomValues(new Uint8Array(32)))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
  
  // 生成code_challenge（SHA256 + Base64URL）
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);
  const hash = await crypto.subtle.digest('SHA-256', data);
  const codeChallenge = btoa(String.fromCharCode(...new Uint8Array(hash)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
  
  // 保存code_verifier到localStorage
  localStorage.setItem('pkce_code_verifier', codeVerifier);
  return codeChallenge;
};

// 2. 启动授权流程
const startAuth = async () => {
  loading.value = true;
  result.value = '';
  try {
    //  调用后端生成 auth url
    const params = new URLSearchParams({
      redirect_uri: CONFIG.redirectUri,
      scope: CONFIG.scope,
    });

    const res = await axios.get(`${CONFIG.backendBaseUrl}/onedrive/oauthurl?${params.toString()}`);
    if (!res.data.success) {
      throw new Error(`获取授权URL失败：${res.data.message}`);
    }
    const authUrl = res.data.authorization_url;

    // 跳转授权页
    window.location.href = authUrl;
  } catch (e) {
    result.value = `生成PKCE失败：${e.message}`;
    loading.value = false;
  }
};

// 3. 处理授权回调
const handleCallback = async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  if (!code) return;

  loading.value = true;
  result.value = '授权码已获取，正在调用后端兑换令牌...';
  
  try {
    // 获取本地存储的code_verifier
    const codeVerifier = localStorage.getItem('pkce_code_verifier');
    if (!codeVerifier) throw new Error('未找到PKCE验证码');

    // 调用后端兑换令牌
    const res = await axios.post(`${CONFIG.backendBaseUrl}/onedrive/token`, {
      code,
      redirect_uri: CONFIG.redirectUri,
    });

    if (res.data.success) {
      result.value = '令牌兑换成功！\n正在获取OneDrive文件列表...';
      // 调用后端获取OneDrive文件
      const fileRes = await axios.get(`${CONFIG.backendBaseUrl}/onedrive/list`);
      result.value = `OneDrive根目录文件列表：\n${JSON.stringify(fileRes.data, null, 2)}`;
      // 清除URL中的code参数
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      result.value = `兑换失败：${res.data.message}`;
    }
  } catch (e) {
    result.value = `回调处理失败：${e.message}`;
  } finally {
    loading.value = false;
  }
};

// 页面加载时检查是否是回调页
if (window.location.search.includes('code=')) {
  handleCallback();
}
</script>

<style scoped>
button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
}
button:disabled {
  background: #999;
  cursor: not-allowed;
}
</style>