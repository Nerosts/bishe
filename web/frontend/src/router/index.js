import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import EventList from '../views/EventList.vue'
import MyRegistrations from '../views/MyRegistrations.vue'
import EventDetail from '../views/EventDetail.vue'
import AdminReview from '../views/AdminReview.vue'
import AdminStats from '../views/AdminStats.vue'
import AdminCheckins from '../views/AdminCheckins.vue'
import AdminUsers from '../views/AdminUsers.vue'
import OrganizerPublish from '../views/OrganizerPublish.vue'
import OrganizerMyEvents from '../views/OrganizerMyEvents.vue'
import OrganizerEventRegistrations from '../views/OrganizerEventRegistrations.vue'
import OrganizerEditEvent from '../views/OrganizerEditEvent.vue'
import OrganizerEventQrcode from '../views/OrganizerEventQrcode.vue'
import OrganizerCheckinStats from '../views/OrganizerCheckinStats.vue'
import CheckinPage from '../views/CheckinPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: {
      public: true
    }
  },
  {
    path: '/home',
    name: 'home',
    component: Home,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/events',
    name: 'events',
    component: EventList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/my-registrations',
    name: 'my-registrations',
    component: MyRegistrations,
    meta: {
      requiresAuth: true,
      roles: ['student']
    }
  },
  {
    path: '/events/:id',
    name: 'event-detail',
    component: EventDetail,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/checkin',
    name: 'checkin',
    component: CheckinPage,
    meta: {
      public: true
    }
  },

  {
    path: '/admin/review',
    name: 'admin-review',
    component: AdminReview,
    meta: {
      requiresAuth: true,
      roles: ['admin']
    }
  },
  {
    path: '/admin/stats',
    name: 'admin-stats',
    component: AdminStats,
    meta: {
      requiresAuth: true,
      roles: ['admin']
    }
  },
  {
    path: '/admin/checkins',
    name: 'admin-checkins',
    component: AdminCheckins,
    meta: {
      requiresAuth: true,
      roles: ['admin']
    }
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: AdminUsers,
    meta: {
      requiresAuth: true,
      roles: ['admin']
    }
  },

  {
    path: '/organizer/publish',
    name: 'organizer-publish',
    component: OrganizerPublish,
    meta: {
      requiresAuth: true,
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/my-events',
    name: 'organizer-my-events',
    component: OrganizerMyEvents,
    meta: {
      requiresAuth: true,
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/events/:id/registrations',
    name: 'organizer-event-registrations',
    component: OrganizerEventRegistrations,
    meta: {
      requiresAuth: true,
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/events/:id/edit',
    name: 'organizer-edit-event',
    component: OrganizerEditEvent,
    meta: {
      requiresAuth: true,
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/events/:id/qrcode',
    name: 'organizer-event-qrcode',
    component: OrganizerEventQrcode,
    meta: {
      requiresAuth: true,
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/events/:id/checkin-stats',
    name: 'organizer-checkin-stats',
    component: OrganizerCheckinStats,
    meta: {
      requiresAuth: true,
      roles: ['organizer']
    }
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')
  const isLoggedIn = !!userId

  // 已登录用户访问登录页，直接去首页
  if (to.path === '/login' && isLoggedIn) {
    next('/home')
    return
  }

  // 公开页面直接放行
  if (to.meta.public) {
    next()
    return
  }

  // 需要登录但未登录
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
    return
  }

  // 需要角色校验
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    if (!role || !to.meta.roles.includes(role)) {
      next('/home')
      return
    }
  }

  next()
})

export default router