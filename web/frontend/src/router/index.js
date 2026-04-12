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
    component: Login
  },
  {
    path: '/home',
    name: 'home',
    component: Home
  },
  {
    path: '/events',
    name: 'events',
    component: EventList
  },
  {
    path: '/my-registrations',
    name: 'my-registrations',
    component: MyRegistrations
  },
  {
    path: '/events/:id',
    name: 'event-detail',
    component: EventDetail
  },
  {
    path: '/admin/review',
    name: 'admin-review',
    component: AdminReview
  },
  {
    path: '/admin/stats',
    name: 'admin-stats',
    component: AdminStats
  },
  {
    path: '/admin/checkins',
    name: 'admin-checkins',
    component: AdminCheckins
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: AdminUsers
  },
  {
    path: '/organizer/publish',
    name: 'organizer-publish',
    component: OrganizerPublish
  },
  {
    path: '/organizer/my-events',
    name: 'organizer-my-events',
    component: OrganizerMyEvents
  },
  {
    path: '/organizer/events/:id/registrations',
    name: 'organizer-event-registrations',
    component: OrganizerEventRegistrations
  },
  {
    path: '/organizer/events/:id/edit',
    name: 'organizer-edit-event',
    component: OrganizerEditEvent
  },
  {
    path: '/organizer/events/:id/qrcode',
    name: 'organizer-event-qrcode',
    component: OrganizerEventQrcode
  },
  {
    path: '/organizer/events/:id/checkin-stats',
    name: 'organizer-checkin-stats',
    component: OrganizerCheckinStats
  },
  {
    path: '/checkin',
    name: 'checkin',
    component: CheckinPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router