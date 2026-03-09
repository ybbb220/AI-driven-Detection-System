import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router'; // 关键：获取路由参数
import { AiCheckerService } from '../../services/ai-checker.service';

// 引入 Ant Design 模块用于美化
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzDividerModule } from 'ng-zorro-antd/divider';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzProgressModule } from 'ng-zorro-antd/progress'; // 用于展示进度条
import { NzTagModule } from 'ng-zorro-antd/tag'; // 用于标记句子

@Component({
  selector: 'app-analysis-detail',
  standalone: true,
  imports: [
    CommonModule,
    NzCardModule,
    NzSpinModule,
    NzDividerModule,
    NzProgressModule,
    NzTagModule
  ],
  templateUrl: './analysis-detail.component.html',
  styleUrls: ['./analysis-detail.component.css']
})
export class AnalysisDetailComponent implements OnInit {
  analysisId: number | null = null;
  detail: any = null;
  isLoading: boolean = true;
  errorMessage: string = '';

  constructor(
    private route: ActivatedRoute, // 注入 ActivatedRoute
    private aiService: AiCheckerService,
    private message: NzMessageService // 用于显示错误提示
  ) { }

  ngOnInit(): void {
    // 1. 从路由中订阅 ID 参数
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.analysisId = +id; // 将字符串转换为数字
        this.fetchAnalysisDetail();
      } else {
        this.errorMessage = '错误：未找到分析记录ID。';
        this.isLoading = false;
        this.message.error(this.errorMessage);
      }
    });
  }

  fetchAnalysisDetail(): void {
    if (!this.analysisId) return;

    this.isLoading = true;
    this.errorMessage = '';

    // 2. 调用服务获取详情
    this.aiService.getAnalysisDetail(this.analysisId).subscribe({
      next: (response) => {
        this.detail = response.result; // 假设后端返回 { result: {...} }
        this.isLoading = false;
        this.message.success('分析详情加载成功！');
      },
      error: (err) => {
        this.errorMessage = '加载详情失败：' + (err.error?.message || '服务器或网络问题');
        this.isLoading = false;
        this.message.error(this.errorMessage);
        console.error('加载详情 API 失败:', err);
      }
    });
  }

  // 辅助方法：获取进度条状态
  getProgressStatus(probability: number): string {
    if (probability < 0.3) return 'success';
    if (probability < 0.7) return 'active';
    return 'exception';
  }
}
