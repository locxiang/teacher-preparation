import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import mkcert from "vite-plugin-mkcert";

/** @type {import('vite').UserConfig} */
export default {
  plugins: [vue(), mkcert()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
  },
  server: {
    https: true,
    port: 5173,
    host: "0.0.0.0", // 允许外部访问
    proxy: {
      // 后端 API 代理
      // Vite 代理在容器内运行，可以使用 Docker 服务名 backend
      "/api": {
        target: "http://backend:5001",
        changeOrigin: true,
        secure: false,
      },
      // WebSocket 代理
      "/socket.io": {
        target: "http://backend:5001",
        ws: true,
        changeOrigin: true,
      },
      // 科大讯飞声纹 API（如果需要）
      "/api/xunfei-voiceprint": {
        target: "https://office-api-personal-dx.iflyaisol.com",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/xunfei-voiceprint/, ""),
        secure: true,
        configure: (proxy) => {
          proxy.on("proxyReq", (proxyReq, req) => {
            // 转发所有必要的请求头
            const headers = ["content-type", "signature"];
            headers.forEach((header) => {
              if (req.headers[header]) {
                proxyReq.setHeader(header, req.headers[header]);
              }
            });
          });
        },
      },
    },
  },
};
