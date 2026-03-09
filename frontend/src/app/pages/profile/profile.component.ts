import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
   imports: [
    CommonModule,
    NzTableModule,
    NzButtonModule,
    HttpClientModule
  ]
})
export class ProfileComponent implements OnInit {
  data: Array<{text:string,result:boolean}> = [];
  isAnonymous: boolean = false;

  constructor(private http: HttpClient) { }

  viewText(item: any) {
    alert(item.text);
  }

  ngOnInit() {
    const token = localStorage.getItem('access_token');
    const username = localStorage.getItem('username');

    if (!token || token === 'anonymous' || !username) {
      this.isAnonymous = true;
      return; // no history for anonymous or missing user info
    }

    // fetch history from backend using existing /history endpoint
    const url = 'http://127.0.0.1:5000/api/analysis/history';
    console.log('请求历史记录', url, token);
    this.http.get<any>(url, {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (resp) => {
        console.log('历史记录响应', resp);
        // resp has {analyses: [...], total, pages, current_page}
        this.data = (resp.analyses || []).map((a: any) => ({
          text: a.original_text,
          result: a.ai_probability > 0.5
        }));
      },
      error: (err) => {
        console.error('获取历史记录失败', err);
      }
    });
  }

}
