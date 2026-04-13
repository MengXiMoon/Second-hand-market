export const getOrderStatusText = (status) => {
  const map = {
    'ordered': '已下单',
    'paid': '已付款',
    'shipped': '已发货',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return map[status] || status
}

export const getOrderStatusType = (status) => {
  const map = {
    'ordered': 'info',
    'paid': 'success',
    'shipped': 'warning',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return map[status] || 'info'
}

export const getProductStatusText = (status) => {
  const map = {
    'pending': '待审核',
    'approved': '已上架',
    'rejected': '已拒绝',
    'sold_out': '已售罄'
  }
  return map[status] || status
}

export const getProductStatusType = (status) => {
  const map = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'sold_out': 'info'
  }
  return map[status] || 'info'
}

export const getTransactionTypeText = (type) => {
  const map = {
    'recharge': '充值',
    'purchase': '购买商品',
    'sale': '销售商品',
    'refund': '退款',
    'withdraw': '提现',
    'commission': '平台佣金'
  }
  return map[type] || type
}

export const getRoleText = (role) => {
  const map = {
    'user': '普通用户',
    'merchant': '商家',
    'admin': '管理员'
  }
  return map[role] || role
}

export const getRoleType = (role) => {
  const map = {
    'user': 'primary',
    'merchant': 'warning',
    'admin': 'danger'
  }
  return map[role] || 'info'
}
