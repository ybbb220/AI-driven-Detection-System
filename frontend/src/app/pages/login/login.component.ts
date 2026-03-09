import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NzFormModule } from 'ng-zorro-antd/form';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-login',
  imports: [CommonModule, NzInputModule, NzButtonModule, NzFormModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  // 1. 这里是声明组件的属性，用于和 HTML 里的 [(ngModel)] 双向绑定
  studentId = '';
  password = '';

  // 2. 注入 Router 和 HttpClient
  constructor(private router: Router, private http: HttpClient) {}

  login() {
    // 如果没有输入学号或密码，直接返回拦截
    if (!this.studentId || !this.password) {
      alert('请输入学号和密码！');
      return;
    }

    // 3. 构造请求体：前端的 studentId 对应后端的 username 字段
    const loginData = {
      username: this.studentId,
      password: this.password
    };

    console.log('正在发送登录请求...', loginData);

    // 4. 发送 POST 请求到 Flask 后端
    this.http.post<any>('http://127.0.0.1:5000/api/auth/login', loginData).subscribe({
      next: (response) => {
        console.log('登录成功!', response);
        // 将后端返回的真实 access_token 存入本地存储
        localStorage.setItem('access_token', response.access_token);

        // 成功拿到并存好 Token 后，守卫就会放行，此时跳转 home
        this.router.navigate(['/home']);
      },
      error: (err) => {
        console.error('登录失败详情:', err);
        // 如果后端返回 401，通常是账号密码错误
        if (err.status === 401) {
           alert('账号或密码错误，请重试！');
        } else {
           alert('服务器连接失败，请检查后端是否已启动并在 5000 端口运行。');
        }
      }
    });
  }

  // 匿名登录方法
  anonymousLogin() {
    // 设置匿名token
    localStorage.setItem('access_token', 'anonymous');
    // 跳转到首页
    this.router.navigate(['/home']);
  }

  ngOnInit() {}
}
