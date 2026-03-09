import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router'; // 关键：获取路由参数
import { AiCheckerService } from '../../services/ai-checker.service';

// 引入 Ant Design 模块用于美化和功能 (移除 NzMessageService 依赖)
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzDividerModule } from 'ng-zorro-antd/divider';
import { NzProgressModule } from 'ng-zorro-antd/progress';
import { NzTagModule } from 'ng-zorro-antd/tag';


@Component({
  selector: 'app-analysis-detail',
  standalone: true,
  imports: [
    CommonModule,
    // 【导入所有需要的 Ant Design 模块】
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
    // 属性保持不变，已添加 public
  public analysisId: number | null = null;
  public detail: any = null;
  public isLoading: boolean = true;
  public errorMessage: string = '';

  constructor(
    private route: ActivatedRoute, // 注入 ActivatedRoute
    private aiService: AiCheckerService,
    // 【关键修改：移除对 private message: NzMessageService 的注入】
  ) { }

  ngOnInit(): void {
    // 从路由中订阅 ID 参数，并触发数据加载
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.analysisId = +id; // 将字符串转换为数字
        this.fetchAnalysisDetail();
      } else {
        this.errorMessage = '错误：未找到分析记录ID。';
        this.isLoading = false;
        // 不再调用 this.message.error()
      }
    });
  }

  public fetchAnalysisDetail(): void {
    if (!this.analysisId) return;

    this.isLoading = true;
    this.errorMessage = '';

    this.aiService.getAnalysisDetail(this.analysisId).subscribe({
      next: (response) => {
        this.detail = response.result; // 假设后端返回 { result: {...} }
        this.isLoading = false;
        // 成功后不再调用 this.message.success()
      },
      error: (err) => {
        this.errorMessage = '加载详情失败：' + (err.error?.message || '服务器或网络问题');
        this.isLoading = false;
        // 错误后不再调用 this.message.error()
        console.error('加载详情 API 失败:', err);
      }
    });
  }

  // 辅助方法：根据概率获取进度条状态
  public getProgressStatus(probability: number): string {
    if (probability < 0.3) return 'success';
    if (probability < 0.7) return 'active';
    return 'exception';
  }
}
