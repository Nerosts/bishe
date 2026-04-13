import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import EventList from '../views/EventList.vue'
import MyRegistrations from '../views/MyRegistrations.vue'
import EventDetail from '../views/EventDetail.vue'
import AdminReview from '../views/AdminReview.vue'
import AdminStats from '../views/AdminStats.vue'
import OrganizerPublish from '../views/OrganizerPublish.vue'
import OrganizerMyEvents from '../views/OrganizerMyEvents.vue'
import OrganizerEventRegistrations from '../views/OrganizerEventRegistrations.vue'
import OrganizerEditEvent from '../views/OrganizerEditEvent.vue'
import OrganizerEventQrcode from '../views/OrganizerEventQrcode.vue'
import CheckinPage from '../views/CheckinPage.vue'
import OrganizerCheckinStats from '../views/OrganizerCheckinStats.vue'
import AdminCheckins from '../views/AdminCheckins.vue'
import AdminUsers from '../views/AdminUsers.vue'
import Forbidden from '../views/Forbidden.vue'
import NotFound from '../views/NotFound.vue'

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
    component: Home
  },

  {
    path: '/events',
    name: 'events',
    component: EventList,
    meta: {
      roles: ['student']
    }
  },
  {
    path: '/my-registrations',
    name: 'my-registrations',
    component: MyRegistrations,
    meta: {
      roles: ['student']
    }
  },
  {
    path: '/events/:id',
    name: 'event-detail',
    component: EventDetail
  },

  {
    path: '/admin/review',
    name: 'admin-review',
    component: AdminReview,
    meta: {
      roles: ['admin']
    }
  },
  {
    path: '/admin/stats',
    name: 'admin-stats',
    component: AdminStats,
    meta: {
      roles: ['admin']
    }
  },
  {
    path: '/admin/checkins',
    name: 'admin-checkins',
    component: AdminCheckins,
    meta: {
      roles: ['admin']
    }
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: AdminUsers,
    meta: {
      roles: ['admin']
    }
  },

  {
    path: '/organizer/publish',
    name: 'organizer-publish',
    component: OrganizerPublish,
    meta: {
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/my-events',
    name: 'organizer-my-events',
    component: OrganizerMyEvents,
    meta: {
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/events/:id/registrations',
    name: 'organizer-event-registrations',
    component: OrganizerEventRegistrations,
    meta: {
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/events/:id/edit',
    name: 'organizer-edit-event',
    component: OrganizerEditEvent,
    meta: {
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/events/:id/qrcode',
    name: 'organizer-event-qrcode',
    component: OrganizerEventQrcode,
    meta: {
      roles: ['organizer']
    }
  },
  {
    path: '/organizer/events/:id/checkin-stats',
    name: 'organizer-checkin-stats',
    component: OrganizerCheckinStats,
    meta: {
      roles: ['organizer']
    }
  },

  {
    path: '/checkin',
    name: 'checkin-page',
    component: CheckinPage,
    meta: {
      public: true
    }
  },

  {
    path: '/forbidden',
    name: 'forbidden',
    component: Forbidden,
    meta: {
      public: true
    }
  },

  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
    meta: {
      public: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')

  if (to.meta.public) {
    next()
    return
  }

  if (!userId || !role) {
    next('/login')
    return
  }

  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    if (!to.meta.roles.includes(role)) {
      next({
        path: '/forbidden',
        query: {
          from: to.fullPath
        }
      })
      return
    }
  }

  next()
})

export default router