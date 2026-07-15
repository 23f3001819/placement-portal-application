import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/authstore.js';
import { computed } from 'vue';
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/company',
      name: 'company',
      component: () => import('../views/CompanyView.vue'),
    },
    {
      path: '/createdrive',
      name: 'createdrive',
      component: () => import('../views/CreateDrive.vue'),
    },
    {
      path: '/editdrive/:id',
      name: 'editdrive',
      component: () => import('../views/EditDrive.vue'),
      props: true,
    },
    {
      path: '/drive/:id/applicants',
      name: 'driveapplicants',
      component: () => import('../views/DriveApplicants.vue'),
      props: true,
    },
    {
      path: '/student',
      name: 'student',
      component: () => import('../views/StudentVew.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
    },
  ],
})
router.beforeEach((to, from, next) => {
  const auth_store = useAuthStore();
  const userRoles = auth_store.getUserRoles();

  const companyRoutes = ['company', 'createdrive', 'editdrive', 'driveapplicants'];

  
  if (companyRoutes.includes(to.name)) {
    console.log(userRoles)
    if (!auth_store.isAuthenticated) {
      
      next({ name: 'login' });
      
    } else if (Array.isArray(userRoles) && userRoles.includes('company')) {
      
      console.log(userRoles)
      next();
      
    } else {
      
      next({ name: 'home' }); 
    }
    
  } else if (to.name === 'student') {
    if (!auth_store.isAuthenticated) {
      next({ name: 'login' });
    } else if (Array.isArray(userRoles) && userRoles.includes('student')) {
      next();
    } else {
      next({ name: 'home' });
    }
  } else if (to.name === 'admin') {
    if (!auth_store.isAuthenticated) {
      next({ name: 'login' });
    } else if (Array.isArray(userRoles) && userRoles.includes('admin')) {
      next();
    } else {
      next({ name: 'home' });
    }
  } else if (to.name === 'profile') {
    if (!auth_store.isAuthenticated) {
      next({ name: 'login' });
    } else {
      next();
    }
  } else {
    
    next();
  }
});
export default router