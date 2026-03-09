import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  // 简单的 Token 检查逻辑（实际应用中应结合服务校验 Token 有效性）
  const token = localStorage.getItem('access_token'); 

  if (token) {
    return true; // 允许放行
  } else {
    router.navigate(['/login']); // 未登录则踢回登录页
    return false;
  }
};
