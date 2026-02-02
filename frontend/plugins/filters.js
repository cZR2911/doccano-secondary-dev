import Vue from 'vue'
import ApiService from '@/services/api.service'

export const truncate = function (text, length, clamp) {
  text = text || ''
  clamp = clamp || '...'
  length = length || 30

  if (text.length <= length) {
    return text
  }

  return text.substring(0, length) + clamp
}

Vue.filter('truncate', truncate)

let interceptorConfigured = false

export default function ({ app, store, redirect }) {
  if (interceptorConfigured) return
  interceptorConfigured = true

  ApiService.instance.interceptors.response.use(
    (response) => response,
    (error) => {
      const status = error?.response?.status
      const url = error?.config?.url || ''
      const currentPath = app?.router?.currentRoute?.path || ''

      if (status && (status === 401 || status === 403)) {
        if (!currentPath.startsWith('/auth') && !url.includes('/auth/login')) {
          store.commit('auth/setAuthenticated', false)
          store.commit('auth/setIsStaff', false)
          store.commit('auth/clearUsername')
          store.commit('auth/setUserId', null)
          store.commit('auth/setLastCheckedAt', Date.now())
          redirect('/auth')
        }
      }

      return Promise.reject(error)
    }
  )
}
