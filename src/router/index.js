import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false, guestOnly: true }
  },
  // Customer Routes
  {
    path: '/customer',
    name: 'CustomerHome',
    component: () => import('../views/CustomerHome.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/customer/login',
    name: 'CustomerLogin',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/customer/products',
    name: 'CustomerProducts',
    component: () => import('../views/Products.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/customer/cart',
    name: 'CustomerCart',
    component: () => import('../views/Cart.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/customer/favorites',
    name: 'CustomerFavorites',
    component: () => import('../views/Favorites.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/customer/notifications',
    name: 'CustomerNotifications',
    component: () => import('../views/NotificationCenter.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/customer/orders',
    name: 'CustomerOrders',
    component: () => import('../views/Orders.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/customer/wallet',
    name: 'CustomerWallet',
    component: () => import('../views/Wallet.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/customer/chat',
    name: 'CustomerChat',
    component: () => import('../views/Chat.vue'),
    meta: { requiresAuth: true }
  },
  // Merchant Routes
  {
    path: '/merchant/login',
    name: 'MerchantLogin',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/merchant',
    name: 'MerchantHome',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true, requiresMerchant: true }
  },
  {
    path: '/merchant/chat',
    name: 'MerchantChat',
    component: () => import('../views/Chat.vue'),
    meta: { requiresAuth: true, requiresMerchant: true }
  },
  {
    path: '/merchant/products',
    name: 'MerchantProducts',
    component: () => import('../views/Products.vue'),
    meta: { requiresAuth: true, requiresMerchant: true }
  },
  {
    path: '/merchant/my-products',
    name: 'MerchantMyProducts',
    component: () => import('../views/MyProducts.vue'),
    meta: { requiresAuth: true, requiresMerchant: true }
  },
  {
    path: '/merchant/sales',
    name: 'MerchantSales',
    component: () => import('../views/Sales.vue'),
    meta: { requiresAuth: true, requiresMerchant: true }
  },
  {
    path: '/merchant/wallet',
    name: 'MerchantWallet',
    component: () => import('../views/Wallet.vue'),
    meta: { requiresAuth: true, requiresMerchant: true }
  },
  {
    path: '/merchant/reviews',
    name: 'MerchantReviews',
    component: () => import('../views/MerchantReviews.vue'),
    meta: { requiresAuth: true, requiresMerchant: true }
  },
  {
    path: '/merchant/notifications',
    name: 'MerchantNotifications',
    component: () => import('../views/NotificationCenter.vue'),
    meta: { requiresAuth: true, requiresMerchant: true }
  },
  // Admin Routes
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/admin/notifications',
    name: 'AdminNotifications',
    component: () => import('../views/NotificationCenter.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('../views/admin/Users.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/chat',
    name: 'AdminChat',
    component: () => import('../views/Chat.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/all-users',
    name: 'AdminAllUsers',
    component: () => import('../views/admin/AllUsers.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/products',
    name: 'AdminProducts',
    component: () => import('../views/admin/Products.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/all-products',
    name: 'AdminAllProducts',
    component: () => import('../views/admin/AllProducts.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/orders',
    name: 'AdminOrders',
    component: () => import('../views/admin/Orders.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const path = to.path
  
  const queryRole = to.query.role
  let role = 'user'

  if (queryRole && ['user', 'merchant', 'admin'].includes(queryRole)) {
    role = queryRole
    localStorage.setItem('last_active_role', role)
  } else if (path.startsWith('/admin')) {
    role = 'admin'
    localStorage.setItem('last_active_role', 'admin')
  } else if (path.startsWith('/merchant')) {
    role = 'merchant'
    localStorage.setItem('last_active_role', 'merchant')
  } else if (path.startsWith('/customer') || path === '/' || path === '/login' || path === '/register') {
    role = 'user'
    localStorage.setItem('last_active_role', 'user')
  } else {
    role = localStorage.getItem('last_active_role') || 'user'
  }

  const token = localStorage.getItem(`${role}_token`)
  const user = JSON.parse(localStorage.getItem(`${role}_info`) || '{}')

  if (to.meta.requiresAuth && !token) {
    ElMessage.warning('请先登录')
    if (path.startsWith('/admin')) {
      next('/admin/login')
    } else if (path.startsWith('/merchant')) {
      next('/merchant/login')
    } else {
      next('/customer/login')
    }
  } else if (to.meta.requiresAdmin && user.role !== 'admin') {
    ElMessage.error('权限不足')
    next('/admin/login')
  } else if (to.meta.requiresMerchant && user.role !== 'merchant' && user.role !== 'admin') {
    ElMessage.error('权限不足')
    next('/merchant/login')
  } else if (to.meta.guestOnly && token) {
    if (path === '/login' || path === '/register') {
      next()
    } else if (path.startsWith('/admin')) {
      next('/admin/all-users')
    } else if (path.startsWith('/merchant')) {
      next('/merchant/my-products')
    } else {
      next('/customer')
    }
  } else {
    next()
  }
})

export default router
