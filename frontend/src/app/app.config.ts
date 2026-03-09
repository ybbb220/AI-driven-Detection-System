import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';

// 【关键依赖】用于 Angular 动画和浏览器特性
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http'; // 【优化：添加 withInterceptorsFromDi】

// 【Ant Design 核心服务】
import { zh_CN, provideNzI18n } from 'ng-zorro-antd/i18n';
import { registerLocaleData } from '@angular/common';
import en from '@angular/common/locales/en';

// 【Ant Design 核心服务提供者】
import { provideNzIcons } from 'ng-zorro-antd/icon';

// 【图标相关】
import { IconDefinition } from '@ant-design/icons-angular';
import * as AllIcons from '@ant-design/icons-angular/icons';

registerLocaleData(en);

// 收集所有 Ant Design 图标
const antDesignIcons = AllIcons as {
  [key: string]: IconDefinition;
};
const icons: IconDefinition[] = Object.keys(antDesignIcons).map(key => antDesignIcons[key]);


export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),

    // ==========================================================
    // 1. 路由和 HTTP 放在前面
    provideRouter(routes),
    provideHttpClient(withInterceptorsFromDi()), // 优化 HttpClient 配置
    // 2. 动画放在 Ant Design 服务之前
    provideAnimations(),

    // 3. Ant Design 核心配置
    provideNzI18n(zh_CN),
    provideNzIcons(icons),
   
    // ==========================================================
  ]
};
