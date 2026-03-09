import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzButtonModule } from 'ng-zorro-antd/button';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
   imports: [
    CommonModule,
    NzTableModule,
    NzButtonModule,
  ]
})
export class ProfileComponent implements OnInit {
  data = [
    { text: '这是第一次检测的文本内容，很长很长很长很长很长很长很长很长很长很长。', result: true },
    { text: '第二次检测文本内容。', result: false },
    { text: '第三次检测文本内容，内容略长。', result: true },
    { text: '第四次检测文本内容。', result: false },
    { text: '第五次检测文本内容。', result: true }
  ];
  constructor() { }
    viewText(item: any) {
    alert(item.text);
  }
  ngOnInit() {
  }

}
