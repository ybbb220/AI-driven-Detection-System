// src/app/services/ai-checker.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// 定义数据接口以增强类型安全 (匹配 Flask 后端返回的结构)
interface AiResultResponse {
  message: string;
  analysis_id?: number;
  // ... 忽略其他字段 ...
  result: {
    ai_probability: number;
    human_probability: number;
    sentence_analysis: any[]; // 简化，不必完整定义
    original_text: string; // 添加原始文本字段，方便详情页展示
  }
}

@Injectable({
  providedIn: 'root'
})
// ==========================================================
// 【关键修正：合并为一个类定义】
export class AiCheckerService {

  // API 基准路径
  private BASE_API_URL = 'http://127.0.0.1:5000/api/analysis';

  constructor(private http: HttpClient) { }

  /**
   * 调用 Flask 后端 AI 查重 API (POST)
   * 完整路径: /api/analysis/analyze
   * @param text 待查重的文本
   */
  checkEssay(text: string): Observable<AiResultResponse> {
    const url = `${this.BASE_API_URL}/analyze`; // 拼接完整路径
    const body = {
      text: text
    };

    // 将本地存储的 token 添加到请求头（如果存在）
    const token = localStorage.getItem('access_token');
    const options = token
      ? { headers: { Authorization: `Bearer ${token}` } }
      : {};

    // 发送 POST 请求
    return this.http.post<AiResultResponse>(url, body, options);
  }

  getAnalysisDetail(id: number): Observable<AiResultResponse> { // 使用相同的返回接口
    // 假设后端有一个 GET /api/analysis/{id} 的接口
    const url = `${this.BASE_API_URL}/${id}`;
    const token = localStorage.getItem('access_token');
    const options = token
      ? { headers: { Authorization: `Bearer ${token}` } }
      : {};
    return this.http.get<AiResultResponse>(url, options);
  }
}
// ==========================================================
