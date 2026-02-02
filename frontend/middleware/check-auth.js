export default async function ({ store }) {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  const username = store.getters['auth/getUsername']
  const lastCheckedAt = store.getters['auth/getLastCheckedAt']
  const shouldRecheck = Date.now() - (lastCheckedAt || 0) > 30 * 1000

  if (!isAuthenticated || !username || shouldRecheck) {
    await store.dispatch('auth/initAuth')
  }
}
