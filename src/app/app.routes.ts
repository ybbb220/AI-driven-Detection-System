import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { ProfileComponent } from './pages/profile/profile.component';
import { LayoutComponent } from './layout/layout.component';
import { LoginComponent } from './pages/login/login.component';
// K E Y 1: 引入 PersonalspaceComponent
import { PersonalspaceComponent } from './pages/personalspace/personalspace.component';

// 【关键新增】引入用于展示结果详情的组件
import { AnalysisDetailComponent } from './pages/analysis-detail/analysis-detail.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
    {
        path: 'login',
        component: LoginComponent
    },
    {
        path: '',
        redirectTo: 'login',
        pathMatch: 'full'
    },
    {
        path: '',
        component: LayoutComponent,
        children: [
            { path: 'home', component: HomeComponent },
            { path: 'profile', component: ProfileComponent, canActivate: [authGuard] },
            { path: 'personalspace', component: PersonalspaceComponent, canActivate: [authGuard] },

            // ===================================================
            // 【关键新增】添加结果详情页路由
            // :id 是一个路由参数，用于传递分析记录的ID
            {
                path: 'analysis/detail/:id',
                component: AnalysisDetailComponent
            },
            // ===================================================
        ]
    }
];
