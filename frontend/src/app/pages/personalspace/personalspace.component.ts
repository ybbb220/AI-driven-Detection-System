// src/app/pages/personalspace/personalspace.component.ts

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'; // 核心 Angular 模块

// 导入所有 Ant Design 模块（独立组件模式）
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzGridModule } from 'ng-zorro-antd/grid';
import { NzAvatarModule } from 'ng-zorro-antd/avatar';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzDividerModule } from 'ng-zorro-antd/divider';
import { NzListModule } from 'ng-zorro-antd/list';


// 接口定义（不变）
interface Activity {
  icon: string;
  title: string;
  time: string;
}

@Component({
  selector: 'app-personalspace',
  // 关键：启用独立组件模式
  standalone: true,
  templateUrl: './personalspace.component.html',
  styleUrls: ['./personalspace.component.css'],

  // K E Y: 所有模板依赖的模块都放在这里
  imports: [
    CommonModule,

    // Ant Design 模块
    NzCardModule,
    NzGridModule,
    NzAvatarModule,
    NzIconModule,
    NzButtonModule,
    NzDividerModule,
    NzListModule
    // 如果有路由，这里可能还需要 RouterModule
  ]
})
export class PersonalspaceComponent implements OnInit {

  // 模拟用户数据
  userInfo = {
    name: '罗欣宇',
    studentId: '2022001',
    major: '计算机科学与技术',
    role: '学生',
    signature: '志存高远，脚踏实地。'
  };

  // 模拟最近活动数据
  recentActivities: Activity[] = [
    { icon: 'book', title: '提交了第3次作业：操作系统', time: '5分钟前' },
    { icon: 'calendar', title: '预约了自习室：A栋303', time: '昨天 15:00' },
    { icon: 'notification', title: '收到了新的通知：关于考试安排', time: '前天 09:00' },
    { icon: 'message', title: '回复了老师的邮件：毕业设计主题', time: '上周一' },
  ];

  // constructor(private router: Router) { } // 如果需要路由
  constructor() { }

  ngOnInit(): void {
  }

  // 绑定到 HTML 的方法
  goToSettings(): void {
    console.log('跳转到个人设置页面...');
  }

  // 绑定到 HTML 的方法
  viewMoreActivities(): void {
    console.log('加载更多活动记录...');
  }
}
