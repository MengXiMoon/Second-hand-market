import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

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
  {
    path: '/products',
    name: 'Products',
    component: () => import('../views/Products.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/Orders.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('../views/Wallet.vue'),
    meta: { requiresAuth: true }
  },
  // Merchant Routes (Strictly prefixed)
  {
    path: '/merchant',
    name: 'MerchantHome',
    component: () => import('../views/Home.vue'),
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
  // Admin Routes (Strictly prefixed)
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('../views/admin/Users.vue'),
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
  let role = 'user'
  if (path.startsWith('/admin')) {
    role = 'admin'
  } else if (path.startsWith('/merchant')) {
    role = 'merchant'
  }

  const token = localStorage.getItem(`${role}_token`)
  const user = JSON.parse(localStorage.getItem(`${role}_info`) || '{}')

  if (to.meta.requiresAuth && !token) {
    ElMessage.warning('请先登录')
    next('/login')
  } else if (to.meta.requiresAdmin && user.role !== 'admin') {
    ElMessage.error('权限不足')
    next('/')
  } else if (to.meta.requiresMerchant && user.role !== 'merchant' && user.role !== 'admin') {
    ElMessage.error('权限不足')
    next('/')
  } else {
    next()
  }
})

export default router
