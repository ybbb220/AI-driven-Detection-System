import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

// 引入我们创建的服务
import { AiCheckerService } from '../../services/ai-checker.service';

// 引入 Angular 路由相关模块
import { Router, RouterModule } from '@angular/router'; // 【关键修改】引入 Router 服务

// 引入 Ant Design 模块 (标准和新的)
import { NzBreadCrumbModule } from 'ng-zorro-antd/breadcrumb';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzLayoutModule } from 'ng-zorro-antd/layout';
import { NzMenuModule } from 'ng-zorro-antd/menu';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzButtonModule } from 'ng-zorro-antd/button';

// 【HTML 模板所需的新模块】
import { NzAlertModule } from 'ng-zorro-antd/alert';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzCollapseModule } from 'ng-zorro-antd/collapse';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzDividerModule } from 'ng-zorro-antd/divider';


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    NzBreadCrumbModule,
    NzIconModule,
    NzMenuModule,
    NzLayoutModule,
    NzInputModule,
    NzButtonModule,
    RouterModule, // 确保 RouterModule 在 imports 数组中

    // 支持美化后的 HTML 模板
    NzAlertModule,
    NzCardModule,
    NzCollapseModule,
    NzSpinModule,
    NzDividerModule
  ],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  isCollapsed = false;
  protected readonly date = new Date();
 
  // 状态变量
  essayInput: string = '';
  aiResult: any = null;
  isLoading: boolean = false;
  errorMessage: string = '';

  // 【修改构造函数】注入 Router
  constructor(
    private aiService: AiCheckerService,
    private router: Router // 【关键新增】注入 Router 服务
) { }
 
  ngOnInit() {
  }

  submitCheck(): void {
    if (!this.essayInput || this.essayInput.length < 10) {
      this.errorMessage = '请输入至少10个字符的文本进行查重！';
      this.aiResult = null;
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.aiService.checkEssay(this.essayInput).subscribe({
      next: (response) => {
        this.aiResult = response.result;
        this.isLoading = false;
        console.log('API 调用成功，AI 查重结果:', this.aiResult);

        // ========================================================
        // 【核心修改：跳转逻辑】
        const analysisId = response.analysis_id; // 假设后端返回 analysis_id

        if (analysisId) {
            // 跳转到结果详情页，路由路径为 /analysis/detail/分析ID
            this.router.navigate(['/analysis/detail', analysisId]);
        } else {
            // 如果没有 ID（例如，仅展示当前页结果），则停留在当前页
            this.errorMessage = '分析完成，但未获取到记录ID。结果已在当前页面展示。';
        }
        // ========================================================
      },
      error: (err) => {
        this.errorMessage = '查重失败：' + (err.error?.error || '服务器或网络问题');
        this.isLoading = false;
        this.aiResult = null;
        console.error('API 调用失败:', err);
      }
    });
  }
}
