import { Component, OnInit } from '@angular/core';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzLayoutModule } from 'ng-zorro-antd/layout';
import { NzMenuModule } from 'ng-zorro-antd/menu';
import { NzAvatarModule } from 'ng-zorro-antd/avatar';
import { RouterModule, Router } from '@angular/router'; // K E Y: 引入 Router

@Component({
  selector: 'app-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css'],
  // 确保 imports 数组中包含 RouterModule
  imports: [NzIconModule, NzMenuModule, NzLayoutModule, NzAvatarModule, RouterModule],
})
export class LayoutComponent implements OnInit {
  isCollapsed = false;
  protected readonly date = new Date();

  // K E Y: 通过构造函数注入 Router
  username: string | null = null;

  constructor(private router: Router) { }

  ngOnInit() {
    this.username = localStorage.getItem('username');
  }

  // K E Y: 添加登出方法
  logout(): void {
    // 1. 清除认证信息 (假设 Token 存储在 localStorage 中)
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');

    // 2. 可以在这里添加清除全局状态管理（如 NGRX, RXJS Service）的代码
    console.log('用户已登出，本地存储信息已清除。');

    // 3. 导航到登录页面
    this.router.navigate(['/login']);
  }
}
