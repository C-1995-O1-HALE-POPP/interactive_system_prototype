// API服务模块 - 处理所有后端API调用
const API_BASE_URL = 'http://localhost:11451';

class RISApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // 通用请求方法
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error(`API请求失败 [${endpoint}]:`, error);
      throw error;
    }
  }

  // 基础系统端点
  async getHealth() {
    return this.request('/health');
  }

  async getSystemInfo() {
    return this.request('/api/system/info');
  }

  // 用户管理端点
  async createUser(userId) {
    return this.request('/api/users', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
  }

  async getUser(userId) {
    return this.request(`/api/users/${userId}`);
  }

  async getUserStats(userId) {
    return this.request(`/api/users/${userId}/stats`);
  }

  // 交互处理端点
  async processInteraction(data) {
    return this.request('/api/interactions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // 角色管理端点
  async getPersonas(userId) {
    return this.request(`/api/personas/${userId}`);
  }

  async getPersona(userId, personaId) {
    return this.request(`/api/personas/${userId}/${personaId}`);
  }

  async updatePersona(userId, personaId, data) {
    return this.request(`/api/personas/${userId}/${personaId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // 回忆管理端点
  async getMemories(userId, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = `/api/memories/${userId}${queryString ? `?${queryString}` : ''}`;
    return this.request(endpoint);
  }

  async getMemory(userId, memoryId) {
    return this.request(`/api/memories/${userId}/${memoryId}`);
  }

  async updateMemory(userId, memoryId, data) {
    return this.request(`/api/memories/${userId}/${memoryId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // 情绪分析端点
  async analyzeEmotion(data) {
    return this.request('/api/emotions/pad', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getEmotionTrends(userId, period = 'week') {
    return this.request(`/api/emotions/${userId}/trends?period=${period}`);
  }

  // 报告生成端点
  async getWeeklyReport(userId) {
    return this.request(`/api/reports/${userId}/weekly`);
  }

  async getMonthlyReport(userId) {
    return this.request(`/api/reports/${userId}/monthly`);
  }

  // 多媒体识别端点
  async recognizeAudio(formData) {
    return this.request('/api/multimedia/recognize_audio', {
      method: 'POST',
      headers: {}, // 让浏览器自动设置Content-Type
      body: formData,
    });
  }

  async recognizeImage(formData) {
    return this.request('/api/multimedia/recognize_image', {
      method: 'POST',
      headers: {}, // 让浏览器自动设置Content-Type
      body: formData,
    });
  }

  async analyzeMultimedia(data) {
    return this.request('/api/multimedia/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // 百炼平台LLM服务端点
  async getLLMStatus() {
    return this.request('/api/llm/status');
  }

  async llmChat(data) {
    return this.request('/api/llm/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async llmGenerate(data) {
    return this.request('/api/llm/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async llmEmotionAnalysis(data) {
    return this.request('/api/llm/emotion_analysis', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async llmPersonaInsights(userId, personaId) {
    return this.request(`/api/llm/persona_insights/${userId}/${personaId}`);
  }

  async llmChatWithPersona(userId, personaId, data) {
    return this.request(`/api/llm/chat_with_persona/${userId}/${personaId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async llmMultimodalAnalysis(data) {
    return this.request('/api/llm/multimodal_analysis', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // 文件上传端点
  async uploadAudio(formData) {
    return this.request('/api/upload/audio', {
      method: 'POST',
      headers: {}, // 让浏览器自动设置Content-Type
      body: formData,
    });
  }

  async uploadImage(formData) {
    return this.request('/api/upload/image', {
      method: 'POST',
      headers: {}, // 让浏览器自动设置Content-Type
      body: formData,
    });
  }
}

// 创建全局API服务实例
export const apiService = new RISApiService();
export default apiService;

